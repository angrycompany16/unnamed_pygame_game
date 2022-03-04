import math, os, vectors, animations, random
import pygame as pyg
import game_manager as gm

class PhysicsObject():
    def __init__(self, position, velocity, acceleration, gravity = True, gravity_multiplier = 50, max_fall_vel = 200, max_jump_vel = 400, max_x_vel = 300, air_friction = 1):
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration

        if gravity:
            self.gravity_multiplier = gravity_multiplier
            self.acceleration = vectors.Vec([0, 9.81 * self.gravity_multiplier])

        self.max_fall_vel = max_fall_vel
        self.max_jump_vel = max_jump_vel
        self.max_x_vel = max_x_vel
        self.air_friction = air_friction


    def calculate_movement(self):
        self.velocity += self.acceleration * gm.delta_time
        self.velocity[0] *= self.air_friction

        if self.velocity[1] > self.max_fall_vel:
            self.velocity[1] = self.max_fall_vel
        elif self.velocity[1] < -self.max_jump_vel:
            self.velocity[1] = -self.max_jump_vel

        if abs(self.velocity[0]) > self.max_x_vel:
            self.velocity[0] = math.copysign(self.max_x_vel, self.velocity[0])

        self.position += self.velocity * gm.delta_time

        return self.position

class Entity():
    def __init__(self, max_HP, contact_damage):
        self.max_HP = max_HP
        self.contact_damage = contact_damage
        self.current_HP = max_HP

    def take_damage(self, damage):
        self.current_HP -= damage

class Turret(Entity):
    def __init__(self, max_HP, contact_damage, pos, image, fire_rate = 0.5):
        super().__init__(max_HP, contact_damage)
        self.pos = pos
        self.bullets = []
        self.image = image
        self.rect = pyg.Rect(
            self.pos, 
            (image.get_width(), image.get_height())
        )
        self.gun = Gun(pyg.image.load(os.path.join('Sprites', 'gun.png')))
        # Shots per second
        self.fire_rate = fire_rate
        self.time = 0

    def shoot(self):
        bullet = Bullet(
            vectors.Vec([
                self.pos[0] + self.image.get_width() / 2,
                self.pos[1] + self.image.get_height() / 2
            ]),
            vectors.Vec([
                -math.cos((self.gun.angle) * math.pi / 180),
                math.sin((self.gun.angle) * math.pi / 180)
            ]),
            pyg.image.load(os.path.join('Sprites', 'enemy_bullet.png')),
            self.gun.angle,
            200
        )
        self.bullets.append(bullet)
    
    def update(self, target=vectors.Vec([0, 0])):
        self.time += gm.delta_time

        if self.time > 1 / self.fire_rate:
            self.shoot()
            self.time = 0
        

class Drone(Entity):
    def __init__(self, max_HP, contact_damage, pos, spritesheet, frame_dur, image, fire_rate = 0.5):
        super().__init__(max_HP, contact_damage)
        self.pos = pos
        self.bullets = []
        self.image = image
        self.animation = animations.Clip(spritesheet, image.get_width(), image.get_height(), frame_dur)
        self.rect = pyg.Rect(
            self.pos, 
            (image.get_width(), image.get_height())
        )
        self.gun = Gun(pyg.image.load(os.path.join('Sprites', 'invisible.png')))
        # Shots per second
        self.fire_rate = fire_rate
        self.vel = vectors.Vec([0, 0])
        self.time = 0

    def shoot(self):
        bullet = Bullet(
            vectors.Vec([
                self.pos[0] + self.image.get_width() / 2,
                self.pos[1] + self.image.get_height() / 2
            ]),
            vectors.Vec([
                -math.cos((self.gun.angle) * math.pi / 180),
                math.sin((self.gun.angle) * math.pi / 180)
            ]),
            pyg.image.load(os.path.join('Sprites', 'enemy_bullet.png')),
            self.gun.angle,
            200
        )
        self.bullets.append(bullet)
    
    def update(self, target=vectors.Vec([0, 0])):
        vel = vectors.Vec.normalize(vectors.Vec([
            target[0] - self.pos[0],
            target[1] - self.pos[1]
        ]))

        self.pos += vel
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

        self.time += gm.delta_time

        self.animation.update()
        self.image = self.animation.image

        if self.time > 1 / self.fire_rate:
            self.shoot()
            self.time = 0
        
       
