#!/usr/bin/env python3

# sprite resources: https://www.spriters-resource.com/snes/superrtype/

# Create a 2d game space ship shmup with pygame
# from lib2to3.pgen2.driver import Driver
# from turtle import back
import pygame
import random
import math

width = 1280
height = 660
ship_speed = 9
background_speed = 1.0
frame_counter = 0
frame_last_shot = 0
game_state = "title"
last_game_state = "title"
state_start_frame = 0
starfield_size = 300

BACKGROUND_SPEED_NORMAL = 1.0
BACKGROUND_SPEED_WARP = 10
FONT_SIZE_NORMAL = 48
FONT_SIZE_SMALL = 36
HEAL_CHANCE = 4
SHOW_PROJECTILE_VALUES = False
BOSS_BASE_HEALTH = 100


# classes

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


# enumerate the projectile types
PROJECTILE_TYPE_CIRCLE = 1
PROJECTILE_TYPE_MEATBALL = 2
PROJECTILE_TYPE_NOODLE = 3
PROJECTILE_TYPE_FOOTBALL = 4
PROJECTILE_TYPE_BASEBALL = 5
PROJECTILE_TYPE_BASKETBALL = 6
PROJECTILE_TYPE_VOLLEYBALL = 7
PROJECTILE_TYPE_SOCCER_BALL = 8
PROJECTILE_TYPE_BOMB = 9
PROJECTILE_TYPE_JAR = 10
PROJECTILE_TYPE_MIRV = 11
PROJECTILE_TYPE_TORPEDO = 12

# enumerate the trash mob types
MOB_TYPE_BOSS = -1
MOB_TYPE_PLAYER = 0
MOB_TYPE_BASIC = 1  # tie fighter sprite ?
MOB_TYPE_GRAVITY = 2  # count down then start pulling objects into it
MOB_TYPE_FIGHTER = 3  # x-wing sprite
MOB_TYPE_HEALER = 4  # medivac srpite
MOB_TYPE_SNARE = 5  # Snare drum sprite? :)


def boss_start_position():
    return width - boss.w * boss.scale - 100


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
        self.x -= self.speed * background_speed

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
        if background_speed > 1.5:
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


class Ship:
    def __init__(self, sprite, x, y, w, h, color_key=None, scale=1, type=MOB_TYPE_BASIC):
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

    def move(self):
        self.x += self.vx
        self.y += self.vy

        edge_hit = False

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
        if(self.color_key is not None):
            self.sprite.set_colorkey(self.color_key)

    def draw(self):
        screen.blit(self.sprite, (self.x, self.y))

    def flip_h(self):
        self.sprite = pygame.transform.flip(self.sprite, True, False)
        if(self.color_key is not None):
            self.sprite.set_colorkey(self.color_key)

    def flip_v(self):
        self.sprite = pygame.transform.flip(self.sprite, False, True)
        if(self.color_key is not None):
            self.sprite.set_colorkey(self.color_key)

    def collide_mask(self, mask, x=0, y=0):
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(self.mask, offset)
        if(poi is not None):
            return True
        else:
            return False

# load a part of an image from a file to be used as a sprite frame


class Projectile:
    def __init__(self, x, y, vx, vy, damage, color, radius, acceleration=1.0, type=PROJECTILE_TYPE_CIRCLE):
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

        self.x += self.vx
        self.y += self.vy

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
                if self.type == PROJECTILE_TYPE_CIRCLE:
                    pygame.draw.circle(screen, self.color,
                                       (self.x, self.y), self.radius)
                    # pygame.draw.circle(screen, (self.color[0]*0.5, self.color[1]*0.5, self.color[2]*0.5),
                    #                    (self.x, self.y), self.radius,
                    #                    width=4)

                elif self.type == PROJECTILE_TYPE_MEATBALL:
                    # screen.blit(meatball, (self.x - meatball.get_width() /
                    #             2, self.y - meatball.get_height() / 2))
                    self.blitRotateCenter(
                        meatball,
                        (self.x - meatball.get_width() / 2,
                         self.y - meatball.get_height() / 2),
                        frame_counter % 360
                    )
                elif self.type == PROJECTILE_TYPE_NOODLE:
                    self.blitRotateCenter(
                        noodle,
                        (self.x - noodle.get_width() / 2,
                         self.y - noodle.get_height() / 2),
                        frame_counter % 360
                    )
        else:
            if(self.damage < 0):
                # if my damage is negative (healing), draw a green value
                text_damage_value = font_small.render(
                    "+" + str(abs(self.damage)), True, GREEN)

            else:
                # otherwise, draw my damage value normally
                text_damage_value = font_small.render(
                    str(self.damage), True, self.color)
            screen.blit(text_damage_value, (self.x, self.y))

    def blitRotateCenter(self, image, topleft, angle):

        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(
            center=image.get_rect(topleft=topleft).center)

        screen.blit(rotated_image, new_rect)


