from doctest import testfile
import math
from numpy import tile
import pygame
import vectors
import os

# ------------------ CONSTANTS ---------------------


WIDTH = 640
HEIGHT = 640
PIXELS_PER_UNIT = 2
RED = pygame.Color(255, 0, 0)


# --------------------------------------------------


# --------- INITIALIZATION & VARIABLES -------------


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
surf = pygame.Surface((WIDTH, HEIGHT))
tilemap_surf = pygame.Surface((WIDTH, HEIGHT))

moving_sprites = pygame.sprite.Group()

main_clock = pygame.time.Clock()
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
tileset_image = pygame.image.load(os.path.join(path, 'Sprites/Tilemaps', 'tilemap-ting.png'))

tileset_width = int(tileset_image.get_width() / 16)
tileset_height = int(tileset_image.get_height() / 16)

# create tileset array of surfaces, each containing a tile

tileset = []

for i in range(tileset_width * tileset_height):
    tileset.append(pygame.Surface((16, 16)))

test_arr = [0] * tileset_width * tileset_height

for i in range(tileset_height):
    for j in range(tileset_width):
        tileset[4 * i + j].blit(tileset_image, (0, 0), pygame.Rect((16 * j, 16 * i), (16, 16)))


# --------------------------------------------------


class PhysicsObject():
    def __init__(self, position, velocity, acceleration):
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration

    def calculate_movement(self):
        self.velocity += self.acceleration * delta_time
        self.position += self.velocity * delta_time

        return self.position


class Player(pygame.sprite.Sprite):
    def __init__(self, player_physics, image):
        pygame.sprite.Sprite.__init__(self)

        self.player_physics = player_physics
        self.image = image
        self.rect = pygame.Rect(
            player_physics.position, 
            (image.get_width(), image.get_height())
        )

        moving_sprites.add(self)

    def update(self):
        new_pos = self.player_physics.calculate_movement()

        self.rect.x = new_pos[0]
        self.rect.y = new_pos[1]

    def change_position(self):
        pass

player = Player(
    PhysicsObject(
        vectors.Vec([32, 32]),
        vectors.Vec([20, 0]),
        vectors.Vec([0, 10])
    ),
    pygame.image.load(os.path.join('Sprites', 'char.png'))
)

def update_physics():
    player.player_physics.calculate_movement()


# ------------------ GAME LOOP ---------------------


running = True
while running:

    update_physics()

    for i in range(len(tilemap)):
        for j in range(len(tilemap[i])):
            surf.blit(tileset[tilemap[i][j]], (16 * j, 16 * i))

    moving_sprites.update()
    moving_sprites.draw(surf)

    screen.blit(pygame.transform.scale(
            surf, 
            (WIDTH * PIXELS_PER_UNIT, HEIGHT * PIXELS_PER_UNIT)
        ), 
        (0, 0)
    )

    pygame.display.update()

    delta_time = main_clock.tick() / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()


# --------------------------------------------------
