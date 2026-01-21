import random

class RandomPlayer:
    def __init__(self, letter):
        self.letter = letter

    def get_move(self, game):
        """
        Determine the move based on the game state.
        implements a random strategy as a placeholder.
        """
        square = random.choice(game.available_moves())
        return square