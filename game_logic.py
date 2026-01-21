"""Tic Tac Toe game logic module."""

class TicTacToe:
    def __init__(self):
        self.board = [" " for _ in range(9)]  # 3x3 grid represented as a list of 9 chars
        self.current_winner = None  # keep track of winner

    def print_board(self):
        """Returns a string representation of the board."""
        # This is mostly for debugging in console
        return f"{self.board[0]}|{self.board[1]}|{self.board[2]}\n-+-+-\n{self.board[3]}|{self.board[4]}|{self.board[5]}\n-+-+-\n{self.board[6]}|{self.board[7]}|{self.board[8]}"

    def available_moves(self):
        """Returns a list of indices (0-8) that are empty."""
        return [i for i, spot in enumerate(self.board) if spot == " "]

    def empty_squares(self):
        """Checks if there are any empty squares left."""
        return " " in self.board

    def num_empty_squares(self):
        """Returns the number of empty squares."""
        return self.board.count(" ")

    def make_move(self, square, letter):
        """
        If the move is valid, make it (assign letter to square) and return True.
        Then check if that move won the game.
        """
        if self.board[square] == " ":
            self.board[square] = letter
            if self.winner(square, letter):
                self.current_winner = letter
            return True
        return False

    def winner(self, square, letter):
        """
        Checks if the last move resulted in a win.
        """
        # check row for similar letters
        row_ind = square // 3
        row = self.board[row_ind*3 : (row_ind+1)*3]
        if all([spot == letter for spot in row]):
            return True
        
        # check column for similar letters
        col_ind = square % 3
        column = [self.board[col_ind+i*3] for i in range(3)]
        if all([spot == letter for spot in column]):
            return True

        # check diagonals
        # but only if the square is an even number (0, 2, 4, 6, 8)
        if square % 2 == 0:
            diagonal1 = [self.board[i] for i in [0, 4, 8]]  # top-left to bottom-right
            if all([spot == letter for spot in diagonal1]):
                return True
            diagonal2 = [self.board[i] for i in [2, 4, 6]]  # top-right to bottom-left
            if all([spot == letter for spot in diagonal2]):
                return True
        
        return False