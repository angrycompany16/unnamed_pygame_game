import math
import pygame as pyg
import vectors
import os
import enum

# ------------------ CONSTANTS ---------------------


WIDTH = 640
HEIGHT = 640
PIXELS_PER_UNIT = 2
RED = pyg.Color(255, 0, 0)


# --------------------------------------------------


# --------- INITIALIZATION & VARIABLES -------------


pyg.init()
screen = pyg.display.set_mode((WIDTH, HEIGHT))
surf = pyg.Surface((WIDTH, HEIGHT))
tilemap_surf = pyg.Surface((WIDTH, HEIGHT))

moving_sprites = pyg.sprite.Group()

main_clock = pyg.time.Clock()
delta_time = 0

tilemap = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 4, 5, 5, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 8, 9, 9, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 8, 9, 9, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 12, 13, 13, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 5, 5, 5, 5],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 9, 9, 9, 9],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 9, 9, 9, 9],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 9, 9, 9, 9],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 9, 9, 9, 9],
    [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9]
]

path = os.getcwd()
tileset_image = pyg.image.load(os.path.join(path, 'Sprites/Tilemaps', 'tilemap-ting.png'))

tileset_width = int(tileset_image.get_width() / 16)
tileset_height = int(tileset_image.get_height() / 16)

# create tileset array of surfaces, each containing a tile

tileset = []

for i in range(tileset_width * tileset_height):
    tileset.append(pyg.Surface((16, 16)))

test_arr = [0] * tileset_width * tileset_height

for i in range(tileset_height):
    for j in range(tileset_width):
        tileset[4 * i + j].blit(tileset_image, (0, 0), pyg.Rect((16 * j, 16 * i), (16, 16)))


# --------------------------------------------------


# ----------------- INPUT & OUTPUT -----------------


class Axis(enum.Enum):
    X = 1
    Y = 2

def GetAxis(axis) -> int:
    if axis == Axis.X:
        if pyg.key.get_pressed()[pyg.K_a]:
            return -1
        elif pyg.key.get_pressed()[pyg.K_d]:
            return 1
        else:
            return 0
    elif axis == Axis.Y:
        if pyg.key.get_pressed()[pyg.K_w]:
            return -1
        elif pyg.key.get_pressed()[pyg.K_s]:
            return 1
        else:
            return 0
    else:
        print("{} is not a valid axis!".format(axis))


# --------------------------------------------------

class PhysicsObject():
    def __init__(self, position, velocity, acceleration, gravity = True):
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration

        if gravity:
            self.acceleration = [0, 9.81]

    def calculate_movement(self):
        self.velocity += self.acceleration * delta_time
        self.position += self.velocity * delta_time

        return self.position


class Player(pyg.sprite.Sprite):
    def __init__(self, player_physics, image, move_speed = 30):
        pyg.sprite.Sprite.__init__(self)

        self.player_physics = player_physics
        self.image = image
        self.rect = pyg.Rect(
            player_physics.position, 
            (image.get_width(), image.get_height())
        )
        self.move_speed = move_speed

        moving_sprites.add(self)

    def update(self):
        new_pos = self.player_physics.calculate_movement()

        self.rect.x = new_pos[0]
        self.rect.y = new_pos[1]

player = Player(
    PhysicsObject(
        vectors.Vec([32, 32]),
        vectors.Vec([0, 0]),
        vectors.Vec([0, 0]),
        gravity=False
    ),
    pyg.image.load(os.path.join('Sprites', 'char.png'))
)

def update_physics():
    player.player_physics.calculate_movement()


# ------------------ GAME LOOP ---------------------


running = True
while running:
    player.player_physics.velocity[0] = GetAxis(Axis.X) * player.move_speed
    player.player_physics.velocity[1] = GetAxis(Axis.Y) * player.move_speed


    update_physics()

    for i in range(len(tilemap)):
        for j in range(len(tilemap[i])):
            surf.blit(tileset[tilemap[i][j]], (16 * j, 16 * i))

    moving_sprites.update()
    moving_sprites.draw(surf)

    screen.blit(pyg.transform.scale(
            surf, 
            (WIDTH * PIXELS_PER_UNIT, HEIGHT * PIXELS_PER_UNIT)
        ), 
        (0, 0)
    )

    pyg.display.update()

    delta_time = main_clock.tick() / 1000

    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            running = False
            pyg.quit()
        if event.type == pyg.KEYDOWN:
            if event.key == pyg.K_w:
                print("w")
            if event.key == pyg.K_a:
                print("a")
            if event.key == pyg.K_s:
                print("s")
            if event.key == pyg.K_d:
                print("d")


# --------------------------------------------------
