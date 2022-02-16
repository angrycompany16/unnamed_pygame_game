import numpy as np
import pygame as pyg
import random
import noise
import copy
import math
import os

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

        for i in range(len(self.tilemap)):
            for j in range(len(self.tilemap[i])):
                if self.tilemap[i][j] == 1:
                    room = Island(60, 51, [30, 27], 30, 25, 500)
                    room.write(j, i)

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

class Island():
    def __init__(self, width, height, center, max_radius_x, max_radius_y, probability_factor):
        self.tilemap = []
        self.center = center
        self.height = height
        self.width = width
        self.max_radius_x = max_radius_x
        self.max_radius_y = max_radius_y
        self.probability_factor = probability_factor
        for i in range(height):
            self.tilemap.append([])
            for j in range(width):
                self.tilemap[i].append(0)

        self.generate_tiles()

    def generate_tiles(self):
        random_seed_1 = np.random.random() * 1000
        random_seed_2 = np.random.random() * 2

        for i in range(len(self.tilemap)):
            for j in range(len(self.tilemap[i])):
                dist_x = math.pow(self.center[0] - j, 2) + 0.1
                dist_y = math.pow(self.center[1] - i, 2) + 0.1
                
                prob = self.probability_factor / (dist_y + dist_x)
                # print(prob)
                
                if dist_x > math.pow(self.max_radius_x, 2):
                    prob = 0
                if dist_y > math.pow(self.max_radius_y, 2):
                    prob = 0

                if prob > 1:
                    if (1 + noise.snoise2(
                            (i + random_seed_1) / 8, 
                            (j + random_seed_1) / 8
                        )) * (1 + noise.snoise2(
                            (i + random_seed_2) / 8, 
                            (j + random_seed_2) / 8
                        )) > 0.8:
                        self.tilemap[i][j] = 1
        
        for i in range(3):
            self.tilemap = self.iterate_cellular_automaton()

    def iterate_cellular_automaton(self):
        tilemap_copy = copy.deepcopy(self.tilemap)

        # i is y value in the tilemap
        # j is x value in the tilemap
        for i in range(len(tilemap_copy)):
            for j in range(len(tilemap_copy[i])):
                wall_count = 0
                for y in range(i - 1, i + 2):
                    for x in range(j - 1, j + 2):
                        if y > 0 and y < self.height - 1:
                            if x > 0 and x < self.width - 1:
                                if y != i or x != j:
                                    if self.tilemap[y][x] == 1:
                                        wall_count += 1


                if wall_count > 4:
                    tilemap_copy[i][j] = 1
                else:
                    tilemap_copy[i][j] = 0

        return tilemap_copy
        # Loop through all tiles, and count the number of neighbours
        # If more than four neighbours are floor, the tile becomes floor
        # If four or fewer are floor, the tile becomes air
        # Iterate through these steps many times 
    
    def write(self, y, x):
        path = os.getcwd()
        file_path = os.path.join(path, "Map/room_{y_coordinate}_{x_coordinate}.txt".format(y_coordinate = y, x_coordinate = x))
        f = open(file_path, "x")

        tilemap_string = ""
        for i in range(len(self.tilemap)):
            tilemap_string += "\n"
            for j in range(len(self.tilemap[i])):
                tilemap_string += str(self.tilemap[i][j])

        f.write(tilemap_string)

