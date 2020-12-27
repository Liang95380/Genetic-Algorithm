import pygame
import os
import neat
import time
import random
import clock


# Window Size
WIN_WIDTH = 400
WIN_HEIGHT = 800


# Import Images
pic = pygame.image.load(os.path.join("imgs", "piplup.png"))
PIPLUP_IMGS = pygame.transform.scale(pic, (88, 68))
pic2 = pygame.image.load(os.path.join("imgs", "bg.jpg"))
BG_IMGS = pygame.transform.scale(pic2, (400, 800))
pic3 = pygame.image.load(os.path.join("imgs", "charmander.png"))
CHARMANDER_IMG = pygame.transform.scale(pic3, (88, 68))
pic4 = pygame.image.load(os.path.join("imgs", "fire.png"))
FIRE_IMG = pygame.transform.scale(pic4, (110, 90))

class Piplup:

    IMG = PIPLUP_IMGS

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel = 0

    def draw(self, win):
        win.blit(self.IMG, (self.x, self.y))

    def move_left(self):
        self.vel = 50
        self.x = self.x - self.vel

    def move_right(self):
        self.vel = 50
        self.x = self.x + self.vel

    def get_mask(self):  # To get mask of the bird for collision
        return pygame.mask.from_surface(self.IMG)


class Enemy:

    IMG = CHARMANDER_IMG

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.movement = 0

    def draw(self, win):
        win.blit(self.IMG, (self.x, self.y))

    def move(self):
        self.movement = random.randrange(-50, 50)
        self.x = self.x + self.movement

        if self.x < 20:
            self.movement = random.randrange(0, 50)
            self.x = self.x + self.movement

        elif self.x + self.IMG.get_width() >= 380:
            self.movement = random.randrange(-50, 0)
            self.x = self.x + self.movement


class Projectile:

    IMG = FIRE_IMG

    def __init__(self, x):
        self.vel = 0
        self.x = x
        self.y = 150
        self.vel = 10
        self.passed = False

    def draw(self, win):
        win.blit(self.IMG, (self.x, self.y))

    def move(self):
        self.y += self.vel

    def collide(self, piplup):
        piplup_mask = piplup.get_mask()
        projectile_mask = pygame.mask.from_surface(self.IMG)

        offset = (self.x - piplup.x, self.y - round(piplup.y))

        point = piplup_mask.overlap(projectile_mask, offset)  # Return True if overlapped

        if point:
            return True

        return False


def draw_window(win, piplup, charmander, projectiles):
    win.blit(BG_IMGS, (0, 0))
    piplup.draw(win)
    charmander.draw(win)

    for projectile in projectiles:
        projectile.draw(win)

    pygame.display.update()

def main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    clock = pygame.time.Clock()

    piplup = Piplup(170, 560)
    charmander = Enemy(170, 60)
    projectiles = [Projectile(random.randrange(50, 350))]

    run = True

    while run:

        charmander.move()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()  # sys.exit() if sys is imported
                quit()
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    piplup.move_left()

                elif event.key == pygame.K_RIGHT:
                    piplup.move_right()

        # To check whether the fire hit penguin
        for projectile in projectiles:

            if projectile.passed is False and projectile.y + projectile.IMG.get_height() > 560:
                projectile.passed = True

            if projectile.collide(piplup):
                print("Die")

            projectile.move()

        if projectile.passed:
            projectiles.append(Projectile(random.randrange(0, 320)))




        clock.tick(30)
        draw_window(win, piplup, charmander, projectiles)


main()