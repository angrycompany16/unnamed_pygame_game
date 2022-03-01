# TODO - make better character sprite and animations
# TODO - clean up the code (make it shorter and group together related stuff)
# TODO - make level generation include trees and stuff

import math, vectors, os, enum, game_debugger, world_gen, copy, entities, random, animations, particle_system
import game_manager as gm
import pygame as pyg
from ast import literal_eval

#region CONSTANTS
# resolution tiles: 60 * 51
# resolution pixels: 480 * 270

# screeen
WIDTH = 1920
HEIGHT = 1080
PIXEL_SCALE_FACTOR = 4
CAMERA_MOVE_SLOWNESS = 20
# Border_x (left border, right border)
CAMERA_BORDERS_X = vectors.Vec([0, WIDTH + WIDTH / PIXEL_SCALE_FACTOR])
# Border_y (top border, bottom border)
CAMERA_BORDERS_Y = vectors.Vec([0, HEIGHT + 2 * HEIGHT / PIXEL_SCALE_FACTOR])
CAMERA_OFFSET_X = 0
CAMERA_OFFSET_Y = 0

# player stats
JUMP_SPEED = 300
MOVE_SPEED = 160
GRAVITY_MULTIPLIER = 50
RELEASE_FALL_SPEED = 80
BULLET_SPEED = 400
SHOOT_BOUNCE_SPEED = 300
MAX_FALL_VEL = 200
MAX_X_VEL = 300
MAX_JUMP_VEL = 400

# movement damping
WALK_DAMPING = 20

# colors
RED = pyg.Color(255, 0, 0)
BLUE = pyg.Color(0, 0, 255)
BLACK = pyg.Color(0, 0, 0)

BG1 = pyg.Color(57, 49, 75)
BG2 = pyg.Color(86, 64, 100)

SQUARE_SIZE = 32

#endregion

#region INITIALIZATION & VARIABLES

pyg.init()
screen = pyg.display.set_mode((WIDTH, HEIGHT), pyg.NOFRAME)
surf = pyg.Surface((WIDTH / PIXEL_SCALE_FACTOR, HEIGHT / PIXEL_SCALE_FACTOR))
bg_surf = pyg.Surface((WIDTH * 2 / PIXEL_SCALE_FACTOR, HEIGHT * 3 / PIXEL_SCALE_FACTOR))
true_camera_scroll = vectors.Vec([0, 0])

main_clock = pyg.time.Clock()

tileset_image = pyg.image.load(os.path.join(gm.path, 'Sprites/Tilemaps', 'tilemap.png')).convert_alpha()

level_layout = []
enemy_list = []

#region MAP
map_index = 0

# Map generation / reading
def load_map():
    if os.listdir(gm.path + "/Map") == []:
        foo = world_gen.RoomLayout(20, 20)
        foo.create_rooms()
    
    map_path = os.path.join(gm.path + "/Map/map.txt")
    f_map = open(map_path, "r")
    level_layout = literal_eval(f_map.read())
    
    room_path = os.path.join(gm.path + "/Map/room_{x_coordinate}_{y_coordinate}.txt".format(x_coordinate = level_layout[map_index][0], y_coordinate = level_layout[map_index][1]))
    f_level = open(room_path, "r")
    tilemap_read = literal_eval(f_level.read())

    # Setting all the elements of the 2D array to 0
    tilemap_fg = list(map(lambda y: list(map(lambda x: 0, y)), copy.deepcopy(tilemap_read)))
    tilemap_mg = list(map(lambda y: list(map(lambda x: 0, y)), copy.deepcopy(tilemap_read)))

    for i in range(len(tilemap_read)):
        for j in range(len(tilemap_read[i])):
            if tilemap_read[i][j] < 10:
                tilemap_fg[i][j] = tilemap_read[i][j]
            else:
                tilemap_mg[i][j] = tilemap_read[i][j]   

    return tilemap_fg, tilemap_mg