def load_image(filename, x: int | None = None, y: int | None = None, w: int | None = None, h: int | None = None, color_key=None, scale=1):
    image = pygame.image.load(filename)

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
    global galaxy1x
    global galaxy1vx

    galaxy1x -= galaxy1vx * background_speed

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
    global player, frame_last_shot

    # reset ship motion
    player.vx = 0
    player.vy = 0

    # handle key presses
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.vx -= ship_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.vx += ship_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player.vy -= ship_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player.vy += ship_speed
    if keys[pygame.K_SPACE]:
        if(frame_counter - frame_last_shot > 5):
            player_shoot()
            frame_last_shot = frame_counter


def handle_game_events():
    global done
    # handle events and key presses
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True


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
    if(frame_counter % constrain((13 - boss.level), 8, 13) == 0):
        if (random.randint(0, 100) < (50+int(boss.level/4))):
            boss_shoot()


def player_shoot():
    global player_projectiles

    # perform basic attack
    player_projectiles.append(
        fire_projectile(
            player,
            boss,
            1,
            player.weapon_level*3,
            WHITE,
            6,
            20
        )
    )

    # player level 2 weapon: quadrant attack
    if player.weapon_level >= 2:
        player_projectiles.append(
            fire_projectile(
                player,
                boss,
                2,
                player.weapon_level*2,
                CYAN,
                6,
                20
            )
        )

    # player level 3 weapon: targeted attack
    if player.weapon_level >= 3:
        player_projectiles.append(
            fire_projectile(
                player,
                boss,
                3,
                player.weapon_level,
                BLUE,
                6,
                20
            )
        )

    # player level 4 weapon: second forward attack
    if player.weapon_level >= 4:
        player_projectiles.append(
            fire_projectile(
                player,
                boss,
                1,
                player.weapon_level*2,
                WHITE_2,
                6,
                20,
                ox=-5,
                oy=-15
            )
        )

    # player level 5 weapon: third forward attack
    if player.weapon_level >= 5:
        player_projectiles.append(
            fire_projectile(
                player,
                boss,
                1,
                player.weapon_level*2,
                WHITE_2,
                6,
                20,
                ox=-5,
                oy=15
            )
        )

    # player level 6 weapon: second quadrant attack
    if player.weapon_level >= 6:
        player_projectiles.append(
            fire_projectile(
                player,
                boss,
                2,
                player.weapon_level,
                CYAN,
                6,
                20,
                ox=-5,
                oy=-15
            )
        )

    # player level 7 weapon: third quadrant attack
    if player.weapon_level >= 7:
        player_projectiles.append(
            fire_projectile(
                player,
                boss,
                2,
                player.weapon_level,
                CYAN,
                6,
                20,
                ox=-5,
                oy=15
            )
        )


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
    projectile_type=PROJECTILE_TYPE_CIRCLE,
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
            vy = random.random() * -speed
        else:
            vy = random.random() * speed

        while (abs(vx) + abs(vy) < speed / 1.5):
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
    projectile_type = PROJECTILE_TYPE_CIRCLE

    # if it's the flying spaghetti monster, set the attack type to a meatball
    if boss.level == 8:
        # 50/50 chance to shoot a meatball or a noodle
        if random.randint(0, 100) < 50:
            projectile_type = PROJECTILE_TYPE_MEATBALL
        else:
            projectile_type = PROJECTILE_TYPE_NOODLE

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

        if projectile.type == PROJECTILE_TYPE_CIRCLE or projectile.damage < 0:
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
    for projectile in player_projectiles:
        # check if the projectile x y is within the boss x y + w h
        #        if(projectile.x > boss.x and projectile.x < boss.x + boss.w * boss.scale and projectile.y > boss.y and projectile.y < boss.y + boss.h * boss.scale):
        if not projectile.hit:
            if(projectile_hits_ship(projectile, boss)):
                # play the player hit sound
                pygame.mixer.Sound.play(sound_player_hit)
                boss.hp -= projectile.damage
                # player_projectiles.remove(projectile)
                projectile.hit = True

    # collide boss projectiles with the player
    for projectile in boss_projectiles:
        # check if the projectile x y is within the player x y + w h
        # if(projectile.x > player.x and projectile.x < player.x + player.w * player.scale and projectile.y > player.y and projectile.y < player.y + player.h * player.scale):
        if not projectile.hit:
            if(projectile_hits_ship(projectile, player)):
                # play the boss hit sound effect

                if projectile.damage < 0:
                    pygame.mixer.Sound.play(sound_player_heal)
                else:
                    pygame.mixer.Sound.play(sound_boss_hit)
                    projectile.damage -= player.defense_level

                player.hp -= projectile.damage

                # boss_projectiles.remove(projectile)
                projectile.hit = True

    # cap the player at double their max hp
    player.hp = constrain(player.hp, -player.max_hp, player.max_hp * 2)


