#!/usr/bin/env python3

# sprite resources: https://www.spriters-resource.com/snes/superrtype/

# Create a 2d game space ship shmup with pygame
import pygame
import random

width = 1280
height = 720
ship_speed = 9
bgspeed = 1.0
frame_counter = 0
frame_last_shot = 0

# classes


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
        self.x -= self.speed * bgspeed

        if(self.x < 0 - self.speed):
            self.x = width + self.speed
            self.y = random.randint(0, height)

    def draw(self):
        pygame.draw.circle(screen, (self.r, self.g, self.b),
                           (self.x, self.y), self.size)


class Ship:
    def __init__(self, sprite, x, y, w, h, color_key=None, scale=1):
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

# load a part of an image from a file to be used as a sprite frame


class Projectile:
    def __init__(self, x, y, vx, vy, damage, color, radius):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.color = color
        self.radius = radius

    def move(self):
        self.x += self.vx
        self.y += self.vy

        if(self.x < 0 or self.x > width or self.y < 0 or self.y > height):
            return True
        else:
            return False

    def draw(self):
        pygame.draw.circle(screen, self.color,
                           (self.x, self.y), self.radius)


def load_image(filename, x, y, w, h, color_key=None, scale=1):
    image = pygame.image.load(filename)
    image = image.subsurface(x, y, w, h)
    image = pygame.transform.scale(image, (int(w * scale), int(h * scale)))
    if(color_key is not None):
        image.set_colorkey(color_key)
    return image


def move_starfield():
    for star in stars:
        star.move()


def move_projectiles():
    global player_projectiles

    # handle player projectiles
    for projectile in player_projectiles:
        if(projectile.move()):
            player_projectiles.remove(projectile)


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


def constrain(value, low, high):
    if(value < low):
        value = low
    if(value > high):
        value = high
    return value


def handle_boss_logic():
    global boss

    if (frame_counter % 60 == 0):
        boss.vx += random.randint(-2, 2)
        boss.vy += random.randint(-2, 2)

        boss.vx = constrain(boss.vx, -5, 5)
        boss.vy = constrain(boss.vy, -5, 5)


def player_shoot():
    global player_projectiles
    player_projectiles.append(
        Projectile(
            player.x + player.w * player.scale / 2,
            player.y + player.h * player.scale / 2,
            12,
            0,
            1,
            (255, 0, 0),
            3
        )
    )


def collide():
    # collide player projectiles with the boss
    global player_projectiles, boss

    for projectile in player_projectiles:
        # check if the projectile x y is within the boss x y + w h
        if(projectile.x > boss.x and projectile.x < boss.x + boss.w * boss.scale and projectile.y > boss.y and projectile.y < boss.y + boss.h * boss.scale):
            boss.hp -= projectile.damage
            player_projectiles.remove(projectile)


def update_game():
    # move the stars
    move_starfield()

    handle_game_events()
    handle_game_inputs()
    handle_boss_logic()

    # move the player ship
    player.move()

    # move the boss and bounce off edges
    if boss.move():
        boss.vx = -boss.vx
        boss.vy = -boss.vy

    # move the projectiles
    move_projectiles()

    # calculate collisions
    collide()

    # bgspeed *= 1.04
    # if bgspeed > 8:
    #     bgspeed = 8


def draw_screen():
    # draw a starry background
    screen.fill((0, 0, 0))
    # draw the stars
    for star in stars:
        star.draw()

    # draw the ship
    player.draw()

    # draw the boss
    boss.draw()

    # draw the projectiles
    for projectile in player_projectiles:
        projectile.draw()

    # draw the boss hp as a bar on the screen below the boss
    pygame.draw.rect(screen, (255, 0, 0), (boss.x, boss.y +
                     boss.h * boss.scale, boss.hp, 10))
    # pygame.draw.rect(screen, (255, 0, 0), (0, 0, boss.hp, 10))

    # update the screen
    pygame.display.flip()


# make a star class to store their position, speed and color
pygame.init()
screen = pygame.display.set_mode((1280, 720))

pygame.display.set_caption("Fractured Sky")
clock = pygame.time.Clock()
done = False

# create a list of stars
stars = []
player_projectiles = []
boss_projectiles = []

for i in range(300):
    stars.append(Star())

# player = Ship("ships/73180.png", 3, 0, 28, 32, (163, 73, 164), 3)
# player.flip_h()
player = Ship("ships/ships_3.png", 1, 585, 310, 150, (38, 37, 37), 0.25)

# boss = Ship("ships/)
boss = Ship("ships/ships_3.png", 1, 1, 310, 150, (38, 37, 37), 1)
boss.flip_h()
boss.x = 1000
boss.y = height/2


while not done:
    update_game()
    draw_screen()

    # increment the frame counter
    frame_counter += 1

    # limit to 60 frames per second
    clock.tick(60)

# quit pygame and clean up
pygame.quit()
