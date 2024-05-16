import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000,800
FPS = 60
PLAYER_VEL = 5 #prędkość

window = pygame.display.set_mode((WIDTH,HEIGHT))

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width,height), pygame.SRCALPHA,32)
            rect = pygame.Rect(i * width, 0 , width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "")+ "_right" ] = sprites
            all_sprites[image.replace(".png", "")+ "_left" ] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def get_block(size):
    path = join("assets","Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0 ,size, size)
    surface.blit(image, (0,0), rect)
    return pygame.transform.scale2x(surface)

def get_top(size):
    path = join("assets","Terrain","Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size/3), pygame.SRCALPHA, 32)
    rect = pygame.Rect(192,64, size, size/3)
    surface.blit(image, (0,0), rect)
    return pygame.transform.scale2x(surface)

def get_polygon(size, dir):
    path = join("assets","Terrain","Terrain2.png")
    image = pygame.image.load(path).convert_alpha()
    if(dir == "L"):
        rect = pygame.Rect(96,0, size, 24)
    elif(dir == "R"):
        rect = pygame.Rect(144,0,size, 24)
    surface = pygame.Surface(rect.size, pygame.SRCALPHA, 32)
    surface.blit(image, (0,0), rect)
    return pygame.transform.scale2x(surface)

def get_halfblock(size):
    path = join("assets","Terrain","Terrain2.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,24), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 24, size, 24)
    surface.blit(image, (0,0), rect)
    return pygame.transform.scale2x(surface)

def get_winblock(size):
    path = join("assets","Terrain","Terrain2.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(271,128, size, size)
    surface.blit(image, (0,0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255,0,0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "BlueCar", 40, 20, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "right"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.sprite = self.SPRITES["idle_right"][0]
        self.angle = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 2:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def rotate(self, angle):
        self.angle += angle
        old_center = self.rect.center
        self.sprite = pygame.transform.rotate(self.SPRITES["idle_"+self.direction][0], self.angle)
        self.rect = self.sprite.get_rect(center=old_center)
        self.update()


    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def move_left(self, vel):
        self.x_vel = -vel
        if(self.direction != "left"):
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if(self.direction != "right"):
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect.topleft = self.rect.x, self.rect.y
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
        

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None, polygon_points=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name
        self.polygon_points = polygon_points
    
    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Top(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size/3)
        top = get_top(size)
        self.image.blit(top, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class HalfBlock(Object):
    def __init__(self,x,y,size):
        super().__init__(x,y,size,size/2)
        halfblock = get_halfblock(size)
        self.image.blit(halfblock, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Polygon(Object):
    def __init__(self,x,y,size, direction):
        super().__init__(x,y,size,size/2)
        polygon = get_polygon(size, direction)
        self.image.blit(polygon, (0, 0))
        self.direction = direction
        self.mask = pygame.mask.from_surface(self.image)

class WinBlock(Object):
    def __init__(self,x,y,size):
        super().__init__(x,y,size,size)
        winblock = get_winblock(size)
        self.image.blit(winblock, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    ANIMATION_DELAY = 3
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps","Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect.topleft = self.rect.x, self.rect.y
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0
        

class Button:
    def __init__(self,x,y,width,height,color,text=''):
        self.rect = pygame.Rect(x,y,width,height)
        self.color = color
        self.text = text
        self.font = pygame.font.Font(None,36)

    def draw(self, window):
        pygame.draw.rect(window, self.color, self.rect)
        if self.text:
            text_surface = self.font.render(self.text, True, (0,0,0))
            text_rect = text_surface.get_rect(center=self.rect.center)
            window.blit(text_surface, text_rect)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


def get_background(name):
    image = pygame.image.load(join("assets","Background",name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)
    
    return tiles, image

def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collied_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if isinstance(obj,Polygon):
                if dy > 0:
                    player.rect.bottom += -dy
                    player.landed()
                    player.y_vel = 0
                elif dy < 0:
                    player.rect.top = obj.rect.bottom
                    player.hit_head()
                    player.y_vel = 0
            else:
                if dy > 0:
                    player.rect.bottom = obj.rect.top
                    player.landed()
                    player.y_vel = 0
                elif dy < 0:
                    player.rect.top = obj.rect.bottom
                    player.hit_head()
                    player.y_vel = 0

            collied_objects.append(obj)

    return collied_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            collided_object = obj
            break
    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if isinstance(collide_right, Polygon) and collide_right.direction == "L":
        if keys[pygame.K_d]:
            player.move(0,-PLAYER_VEL*1.2)
            player.x_vel = PLAYER_VEL
            if(player.direction != "right"):
                player.direction = "right"
                player.animation_count = 0
        elif keys[pygame.K_a]:
            player.move_left(PLAYER_VEL)
    elif isinstance(collide_left, Polygon) and collide_left.direction == "R":
        if keys[pygame.K_a]:
            player.move(0,-PLAYER_VEL*1.2)
            player.x_vel = -PLAYER_VEL
            if(player.direction != "left"):
                player.direction = "left"
                player.animation_count = 0
        elif keys[pygame.K_d]:
            player.move_right(PLAYER_VEL)
    else:
        if keys[pygame.K_a] and not collide_left:
            player.move_left(PLAYER_VEL)
        if keys[pygame.K_d] and not collide_right:
            player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    
    if keys[pygame.K_w] and not vertical_collide:
        player.rotate(5)
    if keys[pygame.K_s] and not vertical_collide:
        player.rotate(-5)

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()

def Text(window, text):
    font = pygame.font.Font(None,96)
    text_surface = font.render(text, True, (0,0,0))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 144))

    window.blit(text_surface, text_rect)

    pygame.display.update()

def Win(player, objects):
    player.move(0, 1)
    player.update()
    win = False
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            if isinstance(obj, WinBlock):
                win = True
                break
    player.move(0, -1)
    player.update()
    return win

def main(window):
    clock = pygame.time.Clock()
    start_time = None
    background, bg_image = get_background("Pink.png")
    block_size = 96

    player = Player(100, HEIGHT - block_size, 50, 50)

    button = Button(WIDTH // 2 - 96, HEIGHT // 2 - 96, 200, 100, (255,172,223), 'Restart')

    #fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    #fire.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, 12*block_size // block_size)]
    floor2 = [Block(i * block_size, HEIGHT - block_size, block_size)
              for i in range(14*block_size // block_size, (WIDTH*5 - block_size*3) // block_size)]
    
    wall = [Block(-WIDTH-56, HEIGHT - i * block_size,block_size)
            for i in range(0, (HEIGHT-block_size) // 2)]
    
    wall2 = [WinBlock(WIDTH*5 - 8, HEIGHT - i * block_size, block_size)
             for i in range(0, (HEIGHT - block_size) // 2)]

    top = [Top(i * block_size, HEIGHT - 8.5*block_size, block_size)
           for i in range(-WIDTH // block_size, (WIDTH * 5) // block_size)]
    
    Jump1 = [Polygon(block_size*8, HEIGHT - block_size * 1.5, block_size, "L"), 
             HalfBlock(block_size*9,HEIGHT-block_size*1.5,block_size),
             Polygon(block_size*9, HEIGHT - block_size * 2, block_size, "L"),
             Block(block_size*10, HEIGHT -block_size*2,block_size),
             Polygon(block_size*10, HEIGHT - block_size * 2.5, block_size, "L"),
             Block(block_size*11, HEIGHT -block_size*2,block_size), 
             HalfBlock(block_size*11,HEIGHT-block_size*2.5,block_size),
             Polygon(block_size*11, HEIGHT - block_size * 3, block_size, "L"),
             
             Block(block_size*14, HEIGHT - block_size*2,block_size), 
             HalfBlock(block_size*14, HEIGHT - block_size*2.5,block_size),
             Polygon(block_size*14, HEIGHT - block_size * 3, block_size, "R"),
             Block(block_size*15, HEIGHT - block_size*2,block_size),
             Polygon(block_size*15, HEIGHT - block_size * 2.5, block_size, "R"),
             HalfBlock(block_size*16,HEIGHT - block_size*1.5,block_size),
             Polygon(block_size*16, HEIGHT - block_size * 2, block_size, "R"),
             Polygon(block_size*17, HEIGHT - block_size * 1.5, block_size, "R"), ]
    
    Jump2 = [Polygon(block_size*26, HEIGHT - block_size * 1.5, block_size, "L"),
             HalfBlock(block_size*27, HEIGHT - block_size*1.5, block_size),
             Polygon(block_size*27, HEIGHT - block_size*2, block_size, "L"),
             
             Block(block_size*28, HEIGHT - block_size*2, block_size),
             Block(block_size*29, HEIGHT - block_size*2, block_size),
             Block(block_size*30, HEIGHT - block_size*2, block_size),
             Polygon(block_size*30, HEIGHT - block_size*3.5, block_size, "L"),
             HalfBlock(block_size*31, HEIGHT - block_size*3.5, block_size),
             Polygon(block_size*31, HEIGHT - block_size*4, block_size, "L"),

             Polygon(block_size*31, HEIGHT - block_size*2,block_size, "R"),
             Polygon(block_size*33, HEIGHT - block_size*2,block_size,"L"),
             HalfBlock(block_size*34, HEIGHT - block_size*2, block_size),
             Polygon(block_size*35,HEIGHT - block_size*2,block_size, "R"),
             Polygon(block_size*36, HEIGHT - block_size*1.5,block_size, "R")]
    
    Jump2FloorBottom = [HalfBlock(i * block_size, HEIGHT - block_size*1.5, block_size)
                  for i in range(block_size*31 // block_size, block_size*36 // block_size)]
    
    Jump2FloorTop = [Block(i * block_size, HEIGHT - block_size*4, block_size)
                     for i in range(block_size*32 // block_size, block_size*37 // block_size)]
    
    WinFloor = [WinBlock(i * block_size, HEIGHT - block_size, block_size)
           for i in range((WIDTH*5 - block_size*3) // block_size, WIDTH*5 // block_size)]
    
    

    objects = [*floor, *wall, *floor2, *top, *Jump1, *Jump2, *Jump2FloorBottom, *Jump2FloorTop, *WinFloor, *wall2] #Block(block_size * 3, HEIGHT - block_size * 4, block_size)]
    
    offset_x = 0
    scroll_area_width = 200

    gameover = False
    run = True
    while run:
        clock.tick(FPS) #60 klatek na sekundę

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN and gameover == False:
                if not start_time:
                    start_time = pygame.time.get_ticks()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if button.is_clicked(pos) and gameover:
                    player = Player(100, HEIGHT - block_size, 50, 50)
                    offset_x = 0
                    gameover = False

        if start_time:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - start_time

            minutes = str(int(elapsed_time / 60000)).zfill(2)
            seconds = str(int(elapsed_time % 60000) / 1000).zfill(2)

            font = pygame.font.Font(None, 36)
            text = font.render(f"{minutes}:{seconds}", True, (0, 0, 0))
            window.blit(text, (10,20))

        pygame.display.update()

        if player.rect.top > HEIGHT and not gameover:
            Text(window, 'Game Over!')
            gameover = True
            button.draw(window)
            start_time = None
        
        if Win(player, objects):
            gameover = True
            Text(window, 'You Won!!!')
            button.draw(window)
            start_time = None
            

        player.loop(FPS)
        #fire.loop()
        if not gameover:
            handle_move(player, objects)
            draw(window, background, bg_image, player, objects, offset_x)

        if((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            if(offset_x + player.x_vel < -WIDTH or offset_x + player.x_vel > WIDTH*4+block_size/2):
                pass
            else:
                offset_x += player.x_vel

if (__name__ == "__main__"):
    main(window)