def update_game():
    global game_state, boss_projectiles, player_projectiles
    # move the stars
    move_starfield()

    handle_game_events()
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
            player.hp = 0
            print("PERFECT CORNER HIT! PAM BEESLEY CHEERS ON " +
                  boss.name + " AS IT DESTROYS YOU")

    # move the projectiles
    move_projectiles()

    # calculate collisions
    collide()

    # check for player death
    if player.hp <= 0:
        # play the player death sound
        pygame.mixer.Sound.play(sound_player_death)
        player.hp = 0
        game_state = "game_over"
        # boss_projectiles = []
        player_projectiles = []

    # check for level up
    if boss.hp <= 0:
        # play the boss death sound
        pygame.mixer.Sound.play(sound_level_up)

        game_state = "victory"
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
    screen.fill((0, 0, 0))
    # draw the stars
    draw_starfield()

    # draw the ship
    player.draw()

    # draw the boss
    boss.draw()

    # for

    # draw the projectiles
    draw_projectiles()

    # draw the boss hp as a bar on the screen below the boss
    pygame.draw.rect(
        screen,
        (255, 255, 0),
        (
            boss.x,
            boss.y + boss.h * boss.scale,
            boss.w * boss.scale,
            10
        )
    )

    pygame.draw.rect(
        screen,
        (255, 0, 0),
        (
            boss.x,
            boss.y + boss.h * boss.scale,
            (boss.w * boss.scale) * (boss.hp / boss.max_hp),
            10
        )
    )

    # draw the player hp bar on the screen below the player
    pygame.draw.rect(
        screen,
        (255, 255, 0),
        (
            player.x,
            player.y + player.h * player.scale,
            player.w * player.scale,
            10
        )
    )

    pygame.draw.rect(
        screen,
        (0, 255, 0),
        (
            player.x,
            player.y + player.h * player.scale,
            (player.w * player.scale) *
            (constrain(player.hp, 0, player.max_hp) / player.max_hp),
            10
        )
    )

    # draw the players shield level bar on the screen below the player
    if player.hp > player.max_hp:
        pygame.draw.rect(
            screen,
            BLUE,
            (
                player.x,
                player.y + player.h * player.scale + 11,
                (player.w * player.scale) *
                ((player.hp - player.max_hp) / player.max_hp),
                10
            )
        )

    # draw the score line
    text_score_line = font.render(
        "Level: " + str(player.level) +
        "  Weapon: " + str(player.weapon_level) +
        "  Defense: " + str(player.defense_level) +
        "  HP: " + str(constrain(player.hp, -player.hp, player.max_hp)) + "/" + str(player.max_hp), True, (255, 255, 255))

    # draw your shield level
    if player.hp > player.max_hp:
        text_shield_level = font.render(
            "+ " + str(player.hp-player.max_hp), True, (100, 100, 255))
        screen.blit(text_shield_level, (text_score_line.get_width() + 10, 680))

    screen.blit(text_score_line, (0, 680))
    draw_boss_text()

    # update the screen
    pygame.display.flip()


