"""Train PolicyValueNet from a bootstrap ``.npz`` dataset."""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np

# Allow ``python Training/train_policy_value.py`` to import project modules.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch
from torch import Tensor, nn
from torch.utils.data import DataLoader, TensorDataset

from AI.neural_model import PolicyValueNet


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def serializable_args(args: argparse.Namespace) -> dict:
    """Convert CLI values such as Path into portable checkpoint metadata."""
    result = vars(args).copy()
    for key, value in result.items():
        if isinstance(value, Path):
            result[key] = str(value)
    return result


def load_dataset(path: str | Path):
    """Load and validate states, one-hot/soft policies, and values."""
    path = Path(path)
    with np.load(path, allow_pickle=False) as data:
        required = {"states", "policies", "values"}
        missing = required.difference(data.files)
        if missing:
            raise ValueError(f"dataset is missing arrays: {sorted(missing)}")

        states = np.asarray(data["states"], dtype=np.float32)
        policies = np.asarray(data["policies"], dtype=np.float32)
        values = np.asarray(data["values"], dtype=np.float32)
        metadata_raw = data["metadata"].item() if "metadata" in data.files else "{}"

    if states.ndim != 4:
        raise ValueError(f"states must have shape (N, 3, H, W), got {states.shape}")
    if policies.ndim != 2:
        raise ValueError(
            f"policies must have shape (N, H*W), got {policies.shape}"
        )
    if values.ndim != 1:
        raise ValueError(f"values must have shape (N,), got {values.shape}")
    if not (len(states) == len(policies) == len(values)):
        raise ValueError(
            "states, policies, and values must have the same number of samples"
        )
    if states.shape[1] != 3 or states.shape[2] != states.shape[3]:
        raise ValueError(
            "states must use the project's 3-plane square board encoding"
        )
    board_size = states.shape[2]
    if policies.shape[1] != board_size * board_size:
        raise ValueError(
            f"policy action count {policies.shape[1]} does not match "
            f"board size {board_size}"
        )
    if not np.isfinite(states).all():
        raise ValueError("states contain NaN or Inf")
    if not np.isfinite(policies).all():
        raise ValueError("policies contain NaN or Inf")
    if not np.isfinite(values).all():
        raise ValueError("values contain NaN or Inf")
    if np.any(values < -1.0) or np.any(values > 1.0):
        raise ValueError("values must be in [-1, 1]")

    policy_sums = policies.sum(axis=1)
    if not np.allclose(policy_sums, 1.0, atol=1e-5):
        raise ValueError("each policy target must sum to 1")
    if np.any(policies < 0):
        raise ValueError("policy targets cannot contain negative values")

    try:
        metadata = json.loads(str(metadata_raw))
    except json.JSONDecodeError:
        metadata = {}

    return states, policies, values, metadata


def make_loaders(
    states: np.ndarray,
    policies: np.ndarray,
    values: np.ndarray,
    batch_size: int,
    validation_split: float,
    seed: int,
):
    """Create deterministic train/validation DataLoaders."""
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero")
    if not 0.0 <= validation_split < 1.0:
        raise ValueError("validation_split must be in [0, 1)")

    generator = np.random.default_rng(seed)
    indices = generator.permutation(len(states))
    validation_count = int(len(states) * validation_split)
    if validation_split > 0 and validation_count == 0 and len(states) > 1:
        validation_count = 1
    if validation_count >= len(states):
        validation_count = len(states) - 1

    validation_indices = indices[:validation_count]
    train_indices = indices[validation_count:]

    train_dataset = TensorDataset(
        torch.from_numpy(states[train_indices]),
        torch.from_numpy(policies[train_indices]),
        torch.from_numpy(values[train_indices]),
    )
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        generator=torch.Generator().manual_seed(seed),
    )

    validation_loader = None
    if validation_count > 0:
        validation_dataset = TensorDataset(
            torch.from_numpy(states[validation_indices]),
            torch.from_numpy(policies[validation_indices]),
            torch.from_numpy(values[validation_indices]),
        )
        validation_loader = DataLoader(
            validation_dataset,
            batch_size=batch_size,
            shuffle=False,
        )

    return train_loader, validation_loader


