#!/usr/bin/env python3

# project page: https://github.com/jwd83/space-game/

# sprite resources: https://www.spriters-resource.com/snes/superrtype/
# pixelator : http://pixelatorapp.com/
# sound resources : https://www.sounds-resource.com/
# sprites/jwd-* Jared's sprites
# sprites/mjd-* Michelle's sprites
# sprites/parallax-space-* https://opengameart.org/content/space-background-3
# sprites/planet*.png https://opengameart.org/content/20-planet-sprites
# sprites/kenney* https://www.kenney.nl/assets/space-shooter-extension & https://www.kenney.nl/assets/space-shooter-redux


# xbox 360 controller notes

# get_button maplike
# A button - 0   (defense upgrade/deflect)
# B button - 1
# X button - 2   (shoot)
# Y button - 3   (weapon upgrade/??)
# LB button - 4
# RB button - 5
# Back button - 6
# Start button - 7
# Left stick (clicked in) - 8
# Right stick (clicked in) - 9
# guide button - 10

# dpad is hat 0

import pygame
import random
import math
import numpy as np
import time
import datetime
import os

# let's define some colors

YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (255, 0, 255)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
BROWN = (139, 69, 19)
WHITE = (255, 255, 255)
WHITE_2 = (238, 238, 238)
WHITE_3 = (210, 210, 210)
BLACK = (0, 0, 0)



# class for boss configuration
class Boss:
    def __init__(self, name, hp, sprite):
        self.name = name
        self.hp = hp
        self.sprite = sprite

class UpgradeType:
    AttackSpeed = 1
    AttackDamage = 2
    ForwardTorpedo = 3
    HomingTorpedo = 4
    WildTorpedo = 5
    MaxHealth = 6
    DeflectCooldown = 7
    ArmorUp = 8
    LifeSteal = 9

# enumerate the projectile types
class ProjectileType:
    Circle = 1
    Meatball = 2
    Noodle = 3
    ForwardTorpedo = 4
    Homing = 5
    Wild = 6
    Spread = 7

# enumerate the game states
class GameState:
    Title = 1
    Game = 2
    Victory = 3
    LevelUp = 4
    GameOver = 5
    StartLevel = 6
    Quit = 7
    Ending = 8


attack_power = 5
background_speed = 1.0
base_fps = 60
cooldown_attack = 0.1
cooldown_deflect = 2.5
damage_done = 0
dps = 0
dt = 1.0
duration_deflect = 1
fps = 60
time_frame_start = time.time()
frame_counter = 0
frame_last_shot = 0
game_state = last_game_state = GameState.Title
height = 660
last_damage_done = 0
ship_speed = 9
starfield_size = 300
state_start_frame = 0
state_start_time = time.time()
time_last_deflect = 0
time_last_attack = 0
volume: int = 10
width = 1280
upgrade_offers = []
upgrade_path = []


BACKGROUND_SPEED_NORMAL = 1.0
BACKGROUND_SPEED_WARP = 10

FONT_SIZE_LARGE = 48
FONT_SIZE_NORMAL = 24
FONT_SIZE_SMALL = 16
FONT_SIZE_TINY = 8

HEAL_CHANCE = 4
SHOW_PROJECTILE_VALUES = False
BOSS_BASE_HEALTH = 100

# jukebox
JUKEBOX = [
    'sounds/music-1-flashman.ogg',
    'sounds/music-2-topgear.ogg',
    'sounds/music-3-zrms.ogg',
    'sounds/music-4-wiley1.ogg',
]

COMM_SOUNDS = [
    'sounds/comm-bird.ogg',
    'sounds/comm-bunny.ogg',
    'sounds/comm-fox.ogg',
    'sounds/comm-frog.ogg',
]

trash_mobs = []

upgrades = [
    {
        'name': 'Attack Speed',
        'info_1': 'Increases your attack',
        'info_2': 'speed allowing you to',
        'info_3': 'shoot more rapidly.',
        'color': ORANGE
    },
    {
        'name': 'Attack Up',
        'info_1': 'Increases your attack',
        'info_2': 'power making each shot',
        'info_3': 'deal more damage.',
        'color': ORANGE
    },
    {
        'name': 'Forward Torpedo',
        'info_1': 'Fire an additional',
        'info_2': 'forward torpedo.',
        'info_3': '100 Potency',
        'color': RED
    },
    {
        'name': 'Homing Torpedo',
        'info_1': 'Fire a high accuracy',
        'info_2': 'but low potency torpedo.',
        'info_3': '40 Potency',
        'color': RED


    },
    {
        'name': 'Wild Shot',
        'info_1': 'An unpredictable but',
        'info_2': 'powerful attack.',
        'info_3': '160 Potency',
        'color': RED

    },
    {
        'name': 'Max Health',
        'info_1': 'Increases your maximum',
        'info_2': 'health allowing you to',
        'info_3': 'take more damage.',
        'color': GREEN
    },
    {
        'name': 'Deflect Cooldown',
        'info_1': 'Decreases the cooldown',
        'info_2': 'between deflects allowing',
        'info_3': 'you to deflect more often.',
        'color': GREEN
    },
    {
        'name': 'Armor Up',
        'info_1': 'Increases your armor',
        'info_2': 'causing you to take',
        'info_3': 'less damage.',
        'color': GREEN
    },
    {
        'name': 'Life Steal',
        'info_1': 'Converts a portion',
        'info_2': 'of your damage into',
        'info_3': 'health for you.',
        'color': GREEN
    }

]

# enumerate the trash mob types
MOB_TYPE_BOSS = -1
MOB_TYPE_PLAYER = 0
MOB_TYPE_BASIC = 1
MOB_TYPE_HANGING = 2
# MOB_TYPE_FIGHTER = 3
# MOB_TYPE_HEALER = 4
# MOB_TYPE_SNARE = 5


def fps_divisor():
    return base_fps / fps


def fps_scaler():
    return fps / base_fps


def boss_start_position():
    return width - boss.w * boss.scale - 100


