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

        self.door_choice = tk.StringVar()
        self.door_choice.set(None)

        a = tk.Radiobutton(self.parent, text='A', variable=self.door_choice,
                           value='a', command=self.win_reveal)
        b = tk.Radiobutton(self.parent, text='B', variable=self.door_choice,
                           value='b', command=self.win_reveal)
        c = tk.Radiobutton(self.parent, text='C', variable=self.door_choice,
                           value='c', command=self.win_reveal)

        self.change_door = tk.StringVar()
        self.change_dor.set(None)

        instr_lbl = tk.Label(self.parent, text='Change doors?')
        instr_lbl.grid(row=2, column=3, columnspan=1, sticky='E')

        self.yes = tk.Radiobutton(self.parent, state='disabled', text='Y',
                                  variable=self.change_door, value='y',
                                  command=self.show_final)
        self.no = tk.Radiobutton(self.parent, state='disabled', text='N',
                                  variable=self.change_door, value='n',
                                  command=self.show_final)

        defaultbg = self.parent.cget('bg')
        self.unchanged_wins_txt = tk.Text(self.parent, width=20,
                                          height=1, wrap=tk.WORD,
                                          bg=defaultbg, fg='black',
                                          borderwidth=0)
        self.changed_wins_txt = tk.Text(self.parent, width=20,
                                        height=1, wrap=tk.WORD,
                                        bg=defaultbg, fg='black',
                                        borderwidth=0)



