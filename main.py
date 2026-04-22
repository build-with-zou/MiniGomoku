# File name : main.py
# Content: A Gomoku game implementation in Python without any imported libraries.

class Board:
    # Initialize the board with a given size
    def __init__(self, size=15):
        self.size = size
        self.board = [[0 for _ in range(size)] for _ in range(size)]
    
    # Place a piece on the board
    def place(self ,player:int ,pos:list ): 
        """
        Use 1 to represent player 1 and 2 to represent player 2;
        Pos is a list of two integers representing the row and column where the piece is to be placed.
        For example, if player 1 wants to place a piece at row 3 and column 4, the pos would be [2, 3].
        """
        # Check if the position is valid and the cell is empty
        if 0 <= pos[0] < self.size and 0 <= pos[1] < self.size and self.board[pos[0]][pos[1]] == 0:
            self.board[pos[0]][pos[1]] = player
            return True
        return False
    
    # Check if a player has won the game
    def check_win(self, player,pos):
        """
        Check if the specified player has won the game by having five pieces in a row.
        We only have to check for a win condition starting from the last placed piece, as that is the only move that could have resulted in a win.

        Return: True if the player has won, False otherwise."""
        # Check horizontal, vertical, and diagonal (both directions) for a win
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            # Check in the positive direction
            r, c = pos[0] + dr, pos[1] + dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc
            # Check in the negative direction
            r, c = pos[0] - dr, pos[1] - dc
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc
            if count >= 5:
                return True
        return False
    # Print the current state of the board
    def print_board(self):
        print("  " + " ".join(f"{i+1:2}" for i in range(self.size)))  # Print column numbers
        for i, row in enumerate(self.board):
            print(f"{i+1:2} " + '  '.join(str(cell) for cell in row))


