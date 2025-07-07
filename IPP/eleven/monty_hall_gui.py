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

    def create_widgets(self):
        """Create label, button, and text widgets for game."""
        img = tk.PhotoImage(file='all_closed.png')
        self.photo_lbl = tk.Label(self.parent, image=img,
                                  text='', borderwidth=0)
        self.photo_lbl.grid(row=0, column=0, columnspan=10, sticky='W')
        self.photo_lbl.image = img

        instr_input = [
                ('Behind one door is CASH!', 1, 0, 5, 'W'),
                ('Behind the others: GOATS!!!', 2, 0, 5, 'W'),
                ('Pick a door:', 1, 3, 1, 'E')
                ]
        for text, row, column, columnspan, sticky in instr_input:
            instr_lbl = tk.Label(self.parent, text=text)
            instr_lbl.grid(row=row, column=column, columnspan=columnspan,
                           sticky=sticky,ipadx=30)