def draw_boss_text():

    text_boss_line = font.render(
        boss.name + " HP: " + "{:0.0f}".format(boss.hp), True, (255, 100, 100))

    screen.blit(text_boss_line, (width - text_boss_line.get_width(), 680))


def run_title_screen():
    global game_state, background_speed

    background_speed = constrain(
        background_speed * 1.01, 1, BACKGROUND_SPEED_WARP)

    handle_game_events()

    # draw a starry background
    screen.fill((0, 0, 0))

    move_starfield()
    draw_starfield()

    player.x = width * 1.5
    boss.x = width * 2

    screen.blit(text_title_start,
                (width / 2 - text_title_start.get_width()/2,
                 height / 2 - text_title_start.get_height()/2))

    screen.blit(controls, (width / 2 - controls.get_width() / 2, 400))

    draw_heading()

    # check for key press of space
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        # start music
        pygame.mixer.music.load('sounds/music-1-flashman.ogg')
        pygame.mixer.music.play()

        game_state = "start_level"

    # check for a key press of escape
    if keys[pygame.K_ESCAPE]:
        game_state = "quit"

    # update the screen
    pygame.display.flip()


def draw_heading():
    screen.blit(text_title_heading,
                (width / 2 - text_title_heading.get_width()/2,
                 50))


def run_victory_screen():
    global game_state, background_speed, player_projectiles
    handle_game_events()

    # draw a starry background
    screen.fill((0, 0, 0))

    move_starfield()
    move_projectiles()

    draw_starfield()
    draw_projectiles()

    if (state_current_frame() / 10 % 2 == 1) and state_current_frame() < 100:
        boss.draw()

    # animate the player charging engines and zooming off
    if state_current_frame() == 0:
        player.vx = (125 - player.x) / 150
        player.vy = (height / 2 - player.y) / 150

    if state_current_frame() == 150:
        player.vx = -1
        player.vy = 0

    if state_current_frame() > 150:
        background_speed = constrain(
            background_speed * 0.99, 0.1, BACKGROUND_SPEED_WARP)
        player_projectiles = []
        # draw a circle expanding out from behind the player
        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (player.x, player.y + player.h * player.scale / 2),
            3 + (state_current_frame() - 150) / 8
        )

    if state_current_frame() < 270:
        player.move()

    if state_current_frame() > 270:
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
    if state_current_frame() >= 300:
        game_state = "level_up"
        load_boss()

    # draw the player
    player.draw()

    # update the screen
    pygame.display.flip()


def load_boss():
    global boss, enemy_units

    # clear enemy units
    enemy_units = []

    # select the boss and name it
    boss_divisor = 10
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
        boss.name = "Morpha"
        boss.change_sprite("ships/ships_3.png", 1, 1,
                           310, 150, (38, 37, 37), 1)
        boss.flip_h()
    elif sprite_selector == 2:
        boss.name = "DVD Dreadnaught"
        boss.change_sprite("ships/dvd.png", 1, 1, 1600, 740, None, 0.2)

    elif sprite_selector == 3:
        boss.name = "Odin"
        boss.change_sprite("ships/atma.gif", 0, 0,
                           256, 256, None, 1)
        boss.flip_h()

    elif sprite_selector == 4:
        boss.name = "Alexander"
        boss.change_sprite("ships/ships_3.png", 1, 150,
                           310, 138, (38, 37, 37), 1)
        boss.flip_h()

    elif sprite_selector == 5:
        boss.name = "Rathtar Overlord"
        boss.change_sprite("ships/plantboy.gif", 0, 0,
                           126, 94, None, 1)
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
                           190, 144, None, 1)
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

    # draw the galaxy1 in the furthest back layer
    screen.blit(galaxy1, (galaxy1x, 0))

    # draw the stars
    for star in stars:
        star.draw()


