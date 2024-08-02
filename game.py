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

# Cargamos sonidos del juego
war_sound = pygame.mixer.Sound("sounds/war_sound.mp3")

# Creamos y configuramos la pantalla del juego
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
pygame.display.set_icon(ICON)

class Ship:
    def __init__(self, pos_x, pos_y, health = 100):
        self.x = pos_x
        self.y = pos_y
        self.health = health
        self.speed = 3
        self.size = 50
        self.img = None
        self.mask = None
        self.lasers = []
        self.laser_color = None
        self.lasers_goes_down = False
    
    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw()
    
    def shoot(self):
        laser = Laser(self.x + self.size//2, self.y+10, self.laser_color, self.lasers_goes_down)
        self.lasers.append(laser)
    
    def move_lasers(self, obj):
        for laser in self.lasers:
            laser.move()
            if laser.off_screen():
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

class Player(Ship):
    def __init__(self, pos_x, pos_y, health = 100):
        super().__init__(pos_x, pos_y, health)
        self.img = pygame.image.load("imgs/x-wing.png")
        self.img = pygame.transform.scale(self.img, (self.size, self.size))
        self.mask = pygame.mask.from_surface(self.img)
        self.laser_color = (255, 0, 0)
        self.lives = 5
        self.destroyed_enemies = 0
    
    def move_lasers(self, objs):
        for laser in self.lasers:
            laser.move()
            if laser.off_screen():
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        self.destroyed_enemies += 1
                        objs.remove(obj)

                        if laser in self.lasers:
                            self.lasers.remove(laser)

class Enemy(Ship):
    def __init__(self, pos_x, pos_y, health = 100):
        super().__init__(pos_x, pos_y, health)
        self.speed = 1
        self.img = pygame.image.load("imgs/tie-fighter.png")
        self.img = pygame.transform.scale(self.img, (self.size, self.size))
        self.mask = pygame.mask.from_surface(self.img)
        self.laser_color = (0, 225, 0)
        self.lasers_goes_down = True
    
    def move(self, screen):
        self.y += self.speed
        self.draw(screen)

class Laser():
    def __init__(self, pos_x, pos_y, color, goes_down):
        self.x = pos_x
        self.y = pos_y
        self.speed = 8 if goes_down else -8
        self.size_x = 3
        self.size_y = 20
        self.color =  color
        self.shape = pygame.Surface((self.size_x, self.size_y))
        self.shape.fill(color)
        self.mask = pygame.mask.from_surface(self.shape)
    
    def draw(self):
        screen.blit(self.shape, (self.x, self.y))

    def move(self):
        self.y += self.speed
    
    def off_screen(self):
        return self.y >= HEIGHT or self.y <= -self.size_y
    
    def collision(self, obj):
        return collide(self, obj)

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

# Variables del juego
font = pygame.font.SysFont("Consolas", 20)
lost_font = pygame.font.SysFont("Consolas", 50)
level = 0
player = Player(WIDTH//2, HEIGHT//2)
enemies = []
wave_length = 0
lost = False
lost_count = 0

def redraw_window():
    # Rellenamos el fondo
    screen.fill(BACKGROUND)     

    # Escribimos los labels de nivel, vidas, etc.
    label_level = font.render(f"Level: {level}", True, (255,255,255))
    label_lives = font.render(f"Lives: {player.lives}", True, (255,255,255))
    label_health = font.render(f"Health: {player.health}", True, (255,255,255))
    label_destroyed = font.render(f"Destroyed: {player.destroyed_enemies}", True, (255,255,255))
    screen.blit(label_level, (10,10))
    screen.blit(label_lives, (10,30))
    screen.blit(label_health, (10,50))
    screen.blit(label_destroyed, (10,70))

    # Si el jugador pierde mostramos el mensaje de derrota
    if lost:
        label_lost = lost_font.render("You Lost!", True, (255,255,255))
        screen.blit(label_lost, ((WIDTH//2)-(label_lost.get_width()//2), (HEIGHT//2)-(label_lost.get_height()//2)))

    player.draw(screen)
    player.move_lasers(enemies)
    
    # Movemos a los enemigos y los eliminamos si salen de la pantalla
    for enemy in enemies:
        enemy.move(screen)
        enemy.move_lasers(player)

        if randrange(0, 1*60) == 1:
            enemy.shoot()

        if collide(enemy, player):
            player.health -= 10
            player.destroyed_enemies += 1
            enemies.remove(enemy)
        elif enemy.y > HEIGHT:
            player.lives -= 1
            enemies.remove(enemy)

    # Actualizamos la pantalla
    pygame.display.update()



is_running = True
while is_running:
    clock.tick(FPS)
    redraw_window()

    # Si pierdes todas las vidas o destruyen la nave del jugador entonces pierde el juego
    if player.lives <= 0 or player.health <= 0:
        lost = True
        lost_count += 1
        if lost_count > FPS*3:
            is_running = False
        else:
            continue

    # Si eliminan todos los enemigos, sube de nivel y agregamos nuevos enemigos
    if not enemies:
        level += 1
        wave_length += 5
        war_sound.play()
        for i in range(wave_length):
            enemy = Enemy(randrange(0, WIDTH-SHIP_SIZE), randrange(-1500, -100))
            enemies.append(enemy)

    # Deteccion de eventos
    for event in pygame.event.get():
        # Cerrar la ventana del juego
        if event.type == pygame.QUIT:
            is_running = False
        # Disparos del jugador
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # Eventos para el movimiento del jugador
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and player.x >= 0:
        player.x -= player.speed
    if keys[pygame.K_d] and player.x <= WIDTH-player.size:
        player.x += player.speed
    if keys[pygame.K_w] and player.y >= 0:
        player.y -= player.speed
    if keys[pygame.K_s] and player.y <= HEIGHT-player.size:
        player.y += player.speed

pygame.quit()