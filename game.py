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
        self.bgm_on = True
        self.effect_on = True

        # font
        self.font = pygame.font.SysFont("comicsans", 30)
        self.font_bold = pygame.font.SysFont("comicsans", 30, True)
        self.font_notify = pygame.font.SysFont("comicsans", 50, True)


    def initialize(self):
        self.score = 0
        self.time = 60

        if self.bgm_on:
            pygame.mixer.music.play(-1)

        # characters
        self.man: Player = Player(300, self.height - 105, 64, 64)
        self.goblins: List[Enemy] = []
        self.bullets: List[Projectile] = []

        # round
        self.round = 1
        self.pass_score = 50

        # loops
        self.shoot_loop = 0
        self.shoot_interval = 5
        self.enemy_loop = 0
        self.enemy_interval = 30
        self.dead_loop = 0
        self.dead_interval = 40
        self.is_dead = False

        # limits
        self.bullets_limit = 5
        self.enemies_limit = 3
        self.enemies_limit = 0

    def next_round(self):
        self.round += 1
        self.pass_score += 50
        self.time = 60
        self.enemies_limit += 1

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
                if self.effect_on:
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
        while True:
            time.sleep(1)

            if self.man.lives == 0 or self.time == 0:
                continue

            self.time -= 1


    def redraw_game_window(self):
        win = self.win

        win.blit(self.bg, (0, 0))

        score_text = self.font.render(f"Score: {self.score}", 1, (0, 0, 0))
        win.blit(score_text, (self.width - 110, 10))
        time_text = self.font.render(f"TIME: {self.time}", 1, (0, 0, 0))
        win.blit(time_text, (self.width // 2 - 50, 10))
        time_text = self.font.render(f"ROUND: {self.round}", 1, (255, 0, 0))
        win.blit(time_text, (self.width // 2 - 50, 50))
        live_text = self.font.render(f"lives: {self.man.lives}", 1, (0, 0, 0))
        win.blit(live_text, (20, 10))

        if self.man.lives == 0 or self.time == 0:
            if self.man.lives == 0:
                text = "GAME OVER"
            elif self.time == 0:
                text = "TIME OVER"

            game_over_text = self.font_notify.render(text, 1, (255, 0, 0))
            self.win.blit(game_over_text, (self.width // 2 - 100, 100))
            restart_text = self.font_bold.render("PRESS 'r' TO RESTART", 1, (0, 0, 0))
            self.win.blit(restart_text, (self.width // 2 - 120, 250))

            self.man.draw(win)


        if self.dead_loop % 2 == 0:
            self.man.draw(win)

        for goblin in self.goblins:
            goblin.draw(win)

        for bullet in self.bullets:
            bullet.draw(win)

        # round complete
        if self.score >= self.pass_score:
            round_complete_text = self.font_notify.render(f"ROUND {self.round} COMPLETE", 1, (255, 0, 0))
            self.win.blit(round_complete_text, (self.width // 2 - 200, 100))
            pygame.display.update()
            time.sleep(3)
            self.dead_loop = 1
            self.next_round()

        pygame.display.update()

    def restart_check(self):
        keys = pygame.key.get_pressed()

        # restart game
        if keys[pygame.K_r]:
            self.initialize()

    def start(self):
        self.initialize()

        # time counting thread
        time_t = threading.Thread(target=self.time_thread, daemon=True)
        time_t.start()

        # main loop
        run = True
        while run:
            self.clock.tick(27)

            # handling exit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            self.redraw_game_window()

            # game over
            if self.time == 0 or self.man.lives == 0:
                self.restart_check()
                continue

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
                if self.dead_loop > 0:
                    break

                if self.man.hitbox[1] < goblin.hitbox[1] + goblin.hitbox[3] and self.man.hitbox[1] + self.man.hitbox[3] > goblin.hitbox[1]:
                    if self.man.hitbox[0] + self.man.hitbox[2] > goblin.hitbox[0] and self.man.hitbox[0] < goblin.hitbox[0] + goblin.hitbox[2]:
                        if self.effect_on:
                            self.hit_sound.play()
                        self.man.hit(self.win)
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

        pygame.quit()
