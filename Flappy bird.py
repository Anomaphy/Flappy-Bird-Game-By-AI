import neat
import pygame
import os
import random

pygame.font.init()
# WINDOW SIZE
WIN_WIDTH = 490
WIN_HEIGHT = 650
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
# LOADING IMAGES OF BIRD, PILLARS AND ANIMATED BIRDS
DIR = os.path.dirname(os.path.realpath(__file__))
IMAGES_DIRECTORY = os.path.join(DIR, "imgs")

BIRD_IMAGES = [(pygame.image.load(os.path.join(IMAGES_DIRECTORY, "bird1.png"))),
               (pygame.image.load(os.path.join(IMAGES_DIRECTORY, "bird2.png"))),
               (pygame.image.load(os.path.join(IMAGES_DIRECTORY, "bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join(IMAGES_DIRECTORY, "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join(IMAGES_DIRECTORY, "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join(IMAGES_DIRECTORY, "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

gen = 0
# BIRD IMAGE BASIC
class Bird:
    IMAGES = BIRD_IMAGES
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 3

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMAGES[0]

    # PLANE OF GAME WORKS DIFFERENTLY SO NEGATIVE HEIGHT MAKES IT GO UP
    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    # PHYSICS
    def move(self):
        self.tick_count += 1

        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2

        # WON'T LET BIRD GO DOWN TOO MUCH
        if d >= 16:
            d = 16
        # WON'T LET BIRD STAY STAGNANT AND FALL
        if d < 0:
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        # Displaying images as it is animated
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMAGES[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMAGES[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMAGES[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMAGES[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMAGES[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMAGES[1]
            self.img_count = self.ANIMATION_TIME * 2

            # Rotates image on the plane and positions it
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 460)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # Making sure that the small image of base circles again and again

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, gen):
    if gen == 0:
        gen = 1

    # Draws image
    win.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win)

    for bird in birds:
        bird.draw(win)

    score_label = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen - 1), 1, (255, 255, 255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)), 1, (255, 255, 255))
    win.blit(score_label, (10, 50))

    pygame.display.update()


# It is going to take all the virtual dna and evaluate
def main(genomes, config):
    global WIN, gen
    gen += 1
    # Neural networks
    nets = []
    # Genomes
    ge = []
    # Birds
    birds = []

    # Genome is a tuple
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(150, 200))
        g.fitness = 0
        ge.append(g)

    pipes = [Pipe(500)]
    base = Base(550)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    running = True
    while running:
        clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
                break

        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_index = 1

        else:
            running = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.15
            # This basically calculates gap between two pillars for neural network
            output = nets[birds.index(bird)].activate(
                (bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].bottom)))

            if output[0] > 0.5:
                bird.jump()
        base.move()

        add_pipe = False
        rem = []

        for pipe in pipes:
            pipe.move()
            # REMOVING THE BIRDS WHO DON'T QUALIFY
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[birds.index(bird)].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

        if add_pipe:
            score += 1
            # Reward system so birds are motivated to go through the pipes
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(425))

        for r in rem:
            pipes.remove(r)

        # TRY BY REMOVING OR STATEMENT( or bird.y < 0)
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 550 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        draw_window(win, birds, pipes, base, score, gen)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    # Statistics for how good is next generation

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 60)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