def run_game_over_screen():
    global game_state, player, boss, boss_projectiles, background_speed

    handle_game_events()

    # draw a starry background
    screen.fill((0, 0, 0))

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
    draw_heading()

    # check for enter key to start a new game
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RETURN]:
        background_speed = 1
        player.hp = player.max_hp
        boss.hp = boss.max_hp
        player.x = 100
        player.y = height / 2 - player.h * player.scale / 2
        boss.x = boss_start_position()
        boss.y = height / 2 - boss.h * boss.scale / 2
        boss_projectiles = []
        game_state = "game"

    # check for a key press of escape
    if keys[pygame.K_ESCAPE]:
        game_state = "quit"

    # update the screen
    pygame.display.flip()


def run_level_up_screen():
    global game_state, player, boss, background_speed

    handle_game_events()

    # draw a starry background
    screen.fill((0, 0, 0))

    move_starfield()

    draw_starfield()

    screen.blit(text_level_up,
                (width / 2 - text_level_up.get_width()/2,
                 height / 2 - text_level_up.get_height()/2-100))

    screen.blit(text_level_weapon,
                (width / 2 - text_level_weapon.get_width()/2,
                 height / 2 - text_level_weapon.get_height()/2))
    screen.blit(text_level_armor,
                (width / 2 - text_level_armor.get_width()/2,
                 height / 2 - text_level_armor.get_height()/2+100))

    # it will be technically possible to get a frame perfect double level up

    # check for enter key to level up weapon
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RETURN]:
        player.weapon_level += 1

    # check for tab key to level up defense
    if keys[pygame.K_TAB]:
        player.defense_level += 1
        player.max_hp += 5
        player.hp = player.max_hp

    # check for the q key to boost both without the frame perfect double level up
    if keys[pygame.K_q]:
        player.weapon_level += 1
        player.defense_level += 1
        player.max_hp += 5
        player.hp = player.max_hp

    # check for a key press of either enter or tab to start the next level
    if keys[pygame.K_RETURN] or keys[pygame.K_TAB]:

        player.x = width * 1.5
        player.y = height / 2 - player.h * player.scale / 2

        boss.x = width * 2
        boss.y = height / 2 - boss.h * boss.scale / 2
        boss.vx = 0
        boss.vy = 0

        game_state = "start_level"

    # check for a key press of escape
    if keys[pygame.K_ESCAPE]:
        game_state = "quit"

    # update the screen
    pygame.display.flip()


def run_start_level_screen():
    global game_state, player, boss, background_speed

    handle_game_events()

    background_speed = constrain(background_speed * 0.97, 1.0, None)
    player.x = constrain(player.x - (10 + 5 * background_speed), 100, None)
    boss.x = constrain(boss.x - (10 + 4 * background_speed),
                       boss_start_position(), None)
    move_starfield()

    # draw a starry background
    screen.fill((0, 0, 0))
    draw_starfield()
    player.draw()
    boss.draw()

    # draw the threat detected text
    screen.blit(text_threat_detected,
                (width / 2 - text_threat_detected.get_width()/2,
                 100)
                )

    if state_current_frame() > 20:
        # draw the bosses name text below the threat detected text
        boss_name_text = font.render("It's " + boss.name, True, (255, 0, 0))

        screen.blit(boss_name_text, (width / 2 -
                    boss_name_text.get_width()/2, 150))

    if background_speed == 1.0 and player.x == 100 and boss.x == boss_start_position():
        game_state = "game"

    # update the screen
    pygame.display.flip()


def state_current_frame():
    return frame_counter - state_start_frame


# start the game
print("Starting game...")
pygame.init()
print("pygame.init() complete. Setting up screen...")
screen = pygame.display.set_mode((width, height+60))
pygame.display.set_caption(
    "Magnetek Engineering Society: Operation Fractured Sky")
print("Screen setup complete.")

print("Generating font objects...")
font = pygame.font.SysFont(None, FONT_SIZE_NORMAL)
font_small = pygame.font.SysFont(None, FONT_SIZE_SMALL)
text_title_heading = font.render(
    "The Hunt for Roy Carnassus", True, (255, 255, 255))
