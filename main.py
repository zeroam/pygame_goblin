import pygame
import random
from abc import ABC, abstractmethod
from pathlib import Path

base_dir = Path(__file__).parent.absolute()
data_dir = base_dir / "data"
print(data_dir / "standing.png")

# Initialize
pygame.init()

win = pygame.display.set_mode((500, 500))

pygame.display.set_caption("Goblin Game")

bg = pygame.image.load(str(data_dir / "bg.jpg"))
char = pygame.image.load(str(data_dir / "standing.png"))

bullet_sound = pygame.mixer.Sound(str(data_dir / "bullet.ogg"))
hit_sound = pygame.mixer.Sound(str(data_dir / "hit.ogg"))
music = pygame.mixer.music.load(str(data_dir / "music.mp3"))
pygame.mixer.music.play(-1)

clock = pygame.time.Clock()
score = 0


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
    walkRight = [pygame.image.load(str(data_dir / f"R{i}.png")) for i in range(1, 10)]
    walkLeft = [pygame.image.load(str(data_dir / f"L{i}.png")) for i in range(1, 10)]

    def __init__(self, x, y, width, height, vel=5):
        super().__init__(x, y, width, height, vel)
        self.isJump = False
        self.left = False
        self.right = False
        self.jumpCount = 10
        self.standing = True
        self.hitbox = (self.x + 17, self.y + 11, 29, 52)

    def draw(self, win):
        if self.walkCount + 1 >= 27:
            self.walkCount = 0

        if not self.standing:
            if self.left:
                win.blit(self.walkLeft[self.walkCount // 3], (self.x, self.y))
                self.walkCount += 1
            elif self.right:
                win.blit(self.walkRight[self.walkCount // 3], (self.x, self.y))
                self.walkCount += 1
        else:
            if self.right:
                win.blit(self.walkRight[0], (self.x, self.y))
            else:
                win.blit(self.walkLeft[0], (self.x, self.y))

        self.hitbox = (self.x + 17, self.y + 11, 29, 52)
        # pygame.draw.rect(win, (255, 0, 0), self.hitbox, 2)

    def hit(self):
        self.isJump = False
        self.jumpCount = 10
        self.x = 60
        self.y = 410
        self.walkCount = 0

        font = pygame.font.SysFont("comicsans", 100)
        text = font.render("-5", 1, (255, 0, 0))
        win.blit(text, (250 - (text.get_width() // 2), 200))
        pygame.display.update()

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
        self.visible = True

    def draw(self, win):
        if self.visible is False:
            return

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
        # pygame.draw.rect(win, (255, 0, 0), self.hitbox, 2)

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
            hit_sound.play()
            self.health -= 1

        if self.health == 0:
            self.visible = False


class Projectile(object):
    def __init__(self, x, y, radius, color, facing):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.facing = facing
        self.vel = 8 * facing

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)


def redrawGameWindow():
    win.blit(bg, (0, 0))
    text = font.render(f"Score: {score}", 1, (0, 0, 0))
    win.blit(text, (380, 10))

    man.draw(win)
    for goblin in goblins:
        goblin.draw(win)

    for bullet in bullets:
        bullet.draw(win)

    pygame.display.update()


# main loop
font = pygame.font.SysFont("comicsans", 30, True)
man = Player(300, 410, 64, 64)
goblins = []
bullets = []
shoot_loop = 0
enemy_loop = 0
dead_loop = 0
is_dead = False
run = True
while run:
    clock.tick(27)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if is_dead:
        dead_loop += 1

    if dead_loop > 30:
        dead_loop = 0
        is_dead = False

    if len(goblins) < 3:
        if enemy_loop == 0:
            start = random.randint(0, 100)
            end = random.randint(300, 450)
            goblins.append(Enemy(start, 410, 64, 64, end))
        enemy_loop += 1

    if enemy_loop > 30:
        enemy_loop = 0

    for goblin in goblins:
        if is_dead:
            break

        if man.hitbox[1] < goblin.hitbox[1] + goblin.hitbox[3] and man.hitbox[1] + man.hitbox[3] > goblin.hitbox[1]:
            if man.hitbox[0] + man.hitbox[2] > goblin.hitbox[0] and man.hitbox[0] < goblin.hitbox[0] + goblin.hitbox[2]:
                man.hit()
                score -= 5
                is_dead = True

    if shoot_loop > 0:
        shoot_loop += 1
    if shoot_loop > 5:
        shoot_loop = 0

    for i, bullet in enumerate(bullets):
        for goblin in goblins:
            if bullet.y + bullet.radius < goblin.hitbox[1] + goblin.hitbox[3] and bullet.y > goblin.hitbox[1]:
                if bullet.x > goblin.hitbox[0] and bullet.x + bullet.radius < goblin.hitbox[0] + goblin.hitbox[2]:
                    goblin.hit()
                    score += 1
                    bullets.pop(i)
                    if goblin.health == 0:
                        goblins.pop(goblins.index(goblin))

        if bullet.x < 500 and bullet.x > 0:
            bullet.x += bullet.vel
        else:
            bullets.pop(i)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE] and shoot_loop == 0:
        if len(bullets) < 5:
            facing = 1 if man.right else -1
            bullet_sound.play()
            bullets.append(Projectile(man.x + man.width // 2, man.y + man.height // 2, 6, (0, 0, 0), facing))

        shoot_loop = 1

    if keys[pygame.K_LEFT] and man.x >= man.vel:
        man.x -= man.vel
        man.left = True
        man.right = False
        man.standing = False
    elif keys[pygame.K_RIGHT] and man.x <= 500 - man.width - man.vel:
        man.x += man.vel
        man.right = True
        man.left = False
        man.standing = False
    else:
        man.standing = True
        man.walkCount = 0

    if not man.isJump:
        if keys[pygame.K_UP]:
            man.isJump = True
            man.right = False
            man.left = False
            man.walkCount = 0
    else:
        if man.jumpCount >= -10:
            neg = 1
            if man.jumpCount < 0:
                neg = -1
            man.y -= int((man.jumpCount ** 2) * 0.5 * neg)
            man.jumpCount -= 1
        else:
            man.isJump = False
            man.jumpCount = 10

    redrawGameWindow()

pygame.quit()
