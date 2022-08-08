#!/usr/bin/env python3

# sprite resources: https://www.spriters-resource.com/snes/superrtype/

# Create a 2d game space ship shmup with pygame
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
        self.x -= self.speed * background_speed

        if(self.x < 0 - self.speed):
            self.x = width + self.speed
            self.y = random.randint(0, height)

    def draw(self):
        pygame.draw.circle(
            screen,
            (self.r, self.g, self.b),
            (self.x, self.y),
            self.size
        )


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
        self.max_hp = 300
        self.level = 1
        self.weapon_level = 1
        self.defense_level = 1

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


def constrain(value, low, high):
    if(value < low):
        value = low
    if(value > high):
        value = high
    return value


def handle_boss_logic():
    global boss

    # control the bosses movement
    if (frame_counter % 60 == 0):
        boss.vx += random.randint(-2, 2)
        boss.vy += random.randint(-2, 2)

        boss.vx = constrain(boss.vx, -5, 5)
        boss.vy = constrain(boss.vy, -5, 5)

    # control the bosses shooting
    if(frame_counter % 10 == 0):
        if (random.randint(0, 100) < 50):
            boss_shoot()


def player_shoot():
    global player_projectiles

    # perform basic attack
    player_projectiles.append(
        Projectile(
            player.x + player.w * player.scale / 2,
            player.y + player.h * player.scale / 2,
            20,
            0,
            1+player.weapon_level,
            (0, 0, 255),
            3
        )
    )

    # player level 2 weapon
    if player.weapon_level >= 2:
        # aim vx and vy at the boss
        if player.x > boss.x:
            vx = random.randint(-20, 0)
        else:
            vx = random.randint(0, 20)

        if player.y > boss.y:
            vy = random.randint(-20, 0)
        else:
            vy = random.randint(0, 20)

        if abs(vx) > abs(vy):
            if vy >= 0:
                vy = 20 - abs(vx)
            else:
                vy = -20 + abs(vx)
        else:
            if vx >= 0:
                vx = 20 - abs(vy)
            else:
                vx = -20 + abs(vy)

        player_projectiles.append(
            Projectile(
                player.x + player.w * player.scale / 2,
                player.y + player.h * player.scale / 2,
                vx,
                vy,
                1,
                (0, 255, 255),
                3
            )
        )


def boss_shoot():
    global boss_projectiles

    # shoot a projectile from the boss straight ahead
    boss_projectiles.append(
        Projectile(
            boss.x + boss.w * boss.scale / 2,
            boss.y + boss.h * boss.scale / 2,
            -10,
            0,
            5 * boss.level,
            (255, 0, 255),
            15
        )
    )

    if boss.level >= 2:
        # shoot a projectile from the boss in a random direction towards the player
        if boss.x > player.x:
            vx = random.randint(-5, 1)
        else:
            vx = random.randint(1, 5)

        if boss.y > player.y:
            vy = random.randint(-5, 1)
        else:
            vy = random.randint(1, 5)

        boss_projectiles.append(
            Projectile(
                boss.x + boss.w * boss.scale / 2,
                boss.y + boss.h * boss.scale / 2,
                vx,
                vy,
                2 * boss.level,
                (255, 180, 0),
                7

            )
        )

    if boss.level >= 3:
        # shoot a projectile from the boss in a random direction towards the player
        # shoot a projectile from the boss in a random direction towards the player
        if boss.x > player.x:
            vx = random.randint(-7, 1)
        else:
            vx = random.randint(1, 7)

        if boss.y > player.y:
            vy = random.randint(-7, 1)
        else:
            vy = random.randint(1, 7)

        boss_projectiles.append(
            Projectile(
                boss.x + boss.w * boss.scale / 2,
                boss.y + boss.h * boss.scale / 2,
                vx,
                vy,
                4 * boss.level,
                (0, 255, 0),
                4
            )
        )


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

    return distance < projectile_r


def collide():
    for projectile in player_projectiles:
        # check if the projectile x y is within the boss x y + w h
        #        if(projectile.x > boss.x and projectile.x < boss.x + boss.w * boss.scale and projectile.y > boss.y and projectile.y < boss.y + boss.h * boss.scale):
        if(projectile_hits_ship(projectile, boss)):
            # play the player hit sound
            pygame.mixer.Sound.play(sound_player_hit)
            boss.hp -= projectile.damage
            player_projectiles.remove(projectile)

    # collide boss projectiles with the player
    for projectile in boss_projectiles:
        # check if the projectile x y is within the player x y + w h
        # if(projectile.x > player.x and projectile.x < player.x + player.w * player.scale and projectile.y > player.y and projectile.y < player.y + player.h * player.scale):
        if(projectile_hits_ship(projectile, player)):
            # play the boss hit sound effect
            pygame.mixer.Sound.play(sound_boss_hit)
            player.hp -= projectile.damage
            boss_projectiles.remove(projectile)


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
        boss.vx = -boss.vx
        boss.vy = -boss.vy

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
        boss_projectiles = []
        player_projectiles = []

    # check for level up
    if boss.hp <= 0:
        # play the boss death sound
        pygame.mixer.Sound.play(sound_boss_death)

        game_state = "level_up"
        # clear active projectiles from the board
        boss_projectiles = []
        player_projectiles = []
        boss.level += 1
        player.level += 1
        boss.max_hp *= 1.5
        boss.hp = boss.max_hp
        player.hp = constrain(player.hp + 10, 0, player.max_hp)
        boss.x = width - 100
        boss.y = height / 2 - 100

    # background_speed *= 1.04
    # if background_speed > 8:
    #     background_speed = 8


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

    # draw the player projectiles
    for projectile in player_projectiles:
        projectile.draw()

    # draw the boss projectiles
    for projectile in boss_projectiles:
        projectile.draw()

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
            (player.w * player.scale) * (player.hp / player.max_hp),
            10
        )
    )
    # draw the score line
    text_score_line = font.render(
        "Level: " + str(player.level) +
        "  Weapon: " + str(player.weapon_level) +
        "  HP: " + str(player.hp) + "/" + str(player.max_hp), True, (255, 255, 255))

    screen.blit(text_score_line, (0, 680))

    # update the screen
    pygame.display.flip()


