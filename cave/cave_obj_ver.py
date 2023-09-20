import sys
from random import randint
import pygame
from pygame.locals import QUIT, Rect, KEYDOWN, K_SPACE

# game constants
SCREENRECT = pygame.Rect(0, 0, 800, 600)
SCORE = 0

img_path = "./images/"
ship_image = pygame.image.load(img_path + "ship.png")
bang_image = pygame.image.load(img_path + "bang.png")


class Player(pygame.sprite.Sprite):
    """Representing the player as a spaceship."""
    images = [ship_image]

    def __init__(self, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midleft=SCREENRECT.midleft)
        self.origleft = self.rect.left
        self.ship_y = 250
        self.velocity = 0

    def move(self, is_space_up):
        self.velocity += -1 if is_space_up else 1
        self.rect.move_ip(0, self.velocity)
        self.rect = self.rect.clamp(SCREENRECT)
        self.rect.left = self.origleft


class Wall(pygame.sprite.Sprite, pygame.sprite.LayeredUpdates):
    speed = 10
    walls = 80
    slope = randint(1, 6)
    upper_bottom = 100
    lower_top = 500
    init_walls = [(i * 10, rect_y, 10, 100) for i in range(walls) for rect_y in (0, 500)]

    def __init__(self, position, *groups):
        _, _, w, h = position
        pygame.sprite.Sprite.__init__(self, *groups)
        self.image = pygame.Surface((10, h))
        self.image.fill((0, 225, 0))
        self.rect = Rect(position)
        self.facing = -1 * Wall.speed

    @classmethod
    def create(clf):
        if clf.upper_bottom < 10 or clf.lower_top > 590:
            clf.slope = randint(3, 6) * (-1 if clf.slope > 0 else 1)
            clf.upper_bottom += 10
            clf.lower_top -= 10
        clf.upper_bottom += clf.slope
        clf.lower_top += clf.slope

    def update(self):
        self.rect.move_ip(self.facing, 0)
        if self.rect.right < 0:
            self.kill()


class Collision(pygame.sprite.Sprite):
    """A collision. Hopefully not the player!"""

    defaultlife = 1
    images = [bang_image]

    def __init__(self, actor, obstacle, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]

        self.rect = self.image.get_rect(center=(actor.rect.center[0] + 20, actor.rect.center[1] + 40))
        self.life = self.defaultlife

    def update(self):
        self.life -= 1
        if self.life == 0:
            self.kill()


class Score(pygame.sprite.Sprite):
    """to keep track of the score."""

    def __init__(self, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.font = pygame.font.Font(None, 36)
        self.color = (0, 0, 225)
        self.update()
        self.rect = self.image.get_rect().move(600, 20)

    def update(self):
        msg = f"score is {SCORE}"
        self.image = self.font.render(msg, True, self.color)


def main():
    pygame.init()
    pygame.key.set_repeat(5, 5)

    # Set the display mode
    winstyle = 0
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    # decorate the game window
    icon = pygame.transform.scale(Player.images[0], (32, 32))
    pygame.display.set_icon(icon)
    pygame.display.set_caption("Pygame Cave")
    pygame.mouse.set_visible(1)

    # create the background
    background = pygame.Surface(SCREENRECT.size)
    background.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    # Initialize Game Groups
    walls = pygame.sprite.Group()
    all = pygame.sprite.LayeredUpdates()

    # Create Some Starting Values
    FPSCLOCK = pygame.time.Clock()

    # Initialize our starting sprites
    global SCORE
    player = Player(all)
    for wall in Wall.init_walls:
        Wall(wall, walls, all)
    all.add(Score(all), all)

    while player.alive():
        is_space_up = False

        # get input
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    is_space_up = True

        # clear/erase the last drawn sprites
        all.clear(screen, background)

        # update all the sprites
        all.update()

        # handle player input
        SCORE += 10
        player.move(is_space_up)

        # Create new wall
        Wall.create()
        all.move_to_back(Wall((790, 0, 10, Wall.upper_bottom), walls, all))
        Wall((790, Wall.lower_top, 10, 600 - Wall.lower_top), walls, all)

        # Detect collisions between walls and player.
        for wall in pygame.sprite.spritecollide(player, walls, 0):
            Collision(player, wall, all)
            player.kill()

        # draw the scene
        dirty = all.draw(screen)
        pygame.display.update(dirty)

        # cap the framerate at 15fps. Also called 15HZ or 15 times per second.
        FPSCLOCK.tick(15)

    pygame.time.wait(1000)


if __name__ == '__main__':
    main()