class Bullet():
    def __init__(self, position, velocity, image, angle, speed, damage=1):
        self.position = position
        self.velocity = velocity
        self.angle = angle
        self.image = pyg.transform.rotate(image, angle)
        self.rect = pyg.Rect((position), (image.get_width(), image.get_height()))
        self.lifetime = 0
        self.speed = speed
        self.damage = damage

    def update(self):
        self.position += self.velocity * gm.delta_time * self.speed
        self.rect.x = self.position[0]
        self.rect.y = self.position[1]
        self.lifetime += gm.delta_time

    def check_collision(self, other_rect) -> bool:
        if pyg.Rect.colliderect(self.rect, other_rect):
            self.kill()

class Gun():
    def __init__(self, image):
        self.image = image
        self.angle = 0
        self.flipped = False
        self.rect = self.image.get_rect()
        self.sprite = pyg.Surface((0, 0))

    def look_at(self, pos, target):
        new_angle = 0

        dist_x = target[0] - (pos[0] - gm.rounded_camera_scroll[0])
        dist_y = (pos[1] - gm.rounded_camera_scroll[1]) - target[1]

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

        self.rect = new_rect
        self.sprite = rot_sprite

        self.angle = new_angle

    def flip_y(self, set_flipped):
        flipped = pyg.transform.flip(self.image, False, True)
        self.image = flipped

        self.flipped = set_flipped

#IDK if there is any point to this
class Interactable():
    def interaction(self, new_img):
        pass

class Chest(Interactable):
    def __init__(self, pos, img, items):
        super().__init__()
        self.pos = pos
        self.img = img
        self.items = items
        self.opened = False

    def open(self, new_img):
        self.img = new_img
        self.opened = True

# make items pick-upable

class Item():
    def __init__(self, img, physics, UI):
        self.img = img
        self.physics = physics
        self.rect = self.img.get_rect()
        self.rect.topleft = physics.position
        self.UI = UI
        
    def update(self, tiles):
        if self.physics.velocity.sqr_magnitude() > 0.2:
            old_pos = self.physics.position
            max_new_pos = self.physics.calculate_movement()

            new_pos = self.check_collision(old_pos, max_new_pos, tiles)

            self.physics.position = new_pos
            self.rect.topleft = new_pos

    def check_collision(self, old_pos, new_pos, tiles) -> vectors.Vec:
        dp = new_pos - old_pos
        collision_types = {
            'top': False,
            'bot': False,
        }

        collision_id_x = pyg.Rect(
                new_pos[0], old_pos[1], self.rect.width, self.rect.height
            ).collidelist(tiles)
        # check for collision in x direction
        if collision_id_x != -1:
            dp[0] = 0
            self.physics.velocity[0] *= -0.3

        collision_id_y = pyg.Rect(
                old_pos[0], new_pos[1], self.rect.width, self.rect.height
            ).collidelist(tiles)
        # check for collision in y direction
        if collision_id_y != -1:
            # check if below ground / jumping
            if self.physics.velocity[1] < 0:
                dp[1] = tiles[collision_id_y].bottom - self.rect.top
                collision_types['top'] = True
            # check if above ground / falling
            elif self.physics.velocity[1] > 0:
                self.on_ground = True
                self.has_double_jumped = False
                dp[1] = tiles[collision_id_y].top - self.rect.bottom
                collision_types['bot'] = True

        if collision_types['top'] == True or collision_types['bot'] == True:
            self.physics.velocity[1] *= -0.6
        
        old_pos += dp
        return old_pos
