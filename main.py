import pygame
from math import *
import random

screen = pygame.display.set_mode((700, 500))
fpsclock = pygame.time.Clock()

pygame.init()

font_fangsong20 = pygame.font.SysFont('fangsong', 20)
font_fangsong15 = pygame.font.SysFont('fangsong', 15)

def fill_text(surface, font, text, pos, color=(0, 0, 0), shadow=False, center=False, shadowcolor=None):
    text1 = font.render(text, True, color)
    text_rect = text1.get_rect()
    if shadow:
        if shadowcolor is None:
            text2 = font.render(text, True, (255 - color[0], 255 - color[1], 255 - color[2]))
        else:
            text2 = font.render(text, True, shadowcolor)
        for p in [(pos[0] - 1, pos[1] - 1),
                  (pos[0] + 1, pos[1] - 1),
                  (pos[0] - 1, pos[1] + 1),
                  (pos[0] + 1, pos[1] + 1)]:
            if center:
                text_rect.center = p
            else:
                text_rect.x = p[0]
                text_rect.y = p[1]
            surface.blit(text2, text_rect)
    if center:
        text_rect.center = pos
    else:
        text_rect.x = pos[0]
        text_rect.y = pos[1]
    surface.blit(text1, text_rect)

class Seg:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color1 = color
        self.color2 = (255 - color[0], 255 - color[1], 255 - color[2])
    def draw(self, surface):
        pygame.draw.circle(surface, self.color1, (self.x, self.y), 10, 0)
        pygame.draw.circle(surface, self.color2, (self.x, self.y), 10, 1)

class Snake:
    def __init__(self, color, bg):
        self.color = color
        self.bg = bg
        self.segs = [Seg(700, 500, color) for i in range(10)]
        self.length = 50
        self.speed = [0, 0]
        self.unit = 9
        self.killed = 0
        self.lasttime = pygame.time.get_ticks()
        self.move = False
    def draw_segs(self, surface):
        for seg in self.segs[:0:-1]:
            seg.draw(surface)
    def draw(self, surface):
        self.draw_segs(surface)
        self.draw_name(surface, '我', (0, 200, 0))
    def draw_name(self, surface, name, color):
        fill_text(surface, font_fangsong15, name, (self.segs[0].x, self.segs[0].y - 18), color=color, center=True, shadow=True, shadowcolor=(255, 255, 255))
    def die(self):
        for enemy in self.bg.enemies:
            if enemy is self:
                for seg in self.segs:
                    self.bg.bigfoods.append(BigFood(seg))
                self.bg.enemies.remove(self)
                return
        if self.bg.snake is self:
            self.bg.snake = None
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            pygame.event.set_grab(False)
            return
    def add_length(self):
        self.length += 1
        if self.length // 5 > len(self.segs):
            x = self.segs[-1].x
            y = self.segs[-1].y
            self.segs.append(Seg(x, y, self.color))
    def update(self):
        self.move = False
        x = self.segs[0].x
        y = self.segs[0].y
        for enemy in self.bg.enemies:
            for seg in enemy.segs[1:]:
                if seg.x - 10 <= x < seg.x + 10 and seg.y - 10 <= y < seg.y + 10:
                    self.die()
                    return
        b1, b2, b3 = pygame.mouse.get_pressed()
        if b1:
            self.unit = 13
        elif b3:
            self.unit = 5
        else:
            self.unit = 9
        mx, my = pygame.mouse.get_pos()
        mx -= self.bg.x
        my -= self.bg.y
        distance = sqrt(pow(x - mx, 2) + pow(y - my, 2))
        angle = atan2(y - my, x - mx)
        cosa = cos(angle) * self.unit
        sina = sin(angle) * self.unit
        if sqrt(pow(-sina, 2) + pow(-cosa, 2)) <= distance:
            self.speed = [-cosa, -sina]
        if len(self.segs) >= 2:
            current = pygame.time.get_ticks()
            if current - self.lasttime >= 50:
                for i in range(len(self.segs) - 1, 0, -1):
                    self.segs[i].x = self.segs[i - 1].x
                    self.segs[i].y = self.segs[i - 1].y
                self.segs[0].x += self.speed[0]
                self.segs[0].y += self.speed[1]
                self.move = True
                self.lasttime = current
        if not (10 <= x < 1390 and 10 <= y < 990):
            self.die()
            return

