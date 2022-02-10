import math
import pygame as pyg
import vectors
import os
import enum
import drawer

# ------------------ CONSTANTS ---------------------
# resolution tiles: 30 * 17

WIDTH = 1920
HEIGHT = 1080
JUMP_SPEED = 130
MOVE_SPEED = 50
GRAVITY_MULTIPLIER = 10
RELEASE_FALL_SPEED = 10


PIXEL_SCALE_FACTOR = 4
RED = pyg.Color(255, 0, 0)
BLUE = pyg.Color(0, 0, 255)
BLACK = pyg.Color(0, 0, 0)


# --------------------------------------------------


# --------- INITIALIZATION & VARIABLES -------------


pyg.init()
screen = pyg.display.set_mode((WIDTH, HEIGHT))
surf = pyg.Surface((WIDTH / PIXEL_SCALE_FACTOR, HEIGHT / PIXEL_SCALE_FACTOR))
# surf_all = pyg.Surface((WIDTH / PIXEL_SCALE_FACTOR, HEIGHT / PIXEL_SCALE_FACTOR))
# surf_fg = pyg.Surface((WIDTH / PIXEL_SCALE_FACTOR, HEIGHT / PIXEL_SCALE_FACTOR))
# surf_mg = pyg.Surface((WIDTH / PIXEL_SCALE_FACTOR, HEIGHT / PIXEL_SCALE_FACTOR))
# surf_bg = pyg.Surface((WIDTH / PIXEL_SCALE_FACTOR, HEIGHT / PIXEL_SCALE_FACTOR))
camera_scroll = vectors.Vec([0, 0])
# all_surfaces_group = drawer.SurfGroup()

# all_surfaces_group.add(surf_bg, 0)
# all_surfaces_group.add(surf_mg, 1)
# all_surfaces_group.add(surf_fg, 2)

main_clock = pyg.time.Clock()
delta_time = 0

tilemap = [
    [0, 0, 0, 0, 0, 4, 5, 5, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 8, 9, 9, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 8, 9, 9, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 12, 13, 13, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9]
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

tile_rects = []

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

# I literally never want to touch this code ever again
# But hey, at least it works
class Gun():
    def __init__(self, image):
        self.image = image
        self.angle = 0

    def look_at(self, pos, target):
        new_angle = 0

        center = vectors.Vec([WIDTH / (2 * PIXEL_SCALE_FACTOR), HEIGHT / (2 * PIXEL_SCALE_FACTOR)])

        dist_x = target[0] - center[0]
        dist_y = center[1] - target[1]

        if target[0] != 0:
            new_angle = 180 * -math.atan2(dist_x, dist_y) / math.pi

        rot_sprite = pyg.transform.rotate(self.image, (new_angle - 90))
        new_rect = rot_sprite.get_rect(center = pos)

        pyg.draw.rect(surf, RED, new_rect, 1)
        surf.blit(rot_sprite, new_rect)

        self.angle = new_angle


class PhysicsObject():
    def __init__(self, position, velocity, acceleration, gravity = True):
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration

        if gravity:
            self.acceleration = vectors.Vec([0, 9.81 * GRAVITY_MULTIPLIER])


    def calculate_movement(self):
        self.velocity += self.acceleration * delta_time
        self.position += self.velocity * delta_time

        return self.position


class Player():
    def __init__(self, player_physics, image, gun, move_speed = MOVE_SPEED):
        self.player_physics = player_physics
        self.image = image
        self.gun = gun
        self.rect = pyg.Rect(
            player_physics.position, 
            (image.get_width(), image.get_height())
        )
        self.move_speed = move_speed
        self.on_ground = False

        self.collision_types = { 
            'top': False,
            'bottom': False,
            'right': False,
            'left': True
        }

    def check_collision(self, old_pos, new_pos) -> vectors.Vec:
        dp = new_pos - old_pos

        for tile in tile_rects:
            # check for collision in x direction
            if tile.colliderect(pyg.Rect(new_pos[0], old_pos[1], self.rect.width, self.rect.height)):
                dp[0] = 0

            # check for collision in y direction
            if tile.colliderect(pyg.Rect(old_pos[0], new_pos[1], self.rect.width, self.rect.height)):
                # check if below ground / jumping
                if self.player_physics.velocity[1] < 0:
                    dp[1] = tile.bottom - self.rect.top
                    self.player_physics.velocity[1] = 0
                # check if above ground / falling
                elif self.player_physics.velocity[1] > 0:
                    self.on_ground = True
                    dp[1] = tile.top - self.rect.bottom
                    self.player_physics.velocity[1] = 0

        old_pos += dp
        return old_pos

    def update(self):
        old_pos = player.player_physics.position
        max_new_pos = self.player_physics.calculate_movement()

        new_pos = self.check_collision(old_pos, max_new_pos)

        pyg.draw.rect(surf, RED, player.rect, 1)
        self.player_physics.position = new_pos
        self.rect.x = new_pos[0]
        self.rect.y = new_pos[1]
        surf.blit(self.image, (self.rect.x, self.rect.y))


player = Player(
    PhysicsObject(
        vectors.Vec([32, 32]),
        vectors.Vec([0, 0]),
        vectors.Vec([0, 0])
    ),
    pyg.image.load(os.path.join('Sprites', 'character.png')),
    Gun(pyg.image.load(os.path.join('Sprites', 'gun.png')))
)

def update_physics():
    player.player_physics.calculate_movement()


# ------------------ GAME LOOP ---------------------


running = True
while running:
    # screen.fill(BLACK)
    # all_surfaces_group.fill(BLACK)
    player.player_physics.velocity[0] = GetAxis(Axis.X) * player.move_speed

    camera_scroll[0] = player.player_physics.position[0] * PIXEL_SCALE_FACTOR - WIDTH / 2
    camera_scroll[1] = player.player_physics.position[1] * PIXEL_SCALE_FACTOR - HEIGHT / 2
    
    tile_rects = []

    for i in range(len(tilemap)):
        for j in range(len(tilemap[i])):
            surf.blit(tileset[tilemap[i][j]], (16 * j, 16 * i))
            if tilemap[i][j] != 0:
                pyg.draw.rect(surf, BLUE, pyg.Rect(16 * j, 16 * i, 16, 16), 1)
                tile_rects.append(pyg.Rect(16 * j, 16 * i, 16, 16))

    player.update()
    # player.gun.look_at(player.player_physics.position, vectors.Vec([0, 50]))
    mouse_pos = pyg.mouse.get_pos()

    player.gun.look_at(player.player_physics.position, (mouse_pos[0] / PIXEL_SCALE_FACTOR, mouse_pos[1] / PIXEL_SCALE_FACTOR))
    print(mouse_pos)

    screen.blit(pyg.transform.scale(
            surf, 
            (WIDTH, HEIGHT)
        ), 
        (-camera_scroll[0], -camera_scroll[1])
    )

    pyg.display.update()

    delta_time = main_clock.tick() / 1000

    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            running = False
            pyg.quit()
        if event.type == pyg.KEYDOWN:
            if event.key == pyg.K_SPACE and player.on_ground:
                player.on_ground = False
                player.player_physics.velocity[1] = -JUMP_SPEED
        if event.type == pyg.KEYUP:
            if (event.key == pyg.K_SPACE 
            and not player.on_ground 
            and player.player_physics.velocity[1] < 0):
                player.player_physics.velocity[1] = RELEASE_FALL_SPEED



# --------------------------------------------------
