import pygame
import os
import neat
import time
import random
import clock
pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
import pickle

# Window Size
WIN_WIDTH = 500
WIN_HEIGHT = 800


# Import Images
pic = pygame.image.load(os.path.join("imgs", "piplup.png"))
PIPLUP_IMGS = pygame.transform.scale(pic, (70, 50))
pic2 = pygame.image.load(os.path.join("imgs", "bg.jpg"))
BG_IMGS = pygame.transform.scale(pic2, (500, 800))
pic3 = pygame.image.load(os.path.join("imgs", "charmander.png"))
CHARMANDER_IMG = pygame.transform.scale(pic3, (88, 68))
pic4 = pygame.image.load(os.path.join("imgs", "fire.png"))
FIRE_IMG = pygame.transform.scale(pic4, (70, 50))

gen = 0

class Piplup:

    IMG = PIPLUP_IMGS

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel = 0

    def draw(self, win):
        win.blit(self.IMG, (self.x, self.y))

    def move(self, dir):
        if self.x != 100:
            if dir == "left":
                self.move_left()
        if self.x != 300:
            if dir == "right":
                self.move_right()

    def move_left(self):
        self.vel = 100
        self.x = self.x - self.vel

    def move_right(self):
        self.vel = 100
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
        self.y = 100
        self.vel = 5
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


def draw_window(win, piplups, charmander, projectiles, score):
    win.blit(BG_IMGS, (0, -20))

    for piplup in piplups:
        piplup.draw(win)

    charmander.draw(win)

    #score
    score_label = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen - 1), 1, (255, 255, 255))
    win.blit(score_label, (10, 10))

    for projectile in projectiles:
        projectile.draw(win)

    pygame.display.update()

def main(genomes, config):

    global gen
    gen += 1

    nets = []  # To initialize list to store all the neural network
    ge = []  # To initialize a list to store all the genomes
    piplups = []  # To initialize a list to store all the piplups
    score = 0
    positions = [100, 200, 300]


    for _, g in genomes:  # Create (N numbers of population) neural networks and birds
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        piplups.append(Piplup(200, 560))  # To initialize all birds starting position
        g.fitness = 0
        ge.append(g)

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    clock = pygame.time.Clock()


    charmander = Enemy(170, 60)
    projectiles = [Projectile(random.choice(positions))]


    run = True

    while run:

        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()  # sys.exit() if sys is imported
                quit()
                break

        for projectile in projectiles:
            for x, piplup in enumerate(piplups):

                if projectile.passed is False and projectile.y + projectile.IMG.get_height() > 560:
                    projectile.passed = True
                    ge[x].fitness += 5
                    projectiles.append(Projectile(random.choice(positions)))
                    score += 1


                if projectile.collide(piplup):
                    ge[x].fitness -= 1
                    piplups.pop(x)
                    nets.pop(x)
                    ge.pop(x)

        for projectile in projectiles:
            for x, piplup in enumerate(piplups):

                projectile.move()

                ge[x].fitness += 0.1
                output = nets[x].activate((piplup.x, piplup.y, projectile.x, projectile.y, abs(piplup.y - projectile.y), abs(piplup.x - projectile.x)))

                if output[0] > 0.5:

                    piplup.move("right")
                    ge[x].fitness -= 0.1

                if output[1] > 0.5:

                    piplup.move("left")
                    ge[x].fitness -= 0.1

        print(len(piplups))



        #  If all birds die, then break while loop to run next generation
        if len(piplups) <= 0:
            run = False
            break

        if score > 100:
            pickle.dump(nets[0], open("best.pickle", "wb"))
            break

        draw_window(win, piplups, charmander, projectiles, score)


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(main, 1000)





if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)