class EnemySnake(Snake):
    def __init__(self, color, name, bg):
        Snake.__init__(self, color, bg)
        self.name = name
        x = random.randint(100, 1299)
        y = random.randint(100, 899)
        self.segs = [Seg(x, y, color) for i in range(random.randint(7, 20))]
        self.angle = radians(random.randint(0, 359))
        self.find_direction(self.angle)
        self.lastangle = 0
        self.out1 = False
        self.out2 = False
        self.lasttime = self.bg.snake.lasttime
        self.lastfind = pygame.time.get_ticks()
    def draw(self, surface):
        self.draw_segs(surface)
        self.draw_name(surface, self.name, (200, 0, 0))
    def find_angle(self):
        x = self.segs[0].x
        y = self.segs[0].y
        angle = self.angle
        if not 20 <= x < 1380:
            if not self.out1:
                angle = pi - angle
                self.out1 = True
        else:
            self.out1 = False
        if not 20 <= y < 980:
            if not self.out2:
                angle = -angle
                self.out2 = True
        else:
            self.out2 = False
        if angle != self.angle:
            return angle
        for seg in self.bg.snake.segs:
            sx = seg.x
            sy = seg.y
            snake_distance = sqrt(pow(x - sx, 2) + pow(y - sy, 2))
            if snake_distance < 30:
                if random.randint(1, 3) != 2:
                    angle = -(3.14 - atan2(y - sy, x - sx))
                    return angle
        for enemy in self.bg.enemies:
            if enemy is not self:
                for seg in enemy.segs:
                    sx = seg.x
                    sy = seg.y
                    snake_distance = sqrt(pow(x - sx, 2) + pow(y - sy, 2))
                    if snake_distance < 30:
                        if random.randint(1, 5) != 3:
                            angle = -(3.14 - atan2(y - sy, x - sx))
                            return angle
        best = (None, None)
        for bigfood in self.bg.bigfoods:
            distance = sqrt(pow(x - bigfood.x, 2) + pow(y - bigfood.y, 2))
            if distance >= 1000:
                continue
            angle = atan2(y - bigfood.y, x - bigfood.x)
            if best == (None, None):
                best = (distance, angle)
            elif distance < best[0]:
                best = (distance, angle)
        if best[1] is not None:
            return best[1]
        best = (None, None)
        for food in self.bg.foods:
            distance = sqrt(pow(x - food.x, 2) + pow(y - food.y, 2))
            if distance >= 1000:
                continue
            angle = atan2(y - food.y, x - food.x)
            if best == (None, None):
                best = (distance, angle)
            elif distance < best[0]:
                best = (distance, angle)
        if best[1] is not None:
            return best[1]
        return self.angle
    def find_direction(self, angle):
        cosa = cos(self.angle) * 7
        sina = sin(self.angle) * 7
        self.speed = [-cosa, -sina]
    def update(self):
        x = self.segs[0].x
        y = self.segs[0].y
        for seg in self.bg.snake.segs[1:]:
            if seg.x - 10 <= x < seg.x + 10 and seg.y - 10 <= y < seg.y + 10:
                self.bg.snake.killed += 1
                self.die()
        for enemy in self.bg.enemies:
            if enemy is not self:
                for seg in enemy.segs[1:]:
                    if seg.x - 10 <= x < seg.x + 10 and seg.y - 10 <= y < seg.y + 10:
                        self.die()
        self.find_direction(self.angle)
        current = pygame.time.get_ticks()
        if current - self.lastfind >= 1000:
            self.angle = self.find_angle()
            self.lastfind = current
        if len(self.segs) >= 2:
            if current - self.lasttime >= 50:
                for i in range(len(self.segs) - 1, 0, -1):
                    self.segs[i].x = self.segs[i - 1].x
                    self.segs[i].y = self.segs[i - 1].y
                self.segs[0].x += self.speed[0]
                self.segs[0].y += self.speed[1]
                if not 10 <= self.segs[0].x < 1390:
                    if not self.out1:
                        self.angle = pi - self.angle
                        self.out1 = True
                else:
                    self.out1 = False
                if not 10 <= self.segs[0].y < 990:
                    if not self.out2:
                        self.angle = -self.angle
                        self.out2 = True
                else:
                    self.out2 = False
                self.lasttime = current

