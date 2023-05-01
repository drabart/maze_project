from gui import *
from agent import *
from multiprocessing import Process
import time
import matplotlib

class Master:
    gui = None
    maze_height = None
    maze_width = None

    def update_maze(self):
        print("Updating maze")
        # get maze size from gui
        maze_dim = self.gui.get_maze_dim_raw()
        self.maze_height, self.maze_width = int(maze_dim[0]), int(maze_dim[1])

        # set maze size
        self.gui.set_maze_dim(self.maze_height, self.maze_width)
        self.agent.maze.resize(self.maze_height, self.maze_width)
        self.agent.maze_height = self.maze_height
        self.agent.maze_width = self.maze_width

        print("Updated maze")

    def random_walk(self):
        print("Starting random walk")
        reps = int(self.gui.get_samples_number_raw())
        paths = []

        for _ in range(reps):
            path = self.agent.random_walk()
            paths.append(path)

        paths = np.array(paths, dtype=float)
        self.gui.set_path_variables(paths.mean(), paths.min(), paths.max(), paths.std())
        print("Finished random walk")

    def start_training(self):
         # generate new maze
        self.agent.maze.reset()
        self.gui.draw_maze(self.agent.maze.connections)
        # compute shortest path
        self.gui.draw_path(self.agent.maze.shortest_path)
        # train
        self.t = Process(target=self.agent.train, args=())
        self.t.start()

    def end_training(self):
        self.t.terminate()
        self.t.join()
        self.agent.end_training = True
        print("Process is dead!")

    def __init__(self, maze_height, maze_width):
        self.gui = App(maze_height, maze_width, self.update_maze, self.random_walk, self.start_training, self.end_training)
        self.maze_height = maze_height
        self.maze_width = maze_width
        self.agent = Agent(self.maze_height, self.maze_width)
        self.gui.mainloop()


def main():
    master = Master(20, 20)

if __name__ == "__main__":
    main()