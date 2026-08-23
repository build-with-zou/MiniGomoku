"""Policy-value neural network for MiniGomoku.

The network receives a board encoded as:

    (batch, 3, board_size, board_size)

and returns:

    policy_logits: (batch, board_size * board_size)
    value:         (batch, 1)

``policy_logits`` are raw scores. They intentionally do not go through
softmax in ``forward`` because training and MCTS need to process logits
differently.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import torch
from torch import Tensor, nn


class PolicyValueNet(nn.Module):
    """A small CNN with one policy head and one value head.

    The class is deliberately small so the first training pipeline can be
    understood and debugged before moving to a larger residual network.
    """

    INPUT_PLANES = 3

    def __init__(
        self,
        board_size: int,
        input_planes: int = INPUT_PLANES,
        channels: int = 64,
        value_hidden: int = 64,
    ) -> None:
        super().__init__()

        if isinstance(board_size, bool) or not isinstance(board_size, int):
            raise TypeError("board_size must be an integer")
        if board_size <= 0:
            raise ValueError("board_size must be greater than zero")
        if input_planes <= 0:
            raise ValueError("input_planes must be greater than zero")
        if channels <= 0:
            raise ValueError("channels must be greater than zero")
        if value_hidden <= 0:
            raise ValueError("value_hidden must be greater than zero")

        self.board_size = board_size
        self.input_planes = input_planes
        self.channels = channels
        self.value_hidden = value_hidden
        self.num_actions = board_size * board_size

        # TODO 1:
        # Decide how much spatial information the shared feature extractor
        # should preserve. For Gomoku, keeping the same H x W resolution is
        # convenient because every board position is also an action.
        self.backbone = nn.Sequential(
            nn.Conv2d(input_planes, channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(channels, channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(channels, channels, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
        )

        # TODO 2:
        # The policy head must produce exactly one logit for every board
        # position. Do not add softmax here; the training loss and MCTS will
        # apply softmax after handling legal moves.
        self.policy_head = nn.Sequential(
            nn.Conv2d(channels, 2, kernel_size=1),
            nn.ReLU(inplace=True),
            nn.Flatten(),
            nn.Linear(2 * self.num_actions, self.num_actions),
        )

        # TODO 3:
        # The value head compresses the whole board into one scalar. Tanh
        # makes the output match the project's [-1, 1] win/loss convention.
        self.value_head = nn.Sequential(
            nn.Conv2d(channels, 1, kernel_size=1),
            nn.ReLU(inplace=True),
            nn.Flatten(),
            nn.Linear(self.num_actions, value_hidden),
            nn.ReLU(inplace=True),
            nn.Linear(value_hidden, 1),
            nn.Tanh(),
        )

        # TODO 4:
        # This initialization is a good default for ReLU CNNs. Later you can
        # compare it with orthogonal initialization or a residual network.
        self._initialize_weights()

    def _initialize_weights(self) -> None:
        """Initialize convolution and linear layers."""
        for layer in self.modules():
            if isinstance(layer, nn.Conv2d):
                nn.init.kaiming_normal_(layer.weight, mode="fan_out", nonlinearity="relu")
                if layer.bias is not None:
                    nn.init.zeros_(layer.bias)
            elif isinstance(layer, nn.Linear):
                nn.init.kaiming_uniform_(layer.weight, nonlinearity="relu")
                if layer.bias is not None:
                    nn.init.zeros_(layer.bias)

    def _prepare_state(self, state: Tensor) -> Tensor:
        """Validate and normalize a single state or a batch of states."""
        if not torch.is_tensor(state):
            raise TypeError("state must be a torch.Tensor")

        # TODO 5:
        # Supporting both (C, H, W) and (B, C, H, W) makes inference from
        # one Board convenient while retaining the normal batch API.
        if state.ndim == 3:
            state = state.unsqueeze(0)
        if state.ndim != 4:
            raise ValueError(
                "state must have shape "
                f"({self.input_planes}, {self.board_size}, {self.board_size}) "
                "or "
                f"(batch, {self.input_planes}, {self.board_size}, {self.board_size})"
            )

        expected_shape = (self.input_planes, self.board_size, self.board_size)
        if tuple(state.shape[1:]) != expected_shape:
            raise ValueError(
                f"state has shape {tuple(state.shape)}, expected "
                f"(batch, {expected_shape[0]}, {expected_shape[1]}, {expected_shape[2]})"
            )

        # Convolution layers expect floating point input. Converting here is
        # useful for uint8/numpy-derived tensors and does not change values.
        if not state.is_floating_point():
            state = state.float()
        return state

    def forward(self, state: Tensor) -> tuple[Tensor, Tensor]:
        """Return policy logits and value predictions."""
        state = self._prepare_state(state)

        # TODO 6:
        # This is the central forward path:
        #   encoded board -> shared features -> policy/value predictions.
        features = self.backbone(state)
        policy_logits = self.policy_head(features)
        value = self.value_head(features)
        return policy_logits, value

    @staticmethod
    def mask_policy_logits(policy_logits: Tensor, legal_mask: Tensor) -> Tensor:
        """Set illegal action logits to a very negative value.

        Args:
            policy_logits: Shape ``(batch, actions)`` or ``(actions,)``.
            legal_mask: Same shape, where 1 means legal and 0 means illegal.

        Raises:
            ValueError: If shapes do not match or a position has no legal move.
        """
        if not torch.is_tensor(policy_logits):
            raise TypeError("policy_logits must be a torch.Tensor")
        if not torch.is_tensor(legal_mask):
            legal_mask = torch.as_tensor(
                legal_mask,
                dtype=policy_logits.dtype,
                device=policy_logits.device,
            )
        else:
            legal_mask = legal_mask.to(
                dtype=policy_logits.dtype,
                device=policy_logits.device,
            )

        was_unbatched = policy_logits.ndim == 1
        if was_unbatched:
            policy_logits = policy_logits.unsqueeze(0)
        if legal_mask.ndim == 1:
            legal_mask = legal_mask.unsqueeze(0)

        if policy_logits.ndim != 2 or legal_mask.ndim != 2:
            raise ValueError("policy_logits and legal_mask must be 1D or 2D")
        if policy_logits.shape != legal_mask.shape:
            raise ValueError(
                "policy_logits and legal_mask must have the same shape, got "
                f"{tuple(policy_logits.shape)} and {tuple(legal_mask.shape)}"
            )
        if torch.any(legal_mask.sum(dim=-1) <= 0):
            raise ValueError("each sample must contain at least one legal move")

        # TODO 7:
        # Mask before softmax, not after softmax. Otherwise illegal actions
        # still affect the normalization denominator.
        masked_logits = policy_logits.masked_fill(legal_mask <= 0, -1e9)
        return masked_logits.squeeze(0) if was_unbatched else masked_logits

    def predict(
        self,
        state: Tensor,
        legal_mask: Tensor | None = None,
        temperature: float = 1.0,
    ) -> tuple[Tensor, Tensor]:
        """Run inference and optionally return a legal policy distribution.

        ``forward`` returns logits. This method converts them to probabilities
        and is intended for MCTS or interactive play.
        """
        if temperature <= 0:
            raise ValueError("temperature must be greater than zero")

        self.eval()
        with torch.no_grad():
            policy_logits, value = self(state)
            if legal_mask is not None:
                policy_logits = self.mask_policy_logits(policy_logits, legal_mask)
            policy = torch.softmax(policy_logits / temperature, dim=-1)
        return policy, value

    def checkpoint(self, **extra: Any) -> dict[str, Any]:
        """Return a serializable checkpoint dictionary."""
        # TODO 8:
        # Add optimizer state, epoch, random seeds, or dataset metadata here
        # when the training script starts producing long-running experiments.
        payload: dict[str, Any] = {
            "board_size": self.board_size,
            "model_config": {
                "input_planes": self.input_planes,
                "channels": self.channels,
                "value_hidden": self.value_hidden,
            },
            "model_state_dict": self.state_dict(),
        }
        payload.update(extra)
        return payload

    def save_checkpoint(self, path: str | Path, **extra: Any) -> None:
        """Save model configuration and parameters to ``path``."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.checkpoint(**extra), path)

    @classmethod
    def from_checkpoint(
        cls,
        path: str | Path,
        map_location: str | torch.device = "cpu",
    ) -> "PolicyValueNet":
        """Create a model and load it from a checkpoint."""
        # TODO 9:
        # Later, validate a model version and reject incompatible
        # architectures instead of relying only on load_state_dict.
        # This method loads a checkpoint produced by this project, which is a
        # trusted local artifact. Newer PyTorch versions default to
        # weights_only=True; that mode rejects metadata objects such as Path.
        try:
            checkpoint = torch.load(
                path,
                map_location=map_location,
                weights_only=False,
            )
        except TypeError:
            # Compatibility with older PyTorch versions without weights_only.
            checkpoint = torch.load(path, map_location=map_location)
        if not isinstance(checkpoint, Mapping):
            raise ValueError("checkpoint must be a dictionary-like object")
        if "board_size" not in checkpoint or "model_state_dict" not in checkpoint:
            raise ValueError(
                "checkpoint must contain 'board_size' and 'model_state_dict'"
            )

        config = checkpoint.get("model_config", {})
        if not isinstance(config, Mapping):
            raise ValueError("checkpoint['model_config'] must be a dictionary")

        model = cls(
            board_size=int(checkpoint["board_size"]),
            input_planes=int(config.get("input_planes", cls.INPUT_PLANES)),
            channels=int(config.get("channels", 64)),
            value_hidden=int(config.get("value_hidden", 64)),
        )
        model.load_state_dict(checkpoint["model_state_dict"])
        return model
    