class Food:
    def __init__(self):
        self.color = randcolor()
        self.x = random.randint(10, 1389)
        self.y = random.randint(10, 989)
        self.r = 4
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.r, 0)
    def update(self, snake, enemies, foods):
        x = snake.segs[0].x
        y = snake.segs[0].y
        if self.x - 15 <= x < self.x + 15 and self.y - 15 <= y < self.y + 15:
            snake.add_length()
            foods.remove(self)
            return
        for enemy in enemies:
            x = enemy.segs[0].x
            y = enemy.segs[0].y
            if self.x - 15 <= x < self.x + 15 and self.y - 15 <= y < self.y + 15:
                enemy.add_length()
                foods.remove(self)
                return

class BigFood:
    def __init__(self, seg):
        self.color1 = seg.color1
        self.color2 = seg.color2
        self.x = seg.x
        self.y = seg.y
        self.r = 8
    def draw(self, surface):
        pygame.draw.circle(surface, self.color1, (self.x, self.y), self.r, 0)
        pygame.draw.circle(surface, self.color2, (self.x, self.y), self.r * 2 // 3, 0)
    def update(self, snake, enemies, bigfoods):
        x = snake.segs[0].x
        y = snake.segs[0].y
        if self.x - 15 <= x < self.x + 15 and self.y - 15 <= y < self.y + 15:
            for i in range(3):
                snake.add_length()
            bigfoods.remove(self)
            return
        for enemy in enemies:
            x = enemy.segs[0].x
            y = enemy.segs[0].y
            if self.x - 15 <= x < self.x + 15 and self.y - 15 <= y < self.y + 15:
                for i in range(3):
                    enemy.add_length()
                bigfoods.remove(self)
                return

class Bg:
    def __init__(self):
        self.surface = pygame.Surface((1400, 1000))
        self.shadow = screen.copy().convert_alpha()
        self.shadow.fill((0, 0, 0, 150))
        self.x = -350
        self.y = -250
        self.snake = Snake((255, 0, 0), self)
        self.current = pygame.time.get_ticks()
        self.enemies = []
        self.lastenemy = self.current
        self.foods = []
        self.lastfood = self.current
        self.bigfoods = []
        self.time = 0
    def draw(self):
        screen.blit(self.surface, (self.x, self.y))
        if self.snake is None:
            screen.blit(self.shadow, (0, 0))
            fill_text(screen, font_fangsong20, 'GAME OVER', (350, 250), center=True, shadow=True)
        else:
            fill_text(screen, font_fangsong20, '长度：%s' % self.snake.length, (5, 5), shadow=True)
            fill_text(screen, font_fangsong20, '击杀：%s' % self.snake.killed, (5, 30), shadow=True)
            fill_text(screen, font_fangsong20, '用时：%.2f' % (self.time / 1000), (5, 55), shadow=True)
    def update(self):
        self.surface.fill((255, 255, 255))
        self.time += pygame.time.get_ticks() - self.current
        self.current = pygame.time.get_ticks()
        for i in range(0, 1000, 50):
            pygame.draw.line(self.surface, (230, 230, 230), (0, i), (1400, i), 1)
        for i in range(0, 1400, 50):
            pygame.draw.line(self.surface, (230, 230, 230), (i, 0), (i, 1000), 1)
        if self.current - self.lastenemy >= 2000:
            if len(self.enemies) < 10:
                self.enemies.append(EnemySnake(randcolor(), randname(), self))
            self.lastenemy = self.current
        if self.current - self.lastfood >= 300:
            if len(self.foods) < 500:
                self.foods.append(Food())
            self.lastfood = self.current
        for food in self.foods[:]:
            food.update(self.snake, self.enemies, self.foods)
            food.draw(self.surface)
        for bigfood in self.bigfoods[:]:
            bigfood.update(self.snake, self.enemies, self.bigfoods)
            bigfood.draw(self.surface)
        for enemy in self.enemies:
            enemy.update()
            enemy.draw(self.surface)
        self.snake.update()
        if self.snake is not None:
            self.snake.draw(self.surface)
            if self.snake.move:
                self.x -= self.snake.speed[0]
                self.y -= self.snake.speed[1]

def randcolor():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return (r, g, b)

def randname():
    return ''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_', random.randint(3, 8)))

bg = Bg()

pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
pygame.event.set_grab(True)
while True:
    screen.fill((0, 0, 0))
    if bg.snake is not None:
        bg.update()
    bg.draw()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
    pygame.display.update()
    fpsclock.tick(30)
