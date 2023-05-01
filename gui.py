import tkinter as tk
from tkinter import ttk
from maze import *
import matplotlib

matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)

class App(tk.Tk):
    def __init__(self, maze_height, maze_width, maze_func, walk_func, train_func, end_func):
        super().__init__()

        self.window_width = 1000
        self.window_height = 1000

        self.title("Maze")

        # get the screen dimension
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        # find the center point
        center_x = int(self.screen_width/2 - self.window_width / 2)
        center_y = int(self.screen_height/2 - self.window_height / 2)

        # set the position of the window to the center of the screen
        self.geometry(f'{self.window_width}x{self.window_height}+{center_x}+{center_y}')

        self.columnconfigure(0, weight=5)
        self.columnconfigure(1, weight=4)

        self.rowconfigure(0, weight=5)
        self.rowconfigure(1, weight=2)

        self.canvas_frame = Canvas_Frame(self)
        self.canvas_frame.grid(column=0, row=0)

        self.button_frame = Button_Frame(self, maze_height, maze_width, maze_func, walk_func, train_func, end_func)
        self.button_frame.grid(column=0, row=1, sticky=tk.N)

    def draw_maze(self, connections):
        self.canvas_frame.draw_maze(connections)

    def draw_path(self, path):
        self.canvas_frame.draw_path(path)

    def set_maze_dim(self, maze_height, maze_width):
        self.canvas_frame.set_maze_dim(maze_height, maze_width)

    def get_maze_dim_raw(self):
        return (self.button_frame.maze_height_raw.get(), self.button_frame.maze_width_raw.get())

    def get_samples_number_raw(self):
        return self.button_frame.samples_number_raw.get()

    def set_path_variables(self, avg, minp, maxp, std):
        self.button_frame.average_out.set("Average: "+str(avg))
        self.button_frame.min_out.set("Min: "+str(int(minp)))
        self.button_frame.max_out.set("Max: "+str(int(maxp)))
        self.button_frame.standard_dev_out.set("Standard deviation: "+str(round(std, 3)))


class Canvas_Frame(tk.Frame):
    canvas_width = 600
    canvas_height = 600
    maze_height = 20
    maze_width = 20
    average = 0.0
    min_path = 0.0
    max_path = 0.0
    std_dev_path = 0.0

    # rendering
    def draw_path(self, path):
        sq_len = 0.5
        pd = 20
        maze_square_height = (self.canvas_height - pd*2) / self.maze_height
        maze_square_width = (self.canvas_width - pd*2) / self.maze_width
        for square in path:
            self.canvas.create_rectangle((pd + maze_square_width*sq_len/2 + maze_square_width*square[1],
                                          pd + maze_square_height*sq_len/2 + maze_square_height*square[0]), 
                                         (pd + maze_square_width*sq_len*3/2 + maze_square_width*square[1],
                                          pd + maze_square_height*sq_len*3/2 + maze_square_height*square[0]),
                                         width=0,
                                         fill='#41ea27')

    def draw_maze(self, connections):
        self.canvas.delete("all")
        pd = 20
        self.canvas.create_rectangle((pd, pd), (self.canvas_width-pd, self.canvas_height-pd), width=4)
        maze_square_height = (self.canvas_height - pd*2) / self.maze_height
        maze_square_width = (self.canvas_width - pd*2) / self.maze_width
        for h in range(self.maze_height):
            for w in range(self.maze_width):
                if connections[h][w][0] == False:
                    self.canvas.create_line((pd+w*maze_square_width, pd+(h+1)*maze_square_height), 
                                            (pd+(w+1)*maze_square_width, pd+(h+1)*maze_square_height), width=4)
                if connections[h][w][2] == False:
                    self.canvas.create_line((pd+(w+1)*maze_square_width, pd+h*maze_square_height), 
                                            (pd+(w+1)*maze_square_width, pd+(h+1)*maze_square_height), width=4)

    def set_maze_dim(self, maze_height, maze_width):
        self.maze_height = maze_height
        self.maze_width = maze_width

    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg='white')
        self.canvas.pack(anchor=tk.CENTER, expand=True)

class Button_Frame(tk.Frame):
    def __init__(self, master, maze_height, maze_width, maze_func, walk_func, train_func, end_func, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        self.columnconfigure(0, weight=1, minsize=150)
        self.columnconfigure(1, weight=1, minsize=150)
        self.columnconfigure(2, weight=1, minsize=150)
        self.columnconfigure(3, weight=1, minsize=150)
        self.columnconfigure(4, weight=1, minsize=150)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.maze_height_raw = tk.StringVar(value=str(maze_height))
        self.maze_width_raw = tk.StringVar(value=str(maze_width))

        self.samples_number_raw = tk.StringVar(value="1")

        self.average_out = tk.StringVar(value="Average: 0.0")
        self.min_out = tk.StringVar(value="Min: 0")
        self.max_out = tk.StringVar(value="Max: 0")
        self.standard_dev_out = tk.StringVar(value="Standard deviation: 0.0")

        # maze generation row
        label = ttk.Label(self, text="Maze height:")
        label.grid(column=0, row=0, sticky=tk.W)

        entry = ttk.Entry(self, textvariable=self.maze_height_raw, width=15)
        entry.grid(column=1, row=0, sticky=tk.W)

        label = ttk.Label(self, text="Maze width:")
        label.grid(column=2, row=0, sticky=tk.W)

        entry = ttk.Entry(self, textvariable=self.maze_width_raw, width=15)
        entry.grid(column=3, row=0, sticky=tk.W)

        button = ttk.Button(self, text="Generate New Maze", command=maze_func)
        button.grid(column=4, row=0, sticky=tk.W)

        # random walk row
        button = ttk.Button(self, text="Generate Random Walk", command=walk_func)
        button.grid(column=0, row=1, sticky=tk.W, columnspan=2)

        label = ttk.Label(self, text="Number of samples: ")
        label.grid(column=2, row=1, sticky=tk.W)

        entry = ttk.Entry(self, textvariable=self.samples_number_raw, width=15)
        entry.grid(column=3, row=1, sticky=tk.W)

        # random walk stats
        label = ttk.Label(self, textvariable=self.average_out)
        label.grid(column=0, row=2, sticky=tk.W)

        label = ttk.Label(self, textvariable=self.min_out)
        label.grid(column=1, row=2, sticky=tk.W)

        label = ttk.Label(self, textvariable=self.max_out)
        label.grid(column=2, row=2, sticky=tk.W)

        label = ttk.Label(self, textvariable=self.standard_dev_out)
        label.grid(column=3, row=2, sticky=tk.W)

        # train menu
        button = ttk.Button(self, text='Start Training', command=train_func)
        button.grid(column=0, row=3, sticky=tk.W, columnspan=2)
        
        button = ttk.Button(self, text='End Training', command=end_func)
        button.grid(column=1, row=3, sticky=tk.W)

        for widget in self.winfo_children():
            widget.grid(padx=5, pady=5)
