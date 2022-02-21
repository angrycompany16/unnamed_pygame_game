import math, os, vectors
import pygame as pyg
import game_manager as gm

class Entity():
    def __init__(self, max_HP, contact_damage):
        self.max_HP = max_HP
        self.contact_damage = contact_damage
        self.current_HP = max_HP

    def take_damage(self, damage):
        print(f"took {damage} damage")
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
    def __init__(self, max_HP, contact_damage, pos, image, fire_rate = 0.5):
        super().__init__(max_HP, contact_damage)
        self.pos = pos
        self.bullets = []
        self.image = image
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