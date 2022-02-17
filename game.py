import math, vectors, os, enum, game_debugger, world_gen
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
CAMERA_OFFSET_Y = 60

# player stats
JUMP_SPEED = 300
MOVE_SPEED = 100
GRAVITY_MULTIPLIER = 50
RELEASE_FALL_SPEED = 10
BULLET_SPEED = 400
SHOOT_BOUNCE_SPEED = 300

# movement damping
WALK_DAMPING = 20

# colors
RED = pyg.Color(255, 0, 0)
BLUE = pyg.Color(0, 0, 255)
BLACK = pyg.Color(0, 0, 0)

#endregion

#region INITIALIZATION & VARIABLES

pyg.init()
screen = pyg.display.set_mode((WIDTH, HEIGHT))
surf = pyg.Surface((WIDTH / PIXEL_SCALE_FACTOR, HEIGHT / PIXEL_SCALE_FACTOR))
true_camera_scroll = vectors.Vec([0, 0])
rounded_camera_scroll = vectors.Vec([0, 0])

main_clock = pyg.time.Clock()
delta_time = 0

# room = world_gen.Island(60, 51, [30, 27], 30, 25, 500)
# room.write(3, 4)

path = os.getcwd()
tileset_image = pyg.image.load(os.path.join(path, 'Sprites/Tilemaps', 'tilemap.png')).convert_alpha()

level_layout = []

if os.listdir(path + "/Map") == []:
    foo = world_gen.RoomLayout(20, 20)
    foo.create_rooms()
    
    map_path = os.path.join(path + "/Map/map.txt")
    f_map = open(map_path, "r")
    map_str = f_map.read()
    level_layout = literal_eval(map_str)

    room_path = os.path.join(path + "/Map/room_{x_coordinate}_{y_coordinate}.txt".format(x_coordinate = level_layout[0][0], y_coordinate = level_layout[0][1]))
    f_level = open(room_path, "r")
    tilemap = world_gen.Island.read_tilemap(f_level.read())
else:
    map_path = os.path.join(path + "/Map/map.txt")
    f_map = open(map_path, "r")
    map_str = f_map.read()
    level_layout = literal_eval(map_str)

    room_path = os.path.join(path + "/Map/room_{x_coordinate}_{y_coordinate}.txt".format(x_coordinate = level_layout[0][0], y_coordinate = level_layout[0][1]))
    f_level = open(room_path, "r")
    tilemap = world_gen.Island.read_tilemap(f_level.read())


tileset_width = int(tileset_image.get_width() / 16)
tileset_height = int(tileset_image.get_height() / 16)

# create tileset array of surfaces, each containing a tile

tileset = []

for i in range(tileset_width * tileset_height):
    tileset.append(pyg.Surface((16, 16)))

test_arr = [0] * tileset_width * tileset_height

for i in range(tileset_height):
    for j in range(tileset_width):
        tileset[3 * i + j].blit(tileset_image, (0, 0), pyg.Rect((16 * j, 16 * i), (16, 16)))

bg_img = pyg.image.load(os.path.join(path, 'Sprites', 'background.png')).convert_alpha()

bullets = []

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
# I literally never want to touch this code ever again
# But hey, at least it works
class Bullet():
    def __init__(self, position, velocity, image, angle):
        self.position = position
        self.velocity = velocity
        self.angle = angle
        self.image = pyg.transform.rotate(image, angle)
        self.rect = pyg.Rect((position), (image.get_width(), image.get_height()))
        self.lifetime = 0

    def update(self):
        self.position += self.velocity * delta_time * BULLET_SPEED
        self.rect.x = self.position[0]
        self.rect.y = self.position[1]
        surf.blit(self.image, (self.rect.x - rounded_camera_scroll[0], self.rect.y - rounded_camera_scroll[1]))
        self.lifetime += delta_time

    def check_collision(self, other_rect) -> bool:
        if pyg.Rect.colliderect(self.rect, other_rect):
            self.kill()

class Gun():
    def __init__(self, image):
        self.image = image
        self.angle = 0
        self.flipped = False

    def look_at(self, pos, target):
        new_angle = 0

        dist_x = target[0] - (pos[0] - rounded_camera_scroll[0])
        dist_y = (pos[1] - rounded_camera_scroll[1]) - target[1]

        if target[0] != 0:
            new_angle = 180 * -math.atan2(dist_x, dist_y) / math.pi - 90

        if dist_x < 0:
            if self.flipped:
                self.flip_y(False)
        elif dist_x >= 0:
            if not self.flipped:
                self.flip_y(True)

        rot_sprite = pyg.transform.rotate(self.image, (new_angle))
        new_rect = rot_sprite.get_rect(center = pos)

        pyg.draw.rect(surf, RED, pyg.Rect(new_rect.x -rounded_camera_scroll[0], new_rect.y -rounded_camera_scroll[1], new_rect.w, new_rect.h), 1)
        surf.blit(rot_sprite, (new_rect.x  - rounded_camera_scroll[0], new_rect.y - rounded_camera_scroll[1]))

        self.angle = new_angle

    def flip_y(self, set_flipped):
        flipped = pyg.transform.flip(self.image, False, True)
        self.image = flipped

        self.flipped = set_flipped

