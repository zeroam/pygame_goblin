import random
import pygame
from abc import ABC, abstractmethod

from settings import data_dir


class Character(ABC):
    def __init__(self, x, y, width, height, vel):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel = vel
        self.walkCount = 0

    @abstractmethod
    def draw(self, window):
        """Draw character"""
        pass

    @abstractmethod
    def hit(self):
        """Action when hitted"""
        pass


class Player(Character):
    standing = pygame.image.load(str(data_dir / "standing.png"))
    walkRight = [pygame.image.load(str(data_dir / f"R{i}.png")) for i in range(1, 10)]
    walkLeft = [pygame.image.load(str(data_dir / f"L{i}.png")) for i in range(1, 10)]

    def __init__(self, x, y, width, height, vel=5):
        super().__init__(x, y, width, height, vel)
        self.isJump = False
        self.left = False
        self.right = False

        self.walkCount = 0
        self.jumpCount = 10
        self.lives = 3

        self.hitbox = (self.x + 17, self.y + 11, 29, 52)

    def draw(self, win):
        if self.walkCount + 1 >= 27:
            self.walkCount = 0

        if self.left:
            win.blit(self.walkLeft[self.walkCount // 3], (self.x, self.y))
            self.walkCount += 1
        elif self.right:
            win.blit(self.walkRight[self.walkCount // 3], (self.x, self.y))
            self.walkCount += 1
        else:
            win.blit(self.standing, (self.x, self.y))

        self.hitbox = (self.x + 17, self.y + 11, 29, 52)
        pygame.draw.rect(win, (255, 0, 0), self.hitbox, 2)

    def hit(self, win):
        width, height = win.get_size()

        self.isJump = False
        self.jumpCount = 10
        self.x = random.randint(0, width - self.width)
        self.y = height - 105
        self.walkCount = 0

        font = pygame.font.SysFont("comicsans", 100)
        text = font.render("-1", 1, (255, 0, 0))
        win.blit(text, (250 - (text.get_width() // 2), 200))
        pygame.display.update()

        self.lives -= 1

        i = 0
        while i < 100:
            pygame.time.delay(10)
            i += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    i = 301
                    pygame.quit()


class Enemy(Character):
    walkRight = [pygame.image.load(str(data_dir / f"R{i}E.png")) for i in range(1, 12)]
    walkLeft = [pygame.image.load(str(data_dir / f"L{i}E.png")) for i in range(1, 12)]

    def __init__(self, x, y, width, height, end, vel=3):
        super().__init__(x, y, width, height, vel)
        self.end = end
        self.path = [self.x, self.end]
        self.hitbox = (self.x + 17, self.y + 2, 31, 57)
        self.health = 10

    def draw(self, win):
        self.move()

        if self.walkCount + 1 >= 33:
            self.walkCount = 0

        if self.vel > 0:
            win.blit(self.walkRight[self.walkCount // 3], (self.x, self.y))
            self.walkCount += 1
        else:
            win.blit(self.walkLeft[self.walkCount // 3], (self.x, self.y))
            self.walkCount += 1

        self.hitbox = (self.x + 17, self.y + 2, 31, 57)
        pygame.draw.rect(win, (255, 0, 0), (self.hitbox[0], self.hitbox[1] - 20, 50, 10))
        pygame.draw.rect(win, (0, 128, 0), (self.hitbox[0], self.hitbox[1] - 20, self.health * 5, 10))
        pygame.draw.rect(win, (255, 0, 0), self.hitbox, 2)

    def move(self):
        if self.vel > 0:
            if self.x + self.vel < self.path[1]:
                self.x += self.vel
            else:
                self.vel = self.vel * -1
                self.walkCount = 0
        else:
            if self.x - self.vel > self.path[0]:
                self.x += self.vel
            else:
                self.vel = self.vel * -1
                self.walkCount = 0

    def hit(self):
        if self.health > 0:
            self.health -= 1


class Projectile(object):
    def __init__(self, x, y, radius, color, facing):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.facing = facing
        self.vel = 8 * facing
        self.remove = False

    def draw(self, win):
        self.move(win)

        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)

    def move(self, win):
        width, _ = win.get_size()
        if self.x < width and self.x > 0:
            self.x += self.vel
        else:
            self.remove = True
