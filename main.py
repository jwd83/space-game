#!/usr/bin/env python3

# sprite resources: https://www.spriters-resource.com/snes/superrtype/

# Create a 2d game space ship shmup with pygame
import pygame
import random

width = 1280
height = 720
bgspeed = 1.0

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
    def __init__(self):
        self.w = 32
        self.h = 32
        self.x = width/2
        self.y = height/2
        self.vx = 0
        self.vy = 0

    def move(self):
        self.x += self.vx
        self.y += self.vy

        if(self.x < 0):
            self.x = 0
        if(self.x > width):
            self.x = width

        if(self.y < 0):
            self.y = 0
        if(self.y > height):
            self.y = height


# load a part of an image from a file to be used as a sprite frame
def load_image(filename, x1, y1, x2, y2):
    image = pygame.image.load(filename)
    image = image.subsurface(x1, y1, x2, y2)
    return image


def draw_screen():
    # draw a starry background
    screen.fill((0, 0, 0))
    # draw the stars
    for star in stars:
        star.draw()

    # update the screen
    pygame.display.flip()


# make a star class to store their position, speed and color
pygame.init()
screen = pygame.display.set_mode((1280, 720))

pygame.display.set_caption("Space Ship")
clock = pygame.time.Clock()
done = False

# create a list of stars
stars = []
for i in range(100):

    star = Star()
    stars.append(star)


while not done:
    # check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # move the stars
    for star in stars:
        star.move()

    draw_screen()
    # bgspeed *= 1.04
    # if bgspeed > 8:
    #     bgspeed = 8

    # limit to 60 frames per second
    clock.tick(60)


# quit pygame and clean up
pygame.quit()