def run_title_screen():
    global game_state

    handle_game_events()

    # draw a starry background
    screen.fill((0, 0, 0))

    move_starfield()

    # draw the stars
    for star in stars:
        star.draw()

    screen.blit(text_title_start,
                (width / 2 - text_title_start.get_width()/2,
                 height / 2 - text_title_start.get_height()/2))

    # check for key press of space
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        game_state = "game"

    # check for a key press of escape
    if keys[pygame.K_ESCAPE]:
        game_state = "quit"

    # update the screen
    pygame.display.flip()


def run_game_over_screen():
    global game_state, player, boss

    handle_game_events()

    # draw a starry background
    screen.fill((0, 0, 0))

    move_starfield()

    # draw the stars
    for star in stars:
        star.draw()

    screen.blit(text_ship_destroyed,
                (width / 2 - text_ship_destroyed.get_width()/2,
                 height / 2 - text_ship_destroyed.get_height()/2 - 125))

    screen.blit(text_journey_again,
                (width / 2 - text_journey_again.get_width()/2,
                 height / 2 - text_journey_again.get_height()/2))

    screen.blit(text_quit_key,
                (width / 2 - text_quit_key.get_width()/2,
                    height / 2 - text_quit_key.get_height()/2 + 50))

    # check for enter key to start a new game
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RETURN]:
        player.hp = player.max_hp
        boss.hp = boss.max_hp
        player.x = 100
        player.y = height / 2 - player.h * player.scale / 2
        boss.x = width - boss.w * boss.scale - 100
        boss.y = height / 2 - boss.h * boss.scale / 2

        game_state = "game"

    # check for a key press of escape
    if keys[pygame.K_ESCAPE]:
        game_state = "quit"

    # update the screen
    pygame.display.flip()


def run_level_up_screen():
    global game_state, player, boss

    handle_game_events()

    # draw a starry background
    screen.fill((0, 0, 0))

    move_starfield()

    # draw the stars
    for star in stars:
        star.draw()

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

    # check for a key press of either enter or tab to start the next level
    if keys[pygame.K_RETURN] or keys[pygame.K_TAB]:
        player.x = 100
        player.y = height / 2 - player.h * player.scale / 2
        boss.x = width - boss.w * boss.scale - 100
        boss.y = height / 2 - boss.h * boss.scale / 2
        game_state = "game"

    # check for a key press of escape
    if keys[pygame.K_ESCAPE]:
        game_state = "quit"

    # update the screen
    pygame.display.flip()


# start the game
print("Starting game...")
pygame.init()
print("pygame.init() complete. Setting up screen...")
screen = pygame.display.set_mode((width, height+60))
pygame.display.set_caption(
    "Magnetek Engineering Society: Operation Fractured Sky")
print("Screen setup complete.")

print("Generating font objects...")
font = pygame.font.SysFont(None, 48)
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
sound_boss_death = pygame.mixer.Sound('sounds/boss_death.wav')

print("Initializing game clock...")
clock = pygame.time.Clock()
done = False

# lists to draw
stars = []
player_projectiles = []
boss_projectiles = []

print("Seeding starfield...")
for i in range(300):
    stars.append(Star())

# player = Ship("ships/73180.png", 3, 0, 28, 32, (163, 73, 164), 3)
# player.flip_h()
player = Ship("ships/ships_3.png", 1, 585, 310, 150, (38, 37, 37), 0.25)
player.max_hp = 15
player.hp = player.max_hp
player.x = 100


# boss = Ship("ships/)
boss = Ship("ships/ships_3.png", 1, 1, 310, 150, (38, 37, 37), 1)
boss.max_hp = 100
boss.hp = boss.max_hp

boss.flip_h()
boss.x = 1000
boss.y = height/2


while not done:

    # check the game state and perform the appropriate actions
    if game_state == "title":
        run_title_screen()

    elif game_state == "game":
        update_game()
        draw_screen()

    elif game_state == "level_up":
        run_level_up_screen()

    elif game_state == "game_over":
        run_game_over_screen()

    elif game_state == "quit":
        done = True

    # increment the frame counter
    frame_counter += 1

    # console the frame rate
    if(frame_counter % 100 == 0):
        print("Frame rate: " + str(round(clock.get_fps())) +
              ", Game State: " + game_state)

    # limit to 60 frames per second
    clock.tick(60)

# quit pygame and clean up
pygame.quit()
