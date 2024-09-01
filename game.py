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

keyboard_img = pygame.transform.scale(pygame.image.load("imgs/teclado.png"), (150,150))
space_key_img = pygame.transform.scale(pygame.image.load("imgs/espacio.png"), (150,150))

# Colors
WHITE = (255,255,255)
BLACK = (0,0,0)

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

def draw_text(surface, text, font, color, x, y, center=True):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
        surface.blit(textobj, textrect)
    else:
        surface.blit(textobj, (x,y))

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
                    if self.text:
                        print(self.text)  # Acción al presionar Enter
                        # player_name = self.text
                        show_menu(self.text)
                        self.text = ''
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

class Button():
    def __init__(self, x, y, width, height, text, color=WHITE, text_color=BLACK, font=font_consolas_20):
        self.rect = pygame.Rect(x, y, width, height)
        self.rect.center = (x,y)
        self.color = color
        self.text = text
        self.font = font
        self.text_color = text_color
        self.pos_x = x
        self.pos_y =y

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        textobj = self.font.render(self.text, True, self.text_color)
        textrect = textobj.get_rect()
        textrect.center = self.rect.center
        surface.blit(textobj, textrect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

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

# Funcion con el codigo del juego
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
        draw_text(screen, f"Level: {level}", font_karma_20, WHITE, 10,10, False)
        draw_text(screen, f"Lives: {player.lives}", font_karma_20, WHITE, 10,30, False)
        draw_text(screen, f"Destroyed: {player.destroyed_enemies}", font_karma_20, WHITE, 10,50, False)

        # Si el jugador pierde mostramos el mensaje de derrota
        if lost:
            draw_text(screen, "You Lost!", font_karma_60, WHITE, WIDTH//2, HEIGHT//2)

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

def show_controls():
    button_back = Button(WIDTH*0.5, HEIGHT*0.8, 110, 28, "<<Back")
    while True:
        clock.tick(FPS)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_back.is_clicked(mouse_pos):
                    return

        screen.fill(BACKGROUND)
        draw_text(screen, "Move:", font_consolas_30, WHITE, WIDTH*0.3, HEIGHT*0.1 + keyboard_img.get_height()//2)
        draw_text(screen, "Shoot:", font_consolas_30, WHITE, WIDTH*0.3, HEIGHT*0.4 + space_key_img.get_height()//2)
        screen.blit(keyboard_img, (WIDTH*0.5, HEIGHT*0.1))
        screen.blit(space_key_img, (WIDTH*0.5, HEIGHT*0.4))
        button_back.draw(screen)

def show_menu(player_name):
    button_play =       Button(WIDTH*0.5, HEIGHT*0.5, 110, 28, "Play!")
    button_controls =   Button(WIDTH*0.5, HEIGHT*0.6, 110, 28, "Controls")
    button_records =    Button(WIDTH*0.5, HEIGHT*0.7, 110, 28, "Records")
    button_back =       Button(WIDTH*0.5, HEIGHT*0.8, 110, 28, "<<Back")

    while True:
        clock.tick(FPS)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_play.is_clicked(mouse_pos):
                    run_game()
                if button_controls.is_clicked(mouse_pos):
                    show_controls()
                if button_back.is_clicked(mouse_pos):
                    return
        
        screen.fill(BACKGROUND)
        draw_text(screen, "Space Invaders", font_karma_60, WHITE, WIDTH//2, HEIGHT*0.3)
        draw_text(screen, f"Welcome {player_name}", font_consolas_20, WHITE, WIDTH//2, HEIGHT*0.4)
        draw_text(screen, "Made by @PakoMtz", font_consolas_15, (200,200,200), WIDTH//2, HEIGHT-18)
        button_play.draw(screen)
        button_controls.draw(screen)
        button_records.draw(screen)
        button_back.draw(screen)

def main():
    # Crear una instancia de Textbox
    textbox = Textbox(pos_x=WIDTH//2 - 70, pos_y=HEIGHT//2, width=140, height=30, font=font_consolas_20)

    # Menu principal
    while True:
        clock.tick(FPS)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            textbox.handle_event(event)

        screen.fill(BACKGROUND)
        draw_text(screen, "Space Invaders", font_karma_60, WHITE, WIDTH//2, HEIGHT*0.3)
        draw_text(screen, "Player Name:", font_consolas_15, WHITE, WIDTH//2, HEIGHT//2 - 15)
        draw_text(screen, "type your name and press <Enter>", font_consolas_15, WHITE, WIDTH//2, HEIGHT*0.6)
        draw_text(screen, "Made by @PakoMtz", font_consolas_15, (200,200,200), WIDTH//2, HEIGHT-18)
        textbox.draw(screen)

if __name__ == "__main__":
    main()