class SpaceObject:
    def __init__(self, name: str, x: int | None = None, y: int | None = None, vx: int | None = None, vy: int | None = None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.name = name
        self.sprite = None
        # check for new start position
        if self.x is None and self.y is None:
            self.reset_position()
        else:
            # check for empty x or y
            if self.x is None:
                self.x = 0
            if self.y is None:
                self.y = 0
        # check for empty vx or vy
        if self.vx is None:
            self.vx = -11
        if self.vy is None:
            self.vy = 0

        self.resize()

    def resize(self):
        new_speed = random.randint(10, 16)

        new_h = images[self.name].get_height() * new_speed / 40
        new_w = images[self.name].get_width() * new_speed / 40

        self.sprite = pygame.transform.scale(images[self.name], (new_h, new_w))
        self.vx = abs(new_speed) * -1

    def reset_position(self):
        self.x = width + width * random.random() * 40
        self.y = random.randint(-20, 600)

    def move(self):
        self.x += self.vx * background_speed * dt
        self.y += self.vy * background_speed * dt

        if self.x < -width:
            self.resize()
            self.reset_position()

    def draw(self):
        # screen.blit(images[self.name], (self.x, self.y))
        screen.blit(self.sprite, (self.x, self.y))


class Star:
    def __init__(self):
        self.x = random.randrange(0, width)
        self.y = random.randrange(0, height)
        self.speed = random.randrange(1, 8)
        self.size = 1 + (self.speed / 4)
        self.set_color()

    def set_color(self):
        # some portion of stars are white
        if(random.randint(0, 100) < 50):
            self.r = 255 * (self.speed/10)
            self.g = 255 * (self.speed/10)
            self.b = 255 * (self.speed/10)

        # remaining stars are colored randomly
        else:
            self.r = random.randrange(80, 255) * self.speed/10
            self.g = random.randrange(80, 255) * self.speed/10
            self.b = random.randrange(80, 255) * self.speed/10

    def move(self):
        self.x -= self.speed * background_speed * fps_divisor()

        if(self.x < 0 - ((self.size + self.speed) * background_speed)):
            self.x = width + self.speed + \
                random.randrange(0, int(self.size + self.speed))
            self.y = random.randint(0, height)

    def draw(self):
        pygame.draw.circle(
            screen,
            (self.r, self.g, self.b),
            (self.x, self.y),
            self.size
        )

        # draw a a line from the center of the towards the right edge of the screen
        if background_speed > 1.1:
            # pygame.draw.line(
            #     screen,
            #     (self.r, self.g, self.b),
            #     (self.x, self.y),
            #     (self.x+background_speed*2*self.speed, self.y),
            #     1
            # )

            # draw a triangle pointing to the right
            pygame.draw.polygon(
                screen,
                (self.r, self.g, self.b),
                (
                    (self.x, self.y+self.size+1),
                    (self.x + background_speed * 2 * self.speed, self.y),
                    (self.x, self.y-self.size)
                )
            )


def tint(surf, r, g, b):
    """surf: pygame.Surface to be reddened. The function returns a new surface."""
    # making a red shade with transparency
    redshade = pygame.Surface(surf.get_rect().size).convert_alpha()
    redshade.fill((r, g, b, 100))  # red with alpha

    # merging the alpha chanel of base image on the redshade, keeping minimum values (most transparent) in each pixel
    alpha_basemask = pygame.surfarray.array_alpha(surf)
    alpha_redmask = pygame.surfarray.pixels_alpha(redshade)
    np.minimum(alpha_basemask, alpha_redmask, out=alpha_redmask)

    # deleting the alpha_redmask reference to unlock redshade (or it cannot be blit)
    del alpha_redmask

    # reddening a copy of the original image
    redsurf = surf.copy()
    redsurf.blit(redshade, (0, 0))

    return redsurf


def reddening(surf):
    """surf: pygame.Surface to be reddened. The function returns a new surface."""
    # making a red shade with transparency
    redshade = pygame.Surface(surf.get_rect().size).convert_alpha()
    redshade.fill((255, 0, 0, 100))  # red with alpha

    # merging the alpha chanel of base image on the redshade, keeping minimum values (most transparent) in each pixel
    alpha_basemask = pygame.surfarray.array_alpha(surf)
    alpha_redmask = pygame.surfarray.pixels_alpha(redshade)
    np.minimum(alpha_basemask, alpha_redmask, out=alpha_redmask)

    # deleting the alpha_redmask reference to unlock redshade (or it cannot be blit)
    del alpha_redmask

    # reddening a copy of the original image
    redsurf = surf.copy()
    redsurf.blit(redshade, (0, 0))

    return redsurf


class Ship:
    def __init__(self, sprite, x=None, y=None, w=None, h=None, color_key=None, scale=1, type=MOB_TYPE_BASIC):
        self.w = w
        self.h = h
        self.x = width/2
        self.y = height/2
        self.vx = 0
        self.vy = 0
        self.color_key = color_key
        self.scale = scale
        self.sprite = load_image(sprite, x, y, w, h, color_key, scale)
        self.hp = 300
        self.max_hp = 300
        self.level = 1
        self.weapon_level = 1
        self.defense_level = 0
        self.name = ""
        self.mask = pygame.mask.from_surface(self.sprite)
        self.type = type
        self.base_y = None
        self.sinusoid_speed = 200
        self.frame_last_hit = 0
        self.weapons = []

        # create the alpha transparency mask for the ship
        self.sprite_damaged = reddening(self.sprite)
        if(self.color_key is not None):
            self.sprite_damaged.set_colorkey(self.color_key)

        if self.w == None:
            self.w = self.sprite.get_width() / self.scale

        if self.h == None:
            self.h = self.sprite.get_height() / self.scale

    def move(self, edge_bound=True):
        self.x += self.vx * fps_divisor()

        if self.type == MOB_TYPE_BOSS or self.type == MOB_TYPE_PLAYER:
            self.y += self.vy * fps_divisor()

        if self.type == MOB_TYPE_BASIC:
            if self.base_y is None:
                self.base_y = self.y

            # move the y along a sinusoidal path
            self.y = self.base_y + math.sin(self.x / 100) * self.sinusoid_speed

        edge_hit = False

        if edge_bound:
            if(self.x < 0):
                self.x = 0
                edge_hit = True
            if(self.x + self.w * self.scale > width):
                self.x = width - self.w * self.scale
                edge_hit = True

            if(self.y < 0):
                self.y = 0
                edge_hit = True
            if(self.y + self.h * self.scale > height):
                self.y = height - self.h * self.scale
                edge_hit = True

        return edge_hit

    def change_sprite(self, sprite, x, y, w, h, color_key=None, scale=1):
        self.w = w
        self.h = h
        self.scale = scale
        self.color_key = color_key
        self.sprite = load_image(sprite, x, y, w, h, color_key, scale)
        self.sprite_damaged = reddening(self.sprite)

        if(self.color_key is not None):
            self.sprite.set_colorkey(self.color_key)
            self.sprite_damaged.set_colorkey(self.color_key)

        # create the alpha transparency mask for the ship

    def draw(self):
        if frame_counter - self.frame_last_hit <= 1:
            screen.blit(self.sprite_damaged, (self.x, self.y))
        else:
            screen.blit(self.sprite, (self.x, self.y))

    def flip_h(self):
        self.sprite = pygame.transform.flip(self.sprite, True, False)
        self.sprite_damaged = pygame.transform.flip(
            self.sprite_damaged, True, False)
        if(self.color_key is not None):
            self.sprite.set_colorkey(self.color_key)
            self.sprite_damaged.set_colorkey(self.color_key)

    def flip_v(self):
        self.sprite = pygame.transform.flip(self.sprite, False, True)
        self.sprite_damaged = pygame.transform.flip(
            self.sprite_damaged, False, True)
        if(self.color_key is not None):
            self.sprite.set_colorkey(self.color_key)
            self.sprite_damaged.set_colorkey(self.color_key)

    def collide_mask(self, mask, x=0, y=0):
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(self.mask, offset)
        if(poi is not None):
            return True
        else:
            return False

    def add_weapon(self, weapon: ProjectileType):
        self.weapons.append(weapon)

# load a part of an image from a file to be used as a sprite frame


class Projectile:
    def __init__(self, x, y, vx, vy, damage, color, radius, acceleration=1.0, type=ProjectileType.Circle):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.color = color
        self.radius = radius
        self.acceleration = acceleration
        self.hit = False
        self.type = type

    def move(self):

        if self.hit:
            self.vx = 0.95 * self.vx
            self.vy = 0.95 * self.vy
            if abs(self.vx) < 2 and abs(self.vy) < 2:
                self.vx = 0
                self.vy = 0
                return True

        if self.acceleration != 1.0:
            if frame_counter % 2 == 0:
                self.vx *= self.acceleration
                self.vy *= self.acceleration

        self.x += self.vx * fps_divisor()
        self.y += self.vy * fps_divisor()

        if(self.x < (0 - self.radius) or self.x > (width + self.radius) or self.y < (0 - self.radius) or self.y > (height + self.radius)):
            return True
        else:
            return False

    def draw(self):
        if not self.hit:

            if(self.damage < 0):
                # if my damage is negative (healing), draw a green circle
                pygame.draw.circle(
                    screen, GREEN, (self.x, self.y), self.radius)
            else:
                # otherwise, draw my circle normally
                match self.type:

                    case ProjectileType.Circle:
                        pygame.draw.circle(screen, self.color,
                                        (self.x, self.y), self.radius)

                    case ProjectileType.Meatball:
                        self.blitRotateCenter(
                            meatball,
                            (self.x - meatball.get_width() / 2,
                            self.y - meatball.get_height() / 2),
                            frame_counter % 360
                        )
                    case ProjectileType.Noodle:
                        self.blitRotateCenter(
                            noodle,
                            (self.x - noodle.get_width() / 2,
                            self.y - noodle.get_height() / 2),
                            frame_counter % 360
                        )
                    case ProjectileType.ForwardTorpedo:
                        angle = 180 if self.vx < 0 else 0 # if shot left, rotate 180 else 0
                        self.blitRotateCenter(
                            player_torpedo,
                            (self.x - player_torpedo.get_width() / 2,
                            self.y - player_torpedo.get_height() / 2),
                            angle
                        )
                    case _:
                        pygame.draw.circle(screen, self.color,
                                        (self.x, self.y), self.radius)
        else:
            if(self.damage < 0):
                # if my damage is negative (healing), draw a green value
                text_damage_value = font_small.render(
                    "+" + str(abs(self.damage)), True, GREEN)

            else:
                # otherwise, draw my damage value normally
                text_damage_value = font_small.render(
                    str(self.damage), True, self.color)

            screen.blit(text_damage_value, (self.x - text_damage_value.get_width() /
                        2, self.y - text_damage_value.get_height()/2))

    def blitRotateCenter(self, image, topleft, angle):

        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(
            center=image.get_rect(topleft=topleft).center)

        screen.blit(rotated_image, new_rect)


def load_image(filename, x: int | None = None, y: int | None = None, w: int | None = None, h: int | None = None, color_key=None, scale=1):
    image = pygame.image.load(filename).convert_alpha()

    if x is None:
        x = 0
    if y is None:
        y = 0
    if w is None:
        w = image.get_width()
    if h is None:
        h = image.get_height()

    image = image.subsurface(x, y, w, h)
    image = pygame.transform.scale(image, (int(w * scale), int(h * scale)))
    if(color_key is not None):
        image.set_colorkey(color_key)
    return image


def move_starfield():
    for so in space_objects:
        so.move()

    for star in stars:
        star.move()


def move_projectiles():
    global player_projectiles, enemy

    # handle player projectiles
    for projectile in player_projectiles:
        if(projectile.move()):
            player_projectiles.remove(projectile)

    # handle boss projectiles
    for projectile in boss_projectiles:
        if(projectile.move()):
            boss_projectiles.remove(projectile)


def handle_game_inputs():
    global player, time_last_deflect, time_last_attack

    # reset ship motion
    player.vx = 0
    player.vy = 0

    # handle key presses
    keys = pygame.key.get_pressed()

    joy_shoot = False
    joy_deflect = False
    joy_up = False
    joy_down = False
    joy_left = False
    joy_right = False

    # check for joystick input
    if joystick is not None:
        if joystick.get_button(0):
            joy_deflect = True
        if joystick.get_button(2):
            joy_shoot = True
        dpad_x, dpad_y = joystick.get_hat(0)  # no idea if this is right
        if dpad_x == -1:
            joy_left = True
        elif dpad_x == 1:
            joy_right = True
        if dpad_y == -1:
            joy_down = True
        elif dpad_y == 1:
            joy_up = True

    if keys[pygame.K_LEFT] or keys[pygame.K_a] or joy_left:
        player.vx -= ship_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d] or joy_right:
        player.vx += ship_speed
    if keys[pygame.K_UP] or keys[pygame.K_w] or joy_up:
        player.vy -= ship_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s] or joy_down:
        player.vy += ship_speed
    if keys[pygame.K_TAB] or joy_deflect:
        if time_frame_start - time_last_deflect > cooldown_deflect:
            time_last_deflect = time_frame_start

    if keys[pygame.K_SPACE] or joy_shoot:
        if time_frame_start - time_last_attack > cooldown_attack:
            time_last_attack = time_frame_start
            player_shoot()

