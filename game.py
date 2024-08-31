import pygame
from random import randrange, randint

# Fonts
# https://www.1001freefonts.com/es/video-game-fonts.php

# Inicializamos pygame
pygame.init()

# Definimos constantes del juego
WIDTH, HEIGHT = 600, 500
TITLE = "Space Invaders"
ICON = pygame.image.load("imgs/tie-fighter.png")
BACKGROUND = (15,15,15)
FPS = 60
SHIP_SIZE = 50

# Creamos reloj
clock = pygame.time.Clock()

# Cargamos sonidos del juego
war_sound = pygame.mixer.Sound("sounds/war_sound.mp3")
shoot_sound = pygame.mixer.Sound("sounds/shoot_sound.mp3")

# Creamos y configuramos la pantalla del juego
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
pygame.display.set_icon(ICON)

# Cargamos las fuentes (tipografia) del juego
font_consolas_15 = pygame.font.SysFont("Consolas", 15)
font_consolas_20 = pygame.font.SysFont("Consolas", 20)
font_consolas_30 = pygame.font.SysFont("Consolas", 30)
font_karma_60 = pygame.font.Font("fonts/KarmaFuture.ttf", 60)
font_karma_20 = pygame.font.Font("fonts/KarmaFuture.ttf", 20)
font_arcade_20 = pygame.font.Font("fonts/ArcadeClassic.ttf", 20)
font_karmatic_20 = pygame.font.Font("fonts/KarmaticArcarde.ttf", 15)

class Textbox():
    def __init__(self, pos_x, pos_y, width, height, font, text_color=(255,255,255), box_color=(50, 50, 50), active_color=(100, 100, 100)):
        self.rect = pygame.Rect(pos_x, pos_y, width, height)
        self.color_inactive = box_color
        self.color_active = active_color
        self.color = self.color_inactive
        self.font = font
        self.text_color = text_color
        self.text = ''
        self.txt_surface = self.font.render(self.text, True, self.text_color)
        self.active = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Si el usuario hace clic dentro de la caja de texto
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            # Cambiar el color de la caja de texto
            self.color = self.color_active if self.active else self.color_inactive
        
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)  # Acción al presionar Enter
                    self.text = ''
                    run_game()
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < 10:
                        self.text += event.unicode 
                # Re-renderizar el texto
                self.txt_surface = self.font.render(self.text, True, self.text_color)

    def draw(self, screen):
        # Dibujar la caja de texto
        pygame.draw.rect(screen, self.color, self.rect)
        # pygame.draw.rect(screen, self.color, self.rect, 2)
        # Dibujar el texto
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

class Stars():
    def __init__(self):
        self.color = (101, 101, 101)
        self.num_stars = 100
        self.radio = 2
        self.speed = 0.4
        self.screen_width = WIDTH
        self.screen_height = HEIGHT

        # Generando mapa de estrellas
        self.stars_list = []
        for star in range(self.num_stars):
            pos_x = randint(0, self.screen_width)
            pos_y = randint(0, self.screen_height)
            self.stars_list.append([pos_x, pos_y])

    def draw(self, screen):
        for star in self.stars_list:
            pygame.draw.circle(screen, self.color, star, self.radio)
            star[1] += self.speed   # Modificamos posicion en y
            if star[1] > self.screen_height:
                star[1] = 0    

