from tkinter import *


class MovingCircle:

    def __init__(self):
        self.window = Tk()
        self.window.title("Moving circles")
        self.window.geometry("500x400")

        self.canvas1 = Canvas(self.window, width=300, height=300, bg="grey")
        self.canvas1.pack(pady=30)
        self.circle1 = self.canvas1.create_oval(10, 10, 50, 50, fill="red")
        self.circle2 = self.canvas1.create_oval(100, 100, 70, 70, fill="red")

        self.window.bind("<ButtonPress-1>", self.start_move)
        self.window.bind("<B1-Motion>", self.move)

        self.window.mainloop()

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def move(self, event):
        deltax = event.x - self._x
        deltay = event.y - self._y
        self._x = event.x
        self._y = event.y
        self.canvas1.move("current", deltax, deltay)


MovingCircle()