def process_upgrade(upgrade_type: UpgradeType):
    global attack_power, cooldown_deflect, cooldown_attack, player, upgrade_path

    print(upgrade_type)
    card_upgrade = upgrades[upgrade_type-1]

    upgrade_path.append(card_upgrade['name'])

    match upgrade_type:
        case UpgradeType.AttackDamage:
            attack_power += 5
        case UpgradeType.MaxHealth:
            player.max_hp = int(player.max_hp * 1.66667)
            player.hp = player.max_hp
        case UpgradeType.DeflectCooldown:
            cooldown_deflect -= 0.1
        case UpgradeType.AttackSpeed:
            cooldown_attack *= 0.9
        case UpgradeType.ForwardTorpedo:
            player.add_weapon(ProjectileType.ForwardTorpedo)
        case UpgradeType.WildTorpedo:
            player.add_weapon(ProjectileType.Wild)
        case UpgradeType.HomingTorpedo:
            player.add_weapon(ProjectileType.Homing)
        case UpgradeType.ArmorUp:
            player.defense_level += 1
        case UpgradeType.LifeSteal:
            player.life_steal += 5
        case _:
            pass






def handle_game_events():
    global done, fps
    # handle events and key presses
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
            if event.key == pygame.K_v:
                change_volume()
            if event.key == pygame.K_f:
                fps = 60 if fps == 120 else 120


# set to none if you do not wish to constrain
def constrain(value, low, high):
    if low is not None:
        if(value < low):
            value = low
    if high is not None:
        if(value > high):
            value = high
    return value


def handle_boss_logic():
    global boss

    # control the bosses movement
    if (frame_counter % 60 == 0):
        boss.vx += random.randint(-2, 2)
        boss.vy += random.randint(-2, 2)

        max_velocity = 5 + int(boss.level / 4)

        boss.vx = constrain(boss.vx, -max_velocity, max_velocity)
        boss.vy = constrain(boss.vy, -max_velocity, max_velocity)

    # control the bosses shooting
    if(frame_counter % constrain((13 - boss.level) * fps_scaler(), 8 * fps_scaler(), 13 * fps_scaler()) == 0):
        if (random.randint(0, 100) < (50+int(boss.level/4))):
            boss_shoot()

    if boss.level >= 2:
        if state_current_frame() % (60 * 15) == 0:
            # pick a random 1 or 2
            boss_summon(random.randint(1, 2))


def boss_summon(mob_type=1):
    global trash_mobs

    if mob_type == 1:

        spacing = 0
        mob_type = 'ships/trash1.gif'
        base_y = random.randint(100, 500)

        for i in range(0, 4):
            new_mob = Ship(mob_type, scale=.5)
            new_mob.max_hp = boss.level * 10
            new_mob.hp = new_mob.max_hp
            new_mob.x = width + new_mob.w * new_mob.scale + spacing
            spacing += int(new_mob.w * new_mob.scale * 1.2)
            new_mob.y = base_y
            new_mob.vx = -3
            new_mob.vy = 0
            new_mob.flip_h()
            trash_mobs.append(new_mob)

    if mob_type == 2:

        spacing = 0
        mob_type = 'ships/trash2.gif'
        base_y = -25

        for i in range(0, 4):
            new_mob = Ship(mob_type, scale=1.25)
            new_mob.max_hp = boss.level * 20
            new_mob.hp = new_mob.max_hp
            new_mob.x = width + new_mob.w * new_mob.scale + spacing
            spacing += int(new_mob.w * new_mob.scale * 1.4)
            new_mob.y = base_y
            new_mob.sinusoid_speed = 30
            new_mob.vx = -3
            new_mob.vy = 0
            new_mob.flip_h()
            trash_mobs.append(new_mob)


def player_shoot():
    global player_projectiles

    fox = 0
    foy = 0

    for weapon in player.weapons:
        match weapon:
            case ProjectileType.Homing:
                player_projectiles.append(
                    fire_projectile(
                        player,
                        boss,
                        3,
                        int(attack_power * .4),
                        BLUE,
                        6,
                        20
                    )
                )
            case ProjectileType.Wild:
                player_projectiles.append(
                    fire_projectile(
                        player,
                        boss,
                        2,
                        int(attack_power * 1.6),
                        CYAN,
                        6,
                        20
                    )
                )
            case ProjectileType.ForwardTorpedo:
                player_projectiles.append(
                    fire_projectile(
                        player,
                        boss,
                        1,
                        attack_power,
                        WHITE,
                        6,
                        20,
                        projectile_type=ProjectileType.ForwardTorpedo,
                        ox = fox,
                        oy = foy
                    )
                )

                if foy == 0:
                    fox -= -5
                    foy = -15
                elif foy == -15:
                    foy = 15
                else:
                    fox += 32
                    foy = 0