class PhysicsObject():
    def __init__(self, position, velocity, acceleration, gravity = True):
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration

        if gravity:
            self.acceleration = vectors.Vec([0, 9.81 * GRAVITY_MULTIPLIER])


    def calculate_movement(self):
        self.velocity += vectors.Vec([0, 9.81 * GRAVITY_MULTIPLIER]) * delta_time
        self.position += self.velocity * delta_time

        return self.position

class Player():
    def __init__(self, physics, image, gun):
        self.physics = physics
        self.image = image
        self.gun = gun
        self.rect = pyg.Rect(
            physics.position, 
            (image.get_width(), image.get_height())
        )
        self.on_ground = False

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

        pyg.draw.rect(surf, RED, (self.rect.x - rounded_camera_scroll[0], self.rect.y -rounded_camera_scroll[1], self.rect.w, self.rect.h), 1)
        self.physics.position = new_pos
        self.rect.x = new_pos[0]
        self.rect.y = new_pos[1]

        surf.blit(self.image, (self.rect.x - rounded_camera_scroll[0], self.rect.y - rounded_camera_scroll[1]))

    def shoot(self):
        # Calculate velocity and the  rest of the arguments
        bullet = Bullet(
            vectors.Vec([
                player.physics.position[0] + player.rect.width / 2,
                player.physics.position[1] + player.rect.height / 2
            ]),
            vectors.Vec([
                -math.cos((self.gun.angle) * math.pi / 180),
                math.sin((self.gun.angle) * math.pi / 180)
            ]),
            pyg.image.load(os.path.join('Sprites', 'bullet.png')),
            self.gun.angle
        )

        self.physics.velocity[0] = math.cos((self.gun.angle) * math.pi / 180) * SHOOT_BOUNCE_SPEED
        self.physics.velocity[1] = -math.sin((self.gun.angle) * math.pi / 180) * SHOOT_BOUNCE_SPEED

        bullets.append(bullet)

player = Player(
    PhysicsObject(
        vectors.Vec([300, -100]),
        vectors.Vec([0, 0]),
        vectors.Vec([0, 0])
    ),
    pyg.image.load(os.path.join('Sprites', 'character.png')),
    Gun(pyg.image.load(os.path.join('Sprites', 'gun.png')))
)

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

    true_camera_scroll[0] += ((player.physics.position[0] + CAMERA_OFFSET_X) * PIXEL_SCALE_FACTOR - true_camera_scroll[0] - WIDTH / 2) / CAMERA_MOVE_SLOWNESS
    true_camera_scroll[1] += ((player.physics.position[1] + CAMERA_OFFSET_Y) * PIXEL_SCALE_FACTOR - true_camera_scroll[1] - HEIGHT / 2) / CAMERA_MOVE_SLOWNESS
    
    # turn the camera scroll value to integer. Helps with bugs apparently
    rounded_camera_scroll = list(map(lambda x: int(x / PIXEL_SCALE_FACTOR), true_camera_scroll))

    # basically just clamps the venter point between specified values
    rounded_camera_scroll[0] = vectors.Math.clamp(rounded_camera_scroll[0], CAMERA_BORDERS_X[0],  CAMERA_BORDERS_X[1] - WIDTH)
    rounded_camera_scroll[1] = vectors.Math.clamp(rounded_camera_scroll[1], CAMERA_BORDERS_Y[0],  CAMERA_BORDERS_Y[1] - HEIGHT)

    tile_rects = []

    surf.blit(bg_img,  (-rounded_camera_scroll[0], -rounded_camera_scroll[1]))

    for i in range(len(tilemap)):
        for j in range(len(tilemap[i])):
            if tilemap[i][j] != 0:
                surf.blit(tileset[tilemap[i][j]], (
                    16 * j - rounded_camera_scroll[0], 
                    16 * i - rounded_camera_scroll[1])
                )
                tile_rects.append(pyg.Rect(16 * j, 16 * i, 16, 16))

    # this can be optimized by calculating the trajectory of the bullet and only checking the rects that overlap, since the bullets move in a straight line
    # collision with enemies will be implemented in the same way
    for bullet in bullets:
        bullet.update()
        for tile in tile_rects:
            if pyg.Rect.colliderect(bullet.rect, tile) and bullet in bullets:
                bullets.remove(bullet)
            elif bullet.lifetime > 3 and bullet in bullets:
                bullets.remove(bullet)

    player.update()
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
            surf, 
            (WIDTH, HEIGHT)
        ), 
        (0, 0)
    )

    # debug_screen.update(screen)

    pyg.display.update()

    delta_time = main_clock.tick() / 1000

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
                if event.key == pyg.K_SPACE and player.on_ground:
                    player.on_ground = False
                    player.physics.velocity[1] = -JUMP_SPEED

        if event.type == pyg.KEYUP:
            if (event.key == pyg.K_SPACE 
            and not player.on_ground 
            and player.physics.velocity[1] < 0):
                player.physics.velocity[1] = RELEASE_FALL_SPEED
        if event.type == pyg.MOUSEBUTTONDOWN:
            if event.button == 1: # 1 is left mouse button
                # if debug_text.rect.collidepoint(event.pos):
                #     debug_text.active = True
                # else:
                #     debug_text.active = False
                    player.shoot()
#endregion