tilemap_fg, tilemap_mg = load_map()
    

def spawn_enemies(amount):
    for i in range(amount):
        drone = entities.Drone(
            5, 
            1, 
            vectors.Vec([random.randint(0, 960), random.randint(0, 810)]), 
            pyg.image.load(os.path.join('Sprites/Spritesheets', 'drone_enemy-Sheet.png')).convert_alpha(),
            0.05,
            pyg.image.load(os.path.join('Sprites', 'drone_enemy.png')).convert_alpha()
        )
        enemy_list.append(drone)

# spawn_enemies(3)

#endregion

def draw_bg():
    bg_surf.fill(BG2)
    for i in range(math.ceil(HEIGHT * 3 / (PIXEL_SCALE_FACTOR * SQUARE_SIZE))):
        for j in range(math.ceil(WIDTH * 2 / (PIXEL_SCALE_FACTOR * SQUARE_SIZE))):
            if (i + j) % 2 == 0:
                pyg.draw.rect(bg_surf, BG1, pyg.Rect(
                    j * SQUARE_SIZE,
                    i * SQUARE_SIZE,
                    SQUARE_SIZE, 
                    SQUARE_SIZE
                    ))

tileset_width = int(tileset_image.get_width() / 16)
tileset_height = int(tileset_image.get_height() / 16)

# create tileset array of surfaces, each containing a tile

tileset = []

for i in range(tileset_width * tileset_height):
    tileset.append(pyg.Surface((16, 16), pyg.SRCALPHA))

for i in range(tileset_height):
    for j in range(tileset_width):
        tileset[i * tileset_width + j].blit(tileset_image, (0, 0), pyg.Rect((16 * j, 16 * i), (16, 16)))

bg_img = pyg.image.load(os.path.join(gm.path, 'Sprites', 'background.png')).convert()

# debug_screen = game_debugger.DebugPanel(vectors.Vec([WIDTH, 80]), vectors.Vec([0, 0]))
# debug_text = debug_screen.input_box

#endregion

#region INPUT STUFF

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

#endregion

#region PLAYER

class PhysicsObject():
    def __init__(self, position, velocity, acceleration, gravity = True):
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration

        if gravity:
            self.acceleration = vectors.Vec([0, 9.81 * GRAVITY_MULTIPLIER])


    def calculate_movement(self):
        self.velocity += vectors.Vec([0, 9.81 * GRAVITY_MULTIPLIER]) * gm.delta_time
        
        if self.velocity[1] > MAX_FALL_VEL:
            self.velocity[1] = MAX_FALL_VEL
        elif self.velocity[1] < -MAX_JUMP_VEL:
            self.velocity[1] = -MAX_JUMP_VEL

        if abs(self.velocity[0]) > MAX_X_VEL:
            self.velocity[0] = math.copysign(MAX_X_VEL, self.velocity[0])

        self.position += self.velocity * gm.delta_time

        return self.position

