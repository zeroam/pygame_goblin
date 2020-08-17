import time
import random
import pygame
from typing import List
import threading

from settings import data_dir
from character import Player, Enemy, Projectile


class Game(object):
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.score = 0
        self.time = 100

        self.win = None
        self.bg = None
        self.clock = None

        # sound
        self.bullet_sound = None
        self.bullet_sound_on = True
        self.hit_sound = None
        self.hit_sound_on = True

        # font
        self.font = None
        self.font_notify = None

        # characters
        self.man: Player = Player(300, self.height - 105, 64, 64)
        self.goblins: List[Enemy] = []
        self.bullets: List[Projectile] = []

        # loops
        self.shoot_loop = 0
        self.shoot_interval = 5
        self.enemy_loop = 0
        self.enemy_interval = 30
        self.dead_loop = 0
        self.dead_interval = 30
        self.is_dead = False

        # limits
        self.bullets_limit = 5
        self.enemies_limit = 3

    def initialize(self):
        pygame.init()

        # window
        self.win = pygame.display.set_mode((self.width, self.height))

        # background
        self.bg = pygame.image.load(str(data_dir / "bg.jpg"))

        # clock
        self.clock = pygame.time.Clock()

        # sound
        self.bullet_sound = pygame.mixer.Sound(str(data_dir / "bullet.ogg"))
        self.hit_sound = pygame.mixer.Sound(str(data_dir / "hit.ogg"))
        self.music = pygame.mixer.music.load(str(data_dir / "music.mp3"))
        pygame.mixer.music.play(-1)

        # font
        self.font = pygame.font.SysFont("comicsans", 30, True)
        self.font_notify = pygame.font.SysFont("comicsans", 50, True)

    def loop_check(self):
        # shoot loop
        if self.shoot_loop > 0:
            self.shoot_loop += 1

        if self.shoot_loop > self.shoot_interval:
            self.shoot_loop = 0

        # enemy loop
        # if self.enemy_loop > 0:
        #     self.enemy_loop += 1

        if self.enemy_loop > self.enemy_interval:
            self.enemy_loop = 0

        # dead loop
        if self.dead_loop > 0:
            self.dead_loop += 1

        if self.dead_loop > self.dead_interval:
            self.dead_loop = 0

    def handling_keys(self):
        man = self.man

        keys = pygame.key.get_pressed()

        # shoot bullet
        if keys[pygame.K_SPACE] and self.shoot_loop == 0:
            if len(self.bullets) < self.bullets_limit:
                facing = 1 if man.right else -1
                self.bullet_sound.play()
                self.bullets.append(Projectile(man.x + man.width // 2, man.y + man.height // 2, 6, (0, 0, 0), facing))

            self.shoot_loop = 1

        if keys[pygame.K_LEFT] and man.x >= man.vel:
            # move left
            man.x -= man.vel
            man.left = True
            man.right = False
        elif keys[pygame.K_RIGHT] and man.x <= self.width - man.width - man.vel:
            # move right
            man.x += man.vel
            man.right = True
            man.left = False
        else:
            man.walkCount = 0

        # jump
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


    def time_thread(self):
        while self.time > 0:
            time.sleep(1)
            self.time -= 1


    def redraw_game_window(self):
        win = self.win

        win.blit(self.bg, (0, 0))

        score_text = self.font.render(f"Score: {self.score}", 1, (0, 0, 0))
        win.blit(score_text, (self.width - 130, 10))
        time_text = self.font.render(f"TIME: {self.time}", 1, (0, 0, 0))
        win.blit(time_text, (self.width // 2 - 50, 10))

        # TIME OVER
        if self.time == 0:
            time_over_text = self.font_notify.render(f"TIME OVER", 1, (255, 0, 0))
            self.win.blit(time_over_text, (self.width // 2 - 100, 100))

        if self.dead_loop % 2 == 0:
            self.man.draw(win)

        for goblin in self.goblins:
            goblin.draw(win)

        for bullet in self.bullets:
            bullet.draw(win)

        pygame.display.update()

    def start(self):
        self.initialize()

        # time counting thread
        time_t = threading.Thread(target=self.time_thread, daemon=True)
        time_t.start()

        # main loop
        man = self.man
        run = True
        while run:
            self.clock.tick(27)

            # handling exit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            self.loop_check()

            # creates enemy
            if len(self.goblins) < self.enemies_limit:
                if self.enemy_loop == 0:
                    start = random.randint(0, 100)
                    end = random.randint(self.width - 150, self.width - 64)
                    self.goblins.append(Enemy(start, self.height - 100, 64, 64, end))
                self.enemy_loop += 1

            # goblins hit player
            for goblin in self.goblins:
                if self.dead_loop > 0 or self.time == 0:
                    break

                if man.hitbox[1] < goblin.hitbox[1] + goblin.hitbox[3] and man.hitbox[1] + man.hitbox[3] > goblin.hitbox[1]:
                    if man.hitbox[0] + man.hitbox[2] > goblin.hitbox[0] and man.hitbox[0] < goblin.hitbox[0] + goblin.hitbox[2]:
                        self.hit_sound.play()
                        man.hit(self.win)
                        self.score -= 5
                        self.dead_loop = 1

            # bullets hit goblins
            for bullet in self.bullets:
                if self.time == 0:
                    break

                for goblin in self.goblins:
                    if bullet.y + bullet.radius < goblin.hitbox[1] + goblin.hitbox[3] and bullet.y > goblin.hitbox[1]:
                        if bullet.x > goblin.hitbox[0] and bullet.x + bullet.radius < goblin.hitbox[0] + goblin.hitbox[2]:
                            goblin.hit()
                            self.score += 1
                            bullet.remove = True
                            if goblin.health == 0:
                                self.goblins.remove(goblin)

            # clear bullets
            self.bullets = list(filter(lambda x: x.remove == False, self.bullets))

            self.handling_keys()

            self.redraw_game_window()

        pygame.quit()
