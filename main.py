from collections import defaultdict

import tkinter as tk
from tkinter import ttk

import threading

import random

from fruit_dictionary import Fruit


class Model:
    def __init__(self):
        self.display = {1: 0, 2: 0, 3: 0}

        self.score = 100
        self.cost = 20

    def get_money(self):
        return self.score / 100

    def check_go(self):
        if (self.score - self.cost) < 0 or self.score < 0:
            return False

        else:
            self.score -= self.cost
            return True

    def nudge_action(self, nudgebutton):
        x = self.display[nudgebutton]
        while x == self.display[nudgebutton]:
            x = random.randint(1, 6)
            if self.display[nudgebutton] != x:
                self.display[nudgebutton] = x
                x += 1

    def roll_action(self):
        for i in range(3):
            self.display[(i + 1)] = random.randint(1, 6)


class View(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        def start_game():
            self.button_names = ["Nudge-1", "Nudge-2", "Nudge-3"]
            self.display_labels = []
            self.fruit_labels = []
            self.nudge_buttons = []
    
            # field options
            options = {'padx': 5, 'pady': 5}
    
            # add padding to the frame and show it
            self.grid(padx=2, pady=2, sticky=tk.NSEW)
    
            # result label
            self.result_label = ttk.Label(self, text=f"£{1.00}")
            self.result_label.grid(column=2, row=4, sticky=tk.E, padx=10, pady=5)
    
            # win label
            self.win_label = ttk.Label(self,
                                       text=f"Your results will be shown here")
            self.win_label.grid(column=1,
                                row=4,
                                rowspan=2,
                                sticky=tk.NS,
                                padx=10,
                                pady=5)
    
            # fruit_displays
            for index in range(3):
                # image of fruit
                self.display_label = tk.Label(self,
                                              text="temporary",
                                              font="Monospace 10",
                                              bg="black",
                                              fg='white')
                self.display_label.grid(column=index, row=1, **options)
    
                self.display_labels.append(self.display_label)
    
                # name of fruit
                self.fruit_label = ttk.Label(self,
                                             text="temporary",
                                             font=("Monospace 10", 8))
                self.fruit_label.grid(column=index, row=2)
    
                self.fruit_labels.append(self.fruit_label)
    
            # nudge buttons
            for index in range(3):
                n = self.button_names[index]
    
                self.nudge_button = ttk.Button(
                    self,
                    text=n,
                    command=lambda index=index + 1: self.nudge_Callback(index),
                    style="C.TButton")
                self.nudge_button.grid(column=index, row=3, **options)
    
                self.nudge_buttons.append(self.nudge_button)
    
            # roll
            self.roll_button = ttk.Button(
                self,
                text="Roll",
                command=lambda t="roll_button": self.roll_Callback(),
                style="C.TButton")
            self.roll_button.grid(column=0,
                                  row=4,
                                  rowspan=2,
                                  sticky=tk.W,
                                  padx=20,
                                  pady=5)
    
            # exit button
            self.exit_button = ttk.Button(
                self,
                text="Win",
                command=lambda t="exit_button": self.exit_callback(),
                style="C.TButton")
            self.exit_button.grid(column=2, row=5, sticky=tk.E, **options)
    
            self.disable_buttons()
            self.controller = None
    

        def disable_buttons(self):
            for index in range(3):
                self.nudge_buttons[index].config(state="disabled")
    
            self.exit_button.config(state="disabled")
    
        def enable_buttons(self):
            for index in range(3):
                self.nudge_buttons[index].config(state="enabled")
    
            self.exit_button.config(state="enabled")
    
        def exit_callback(self):
            """
          Handle button click event
          :return:
          """
            if self.controller:
                self.controller.exit()
    
        def nudge_Callback(self, index):
            """
          Handle button click event
          :return:
          """
            if self.controller:
                self.disable_buttons()
                self.controller.nudge(index)
    
        def roll_Callback(self):
            """
          Handle button click event
          :return:
          """
            if self.controller:
                self.enable_buttons()
                self.controller.roll()
    

    def set_controller(self, controller):
        """
      Set the controller
      :param controller:
      :return:
      """
        self.controller = controller

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.dd = defaultdict(set)
        self.special_cases = [{6: 3}, {6: 2}, {2: 3}, {"n", 3}]

        self.fruit_names = [
            "Blank", "Cherry", "Bell", "Lemon", "Orange", "Star", "Skull"
        ]

    def update_display(self):
        money = f"£{self.model.get_money()}"
        self.view.result_label.config(text=money)
        for index in range(3):
            x = self.model.display[index + 1]
            self.view.display_labels[index].config(text=Fruit[x])
            self.view.fruit_labels[index].config(
                text=f"display_window ({index+1}) = |{self.fruit_names[x]}|")

    def check_display(self):
        self.dd = defaultdict(set)

        for k, v in self.model.display.items():
            self.dd[v].add(k)
        self.dd = {k: len(v) for k, v in self.dd.items() if len(v) > 1}
        if len(self.dd) > 0:
            self.special_cases[-1] = {k: 3 for k, v in self.dd.items()}

        if self.dd in self.special_cases:
            self.view.disable_buttons()
            self.auto_win()

        else:
            self.view.exit_button.config(state="enabled")
            self.view.win_label.config(text=f"Your results will be shown here")

    def auto_win(self):
        x = self.model.score
        for k, v in self.dd.items():
            y = k
            if self.dd == {6: 3}:
                self.model.score -= self.model.score

            elif self.dd == {6: 2}:
                if self.model.score - 100 > 0:
                    self.model.score -= 100

                else:
                    self.model.score -= self.model.score

            elif self.dd == {2: 3}:
                self.model.score += 500

            elif self.dd[k] == 3:
                self.model.score += 100

        x = (self.model.score - x) / 100
        self.view.win_label.config(
            text=f"You have {self.dd[y]} {self.fruit_names[y]}s - You win £{x}"
        )

    def check_win(self):
        for k, v in self.dd.items():
            y = k
            if self.dd[k] == 2:
                self.model.score += 50
            self.view.win_label.config(
                text=
                f"You have {self.dd[y]} {self.fruit_names[y]}s - You win £{0.50}"
            )

    def nudge(self, nudgebutton):
        alive = self.model.check_go()
        if alive:
            self.model.nudge_action(nudgebutton)
            self.check_display()

        self.check_win()
        self.update_display()
        self.view.exit_button.config(state="disabled")

    def roll(self):
        alive = self.model.check_go()
        if alive:
            self.model.roll_action()
            self.check_display()

        else:
            self.view.disable_buttons()
            self.view.roll_button.config(state="disabled")
            self.view.win_label.config(text=f"You Lose")

        self.update_display()

    def exit(self):
        self.view.disable_buttons()
        self.check_win()
        self.update_display()
        self.view.exit_button.config(state="disabled")


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Fruit Machine")
        self.resizable(False, False)

        model = Model()
        view = View(self)

        controller = Controller(model, view)
        controller.update_display()
        view.set_controller(controller)

        self.style = ttk.Style()
        self.style.map("C.TButton",
                       foreground=[('active', 'blue')],
                       background=[('pressed', '!disabled', 'lightgrey'),
                                   ('active', 'white')])


if __name__ == "__main__":
    app = App()
    app.mainloop()
