import numpy as np
import pygame as pyg
import random
import noise

# create a tilemap that just contains random noise
class RoomLayout():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rooms = []
        self.tilemap = []
        for i in range(height):
            self.tilemap.append([])
            for j in range(width):
                self.tilemap[i].append(0)

    def create_rooms(self):
        # 1 equals room, 0 equals not a room
        # rand becomes a random int within the rows
        rand = random.randint(0, self.width - 1)
        # starting tile is the tile at the top row and random number
        start = [0, rand]
        # print(start)
        activetile = start
        # setting the tile to a room
        self.tilemap[0][rand] = 1

        # looping to generate the map
        for i in range(self.width + 10):
            if activetile[0] == self.width - 1:
                break
            activetile = self.step(activetile)

        # for tile in self.tilemap:
            # print(tile)

    def step(self, tile):
        # gets neighbours
        neighbours = self.get_neighbours(tile[1], tile[0])
        # print(neighbours)
        tile = random.choice(neighbours)
        # print(tile)
        self.tilemap[tile[0]][tile[1]] = 1
        return tile


    def get_neighbours(self, x, y):
        neighbours = []
        # min index: 0
        if x >= 1:
            if self.tilemap[y][x - 1] == 0:
                neighbours.append([y, x - 1])
        # max index: 19
        if x <= self.width - 2:
            if self.tilemap[y][x + 1] == 0:
                neighbours.append([y, x + 1])
        # max index: 19
        if y <= self.height - 2:
            if self.tilemap[y + 1][x] == 0:
                neighbours.append([y + 1, x])

        return neighbours

class Room():
    def __init__(self):
        self.tilemap = []
        
        for i in range(30):
            self.tilemap.append([])
            for j in range(17):
                self.tilemap[i].append(0)

    def generate_tiles(self):
        random_seed = np.random.random() * 1000

        #TODO - make perlin noise actually generate an island instead of noise
        for i in range(len(self.tilemap)):
            for j in range(len(self.tilemap[i])):
                self.tilemap[i][j] = round((1 + noise.snoise2(i, j)) / 2)
    
            print(self.tilemap[i])