class normalAIplayer:
    """
    A simple AI player that makes random valid moves. This is a placeholder for more advanced AI implementations in the future.
    We will first calculate the score for each empty cell based on potential winning lines for both players, and then choose the move with the highest score.

    这是一个简单的AI程序，我们首先进行特征提取，然后根据这些特征计算每个空格的得分，最后选择得分最高的空格进行落子。
    """
    def __init__(self,Board,player):
        self.board = Board
        self.player = player
        self.shape_score = { # The number represent the score for that feature, which will be used to evaluate the potential moves.
            "potential":{
            '活二': 1,  # Potential to create a two in a row with open ends like "0 1 1 0 " or "0 1 0 1 0 "
            '活三': 10,  # Potential to create a three in a row with open ends like "0 1 1 1 0 " or "0 1 1 0 1 0 "
            '活四': 100,  # Potential to create a four in a row with open ends like "0 1 1 1 1 0 "
            '五': 10000,  # Five in a row like "1 1 1 1 1 "
            },
            "sleep":{
            '眠二': 0,  # Two in a row that is blocked on one end like "2 1 1 0 " or "0 1 1 2 "
            '眠三': 5,  # Three in a row that is blocked on one end like "2 1 1 1 0 " or "0 1 1 1 2 "
            '眠四': 50,  # Four in a row that is blocked on one end like "2 1 1 1 1 0 " or "0 1 1 1 1 2 "
            }
        }

        
    def get_line_string(self,row,col,dr,dc):
        # This function will return a string representation of the pieces in a line in the specified direction (dr, dc) starting from (row, col).
        # For example, if dr=0 and dc=1, it will return the string for the horizontal line passing through (row, col).
        # The string will use '0' for empty cells, '1' for player 1's pieces, and '2' for player 2's pieces.

        line = ''
        # Move to the start of the line
        start_r, start_c = row, col
        while 0 <= start_r - dr < self.board.size and 0 <= start_c - dc < self.board.size:
            start_r -= dr   
            start_c -= dc
        
        # Traverse the entire line
        r, c = start_r, start_c
        while 0 <= r < self.board.size and 0 <= c < self.board.size:
            line += str(self.board.board[r][c])
            r += dr
            c += dc
        return line

    def evaluate_line(self,line:str):
        # This function will evaluate a line string and return the corresponding feature based on the patterns defined in self.patterns.

        total_score  = 0
        for pattern, feature in self.patterns.items():
            if pattern in line:
                total_score += self.shape_score["potential"].get(feature, 0) + self.shape_score["sleep"].get(feature, 0)
        return total_score
    
    def evaluate_board(self,for_player=None):
        """
        Return the total score for the current board state from the perspective of the AI player. 
        This will involve evaluating all lines (horizontal, vertical, and both diagonals) for potential winning patterns and summing their scores.
        """
        if for_player is None:
            for_player = self.player

        if for_player == 1:
            self.patterns = {
                '0110': '活二',
                '01110': '活三',
                '011110': '活四',
                '2110': '眠二',
                '0112': '眠二',
                '21110': '眠三',
                '01112': '眠三',
                '211110': '眠四',
                '011112': '眠四',
                '11111': '五',
            }
        else:
            self.patterns = {
                '0220': '活二',
                '02220': '活三',
                '022220': '活四',
                '1220': '眠二',
                '0221': '眠二',
                '12220': '眠三',
                '02221': '眠三',
                '122220': '眠四',
                '022221': '眠四',
                '22222': '五',
            }
        # We need to evaluate all lines (horizontal, vertical, and both diagonals) for potential winning patterns and sum their scores to get the total score for the current board state from the perspective of the AI player.
        total_score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        # 这里需要注意不把一条边重复计算两次
        for dr, dc in directions:
            if dr == 0 and dc == 1: # Horizontal
                # We only need to evaluate each row once for horizontal lines
                for row in range(self.board.size):
                    line = self.get_line_string(row, 0, dr, dc)
                    total_score += self.evaluate_line(line)

            elif dr == 1 and dc == 0: # Vertical
                # We only need to evaluate each column once for vertical lines
                for col in range(self.board.size):
                    line = self.get_line_string(0, col, dr, dc)
                    total_score += self.evaluate_line(line)

            elif dr == 1 and dc == 1: # Diagonal \
                # We only need to evaluate each diagonal once for \ lines
                # We use the first row and the first column as the starting points for the diagonals
                for row in range(self.board.size):
                    line = self.get_line_string(row, 0, dr, dc)
                    total_score += self.evaluate_line(line)
                for col in range(1, self.board.size):
                    line = self.get_line_string(0, col, dr, dc)
                    total_score += self.evaluate_line(line)
                
            
            elif dr == 1 and dc == -1: # Diagonal /
                # We only need to evaluate each diagonal once for / lines
                # We use the first row and the last column as the starting points for the diagonals
                for row in range(self.board.size):
                    line = self.get_line_string(row, self.board.size - 1, dr, dc)
                    total_score += self.evaluate_line(line)
                for col in range(self.board.size - 1):
                    line = self.get_line_string(0, col, dr, dc)
                    total_score += self.evaluate_line(line)
        return total_score

    def score_move(self, row, col):
        """
        This function will calculate the score for placing a piece at the specified row and column. 
        The score is made up of the attacking score (potential to create winning lines for the AI player) and the defensive score (potential to block the opponent's winning lines).
        We calculate the score by attacking score + 0.8 * defensive score, where the attacking score is the score for the AI player and the defensive score is the score for the opponent player. 
        The factor of 0.8 is used to give slightly more weight to offensive moves while still considering defensive moves.

        Return: The total score for placing a piece at the specified row and column.
        """
        weight = 0.8
        # Temporarily place the piece on the board to evaluate the move
        self.board.board[row][col] = self.player
        attacking_score = self.evaluate_board()  # Score for the AI player
        self.board.board[row][col] = 3 - self.player  # Temporarily place the opponent's piece
        self.opponent = 3 - self.player
        defensive_score = self.evaluate_board(for_player=self.opponent)  # Score for the opponent player

        self.board.board[row][col] = 0  # Remove the temporary piece
        return attacking_score + weight * defensive_score

    def get_best_move(self):
        """
        This function will iterate through all empty cells on the board, calculate the score for placing a piece in each cell using the score_move function, and return the position of the cell with the highest score as the best move for the AI player.

        Return: A list containing the row and column of the best move for the AI player.
        """
        best_score = float('-inf')
        best_move = None
        for row in range(self.board.size):
            for col in range(self.board.size):
                if self.board.board[row][col] == 0:  # Check only empty cells
                    move_score = self.score_move(row, col)
                    if move_score > best_score:
                        best_score = move_score
                        best_move = [row, col]
        return best_move
    
    def make_move(self):
        """
        This function will get the best move for the AI player using the get_best_move function and then place the piece on the board at that position.

        Return: True if the move was successfully made, False otherwise.
        """
        best_move = self.get_best_move()
        if best_move:
            self.board.place(self.player, best_move)
            return best_move
        return False

    


