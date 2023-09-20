import sys
from random import randint
import pygame
from pygame.locals import QUIT, Rect, KEYDOWN, K_SPACE


def change(value: int, is_increased: bool, add: int, sub: int = 0) -> int:
    _value = value
    _value += add if is_increased else sub
    return _value


class Screen:
    width = 800
    height = 600
    rect = pygame.Rect(0, 0, width, height)


class Image:
    path = "./images/"
    ship = pygame.image.load(path + "ship.png")
    bang = pygame.image.load(path + "bang.png")


class Player(pygame.sprite.Sprite):
    """Representing the player as a spaceship."""
    images = [Image.ship]

    def __init__(self, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midleft=Screen.rect.midleft)
        self.origleft = self.rect.left
        self.ship_y = 250
        self.velocity = 0

    def move(self, is_space_up):
        self.velocity = change(self.velocity, is_space_up, -1, 1)
        self.rect.move_ip(0, self.velocity)
        self.rect = self.rect.clamp(Screen.rect)
        self.rect.left = self.origleft


class Wall(pygame.sprite.Sprite, pygame.sprite.LayeredUpdates):
    speed = 10
    slope = randint(1, 6)
    width = 10
    upper_bottom = 100
    lower_top = Screen.height - 100
    shrinkage = 10

    def __init__(self, position, *groups):
        _, _, w, h = position
        pygame.sprite.Sprite.__init__(self, *groups)
        self.image = pygame.Surface((10, h))
        self.image.fill((0, 225, 0))
        self.rect = Rect(position)
        self.facing = -1 * self.speed

    @staticmethod
    def build(rects, walls, all):
        for rect in rects:
            all.move_to_back(Wall(rect, walls, all))

    @classmethod
    def is_dismissed(cls):
        if cls.upper_bottom < cls.width or cls.lower_top > Screen.height - cls.width:
            return True
        return False

    @classmethod
    def create_init(cls):
        walls = Screen.width // cls.width
        init_walls = []
        for i in range(walls):
            init_walls.extend(cls.create(i * cls.width))
        return init_walls

    @classmethod
    def create_last(cls):
        shrinked = 0
        if cls.is_dismissed():
            cls.slope = randint(3, 6) * (-1 if cls.slope > 0 else 1)
            shrinked = cls.shrinkage
        cls.upper_bottom = change(cls.upper_bottom, True, cls.slope + shrinked)
        cls.lower_top = change(cls.lower_top, True, cls.slope - shrinked)
        return cls.create(Screen.width - cls.width)

    @classmethod
    def create(cls, rect_x: int):
        return [(rect_x, 0, cls.width, cls.upper_bottom),
                (rect_x, cls.lower_top, cls.width, Screen.height - cls.lower_top)]

    def update(self):
        self.rect.move_ip(self.facing, 0)
        if self.rect.right < 0:
            self.kill()


class Collision(pygame.sprite.Sprite):
    """A collision. Hopefully not the player!"""
    defaultlife = 1
    images = [Image.bang]

    def __init__(self, actor, obstacle, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]

        self.rect = self.image.get_rect(center=(actor.rect.center[0] + 20, actor.rect.center[1] + 40))
        self.life = self.defaultlife

    def update(self):
        self.life = change(self.life, True, -1)
        if self.life == 0:
            self.kill()


class Score(pygame.sprite.Sprite):
    """to keep track of the score."""
    score = 0
    addition = 10

    def __init__(self, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.font = pygame.font.Font(None, 36)
        self.color = (0, 0, 225)
        self.update()
        self.rect = self.image.get_rect().move(600, 20)

    def increase(self):
        self.score = change(self.score, True, self.addition)

    def update(self):
        msg = f"score is {self.score}"
        self.image = self.font.render(msg, True, self.color)


def main():
    pygame.init()
    pygame.key.set_repeat(5, 5)

    # Set the display mode
    winstyle = 0
    bestdepth = pygame.display.mode_ok(Screen.rect.size, winstyle, 32)
    screen = pygame.display.set_mode(Screen.rect.size, winstyle, bestdepth)

    # decorate the game window
    icon = pygame.transform.scale(Player.images[0], (32, 32))
    pygame.display.set_icon(icon)
    pygame.display.set_caption("Pygame Cave")
    pygame.mouse.set_visible(1)

    # create the background
    background = pygame.Surface(Screen.rect.size)
    background.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    # Initialize Game Groups
    walls = pygame.sprite.Group()
    all = pygame.sprite.LayeredUpdates()

    # Create Some Starting Values
    FPSCLOCK = pygame.time.Clock()

    # Initialize our starting sprites
    player = Player(all)
    Wall.build(Wall.create_init(), walls, all)
    score = Score(all)
    all.add(score, all)

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
        score.increase()
        player.move(is_space_up)

        # Create new wall
        Wall.build(Wall.create_last(), walls, all)

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
