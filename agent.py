import random
import torch
from maze import Maze
from collections import deque
import numpy as np
from model import Linear_QNet, QTrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001
EXPLORATION = 80
BITS = 2

class Agent:
    def __init__(self, maze_height, maze_width):
        # down up right left
        self.directions = [(1,0),(-1,0),(0,1),(0,-1)]
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discounty rate (0, 1)
        self.memory = deque(maxlen=MAX_MEMORY)
        self.end_training = False

        self.bits = []
        for _ in range(BITS):
            self.bits.append(0)

        self.maze_height = maze_height
        self.maze_width = maze_width
        self.maze = Maze(self.maze_height, self.maze_height)
        self.maze.reset()
        self.model = Linear_QNet(4+BITS, 256, 4+BITS)
        self.trainer = QTrainer(self.model, LR, self.gamma)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)


    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    # generate action using nn
    def get_action(self, state):
        # print('state: ', state)
        self.epsilon = EXPLORATION - self.n_games
        final_move = [1,1,1,1]
        if random.randint(0, 200) < self.epsilon:
            for _ in range(BITS):
                final_move.append(1)
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model.forward(state0)
            final_move = prediction.tolist()

        self.bits = final_move[4:]
        for i in range(BITS):
            if self.bits[i] > 0:
                self.bits[i] = 1
            else:
                self.bits[i] = 0
        return final_move

    def train(self):
        plot_scores = []
        plot_mean_scores = []
        total_score = 0
        self.record = 999999999
        self.end_training = False
        while not self.end_training:
            state_old = self.maze.get_state()
            state_old += self.bits

            final_move = self.get_action(state_old)

            reward, score, done = self.maze.move_step(final_move[:4])
            state_new = self.maze.get_state()
            state_new += self.bits

            # train short
            self.train_short_memory(state_old, final_move, reward, state_new, done)

            # remember
            self.remember(state_old, final_move, reward, state_new, done)

            if done:
                # train long
                self.train_long_memory()
                # plot

                # update
                self.n_games += 1
                if score < self.record:
                    self.record = score
                    self.model.save()

                print('Game', self.n_games, 'Score', score, 'pos:', self.maze.pos)
                self.maze.soft_reset()

    def random_walk(self):
        h = 0
        w = 0
        path = 0
        while h != self.maze_height-1 or w != self.maze_width-1:
            mv = []
            path += 1
            for i in range(4):
                dh, dw = self.directions[i]
                if not (h + dh >= 0 and h + dh < self.maze_height and w + dw >= 0 and w + dw < self.maze_width):
                    continue
                if self.maze.connections[h][w][i] == False:
                    continue
                mv.append((h+dh, w+dw))
            am = random.randrange(0, len(mv))
            h, w = mv[am]
        path += 1
        return path