class Player(entities.Entity):
    def __init__(self, physics, image, gun, max_HP):
        super().__init__(max_HP, 0)
        self.physics = physics
        self.image = image
        self.gun = gun
        self.rect = pyg.Rect(
            physics.position, 
            (image.get_width(), image.get_height())
        )
        self.on_ground = False
        self.has_double_jumped = False

        self.bullets = []
        self.collision_types = { 
            'top': False,
            'bottom': False,
            'right': False,
            'left': True
        }

    def check_collision(self, old_pos, new_pos) -> vectors.Vec:
        dp = new_pos - old_pos
        collision_types = {
            'top': False,
            'bot': False,
        }

        for tile in tile_rects:
            # check for collision in x direction
            if tile.colliderect(pyg.Rect(new_pos[0], old_pos[1], self.rect.width, self.rect.height)):
                dp[0] = 0

            # check for collision in y direction
            if tile.colliderect(pyg.Rect(old_pos[0], new_pos[1], self.rect.width, self.rect.height)):
                # check if below ground / jumping
                if self.physics.velocity[1] < 0:
                    dp[1] = tile.bottom - self.rect.top
                    collision_types['top'] = True
                # check if above ground / falling
                elif self.physics.velocity[1] > 0:
                    self.on_ground = True
                    self.has_double_jumped = False
                    dp[1] = tile.top - self.rect.bottom
                    collision_types['bot'] = True

        if collision_types['top'] == True:
            self.physics.velocity[1] = RELEASE_FALL_SPEED
        elif collision_types['bot'] == True:
            self.physics.velocity[1] = 0
        
        old_pos += dp
        return old_pos

    def update(self):
        old_pos = self.physics.position
        max_new_pos = self.physics.calculate_movement()

        new_pos = self.check_collision(old_pos, max_new_pos)

        pyg.draw.rect(surf, RED, (self.rect.x - gm.rounded_camera_scroll[0], self.rect.y -gm.rounded_camera_scroll[1], self.rect.w, self.rect.h), 1)
        self.physics.position = new_pos
        self.rect.x = new_pos[0]
        self.rect.y = new_pos[1]

        surf.blit(self.image, (self.rect.x - gm.rounded_camera_scroll[0], self.rect.y - gm.rounded_camera_scroll[1]))

    def shoot(self):
        # Calculate velocity and the  rest of the arguments
        bullet = entities.Bullet(
            vectors.Vec([
                player.physics.position[0] + player.rect.width / 2,
                player.physics.position[1] + player.rect.height / 2
            ]),
            vectors.Vec([
                -math.cos((self.gun.angle) * math.pi / 180),
                math.sin((self.gun.angle) * math.pi / 180)
            ]),
            pyg.image.load(os.path.join('Sprites', 'bullet.png')).convert(),
            self.gun.angle,
            BULLET_SPEED
        )

        self.physics.velocity[0] += math.cos((self.gun.angle) * math.pi / 180) * SHOOT_BOUNCE_SPEED
        self.physics.velocity[1] -= math.sin((self.gun.angle) * math.pi / 180) * SHOOT_BOUNCE_SPEED

        self.bullets.append(bullet)

player = Player(
    PhysicsObject(
        vectors.Vec([300, -100]),
        vectors.Vec([0, 0]),
        vectors.Vec([0, 0])
    ),
    pyg.image.load(os.path.join('Sprites', 'character.png')).convert_alpha(),
    entities.Gun(pyg.image.load(os.path.join('Sprites', 'gun.png')).convert_alpha()),
    5
)

# turret = entities.Turret(10, 1, vectors.Vec([500, 500]), pyg.image.load(os.path.join('Sprites', 'turret.png')))
# enemy_list.append(turret)

# for i in range(4):
#     drone = entities.Drone(5, 1, vectors.Vec([random.randint(0, 960), random.randint(0, 810)]), pyg.image.load(os.path.join('Sprites', 'drone_enemy.png')))
#     enemy_list.append(drone)

#endregion

#region GAME LOOP

