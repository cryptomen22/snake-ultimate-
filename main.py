import pygame
import random
import sys

pygame.init()

class Snake16Ultimate:
    def __init__(self):
        info = pygame.display.Info()
        self.W, self.H = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((self.W, self.H))
        
        # Разметка экрана
        self.SAFE_B, self.CONTROLS_H, self.TOP_H = 150, 550, 250
        self.GAME_H = self.H - self.TOP_H - self.CONTROLS_H - self.SAFE_B - 50
        self.CELL = self.W // 16
        self.cols, self.rows = self.W // self.CELL, self.GAME_H // self.CELL
        
        # Шрифты (Используем None для стандартного шрифта Pygame)
        self.font_s = pygame.font.Font(None, 45)
        self.font_m = pygame.font.Font(None, 70)
        self.font_l = pygame.font.Font(None, 130)
        
        self.high_score = 0
        self.state = "MENU"
        
        # Окружение
        self.clouds = [[random.randint(0, self.W), random.randint(40, 140), random.randint(70, 100)] for _ in range(4)]
        self.cars = [[random.randint(0, self.W), self.H - 260, random.randint(5, 8), 
                      random.choice([(180,20,20), (20,20,180), (60,60,60)])] for _ in range(5)]
        
        self.reset()

    def reset(self):
        if hasattr(self, 'score') and self.score > self.high_score:
            self.high_score = self.score
        self.snake = [[(self.cols//2)*self.CELL, self.TOP_H + (self.rows//2)*self.CELL]]
        self.direction = [0, 0]
        self.next_dir = [0, 0]
        self.score = 0
        self.move_progress = 0
        self.base_speed = 0.08
        self.spawn_apple()

    def spawn_apple(self):
        self.apple = [random.randint(0, self.cols-1)*self.CELL, 
                      self.TOP_H + random.randint(0, self.rows-1)*self.CELL]

    def draw_world(self):
        # Небо и Солнце
        pygame.draw.rect(self.screen, (100, 200, 255), (0, 0, self.W, self.TOP_H + self.GAME_H))
        pygame.draw.circle(self.screen, (255, 255, 0), (self.W - 130, 130), 110)
        
        # Облака
        for c in self.clouds:
            c[0] = (c[0] + 0.4) % (self.W + 300)
            x, y, r = int(c[0]), c[1], c[2]
            pygame.draw.circle(self.screen, (255,255,255), (x, y), r)
            pygame.draw.circle(self.screen, (240,240,240), (x+50, y+20), int(r*0.9))
            pygame.draw.circle(self.screen, (255,255,255), (x-40, y+10), int(r*0.7))

        # Сетка
        for x in range(0, self.W + 1, self.CELL):
            pygame.draw.line(self.screen, (80, 80, 150, 40), (x, self.TOP_H), (x, self.TOP_H + self.rows*self.CELL))
        for y in range(self.TOP_H, self.TOP_H + self.rows*self.CELL + 1, self.CELL):
            pygame.draw.line(self.screen, (80, 80, 150, 40), (0, y), (self.W, y))

        # Дорога
        road_y = self.H - self.CONTROLS_H - self.SAFE_B - 50
        pygame.draw.rect(self.screen, (40, 40, 45), (0, road_y, self.W, 1000))
        for i in range(0, self.W, 120):
            pygame.draw.rect(self.screen, (180, 180, 180), (i, road_y + 70, 60, 10))

        # Трафик
        for c in self.cars:
            c[0] = (c[0] + c[2]) % (self.W + 400)
            x, y = c[0]-300, c[1]
            pygame.draw.rect(self.screen, c[3], (x, y, 160, 75), border_radius=15)
            pygame.draw.rect(self.screen, (150, 220, 255), (x+100, y+10, 45, 30), border_radius=5)
            pygame.draw.circle(self.screen, (0,0,0), (x+35, y+75), 18)
            pygame.draw.circle(self.screen, (0,0,0), (x+125, y+75), 18)

    def draw_entities(self):
        # Рисуем яблоко
        ax, ay = self.apple[0] + self.CELL//2, self.apple[1] + self.CELL//2
        ar = self.CELL//2 - 5
        pygame.draw.circle(self.screen, (150, 0, 0), (ax+3, ay+3), ar) 
        pygame.draw.circle(self.screen, (220, 20, 20), (ax, ay), ar) 
        pygame.draw.circle(self.screen, (255, 120, 120), (ax-4, ay-4), ar//2) 
        pygame.draw.rect(self.screen, (0, 120, 0), (ax-2, ay-ar-8, 4, 10)) 

        # Рисуем змейку
        for i, p in enumerate(self.snake):
            is_head = (i == len(self.snake)-1)
            cx, cy = int(p[0] + self.CELL//2), int(p[1] + self.CELL//2)
            r = self.CELL//2 - 2
            
            base_c = (0, 180, 80) if is_head else (0, 130, 60)
            pygame.draw.circle(self.screen, base_c, (cx, cy), r)
            pygame.draw.circle(self.screen, (min(255, base_c[0]+50), min(255, base_c[1]+50), 60), (cx-5, cy-5), r//2)
            
            if is_head:
                for s in [-1, 1]:
                    pygame.draw.circle(self.screen, (255,255,255), (cx+s*13, cy-7), 10)
                    pygame.draw.circle(self.screen, (0,0,0), (cx+s*13, cy-9), 5)
                if (pygame.time.get_ticks() // 350) % 2 == 0:
                    pygame.draw.polygon(self.screen, (255, 50, 50), [(cx-2, cy-r), (cx+2, cy-r), (cx+4, cy-r-15), (cx-4, cy-r-15)])

    def update(self):
        if self.direction == [0, 0]: return
        self.move_progress += self.base_speed + (self.score * 0.001)
        if self.move_progress >= 1.0:
            self.move_progress = 0
            self.direction = self.next_dir
            new_h = [self.snake[-1][0] + self.direction[0]*self.CELL, self.snake[-1][1] + self.direction[1]*self.CELL]
            new_h[0] %= (self.cols * self.CELL)
            new_h[1] = self.TOP_H + ((new_h[1] - self.TOP_H) % (self.rows * self.CELL))
            if new_h in self.snake: self.state = "OVER"; return
            self.snake.append(new_h)
            if new_h == self.apple: self.score += 1; self.spawn_apple()
            else: self.snake.pop(0)

    def btn(self, txt, x, y, w, h, c=(50, 60, 90)):
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, c, rect, border_radius=20)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 3, border_radius=20)
        text = self.font_m.render(txt, True, (255, 255, 255))
        self.screen.blit(text, text.get_rect(center=rect.center))
        return rect

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.draw_world()
            if self.state == "MENU":
                t_img = self.font_l.render("Snake 1.6", True, (0, 90, 0))
                self.screen.blit(t_img, t_img.get_rect(center=(self.W//2, self.H//4)))
                auth = self.font_s.render("Authors: Vseznaushchy & Gemini", True, (40, 40, 40))
                self.screen.blit(auth, auth.get_rect(center=(self.W//2, self.H - 60)))
                b1, b2 = self.btn("START", self.W//2-220, self.H//2-90, 440, 120), self.btn("EXIT", self.W//2-220, self.H//2+80, 440, 120, (140, 40, 40))
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if e.type == pygame.MOUSEBUTTONDOWN:
                        if b1.collidepoint(e.pos): self.state = "GAME"
                        if b2.collidepoint(e.pos): pygame.quit(); sys.exit()
            
            elif self.state == "GAME":
                self.draw_entities()
                self.update()
                self.screen.blit(self.font_s.render(f"SCORE: {self.score}", True, (255,255,255)), (40, 40))
                self.screen.blit(self.font_s.render(f"BEST: {max(self.score, self.high_score)}", True, (255,255,0)), (40, 100))
                bp = self.btn("||", self.W-130, 40, 100, 100)
                bx, by = self.W // 2, self.H - self.SAFE_B - 300
                bw, bh = 180, 150
                b_w, b_s = self.btn("W", bx-90, by-165, bw, bh), self.btn("S", bx-90, by+165, bw, bh)
                b_a, b_d = self.btn("A", bx-285, by, bw, bh), self.btn("D", bx+105, by, bw, bh)
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if e.type == pygame.MOUSEBUTTONDOWN:
                        if bp.collidepoint(e.pos): self.state = "PAUSE"
                        if b_w.collidepoint(e.pos) and self.direction[1] == 0: self.next_dir = [0, -1]
                        if b_s.collidepoint(e.pos) and self.direction[1] == 0: self.next_dir = [0, 1]
                        if b_a.collidepoint(e.pos) and self.direction[0] == 0: self.next_dir = [-1, 0]
                        if b_d.collidepoint(e.pos) and self.direction[0] == 0: self.next_dir = [1, 0]
                        if self.direction == [0,0]: self.direction = self.next_dir

            elif self.state == "PAUSE":
                b1, b2 = self.btn("RESUME", self.W//2-220, self.H//2-90, 440, 120), self.btn("EXIT", self.W//2-220, self.H//2+80, 440, 120, (140, 40, 40))
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if e.type == pygame.MOUSEBUTTONDOWN:
                        if b1.collidepoint(e.pos): self.state = "GAME"
                        if b2.collidepoint(e.pos): pygame.quit(); sys.exit()

            elif self.state == "OVER":
                msg = self.font_m.render("GAME OVER", True, (180, 0, 0))
                self.screen.blit(msg, msg.get_rect(center=(self.W//2, self.H//4)))
                b1, b2 = self.btn("RETRY", self.W//2-220, self.H//2-90, 440, 120), self.btn("EXIT", self.W//2-220, self.H//2+80, 440, 120, (140, 40, 40))
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if e.type == pygame.MOUSEBUTTONDOWN:
                        if b1.collidepoint(e.pos): self.reset(); self.state = "GAME"
                        if b2.collidepoint(e.pos): pygame.quit(); sys.exit()

            pygame.display.flip(); clock.tick(60)

if __name__ == "__main__":
    Snake16Ultimate().run()
      