def fire_projectile(
    source,
    target,
    mode,
    damage,
    color,
    radius,
    speed,
    accel=1.0,
    can_heal=False,
    projectile_type=ProjectileType.Circle,
    ox=0,
    oy=0
):
    source_x_center = source.x + source.w * source.scale / 2
    source_y_center = source.y + source.h * source.scale / 2

    target_x_center = target.x + target.w * target.scale / 2
    target_y_center = target.y + target.h * target.scale / 2

    vx = 0
    vy = 0

    # mode 1: horizontal shot towards target
    if mode == 1:
        if source_x_center > target_x_center:
            vx = -speed
        else:
            vx = speed

    # mode 2: quadrant spray
    if mode == 2:
        if source_x_center > target_x_center:
            vx = random.random() * -speed
        else:
            vx = random.random() * speed

        if source_y_center > target_y_center:
            vy = abs(vx) - speed
        else:
            vy = speed - abs(vx)

        while (abs(vx) + abs(vy) < speed):
            vx *= 2
            vy *= 2

    # mode 3: auto-aim
    if mode == 3:
        dx = target_x_center - source_x_center
        dy = target_y_center - source_y_center
        drt = math.sqrt(dx * dx + dy * dy)
        if drt != 0:
            vx = dx / drt * speed
            vy = dy / drt * speed
        else:
            # if the target is the same as the source, just shoot straight
            vx = speed
            vy = 0

    # check if this shot will be a heal
    if can_heal:
        damage *= boss_shoot_random_heal()

    # return the custom projectile
    return Projectile(
        source_x_center + ox,
        source_y_center + oy,
        vx,
        vy,
        damage,
        color,
        radius,
        accel,
        projectile_type,
    )


def boss_shoot():
    # global boss_projectiles

    # set default attack to circle
    projectile_type = ProjectileType.Circle

    # if it's the flying spaghetti monster, set the attack type to a meatball
    if boss.level == 8:
        # 50/50 chance to shoot a meatball or a noodle
        if random.randint(0, 100) < 50:
            projectile_type = ProjectileType.Meatball
        else:
            projectile_type = ProjectileType.Noodle

    # shoot a projectile from the boss straight ahead
    boss_projectiles.append(
        fire_projectile(
            boss,
            player,
            1,
            5 + boss.level,
            YELLOW,
            15,
            10,
            can_heal=True,
            projectile_type=projectile_type
        )
    )

    if boss.level >= 2:
        boss_projectiles.append(
            fire_projectile(
                boss,
                player,
                2,
                2 + boss.level,
                ORANGE,
                10,
                6,
                can_heal=True,
                projectile_type=projectile_type
            )
        )

    if boss.level >= 3:
        # target the player directly
        boss_projectiles.append(
            fire_projectile(
                boss,
                player,
                3,
                boss.level,
                RED,
                10,
                7,
                can_heal=True,
                projectile_type=projectile_type
            )
        )

    if boss.level >= 4:
        # mode 3 with acceleration
        boss_projectiles.append(
            fire_projectile(
                boss,
                player,
                3,
                boss.level,
                PURPLE,
                10,
                speed=5,
                can_heal=True,
                accel=1.05,
                projectile_type=projectile_type
            )
        )


def boss_shoot_random_heal():
    # a random % chance shoot a heal projectile instead of a damage one
    if random.randint(0, 100) < HEAL_CHANCE:
        return -1
    else:
        return 1


def projectile_hits_ship(projectile, ship):

    # save the bounding box of the ship
    ship_box = [(ship.x, ship.y),
                (ship.x + (ship.w * ship.scale), ship.y + (ship.h * ship.scale))]

    # save the location of the projectile and it's raidius
    projectile_r = projectile.radius
    projectile_center = (projectile.x, projectile.y)

    # calculate the distance from the box to the projectile
    dx = max(
        ship_box[0][0] - projectile_center[0],
        0,
        projectile_center[0] - ship_box[1][0]
    )

    dy = max(
        ship_box[0][1] - projectile_center[1],
        0,
        projectile_center[1] - ship_box[1][1]
    )

    # solve the distance from the box to the projectile
    distance = math.sqrt(dx * dx + dy * dy)

    # if it appears the projectile is inside the box perform a collision against the mask
    if distance <= projectile_r:

        if projectile.type == ProjectileType.Circle or projectile.damage < 0 or projectile.type == ProjectileType.ForwardTorpedo:
            # if the projectile is a circle, perform a circle collision
            # against the mask of a circle. begin by drawing the bullet
            # collision mask
            surface = pygame.Surface(
                (projectile.radius * 2, projectile.radius * 2))
            pygame.draw.circle(
                surface,
                (0, 0, 0),
                (projectile.radius, projectile.radius),
                projectile.radius
            )
            projectile_mask = pygame.mask.from_surface(surface)
            return ship.collide_mask(projectile_mask, projectile.x - projectile.radius, projectile.y - projectile.radius)
        else:
            # if the projectile is a sprite we will need to draw
            # collide the sprite's mask against the ship's mask
            # for now just return false
            return False

    else:
        return False


def collide():
    global damage_done


    for projectile in player_projectiles:
        # check if the projectile x y is within the boss x y + w h
        #        if(projectile.x > boss.x and projectile.x < boss.x + boss.w * boss.scale and projectile.y > boss.y and projectile.y < boss.y + boss.h * boss.scale):
        if not projectile.hit:
            if(projectile_hits_ship(projectile, boss)):
                # play the player hit sound
                pygame.mixer.Sound.play(sfx['player_hit'])
                boss.hp -= projectile.damage
                # record the damage done
                damage_done += projectile.damage
                # player_projectiles.remove(projectile)
                projectile.hit = True
                boss.frame_last_hit = frame_counter
            for trash_mob in trash_mobs:
                if projectile_hits_ship(projectile, trash_mob):
                    # play the player hit sound
                    pygame.mixer.Sound.play(sfx['player_hit'])
                    trash_mob.hp -= projectile.damage
                    trash_mob.frame_last_hit = frame_counter
                    # player_projectiles.remove(projectile)
                    projectile.hit = True
                    if trash_mob.hp <= 0:
                        trash_mobs.remove(trash_mob)

            # if the projectile is now a hit perform life steal if the player
            # has a life steal upgrade
            if projectile.hit and player.life_steal > 0:
                player.hp += math.ceil(projectile.damage * (player.life_steal / 100))

    # collide boss projectiles with the player
    for projectile in boss_projectiles:
        # check if the projectile x y is within the player x y + w h
        # if(projectile.x > player.x and projectile.x < player.x + player.w * player.scale and projectile.y > player.y and projectile.y < player.y + player.h * player.scale):
        if not projectile.hit:
            if(projectile_hits_ship(projectile, player)):
                # play the boss hit sound effect

                if projectile.damage < 0:
                    pygame.mixer.Sound.play(sfx['player_heal'])
                else:
                    # check if the player has a deflect active
                    if time_frame_start - time_last_deflect < duration_deflect:
                        projectile.damage = 0
                        pygame.mixer.Sound.play(sfx['deflect'])
                        # create a new projectile that is a player projectile with reversed direction
                        player_projectiles.append(
                            fire_projectile(
                                player,
                                boss,
                                3,
                                int(attack_power * 2),
                                PURPLE,
                                6,
                                20
                            )
                        )

                    else:
                        pygame.mixer.Sound.play(sfx['boss_hit'])
                        projectile.damage -= player.defense_level
                        projectile.damage = constrain(projectile.damage, 1, None)
                        player.frame_last_hit = frame_counter

                player.hp -= projectile.damage

                # boss_projectiles.remove(projectile)
                projectile.hit = True

    # cap the player at double their max hp
    player.hp = constrain(player.hp, -player.max_hp, player.max_hp * 2)


