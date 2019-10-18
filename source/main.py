#!/usr/bin/env python3

import tkinter as tk
from tkinter import filedialog


class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        self.path = tk.StringVar()

        self.grid()
        self.create_widgets()

    def create_widgets(self):
        btSelectFolder = tk.Button(
            text="Browse",
            command=self.bt_browse
        )

        lbPath = tk.Label(master=self.master, textvariable=self.path)

        lbPath.grid(row=0, column=1)
        btSelectFolder.grid(row=0, column=3)

        # self.hi_there = tk.Button(self)
        # self.hi_there["text"] = "Hello World\n(click me)"
        # self.hi_there["command"] = self.say_hi
        # self.hi_there.pack(side="top")

        # self.quit = tk.Button(self, text="QUIT", fg="red",
        #                       command=self.master.destroy)
        # self.quit.pack(side="bottom")

    def bt_browse(self):
        name = filedialog.askdirectory()
        if name:
            self.path.set(name)

    def say_hi(self):
        print("hi there, everyone!")


if __name__ == "__main__":
    root = tk.Tk()
    # Setup
    root.title("Архив видео работ")
    root.geometry("400x600")

    app = Application(master=root)
    app.mainloop()