class Ship:
    def __init__(self, pos_x, pos_y, health = 100):
        self.x = pos_x
        self.y = pos_y
        self.max_health = health
        self.health = health
        self.speed = 3
        self.size = 50
        self.img = None
        self.mask = None
        self.lasers = []
        self.laser_color = None
        self.lasers_goes_down = False
    
    # Dibuja la nave en la pantalla y si tiene lasers los dibuja tambien
    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw()
    
    # Al disparar crea un objeto Laser y lo agrega en la lista de laseres
    def shoot(self):
        if self.y >= 0:
            laser = Laser(self.x + self.size//2, self.y+10, self.laser_color, self.lasers_goes_down)
            self.lasers.append(laser)
            shoot_sound.play()
    
    def move_lasers(self, obj):
        for laser in self.lasers:
            laser.move()
            if laser.off_screen():
                self.lasers.remove(laser)
            elif laser.collision(obj):
                self.lasers.remove(laser)
                if obj.health > 0:
                    obj.health -= 10

class Player(Ship):
    def __init__(self, pos_x, pos_y, health = 100):
        super().__init__(pos_x, pos_y, health)
        self.img = pygame.image.load("imgs/x-wing.png")
        self.img = pygame.transform.scale(self.img, (self.size, self.size))
        self.mask = pygame.mask.from_surface(self.img)
        self.laser_color = (255, 0, 0)
        self.lives = 5
        self.destroyed_enemies = 0
    
    def healthbar(self, screen):
        pygame.draw.rect(screen, (255,0,0), (self.x, self.y + self.size + 2, self.size, 5))
        pygame.draw.rect(screen, (0,255,0), (self.x, self.y + self.size + 2, self.size*(self.health/self.max_health), 5))

    def draw(self, screen):
        super().draw(screen)
        self.healthbar(screen)
    
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

# Funciones para verificar colisiones
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

# Juego
def run_game():
    # Variables del juego
    stars = Stars()
    level = 0
    player = Player(WIDTH//2, HEIGHT//2)
    enemies = []
    wave_length = 0
    lost = False
    lost_count = 0

    def redraw_window():
        screen.fill(BACKGROUND)     # Rellenamos el fondo    
        stars.draw(screen)
        
        # Dibuja al jugador y sus lasers
        player.move_lasers(enemies)
        player.draw(screen)
        
        # Movemos a los enemigos y los eliminamos si salen de la pantalla
        for enemy in enemies:
            enemy.move_lasers(player)
            enemy.move(screen)

            if randrange(0, 1*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                player.destroyed_enemies += 1
                enemies.remove(enemy)
            elif enemy.y > HEIGHT:
                enemies.remove(enemy)
                if player.lives > 0:
                    player.lives -= 1

        # Escribimos los labels de nivel, vidas, etc.
        label_level = font_karmatic_20.render(f"Level: {level}", True, (255,255,255))
        label_lives = font_karmatic_20.render(f"Lives: {player.lives}", True, (255,255,255))
        label_destroyed = font_karmatic_20.render(f"Destroyed: {player.destroyed_enemies}", True, (255,255,255))
        screen.blit(label_level, (10,10))
        screen.blit(label_lives, (10,30))
        screen.blit(label_destroyed, (10,50))

        # Si el jugador pierde mostramos el mensaje de derrota
        if lost:
            label_lost = font_karma_60.render("You Lost!", True, (255,255,255))
            screen.blit(label_lost, ((WIDTH//2)-(label_lost.get_width()//2), (HEIGHT//2)-(label_lost.get_height()//2)))

        # Actualizamos la pantalla
        pygame.display.update()

    run = True
    while run:
        clock.tick(FPS)
        redraw_window()

        # Si pierdes todas las vidas o destruyen la nave del jugador entonces pierde el juego
        if player.lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
            if lost_count > FPS*3:
                run = False
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
                quit()
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


# Creamos los labels
label_title_game = font_karma_60.render("Space Invaders", True, (255,255,255))
label_player_name = font_consolas_15.render("Player Name:", True, (255,255,255))
label_made_by = font_consolas_15.render("Made by @PakoMtz", True, (200,200,200))
# label_title = font_consolas_30.render("Press any key to begin", True, (255,255,255))

# Crear una instancia de Textbox
textbox = Textbox(pos_x=WIDTH//2 - 70, pos_y=HEIGHT//2, width=140, height=30, font=font_consolas_20)

# Menu principal
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # if event.type == pygame.KEYDOWN:
        #     run_game()
        textbox.handle_event(event)

    screen.fill(BACKGROUND)
    screen.blit(label_title_game, (WIDTH//2 - label_title_game.get_width()//2, HEIGHT*0.2))
    screen.blit(label_player_name, (WIDTH//2 - label_player_name.get_width()//2, HEIGHT//2 - 18))
    screen.blit(label_made_by, (WIDTH//2 - label_made_by.get_width()//2, HEIGHT-18))
    # screen.blit(label_title, (WIDTH//2 - label_title.get_width()//2, HEIGHT//2))
    textbox.draw(screen)
    pygame.display.update()

pygame.quit()