running = True
while running:
    screen.fill(BLACK)

    # if not debug_text.active:
    if player.on_ground:
        player.physics.velocity[0] += (GetAxis(Axis.X) * MOVE_SPEED - player.physics.velocity[0]) / WALK_DAMPING
    elif not player.on_ground:
        player.physics.velocity[0] += (GetAxis(Axis.X) * MOVE_SPEED - player.physics.velocity[0]) / WALK_DAMPING

    if player.physics.velocity[1] != 0:
        player.on_ground = False

    true_camera_scroll[0] += ((player.physics.position[0] + CAMERA_OFFSET_X) * PIXEL_SCALE_FACTOR - true_camera_scroll[0] - WIDTH / 2) / CAMERA_MOVE_SLOWNESS
    true_camera_scroll[1] += ((player.physics.position[1] + CAMERA_OFFSET_Y) * PIXEL_SCALE_FACTOR - true_camera_scroll[1] - HEIGHT / 2) / CAMERA_MOVE_SLOWNESS
    
    # turn the camera scroll value to integer. Helps with bugs apparently
    gm.rounded_camera_scroll = list(map(lambda x: int(x / PIXEL_SCALE_FACTOR), true_camera_scroll))

    # basically just clamps the venter point between specified values
    gm.rounded_camera_scroll[0] = vectors.Math.clamp(gm.rounded_camera_scroll[0], CAMERA_BORDERS_X[0],  CAMERA_BORDERS_X[1] - WIDTH)
    gm.rounded_camera_scroll[1] = vectors.Math.clamp(gm.rounded_camera_scroll[1], CAMERA_BORDERS_Y[0],  CAMERA_BORDERS_Y[1] - HEIGHT)

    draw_bg()
    surf.blit(bg_surf, (-gm.rounded_camera_scroll[0], -gm.rounded_camera_scroll[1]))

    tile_rects = []

    for i in range(len(tilemap_fg)):
        for j in range(len(tilemap_fg[i])):
            if tilemap_fg[i][j] != 0:
                surf.blit(tileset[tilemap_fg[i][j]], (
                    16 * j - gm.rounded_camera_scroll[0], 
                    16 * i - gm.rounded_camera_scroll[1])
                )
                tile_rects.append(pyg.Rect(16 * j, 16 * i, 16, 16))

    for i in range(len(tilemap_mg)):
        for j in range(len(tilemap_mg[i])):
            if tilemap_mg[i][j] != 0:
                surf.blit(tileset[tilemap_mg[i][j]], (
                    16 * j - gm.rounded_camera_scroll[0], 
                    16 * i - gm.rounded_camera_scroll[1])
                )
    

    for enemy in enemy_list:
        enemy.update(player.physics.position)
        surf.blit(enemy.image, (
                enemy.rect.x - gm.rounded_camera_scroll[0],
                enemy.rect.y - gm.rounded_camera_scroll[1])
            )
        enemy.gun.look_at(
            (
                enemy.pos[0] + enemy.image.get_width() / 2,
                enemy.pos[1] + enemy.image.get_height() / 2
            ), 
            (
                player.physics.position[0] - gm.rounded_camera_scroll[0] + player.image.get_width() / 2,
                player.physics.position[1] - gm.rounded_camera_scroll[1] + player.image.get_height() / 2
            )
        )

        surf.blit(enemy.gun.sprite, (enemy.gun.rect.x  - gm.rounded_camera_scroll[0], enemy.gun.rect.y - gm.rounded_camera_scroll[1]))
        
        for bullet in enemy.bullets:
            bullet.update()
            surf.blit(bullet.image, (bullet.rect.x - gm.rounded_camera_scroll[0], bullet.rect.y - gm.rounded_camera_scroll[1]))
            if pyg.Rect.colliderect(bullet.rect, player.rect):
                player.take_damage(bullet.damage)
                enemy.bullets.remove(bullet)
                if player.current_HP <= 0:
                    running = False
            

    # this can be optimized by calculating the trajectory of the bullet and only checking the rects that overlap, since the bullets move in a straight line
    # collision with enemies will be implemented in the same way
    enemy_rects = [enemy.rect for enemy in enemy_list]

    for bullet in player.bullets:
        bullet.update()
        surf.blit(bullet.image, (bullet.rect.x - gm.rounded_camera_scroll[0], bullet.rect.y - gm.rounded_camera_scroll[1]))
        for tile in tile_rects:
            if pyg.Rect.colliderect(bullet.rect, tile) and bullet in player.bullets:
                player.bullets.remove(bullet)
            elif bullet.lifetime > 3 and bullet in player.bullets:
                player.bullets.remove(bullet)

        enemy_index = pyg.Rect.collidelist(bullet.rect, enemy_rects)
        
        if enemy_index != -1:
            enemy_list[enemy_index].take_damage(bullet.damage)
            if enemy_list[enemy_index].current_HP <= 0:
                enemy_list.pop(enemy_index)
            if bullet in player.bullets:
                player.bullets.remove(bullet)


    player.update()

    pyg.draw.rect(surf, RED, pyg.Rect(player.gun.rect.x -gm.rounded_camera_scroll[0], player.gun.rect.y -gm.rounded_camera_scroll[1], player.gun.rect.w, player.gun.rect.h), 1)
    surf.blit(player.gun.sprite, (player.gun.rect.x  - gm.rounded_camera_scroll[0], player.gun.rect.y - gm.rounded_camera_scroll[1]))

    if player.physics.position[0] > (WIDTH * 2 - CAMERA_BORDERS_X[0]) / PIXEL_SCALE_FACTOR:
        if enemy_list == []:
            map_index += 1
            tilemap_fg, tilemap_mg = load_map()
            # spawn_enemies(3)
        player.physics.position[0] = 0
    elif player.physics.position[0] < 0: 
        if enemy_list == []:
            map_index += 1
            tilemap_fg, tilemap_mg = load_map()
            # spawn_enemies(3)
        player.physics.position[0] = (WIDTH * 2 - CAMERA_BORDERS_X[0]) / PIXEL_SCALE_FACTOR - player.image.get_width()


    if player.physics.position[1] > (HEIGHT * 3 - CAMERA_BORDERS_Y[0]) / PIXEL_SCALE_FACTOR:
        if enemy_list == []:
            map_index += 1
            tilemap_fg, tilemap_mg = load_map()
            # spawn_enemies(3)

        player.physics.position[1] = 0

    mouse_pos = pyg.mouse.get_pos()

    player.gun.look_at(
        (
            player.physics.position[0] + player.image.get_width() / 2,
            player.physics.position[1] + player.image.get_height() / 2
        ), 
        (
            mouse_pos[0] / PIXEL_SCALE_FACTOR, 
            mouse_pos[1] / PIXEL_SCALE_FACTOR
        )
    )

    screen.blit(pyg.transform.scale(
            surf.convert(), 
            (WIDTH, HEIGHT)
        ), 
        (0, 0)
    )

    # debug_screen.update(screen)

    pyg.display.update()

    gm.delta_time = main_clock.tick() / 1000

    for event in pyg.event.get():
        if event.type == pyg.QUIT:
            running = False
            # debug_game.reset_all()
            pyg.quit()
        if event.type == pyg.KEYDOWN:
            # if debug_text.active:
                # if event.key == pyg.K_BACKSPACE:
                    # debug_text.text = debug_text.text[:-1]
                # elif event.key == pyg.K_RETURN:
                #     changed = debug_screen.parse_input()
                #     if changed != ():
                #         exec("%s = %d" % changed)

                #     debug_text.active = False
                # else:
                #     debug_text.text += event.unicode

                # debug_text.update_text()
            # else:
                if event.key == pyg.K_SPACE:
                    if player.on_ground:
                        player.physics.velocity[1] = -JUMP_SPEED
                    elif not player.has_double_jumped:
                        player.physics.velocity[1] = -JUMP_SPEED
                        player.has_double_jumped = True

        if event.type == pyg.KEYUP:
            if (event.key == pyg.K_SPACE 
            and not player.on_ground 
            and player.physics.velocity[1] < 0):
                player.physics.velocity[1] += RELEASE_FALL_SPEED
        if event.type == pyg.MOUSEBUTTONDOWN:
            if event.button == 1: # 1 is left mouse button
                # if debug_text.rect.collidepoint(event.pos):
                #     debug_text.active = True
                # else:
                #     debug_text.active = False
                    player.shoot()
#endregion
