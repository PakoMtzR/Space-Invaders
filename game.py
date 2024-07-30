import pygame
from random import randrange

# Inicializamos pygame
pygame.init()

# Definimos constantes del juego
WIDTH, HEIGHT = 600, 500
TITLE = "StarWars Battle"
ICON = pygame.image.load("imgs/tie-fighter.png")
BACKGROUND = (15,15,15)
FPS = 60
SHIP_SIZE = 50

# Creamos reloj
clock = pygame.time.Clock()

# Creamos y configuramos la pantalla del juego
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
pygame.display.set_icon(ICON)

class Ship:
    def __init__(self, pos_x, pos_y, health = 100):
        self.x = pos_x
        self.y = pos_y
        self.health = health
        self.velocity = 3
        self.size = 50
        self.img = None
    
    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

class Player(Ship):
    def __init__(self, pos_x, pos_y, health = 100):
        super().__init__(pos_x, pos_y, health)
        self.img = pygame.image.load("imgs/x-wing.png")
        self.img = pygame.transform.scale(self.img, (self.size, self.size))

class Enemy(Ship):
    def __init__(self, pos_x, pos_y, health = 100):
        super().__init__(pos_x, pos_y, health)
        self.velocity = 1
        self.img = pygame.image.load("imgs/tie-fighter.png")
        self.img = pygame.transform.scale(self.img, (self.size, self.size))
    
    def move(self):
        self.y += self.velocity

# Variables del juego
font = pygame.font.SysFont("Consolas", 20)
lost_font = pygame.font.SysFont("Consolas", 50)
level = 0
lives = 2
player = Player(WIDTH//2, HEIGHT//2)
enemies = []
wave_length = 0
lost = False
lost_count = 0

def redraw_window():
    screen.fill(BACKGROUND)

    label_level = font.render(f"Level: {level}", True, (255,255,255))
    label_lives = font.render(f"Lives: {lives}", True, (255,255,255))
    screen.blit(label_level, (10,10))
    screen.blit(label_lives, (10,30))

    if lost:
        label_lost = lost_font.render("You Lost!", True, (255,255,255))
        screen.blit(label_lost, ((WIDTH//2)-(label_lost.get_width()//2), (HEIGHT//2)-(label_lost.get_height()//2)))

    player.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)
    pygame.display.update()

is_running = True
while is_running:
    clock.tick(FPS)
    redraw_window()

    if lives <= 0 or player.health <= 0:
        lost = True
        lost_count += 1
        if lost_count > FPS*3:
            is_running = False
        else:
            continue

    if not enemies:
        level += 1
        wave_length += 5
        for i in range(wave_length):
            enemy = Enemy(randrange(0, WIDTH-SHIP_SIZE), randrange(-1500, -100))
            enemies.append(enemy)
    
    for enemy in enemies:
        enemy.move()
        if enemy.y > HEIGHT:
            lives -= 1
            enemies.remove(enemy)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and player.x >= 0:
        player.x -= player.velocity
    if keys[pygame.K_d] and player.x <= WIDTH-player.size:
        player.x += player.velocity
    if keys[pygame.K_w] and player.y >= 0:
        player.y -= player.velocity
    if keys[pygame.K_s] and player.y <= HEIGHT-player.size:
        player.y += player.velocity

pygame.quit()