def update_game():
    global game_state, boss_projectiles, player_projectiles, trash_mobs
    # move the stars
    move_starfield()

    handle_game_inputs()
    handle_boss_logic()

    # move the player ship
    player.move()

    # move the boss and bounce off edges
    if boss.move():
        y_bounce = False
        x_bounce = False

        if boss.y == 0 or boss.y == height - boss.h * boss.scale:
            boss.vy *= -1
            y_bounce = True
        if boss.x == 0 or boss.x == width - boss.w * boss.scale:
            boss.vx *= -1
            x_bounce = True

        # if the boss perfectly hits a corner kill the player
        if x_bounce and y_bounce:
            if 'DVD' in boss.name:
                player.hp = 0
                print("PERFECT CORNER HIT! CHEERS ERUPT FROM SCRANTON, PA FOR " +
                      boss.name + " AS IT DESTROYS YOU")

    for trash_mob in trash_mobs:
        trash_mob.move(False)

    # check for trash mobs that are off screen and remove them
    for trash_mob in trash_mobs:
        if trash_mob.x < -trash_mob.w * trash_mob.scale:
            trash_mobs.remove(trash_mob)

    if state_current_frame() % 60 == 0:
        for trash_mob in trash_mobs:
            boss_projectiles.append(
                fire_projectile(trash_mob, player, 2, boss.level,
                                ORANGE, 8, 8, can_heal=False, ox=-10, oy=20)
            )

    # move the projectiles
    move_projectiles()

    # calculate collisions
    collide()

    # check for player death
    if player.hp <= 0:
        # play the player death sound
        pygame.mixer.Sound.play(sfx['player_death'])

        player.hp = 0
        player.deaths += 1
        game_state = GameState.GameOver
        # boss_projectiles = []
        player_projectiles = []
        trash_mobs = []

    # check for level up
    if boss.hp <= 0:
        # play the boss death sound
        pygame.mixer.Sound.play(sfx['level_up'])
        trash_mobs = []
        game_state = GameState.Victory
        # clear active projectiles from the board
        boss_projectiles = []
        # player_projectiles = []
        boss.level += 1
        player.level += 1
        boss.max_hp *= 1.5
        boss.hp = boss.max_hp
        player.hp = constrain(player.hp + 10, 0, player.max_hp)


def draw_projectiles():
    # draw the player projectiles
    for projectile in player_projectiles:
        projectile.draw()

    # draw the boss projectiles
    for projectile in boss_projectiles:
        projectile.draw()


def draw_screen():
    # draw a starry background
    screen.fill(BLACK)
    # draw the stars
    draw_starfield()

    # draw the ship
    player.draw()

    # if the player is deflecting draw the deflect shield
    if time_frame_start - time_last_deflect < duration_deflect:
        pct = (time_frame_start - time_last_deflect) / duration_deflect
        pct = constrain(pct, 0, 1)
        pygame.draw.circle(
            screen,
            PURPLE,
            (player.x + player.w * player.scale / 2,
             player.y + player.h * player.scale / 2),
            player.w * player.scale * (1-pct),
            3
        )



    # draw the boss
    boss.draw()

    # draw the trash mobs
    for trash_mob in trash_mobs:
        trash_mob.draw()

    # draw the projectiles
    draw_projectiles()

    draw_bar(player, 0, player.hp, player.max_hp, GREEN, YELLOW)                        # player health
    draw_bar(player, 1, player.hp - player.max_hp, player.max_hp, BLUE, YELLOW, True)   # player shield (if hp > max_hp)
    if time_frame_start - time_last_deflect < cooldown_deflect:
        draw_bar(player, 2, time_frame_start - time_last_deflect, cooldown_deflect, PURPLE, YELLOW)

    draw_bar(boss, 0, boss.hp, boss.max_hp, RED, YELLOW)                                # boss health

    for trash_mob in trash_mobs:
        draw_bar(trash_mob, 0, trash_mob.hp, trash_mob.max_hp, BLUE, YELLOW)
        draw_hp_bar(BLUE, trash_mob)


    draw_score_line()

    draw_boss_text()

    # update the screen
    pygame.display.flip()


def draw_score_line():
    # draw the score line

    text_score_line = font_small.render(
        "Deaths: " + str(player.deaths) +
        # "Level: " + str(player.level) +
        "  Power: " + str(attack_power) +

        "  Speed: " + "{0:.3f}".format(cooldown_attack) +
        "  Defense: " + str(player.defense_level + 1) +
        "  HP: " + str(constrain(player.hp, -player.hp,
                                 player.max_hp)) + "/" + str(player.max_hp),
        True,
        (255, 255, 255)
    )

    # draw your shield level
    if player.hp > player.max_hp:
        text_shield_level = font_small.render(
            "+ " + str(player.hp-player.max_hp), True, (100, 100, 255))
        screen.blit(text_shield_level, (text_score_line.get_width() + 10, 680))

    text_status_line = font_tiny.render(
        "DPS: " + str(dps) +
        "  Volume: " + str(volume) + "%" +
        "  FPS (Target): " + str(round(clock.get_fps())) +
        " (" + str(fps) + ")",
        True,
        (180, 180, 180)
    )

    screen.blit(text_score_line, (0, 680))
    screen.blit(text_status_line, (0, 680+text_score_line.get_height()))


def draw_bar(ship, position, value_current, value_max, foreground_color, background_color = YELLOW, background_transparent: bool = False, bar_height = 8):

    bar_top_left_x = ship.x
    bar_top_left_y = ship.y + (ship.h * ship.scale) + (position * (bar_height + 2))
    bar_background_width = ship.w * ship.scale
    bar_foreground_width = constrain(value_current, 0, value_max) / value_max * bar_background_width

    # draw the background
    if not background_transparent:
        pygame.draw.rect(
            screen,
            background_color,
            (
                bar_top_left_x,
                bar_top_left_y,
                bar_background_width,
                bar_height,
            )
        )

    # draw the background
    pygame.draw.rect(
        screen,
        foreground_color,
        (
            bar_top_left_x,
            bar_top_left_y,
            bar_foreground_width,
            bar_height,
        )
    )



def draw_hp_bar(color, ship):
    pygame.draw.rect(
        screen,
        (255, 255, 0),
        (
            ship.x,
            ship.y + ship.h * ship.scale,
            ship.w * ship.scale,
            10
        )
    )

    pygame.draw.rect(
        screen,
        color,
        (
            ship.x,
            ship.y + ship.h * ship.scale,
            (ship.w * ship.scale) *
            (constrain(ship.hp, 0, ship.max_hp) / ship.max_hp),
            10
        )
    )


def draw_boss_text():

    text_boss_line = font_small.render(
        boss.name + " HP: " + "{:0.0f}".format(boss.hp), True, (255, 100, 100))

    screen.blit(text_boss_line, (width - text_boss_line.get_width(), 680))


def run_title_screen():
    global game_state, background_speed

    background_speed = constrain(
        background_speed * 1.01, 1, BACKGROUND_SPEED_WARP)

    # draw a starry background
    screen.fill(BLACK)

    move_starfield()
    draw_starfield()

    player.x = width * 1.5
    boss.x = width * 2

    screen.blit(text_title_start,
                (width / 2 - text_title_start.get_width()/2,
                 height / 2 - text_title_start.get_height()/2))

    screen.blit(text_title_deflect,
                (width / 2 - text_title_deflect.get_width()/2,
                 height / 2 - text_title_deflect.get_height()/2 + 50))

    screen.blit(controls, (width / 2 - controls.get_width() / 2, 400))

    draw_heading()

    # check for key press of space
    keys = pygame.key.get_pressed()

    joy_shoot = False

    # check if the X button was pressed on the xbox controller
    if joystick is not None:
        if joystick.get_button(2):
            joy_shoot = True

    if keys[pygame.K_SPACE] or joy_shoot:
        game_state = GameState.StartLevel

    # check for a key press of escape
    if keys[pygame.K_ESCAPE]:
        game_state = GameState.Quit

    # update the screen
    pygame.display.flip()


def draw_heading():
    screen.blit(text_title_heading,
                (width / 2 - text_title_heading.get_width()/2,
                 50))