text_threat_detected = font.render(
    "THREAT DETECTED !!", True, (255, 0, 0))
text_title_start = font.render(
    '[space] TO SHOOT', True, (0, 255, 255))
text_quit_key = font.render('[escape] TO QUIT', True, (255, 255, 255))
text_ship_destroyed = font.render('SHIP DESTROYED!', True, (255, 0, 0))
text_journey_again = font.render(
    '[enter] TO JOURNEY AGAIN', True, (0, 255, 255))
text_level_up = font.render('LEVEL UP!', True, (0, 255, 255))
text_level_weapon = font.render('[enter] WEAPON RESEARCH', True, (0, 255, 255))
text_level_armor = font.render('[tab] DEFENSE RESEARCH', True, (0, 255, 0))
print("Font objects generated.")

print("Loading sounds...")
sound_player_hit = pygame.mixer.Sound('sounds/player_hit.wav')
sound_player_death = pygame.mixer.Sound('sounds/player_death.wav')
sound_boss_hit = pygame.mixer.Sound('sounds/boss_hit.wav')
sound_player_heal = pygame.mixer.Sound('sounds/player_heal.wav')
# sound_boss_death = pygame.mixer.Sound('sounds/boss_death.wav')
sound_level_up = pygame.mixer.Sound('sounds/level_up.wav')
print("Sounds loaded.")
print("Increasing sound channels...")  # pygame defaults to 8, but we need more
pygame.mixer.set_num_channels(32)
print("Sound channels increased.")

print("Initializing game clock...")
clock = pygame.time.Clock()
done = False

# lists to draw
stars = []
player_projectiles = []
boss_projectiles = []
enemy_units = []


print("Seeding starfield...")
for i in range(starfield_size):
    stars.append(Star())

# player = Ship("ships/73180.png", 3, 0, 28, 32, (163, 73, 164), 3)
# player.flip_h()
# player = Ship("ships/ships_3.png", 1, 585, 310, 150, (38, 37, 37), 0.25)
player = Ship("sprites/mjd-player.png", 0, 0, 58, 23, None, 1.4)
player.type = MOB_TYPE_PLAYER
player.max_hp = 15
player.hp = player.max_hp
player.x = 100


# boss = Ship("ships/)
boss = Ship("ships/ships_3.png", 1, 1, 310, 150, (38, 37, 37), 1)
boss.type = MOB_TYPE_BOSS
boss.level = 1
boss.max_hp = BOSS_BASE_HEALTH
boss.hp = boss.max_hp
load_boss()
# boss.flip_h()
# boss.name = "Spike"

# galaxy1 = load_image("ships/galaxy1.png", 0, 0, 1624, 1370, None, 0.5)
# https://www.pngmart.com/image/37328/png/37327
galaxy1 = load_image("ships/galaxy2.png", 0, 0, 800, 424, None, 0.25)
galaxy1x = width - galaxy1.get_width()
galaxy1vx = 1/30

meatball = load_image("sprites/jwd-meatball.png")
noodle = load_image("ships/macaroni.png", 0, 0, 1293, 1010, None, 0.03)
controls = load_image("sprites/jwd-move.png")


# boss.flip_h()
boss.x = boss_start_position()
boss.y = height/2

# Begin main loop
while not done:

    # check the game state and perform the appropriate actions
    if game_state == "title":
        run_title_screen()

    elif game_state == "game":
        update_game()
        draw_screen()

    elif game_state == "victory":
        run_victory_screen()

    elif game_state == "level_up":
        run_level_up_screen()

    elif game_state == "game_over":
        run_game_over_screen()

    elif game_state == "start_level":
        run_start_level_screen()

    elif game_state == "quit":
        done = True

    # increment the frame counter
    frame_counter += 1

    # if the game state changes record the frame counter
    if game_state != last_game_state:
        last_game_state = game_state
        state_start_frame = frame_counter

    # console the frame rate
    if(frame_counter % 60 == 0):
        print("Frame rate: " + str(round(clock.get_fps())) +
              ", Game State: " + game_state)

    # limit to 60 frames per second
    clock.tick(60)

# quit pygame and clean up
pygame.quit()
