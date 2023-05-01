import numpy as np
from collections import deque
import random
from copy import copy

class Maze:
    height = 0
    width = 0
    connections = None
    pos = [0, 0]
    # down up right left
    directions = [(1,0),(-1,0),(0,1),(0,-1)]
    dist = None
    move_nb = 0
    shortest_path = None

    def get_state(self):
        ret = []
        for e in self.connections[self.pos[0]][self.pos[1]]:
            if e:
                ret.append(1)
            else:
                ret.append(0)
        return ret

    def move_step(self, action):
        for i in range(4):
            if not self.connections[self.pos[0]][self.pos[1]][i]:
                action[i] = 0

        action = [abs(x) for x in action]

        move = random.choices(range(4), action, k=1)[0]
        # print(move, range(4))

        # print(move)
        reward = 0
        done = False
        self.move_nb += 1
        score = self.move_nb
        old_pos = copy(self.pos)
        
        self.pos[0] += self.directions[move][0]
        self.pos[1] += self.directions[move][1]

        if self.move_nb > 1000 * (self.height * 5 + self.dist[0][0] - self.dist[self.pos[0]][self.pos[1]]):
            done = True
            reward = -6
            score = 1000000000 + score
            return reward, score, done

        if self.pos[0] == self.height-1 and self.pos[1] == self.width-1:
            done = True
            reward = 10
            return reward, score, done

        if self.dist[self.pos[0]][self.pos[1]] < self.dist[old_pos[0]][old_pos[1]]:
            reward = 4
        else:
            reward = -6

        return reward, score, done

    def resize(self, height, width):
        self.height = height
        self.width = width

    def soft_reset(self):
        self.pos = [0, 0]
        self.move_nb = 0

    def reset(self):
        self.pos = [0, 0]
        self.move_nb = 0
        self.generate_random()
        self.compute_best_path()

    def find(self, tp):
        a = tp[0]
        b = tp[1]
        rp = self.rep[tp[0]][tp[1]]
        if rp[0] != tp[0] or rp[1] != tp[1]:
            self.rep[tp[0]][tp[1]] = self.find(rp)
        return self.rep[tp[0]][tp[1]]

    def generate_random(self):
        self.connections = np.zeros((self.height, self.width, 4), dtype=bool)
        self.rep = []
        for i in range(self.height):
            self.rep.append([])
            for j in range(self.width):
                self.rep[i].append((i,j))
        # add all possible edges
        to_add = []
        for h in range(self.height):
            for w in range(self.width):
                for dh, dw in self.directions:
                    if not (h + dh >= 0 and h + dh < self.height and w + dw >= 0 and w + dw < self.width):
                        continue
                    to_add.append(((h, w), (h+dh, w+dw)))

        # shuffle them
        random.shuffle(to_add)
        # remove wall if it doesn't create a cycle
        for e in to_add:
            a = self.find(e[0])
            b = self.find(e[1])
            # print(a, b, "\n")
            if a[0] == b[0] and a[1] == b[1]:
                continue
            self.rep[b[0]][b[1]] = a
            d = (e[0][0] - e[1][0], e[0][1] - e[1][1])
            dr = self.directions.index(d)
            self.connections[e[0][0]][e[0][1]][dr ^ 1] = True
            self.connections[e[1][0]][e[1][1]][dr] = True
            # print(e)
            

    def compute_best_path(self):
        # find path from 0,0 to height-1,width-1
        vis = np.zeros((self.height, self.width), dtype=bool)
        self.dist = np.zeros((self.height, self.width), dtype=int) 
        dq = deque()
        dq.append((self.height-1,self.width-1,0))
        while len(dq) > 0:
            h, w, d = dq.popleft()
            if vis[h][w]:
                continue
            vis[h][w] = True
            for dh, dw in self.directions:
                if not (h + dh >= 0 and h + dh < self.height and w + dw >= 0 and w + dw < self.width):
                    continue
                if self.connections[h][w][self.directions.index((dh, dw))] == False:
                    continue
                if vis[h + dh][w + dw] == 0:
                    self.dist[h + dh][w + dw] = d+1
                    dq.append((h + dh, w + dw, d+1))
        best = []
        node = np.array([0, 0])
        while node[0] != self.height-1 or node[1] != self.width-1:
            best.append(node)
            h, w = node[0], node[1]
            for dh, dw in self.directions:
                if not (h + dh >= 0 and h + dh < self.height and w + dw >= 0 and w + dw < self.width):
                    continue
                if self.connections[h][w][self.directions.index((dh, dw))] == False:
                    continue
                if(self.dist[h+dh][w+dw] < self.dist[node[0], node[1]]):
                    node = np.array([h+dh, w+dw])
        best.append(node)
        best.reverse()
        self.shortest_path = best


    def print(self):
        print(self.connections)

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.reset()
    