def run_ending_screen():
    # draw a starry background
    screen.fill(BLACK)
    move_starfield()
    draw_starfield()

    CONGRATULATIONS = "CONGRATULATIONS!!!"
    text_congratulations = font_large.render(CONGRATULATIONS, True, (255, 255, 255))
    screen.blit(text_congratulations, (width / 2 - text_congratulations.get_width()/2, 50))


    build_path_raw = "Upgrades : " + " > ".join(upgrade_path)

    # split build path into lines of 60 characters
    build_path_1 = ""
    build_path_2 = ""
    build_path_3 = ""
    build_path_4 = ""

    build_path_1 = build_path_raw[:60]
    if len(build_path_raw) > 60:
        build_path_2 = build_path_raw[60:120]
    if len(build_path_raw) > 120:
        build_path_3 = build_path_raw[120:180]
    if len(build_path_raw) > 180:
        build_path_4 = build_path_raw[180:240]


    ending_dialog = [
        "As Captain Jack lands the final blow on Roy Carnassus, the tyrant's",
        "body crumbles into a cloud of cosmic dust. The galaxy is saved, and",
        "the universe is at peace. Captain Jack is hailed as a hero, and the",
        "galaxy rejoices in a new era of peace and prosperity.",
        "",
        "\"Captain Jack, Savior of the Galaxy! In the face of insurmountable",
        "odds, you have vanquished the malevolent Roy Carnassus, restoring",
        "hope and prosperity to the cosmos. The stars themselves bear witness",
        "to your valor, and your tale shall be etched in the annals of time.",
        "Now, prepare to embark on your next adventure, for the universe is",
        "yours to explore!\"",
        "",
        "Deaths: " + str(player.deaths),
        # "Weapons: " + str(player.weapon_level),
        # "Defense: " + str(player.defense_level + 1),
        # "",
        build_path_1,
        build_path_2,
        build_path_3,
        build_path_4,
        "",
        "[escape] TO QUIT"
    ]



    for i in range(len(ending_dialog)):
        text = font_small.render(ending_dialog[i], True, (255, 255, 255))
        screen.blit(text, (width / 2 - text.get_width()/2, 150 + i * 25))


    # update the screen
    pygame.display.flip()

    # save the display to a file in my pictures
    if state_current_frame() == 0:
        # name the file with the current date and time
        now = datetime.datetime.now()
        filename = "THFRC-" + now.strftime("%Y-%m-%d_%H-%M-%S") + ".png"
        pygame.image.save(screen, os.path.expanduser("~/" + filename))


def run_victory_screen():
    global game_state, background_speed, player_projectiles, upgrade_offers

    # draw a starry background
    screen.fill(BLACK)

    move_starfield()
    move_projectiles()

    draw_starfield()
    draw_projectiles()

    if (state_current_frame() / 10 % 2 == 1) and state_current_frame() < 100 * fps_scaler():
        boss.draw()

    # animate the player charging engines and zooming off
    if state_current_frame() == 0:
        player.vx = (400 - player.x) / (150 * fps_scaler())
        player.vy = (height / 2 - player.y) / (150 * fps_scaler())

    if state_current_frame() >= 150 * fps_scaler():
        player.vx = -3
        player.vy = 0

    if state_current_frame() > 150 * fps_scaler():
        background_speed = constrain(
            background_speed * 0.99, 0.1, BACKGROUND_SPEED_WARP)
        player_projectiles = []
        # draw a circle expanding out from behind the player
        flame_color_heating_up = 80 + \
            (state_current_frame() * fps_divisor() - 150)
        pygame.draw.circle(
            screen,
            (255, flame_color_heating_up, flame_color_heating_up),
            (player.x, player.y + player.h * player.scale / 2),
            3 + (state_current_frame() - 150) / 8
        )

    # if state_current_frame() < 270 * fps_scaler():
    if state_current_time() < 4.5:
        player.move()

    if state_current_time() >= 4.5:
        player.x = width * 3
        background_speed = BACKGROUND_SPEED_WARP
        # draw a white box where the player left off from across the screen
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (
                0,
                player.y,
                width,
                player.h * player.scale
            )
        )

    # end the animation and go to the level up screen
    if state_current_time() >= 5:
        if boss.name == "Roy Carnassus":
            game_state = GameState.Ending
        else:
            game_state = GameState.LevelUp
            upgrade_offers = [
                UpgradeType.AttackSpeed,
                UpgradeType.AttackDamage,
                UpgradeType.ForwardTorpedo,
                UpgradeType.HomingTorpedo,
                UpgradeType.WildTorpedo,
                UpgradeType.MaxHealth,
                UpgradeType.DeflectCooldown,
                UpgradeType.ArmorUp,
                UpgradeType.LifeSteal,
            ]
            random.shuffle(upgrade_offers)
            load_boss()

    # draw the player
    player.draw()

    draw_score_line()

    # update the screen
    pygame.display.flip()


def load_boss():
    global boss, enemy_units

    # clear enemy units
    enemy_units = []

    # select the boss and name it
    boss_divisor = 15
    sprite_selector = boss.level % boss_divisor

    boss_name_mark = 0
    boss_level = boss.level
    while boss_level > 0:
        boss_level -= boss_divisor
        boss_name_mark += 1

    if sprite_selector == 0:
        boss.name = "Roy Carnassus"
        boss.change_sprite("ships/Zeromus2.gif", 0, 0,
                           304, 256, None, 1)
        boss.flip_h()
    elif sprite_selector == 1:
        boss.name = "Doge"
        boss.change_sprite("ships/doge.png", 0, 0,
                           240, 174, None, 1)

    elif sprite_selector == 2:
        boss.name = "DVD Dreadnaught"
        boss.change_sprite("ships/dvd.png", 1, 1, 1600, 740, None, 0.2)

    elif sprite_selector == 3:
        boss.name = "Sus Man"
        boss.change_sprite("ships/susman.png", 0, 0,
                           192, 231, None, 1)


    elif sprite_selector == 4:
        boss.name = "Evil Car"
        boss.change_sprite("ships/evil-car.png", 0, 0,
                           240, 131, None, 1)

    elif sprite_selector == 5:
        boss.name = "Rathtar Overlord"
        boss.change_sprite("ships/plantboy.gif", 0, 0,
                           126, 94, None, 1.5)
        boss.flip_h()

    elif sprite_selector == 6:
        boss.name = "Doom Train"
        boss.change_sprite("ships/train.gif", 0, 0,
                           240, 208, None, 1)

    elif sprite_selector == 7:
        boss.name = "The Great Cthulhu"
        boss.change_sprite("ships/cthulhu.png", 0, 0,
                           722, 608, None, 0.3)

    elif sprite_selector == 8:
        boss.name = "Flying Spaghetti Monster"
        boss.change_sprite("ships/sgetti.png", 0, 0,
                           1280, 1027, None, 0.25)

    elif sprite_selector == 9:
        boss.name = "Zone Eater"
        boss.change_sprite("ships/zone-eater.gif", 0, 0,
                           190, 144, None, 1.5)
        boss.flip_h()

    elif sprite_selector == 10:
        boss.name = "Morpha"
        boss.change_sprite("ships/zombone.gif", 0, 0,
                           128, 128, None, 2)
        boss.flip_h()

    elif sprite_selector == 11:
        boss.name = "Odin"
        boss.change_sprite("ships/atma.gif", 0, 0,
                           256, 256, None, 1)
        boss.flip_h()

    elif sprite_selector == 12:
        boss.name = "Zombie Villager"
        boss.change_sprite("ships/zombieeeeeee.png", 0, 0,
                           146, 256, None, 1)


    elif sprite_selector == 13:

        boss.name = "Alexander"
        boss.change_sprite("ships/Behemoth.gif", 0, 0,
                           190, 96, None, 1.25)
        boss.flip_h()

    elif sprite_selector == 14:

        boss.name = "Windows XP"
        boss.change_sprite("ships/windoze.png", 0, 0,
                           1364, 1203, None, 0.2)
        boss.flip_h()


    boss.mask = pygame.mask.from_surface(boss.sprite)

    if boss_name_mark > 1:
        boss.name += " Mk " + get_roman_numeral(boss_name_mark)


def get_roman_numeral(number):
    num = [1, 4, 5, 9, 10, 40, 50, 90,
           100, 400, 500, 900, 1000]
    sym = ["I", "IV", "V", "IX", "X", "XL",
           "L", "XC", "C", "CD", "D", "CM", "M"]
    i = 12

    str_out = ""

    while number:
        div = number // num[i]
        number %= num[i]

        while div:
            str_out += sym[i]
            # print(sym[i], end = "")
            div -= 1
        i -= 1

    return str_out


def draw_starfield():
    # draw the stars
    for star in stars:
        star.draw()

    # draw the nearfield space objects
    for so in space_objects:
        so.draw()