def compute_losses(
    policy_logits: Tensor,
    predicted_value: Tensor,
    target_policy: Tensor,
    target_value: Tensor,
):
    """Compute the two losses used by the first training version."""
    # This supports both one-hot teacher labels and future MCTS visit
    # distributions.
    log_probs = torch.log_softmax(policy_logits, dim=-1)
    policy_loss = -(target_policy * log_probs).sum(dim=-1).mean()

    value_loss = nn.functional.mse_loss(
        predicted_value.squeeze(-1),
        target_value,
    )
    total_loss = policy_loss + value_loss
    return total_loss, policy_loss, value_loss


def run_epoch(model, loader, optimizer=None, device="cpu"):
    """Run one train or evaluation epoch."""
    is_training = optimizer is not None
    model.train(is_training)
    total_samples = 0
    totals = {"total": 0.0, "policy": 0.0, "value": 0.0}

    context = torch.enable_grad() if is_training else torch.no_grad()
    with context:
        for states, target_policy, target_value in loader:
            states = states.to(device)
            target_policy = target_policy.to(device)
            target_value = target_value.to(device)

            if is_training:
                optimizer.zero_grad(set_to_none=True)

            policy_logits, predicted_value = model(states)
            total_loss, policy_loss, value_loss = compute_losses(
                policy_logits,
                predicted_value,
                target_policy,
                target_value,
            )

            if is_training:
                total_loss.backward()
                optimizer.step()

            batch_size = states.shape[0]
            total_samples += batch_size
            totals["total"] += total_loss.item() * batch_size
            totals["policy"] += policy_loss.item() * batch_size
            totals["value"] += value_loss.item() * batch_size

    if total_samples == 0:
        raise ValueError("cannot run an epoch with zero samples")
    return {key: value / total_samples for key, value in totals.items()}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train PolicyValueNet from a bootstrap npz dataset."
    )
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--validation-split", type=float, default=0.1)
    parser.add_argument("--channels", type=int, default=32)
    parser.add_argument("--value-hidden", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--model-out",
        type=Path,
        default=Path("models/checkpoints/pvnet_bootstrap.pt"),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.epochs <= 0:
        raise ValueError("epochs must be greater than zero")
    if args.learning_rate <= 0:
        raise ValueError("learning-rate must be greater than zero")
    if args.weight_decay < 0:
        raise ValueError("weight-decay cannot be negative")

    set_seed(args.seed)
    device = torch.device(args.device)
    states, policies, values, metadata = load_dataset(args.data)
    if metadata.get("board_size", states.shape[2]) != states.shape[2]:
        raise ValueError("dataset metadata board_size disagrees with states")

    train_loader, validation_loader = make_loaders(
        states,
        policies,
        values,
        batch_size=args.batch_size,
        validation_split=args.validation_split,
        seed=args.seed,
    )

    model = PolicyValueNet(
        board_size=states.shape[2],
        channels=args.channels,
        value_hidden=args.value_hidden,
    ).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )

    print(
        f"data={args.data} samples={len(states)} "
        f"board_size={states.shape[2]} device={device}"
    )
    for epoch in range(1, args.epochs + 1):
        train_metrics = run_epoch(
            model,
            train_loader,
            optimizer=optimizer,
            device=device,
        )
        validation_metrics = None
        if validation_loader is not None:
            validation_metrics = run_epoch(
                model,
                validation_loader,
                optimizer=None,
                device=device,
            )

        message = (
            f"epoch {epoch}/{args.epochs} "
            f"train_total={train_metrics['total']:.4f} "
            f"train_policy={train_metrics['policy']:.4f} "
            f"train_value={train_metrics['value']:.4f}"
        )
        if validation_metrics is not None:
            message += (
                f" val_total={validation_metrics['total']:.4f}"
                f" val_policy={validation_metrics['policy']:.4f}"
                f" val_value={validation_metrics['value']:.4f}"
            )
        print(message)

    model.save_checkpoint(
        args.model_out,
        epoch=args.epochs,
        optimizer_state_dict=optimizer.state_dict(),
        training_config=serializable_args(args),
        final_train_metrics=train_metrics,
        final_validation_metrics=validation_metrics,
    )
    print(f"saved model: {args.model_out}")


if __name__ == "__main__":
    main()
