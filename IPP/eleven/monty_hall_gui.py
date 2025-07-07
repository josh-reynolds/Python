import random
import tkinter as tk

class Game(tk.Frame):
    """GUI application for Monty Hall Problem game."""

    doors = ('a', 'b', 'c')

    def __init__(self, parent):
        """Initialize the frame."""
        super(Game, self).__init__(parent)
        self.parent = parent
        self.img_file = 'all_closed.png'
        self.choice = ''
        self.winner = ''
        self.reveal = ''
        self.first_choice_wins = 0
        self.pick_change_wins = 0
        self.create_widgets()