def run_game_over_screen():
    global game_state, player, boss, boss_projectiles, background_speed

    # draw a starry background
    screen.fill(BLACK)

    move_starfield()
    draw_starfield()

    background_speed = constrain(background_speed * 0.99, 0.5, None)

    boss.vx = 1
    boss.vy = 0
    boss.move()
    boss.draw()

    # draw the projectiles
    move_projectiles()
    draw_projectiles()

    screen.blit(text_ship_destroyed,
                (width / 2 - text_ship_destroyed.get_width()/2,
                 height / 2 - text_ship_destroyed.get_height()/2 - 125))

    screen.blit(text_journey_again,
                (width / 2 - text_journey_again.get_width()/2,
                 height / 2 - text_journey_again.get_height()/2))

    screen.blit(text_quit_key,
                (width / 2 - text_quit_key.get_width()/2,
                    height / 2 - text_quit_key.get_height()/2 + 50))

    draw_boss_text()

    # check for enter key to start a new game
    keys = pygame.key.get_pressed()

    # check for joystick input
    joy_weapon_upgrade = False

    if joystick is not None:
        if joystick.get_button(3):
            joy_weapon_upgrade = True

    if keys[pygame.K_RETURN] or joy_weapon_upgrade:
        background_speed = 1
        player.hp = player.max_hp
        # boss.hp = boss.max_hp
        player.x = 100
        player.y = height / 2 - player.h * player.scale / 2
        boss.x = boss_start_position()
        boss.y = height / 2 - boss.h * boss.scale / 2
        boss_projectiles = []
        game_state = GameState.Game

    # check for a key press of escape
    if keys[pygame.K_ESCAPE]:
        game_state = GameState.Quit

    draw_score_line()

    # update the screen
    pygame.display.flip()


def run_level_up_screen():
    global game_state, player, boss, background_speed

    # draw a starry background
    screen.fill(BLACK)

    move_starfield()
    draw_starfield()

    screen.blit(text_level_up, (width / 2 - text_level_up.get_width() / 2, 25))
    screen.blit(text_level_select_an_upgrade, (width / 2 - text_level_up.get_width() / 2, 75))

    card_spacing = int(width / 5)
    card_width = 250
    card_height = 200

    for i in range(4):
        card_upgrade = upgrades[upgrade_offers[i] - 1]
        card_name = card_upgrade['name']
        card_info_1 = card_upgrade['info_1']
        card_info_2 = card_upgrade['info_2']
        card_info_3 = card_upgrade['info_3']
        color = card_upgrade['color']
        card_top = 128
        card_center = card_spacing * (i + 1)
        card_left = card_spacing * (i + 1) - card_width / 2

        # draw the card border
        pygame.draw.rect(screen, color, (card_left, card_top, card_width, card_height), 3, 10)

        # draw the number of the card at the top center of the card
        text_card_number = font.render(str(i + 1), True, color)
        screen.blit(text_card_number, (card_center - text_card_number.get_width() / 2, card_top + 10))
        screen.blit(text_card_number, (card_center - text_card_number.get_width() / 2, card_top + card_height - text_card_number.get_height() - 10))

        # draw a line above and below the card number
        top_line_y = card_top + text_card_number.get_height() + 20
        bottom_line_y = card_top + card_height - text_card_number.get_height() - 20
        pygame.draw.line(screen, color, (card_left, top_line_y), (card_left + card_width - 1, top_line_y), 3)
        pygame.draw.line(screen, color, (card_left, bottom_line_y), (card_left + card_width - 1, bottom_line_y), 3)

        # draw the card text based on the upgrade_offers
        # and their text data in the upgrades dictionary
        text_card_title = font_small.render(card_name, True, color)
        text_card_info_1 = font_tiny.render(card_info_1, True, color)
        text_card_info_2 = font_tiny.render(card_info_2, True, color)
        text_card_info_3 = font_tiny.render(card_info_3, True, color)
        screen.blit(text_card_title, (card_center - text_card_title.get_width() / 2, top_line_y + 10))
        screen.blit(text_card_info_1, (card_center - text_card_info_1.get_width() / 2, top_line_y + 50))
        screen.blit(text_card_info_2, (card_center - text_card_info_2.get_width() / 2, top_line_y + 75))
        screen.blit(text_card_info_3, (card_center - text_card_info_3.get_width() / 2, top_line_y + 100))

    # check for enter key to level up weapon
    keys = pygame.key.get_pressed()



    proceed = False
    if keys[pygame.K_1]:
        proceed = True
        process_upgrade(upgrade_offers[0])
    elif keys[pygame.K_2]:
        proceed = True
        process_upgrade(upgrade_offers[1])
    elif keys[pygame.K_3]:
        proceed = True
        process_upgrade(upgrade_offers[2])
    elif keys[pygame.K_4]:
        proceed = True
        process_upgrade(upgrade_offers[3])
    elif keys[pygame.K_q]:
        # cheat code 'q' to level up all upgrades
        process_upgrade(upgrade_offers[0])
        process_upgrade(upgrade_offers[1])
        process_upgrade(upgrade_offers[2])
        process_upgrade(upgrade_offers[3])
        proceed = True
    elif keys[pygame.K_9]:
        # cheat code '9' to level up all upgrades
        process_upgrade(upgrade_offers[0])
        process_upgrade(upgrade_offers[1])
        process_upgrade(upgrade_offers[2])
        process_upgrade(upgrade_offers[3])
        game_state = GameState.Ending



    # check for a key press of either enter or tab to start the next level
    if proceed:
        player.x = width * 1.5
        player.y = height / 2 - player.h * player.scale / 2

        boss.x = width * 2
        boss.y = height / 2 - boss.h * boss.scale / 2
        boss.vx = 0
        boss.vy = 0

        game_state = GameState.StartLevel

    # check for a key press of escape
    if keys[pygame.K_ESCAPE]:
        game_state = GameState.Quit

    draw_score_line()

    # update the screen
    pygame.display.flip()


def run_start_level_screen():
    global game_state, player, boss, background_speed

    background_speed = constrain(background_speed * 0.97, 1.0, None)
    player.x = constrain(player.x - (10 + 5 * background_speed), 100, None)
    boss.x = constrain(boss.x - (10 + 3 * background_speed),
                       boss_start_position(), None)
    move_starfield()

    # draw a starry background
    screen.fill(BLACK)
    draw_starfield()
    player.draw()
    boss.draw()

    # draw the threat detected text
    screen.blit(
        text_threat_detected,
        (width / 2 - text_threat_detected.get_width() / 2, 100)
    )

    if state_current_frame() == 0:
        boss_warning = boss.level % 4 + 1
        if boss_warning == 1:
            pygame.mixer.Sound.play(sfx['comm_bird'])
        elif boss_warning == 2:
            pygame.mixer.Sound.play(sfx['comm_fox'])
        elif boss_warning == 3:
            pygame.mixer.Sound.play(sfx['comm_bunny'])
        elif boss_warning == 4:
            pygame.mixer.Sound.play(sfx['comm_bunny'])

    if state_current_frame() > 20 * fps_scaler():
        # draw the bosses name text below the threat detected text
        boss_name_text = font_large.render(boss.name, True, (255, 0, 0))

        screen.blit(boss_name_text, (width / 2 -
                    boss_name_text.get_width()/2, 150))

    if background_speed == 1.0 and player.x == 100 and boss.x == boss_start_position():
        game_state = GameState.Game

    draw_score_line()

    # update the screen
    pygame.display.flip()


def state_current_frame():
    return frame_counter - state_start_frame

def state_current_time():
    return time.time() - state_start_time

def set_volume(level: int = 100):
    global volume
    volume = level
    pygame.mixer.music.set_volume(volume / 100)
    for sound in sfx:
        sfx[sound].set_volume(volume / 100)


def change_volume():
    global volume
    volume += 10
    if volume > 100:
        volume = 0
    set_volume(volume)

###############################################################################
# main entry point for the game
###############################################################################

