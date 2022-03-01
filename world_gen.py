import numpy as np
import random, noise, copy, math, os, vectors

# region RULES(tiles)

L_TOP_CORNER = (
    (0, -1, 0),
    (-1, 1, 0),
    (0, 0, 1)
)

TOP_SIDE = (
    (0, -1, 0),
    (1, 1, 1),
    (0, 0, 0)
)

R_TOP_CORNER = (
    (0, -1, 0),
    (0, 1, -1),
    (1, 0, 0)
)

LEFT_SIDE = (
    (0, 1, 0),
    (-1, 1, 0),
    (0, 1, 0)
)

RIGHT_SIDE = (
    (0, 1, 0),
    (0, 1, -1),
    (0, 1, 0)
)

L_BOT_CORNER = (
    (0, 0, 1),
    (-1, 1, 0),
    (0, -1, 0)
)

BOT_SIDE = (
    (0, 0, 0),
    (1, 1, 1),
    (0, -1, 0)
)

R_BOT_CORNER = (
    (1, 0, 0),
    (0, 1, -1),
    (0, -1, 0)
)

TOP_LEFT_GRASS = (
    (0, 0, 0),
    (-1, -1, 0),
    (-1, 1, 0)
)

TOP_MID_GRASS = (
    (0, -1, 0),
    (0, -1, 0),
    (1, 1, 1)
)

TOP_RIGHT_GRASS = (
    (0, 0, 0),
    (0, -1, -1),
    (0, 1, -1)
)

tile_rules = {
    L_TOP_CORNER: 1,
    TOP_SIDE: 2,
    R_TOP_CORNER: 3,
    LEFT_SIDE: 4,
    RIGHT_SIDE: 6,
    L_BOT_CORNER: 7,
    BOT_SIDE: 8,
    R_BOT_CORNER: 9,
    TOP_LEFT_GRASS: 10,
    TOP_MID_GRASS: 11,
    TOP_RIGHT_GRASS: 12,
}

#endregion

class ComboTile():
    def __init__(self, width, height, tile_order):
        self.width = width
        self.height = height
        self.tile_order = tile_order

combo_tiles = (
    ComboTile(
        2,
        3,
        [13, 14, 15, 16, 17, 18]
    ),
    ComboTile(
        5,
        5,
        [0, 0, 19, 20, 0, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34 ,35, 36, 37, 38, 39, 40]
    ),
)

# TODO - (low priority) add randomization to the levels

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
        print("generating rooms... plase wait")
        rand = random.randint(0, self.width - 1)
        # starting tile is the tile at the top row and random number
        start = [0, rand]
        activetile = start
        self.rooms.append(activetile)
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
                    room = Island(60, 51, [30, 27], 30, 25, 500, tile_rules)

                    path = os.getcwd()
                    room_map_path = os.path.join(path, "Map/room_{x_coordinate}_{y_coordinate}.txt".format(x_coordinate = i, y_coordinate = j))
                    
                    f_room = open(room_map_path, "x")

                    room.write(f_room)

        # for i in range(self.height):
        #     print(self.tilemap[i])

        self.write_map()

    def step(self, tile):
        # gets neighbours
        neighbours = self.get_neighbours(tile[1], tile[0])
        # print(neighbours)
        tile = random.choice(neighbours)
        # print(tile)
        self.tilemap[tile[0]][tile[1]] = 1

        self.rooms.append(tile)

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

    def write_map(self):
        path = os.getcwd()
        map_path = os.path.join(path, "Map/map.txt")

        f_map = open(map_path, "x")
        
        f_map.write(str(self.rooms))

class Island():
    def __init__(self, width, height, center, max_radius_x, max_radius_y, probability_factor, rules):
        self.tilemap = []
        self.center = center
        self.height = height
        self.width = width
        self.max_radius_x = max_radius_x
        self.max_radius_y = max_radius_y
        self.probability_factor = probability_factor

        self.rules = rules

        self.sprites = []

        for i in range(height):
            self.tilemap.append([])
            for j in range(width):
                self.tilemap[i].append(0)

        self.generate_tiles()
        self.apply_rules()
        
        # for row in self.tilemap:
            # print(row)

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

    def apply_rules(self):
        tilemap_copy = copy.deepcopy(self.tilemap)
        # printed = False

        for i in range(len(tilemap_copy)):
            for j in range(len(tilemap_copy[i])):
                neighbours = [
                    [0, 0, 0],
                    [0, 0, 0],
                    [0, 0, 0]
                ]

                for y in range(i - 1, i + 2):
                    for x in range(j - 1, j + 2):
                        if y > 0 and y < self.height - 1:
                            if x > 0 and x < self.width - 1:
                                neighbours[y - i + 1][x - j + 1] = self.tilemap[y][x]

                for key in self.rules:
                    check = [
                        [False, False, False],
                        [False, False, False],
                        [False, False, False]
                    ]

                    for y in range(len(key)):
                        for x in range(len(key[y])):
        
                            if key[y][x] == 0:
                                check[y][x] = True
                            elif key[y][x] == -1 and neighbours[y][x] == 0:
                                check[y][x] = True
                            elif key[y][x] == 1 and neighbours[y][x] == 1:
                                check[y][x] = True

                    # if self.tilemap[i][j] != 0 and not printed:
                        # print(neighbours, key)
                        # print(i, j)
                        # print(check)
                        # printed = True
                    # for row in check:
                    #     print(row)

                    if self.tilemap[i][j] != 0:
                        if check == [
                            [True, True, True],
                            [True, True, True],
                            [True, True, True]
                        ]:    
                            # print("set tile to " + str(self.rules[key]))
                            tilemap_copy[i][j] = self.rules[key]
                            break
                        else:
                            # print("yees")
                            tilemap_copy[i][j] = 5
                    else:
                        if check == [
                            [True, True, True],
                            [True, True, True],
                            [True, True, True]
                        ]:    
                            # print("changed air block")
                            # print("set tile to " + str(self.rules[key]))
                            tilemap_copy[i][j] = self.rules[key]
                            break
        
        # TODO - fix the tree placing system so it doesn't overwrite other tiles and doesn't place trees in the air
        for combo_tile in combo_tiles:
            for i in range(len(tilemap_copy)):
                for j in range(len(tilemap_copy[i])):
                    if tilemap_copy[i][j] == 11 and random.randint(0, 10) > 7:
                        contains_block = False
                        # print(combo_tile.height)
                        # print(combo_tile.width)
                        for y in range(i, i + combo_tile.height):
                            for x in range(j, combo_tile.width):
                                if tilemap_copy[y][x] != 0:
                                    contains_block = True

                        if not contains_block:
                            for y in range(combo_tile.height):
                                for x in range(combo_tile.width):
                                    # print(x, y)
                                    tilemap_copy[i - y][j + x] = combo_tile.tile_order[y * combo_tile.width + x]


        self.tilemap = tilemap_copy

    def write(self, file):
        tilemap_string = "["
        for row in self.tilemap:
            tilemap_string += "\n"
            tilemap_string += str(row)
            tilemap_string += ","

        tilemap_string += "]"        

        file.write(tilemap_string)

    @staticmethod
    def read_tilemap(tilemap_data):
        rows = tilemap_data.split("\n")
        rows.pop(0)

        for i in range(len(rows)):
            str_list = list(rows[i])
            rows[i] = [int(i) for i in str_list]
            
        return rows

# random ass test function
def generate_test_map():
    island = Island(60, 51, [30, 27], 30, 25, 500, tile_rules)
    print(island.tilemap)