def main():
    print("Welcome to Gomoku!")
    print("Choose the size of the board (default is 15):")
    try:
        size = int(input())
        board = Board(size)
    except ValueError:
        board = Board()
    current_player = 1
    print("Do you want to play against the AI? (y/n):")
    print("Enter 'y' for yes or 'n' for no:")
    play_ai = input().lower() == 'y'
    ai_player = None
    if play_ai:
        print("Do you want to be Player 1 or Player 2? (Enter 1 or 2):")
        ai_player = 2 if int(input()) == 1 else 1

    # The main loop of the game will continue until a player wins or the board is full. In each iteration, 
    # we will print the current state of the board, prompt the current player for their move, and check for a win condition after each move. 
    # If the player is an AI, we will call the make_move function to let the AI make its move. 
    if play_ai :
        while True:
            board.print_board()
            print("-" * (board.size * 2 - 1))
            if current_player == ai_player:
                print(f"AI Player {current_player}'s turn.")
                ai_player_instance = normalAIplayer(board, current_player)
                move = ai_player_instance.make_move()
                row, col = move[0], move[1]  # Get the last move made by the AI for win checking
                print(f"AI Player {current_player} placed a piece at ({row + 1}, {col + 1}).")
            else:
                print(f"Player {current_player}'s turn. Enter row and column (1-{board.size}):")
                try:
                    row, col = map(int, input().split())
                    if not board.place(current_player, [row - 1, col - 1]):
                        print("Invalid move. Try again.")
                        continue
                except ValueError:
                    print("Invalid input. Please enter two integers separated by a space.")
                    continue
                print(f"Player {current_player} placed a piece at ({row}, {col}).")

            if board.check_win(current_player, [row , col]):
                board.print_board()
                print(f"Player {current_player} wins!")
                break
            current_player = 2 if current_player == 1 else 1


    if not play_ai:
        while True:
            board.print_board()
            print("-" * (board.size * 2 - 1))
            print(f"Player {current_player}'s turn. Enter row and column (1-{board.size}):")
            # The input is expected to be two integers separated by a space, representing the row and column where the player wants to place their piece.
            try:
                row, col = map(int, input().split())
                if board.place(current_player, [row - 1, col - 1]):
                    if board.check_win(current_player, [row - 1, col - 1]):
                        board.print_board()
                        print(f"Player {current_player} wins!")
                        break
                    current_player = 2 if current_player == 1 else 1
                else:
                    print("Invalid move. Try again.")
            except ValueError:
                print("Invalid input. Please enter two integers separated by a space.")
            # The game continues until a player wins or the board is full.
            print(f"Player {current_player} placed a piece at ({row}, {col}).")
            if all(cell != 0 for row in board.board for cell in row):
                board.print_board()
                print("It's a draw!")
                break

if __name__ == "__main__":
    main()