# start the game
print("Starting game...")
pygame.init()
print("pygame.init() complete. Setting up screen...")
screen = pygame.display.set_mode(
    (width, height+60), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption(
    "The Hunt for Roy Carnassus")
print("Screen setup complete.")

print("Generating font objects...")
font_large = pygame.font.Font('fonts/PressStart2P.ttf', FONT_SIZE_LARGE)
font = pygame.font.Font('fonts/PressStart2P.ttf', FONT_SIZE_NORMAL)
font_small = pygame.font.Font('fonts/PressStart2P.ttf', FONT_SIZE_SMALL)
font_tiny = pygame.font.Font('fonts/PressStart2P.ttf', FONT_SIZE_TINY)

text_title_heading = font_large.render(
    "The Hunt for Roy Carnassus", True, (255, 255, 255))
text_threat_detected = font.render(
    "THREAT DETECTED !! Sensors indicate...", True, (255, 255, 255), (255,0,0))
text_title_start = font_large.render(
    '[space] TO SHOOT', True, (0, 255, 255))
text_title_deflect = font_large.render(
    '[tab] TO DEFLECT', True, (0, 255, 255))

text_quit_key = font_large.render('[escape] TO QUIT', True, (255, 255, 255))
text_ship_destroyed = font_large.render('SHIP DESTROYED!', True, (255, 0, 0))
text_journey_again = font_large.render(
    '[enter] TO JOURNEY AGAIN', True, (0, 255, 255))
text_level_up = font_large.render('LEVEL UP!', True, (0, 255, 255))
text_level_select_an_upgrade = font.render('SELECT AN UPGRADE', True, (0, 255, 255))
text_level_weapon = font.render('[enter] WEAPON RESEARCH', True, (0, 255, 255))
text_level_armor = font.render('[tab] DEFENSE RESEARCH', True, (0, 255, 0))
print("Font objects generated.")

print("Loading sounds...")

# make a dictionary of the sound effect files
sfx = {
    "player_hit": pygame.mixer.Sound('sounds/player_hit.wav'),
    "player_death": pygame.mixer.Sound('sounds/player_death.wav'),
    "boss_hit": pygame.mixer.Sound('sounds/boss_hit.wav'),
    "player_heal": pygame.mixer.Sound('sounds/player_heal.wav'),
    "comm_bird": pygame.mixer.Sound('sounds/comm-bird.ogg'),
    "comm_bunny": pygame.mixer.Sound('sounds/comm-bunny.ogg'),
    "comm_fox": pygame.mixer.Sound('sounds/comm-fox.ogg'),
    "comm_frog": pygame.mixer.Sound('sounds/comm-frog.ogg'),
    "level_up": pygame.mixer.Sound('sounds/level_up.wav'),
    "deflect": pygame.mixer.Sound('sounds/deflect.wav'),
}

# make a dictionary of various space images
images = {
    # "galaxy": load_image('sprites/parallax-space-background.png'),
    # "near_planet": load_image('sprites/parallax-space-big-planet.png'),
    # "far_planet": load_image('sprites/parallax-space-far-planets.png'),
    # "ring_planet": load_image('sprites/parallax-space-ring-planet.png'),
    "planet1": load_image('sprites/planet1.png'),
    "planet2": load_image('sprites/planet2.png'),
    "planet3": load_image('sprites/planet3.png'),
    "planet4": load_image('sprites/planet4.png'),
    "planet5": load_image('sprites/planet5.png'),
    "planet6": load_image('sprites/planet6.png'),
    "planet7": load_image('sprites/planet7.png'),
    "planet10": load_image('sprites/planet10.png'),
    "planet11": load_image('sprites/planet11.png'),
    "planet12": load_image('sprites/planet12.png'),
    "planet13": load_image('sprites/planet13.png'),
    "planet14": load_image('sprites/planet14.png'),
    "planet15": load_image('sprites/planet15.png'),
    "planet16": load_image('sprites/planet16.png'),
    "planet17": load_image('sprites/planet17.png'),
    "planet18_0": load_image('sprites/planet18_0.png'),
    "planet19": load_image('sprites/planet19.png'),
    "planet20": load_image('sprites/planet20.png'),


}


print("Sounds loaded.")

print("Increasing sound channels...")  # pygame defaults to 8, but we need more
pygame.mixer.set_num_channels(32)

print("Setting volume levels...")
set_volume(volume)

print("Initializing game clock...")
clock = pygame.time.Clock()
done = False

# lists to draw
stars = []
player_projectiles = []
boss_projectiles = []
enemy_units = []
space_objects = []


print("Seeding starfield...")
for i in range(starfield_size):
    stars.append(Star())

player = Ship("ships/kenney-ship-3.png", scale=0.5)
player.type = MOB_TYPE_PLAYER
player.max_hp = 15
player.hp = player.max_hp
player.x = 100
player.deaths = 0
player.score = 0
player.life_steal = 0
player.add_weapon(ProjectileType.ForwardTorpedo)

boss = Ship("ships/ships_3.png", 1, 1, 310, 150, (38, 37, 37), 1)
boss.type = MOB_TYPE_BOSS
boss.level = 1
boss.max_hp = BOSS_BASE_HEALTH
boss.hp = boss.max_hp
load_boss()

# space_objects.append(SpaceObject('ring_planet'))
# space_objects.append(SpaceObject('far_planet'))
# space_objects.append(SpaceObject('near_planet'))
space_objects.append(SpaceObject('planet1'))
space_objects.append(SpaceObject('planet2'))
space_objects.append(SpaceObject('planet3'))
space_objects.append(SpaceObject('planet4'))
space_objects.append(SpaceObject('planet5'))
space_objects.append(SpaceObject('planet6'))
space_objects.append(SpaceObject('planet7'))
space_objects.append(SpaceObject('planet10'))
space_objects.append(SpaceObject('planet11'))
space_objects.append(SpaceObject('planet12'))
space_objects.append(SpaceObject('planet13'))
space_objects.append(SpaceObject('planet14'))
space_objects.append(SpaceObject('planet15'))
space_objects.append(SpaceObject('planet16'))
space_objects.append(SpaceObject('planet17'))
space_objects.append(SpaceObject('planet18_0'))
space_objects.append(SpaceObject('planet19'))
space_objects.append(SpaceObject('planet20'))


meatball = load_image("sprites/jwd-meatball.png")
noodle = load_image("ships/macaroni.png", scale=0.03)
controls = load_image("sprites/jwd-move.png")
player_torpedo = load_image("sprites/kenney-player-torpedo.png", scale=0.75)


# boss.flip_h()
boss.x = boss_start_position()
boss.y = height/2

# start joystick control and select the default joystick
joystick = None
try:
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
except:
    print("No joystick found.")
    joystick = None


def handle_jukebox():
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load(random.choice(JUKEBOX))
        pygame.mixer.music.play()


# Begin main loop
while not done:

    handle_game_events()
    handle_jukebox()

    # check the game state and perform the appropriate actions
    match game_state:
        case GameState.Title:
            run_title_screen()
        case GameState.Game:
            update_game()
            draw_screen()
        case GameState.Victory:
            run_victory_screen()
        case GameState.LevelUp:
            run_level_up_screen()
        case GameState.GameOver:
            run_game_over_screen()
        case GameState.StartLevel:
            run_start_level_screen()
        case GameState.Quit:
            done = True
        case GameState.Ending:
            run_ending_screen()
        case _:
            print("Unknown game state: " + str(game_state))
            done = True

    # increment the frame counter
    frame_counter += 1

    # if the game state changes record the frame and timing counter
    if game_state != last_game_state:
        print("State Change: " + str(last_game_state) + " -> " +str(game_state) +
              ", State Duration: " + str(state_current_time()))

        last_game_state = game_state
        state_start_frame = frame_counter
        state_start_time = time.time()

    # console the frame rate
    if(frame_counter % fps == 0):
        dps = damage_done - last_damage_done
        last_damage_done = damage_done
        print("Frame Rate: " + str(round(clock.get_fps())) +
              ", Game State: " + str(game_state) + ", State Time: " +
              str(time.time() - state_start_time) + ", DPS: " + str(dps) +
              ", Last dt: " + str(dt)
              )

    # limit to 60 frames per second
    dt = clock.tick(fps) / 1000
    time_frame_start = time.time()


# quit pygame and clean up
pygame.quit()
