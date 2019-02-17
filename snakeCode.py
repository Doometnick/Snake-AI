import gamemanager as gm
from snake import Snake
from cube import Cube
from time import sleep
import pygame
import random
    
def drawGrid(surface):
    width = gm.window_width
    size_btwn = width // gm.rows
    x, y = 0, 0
    for _ in range(gm.rows):
        x += size_btwn
        y += size_btwn
        pygame.draw.line(surface, (255, 255, 255), (x, 0), (x, width))
        pygame.draw.line(surface, (255, 255, 255), (0, y), (width, y))

def redraw_window(surface):
    global snake, food
    surface.fill((150, 150, 150))
    snake.draw(surface)
    food.draw(surface)
    # drawGrid(surface)
    pygame.display.update()

def generate_food(restricted_positions):
    while True:
        x = random.randrange(gm.rows)
        y = random.randrange(gm.rows)
        if len(list(filter(lambda z: z.pos == (x, y), restricted_positions))) > 0:
            continue
        else:
            break
    return (x, y)

def message_box(subject, content):
    pass

def main():
    global snake, food
    rows = gm.rows
    window = pygame.display.set_mode((gm.window_width, gm.window_width))

    snake = Snake((192, 0, 0), (rows // 2, rows // 2))
    food = Cube(generate_food(snake.body), color=(0, 220, 0))

    clock = pygame.time.Clock()

    while True:
        pygame.time.delay(0)
        clock.tick(gm.speed)
        snake.move()
        if snake.body[0].pos == food.pos:
            snake.grow()
            food = Cube(generate_food(snake.body), color=(0, 220, 0))
        for x in range(len(snake.body)):
            if snake.body[x].pos in list(map(lambda z: z.pos, snake.body[x +1:])):
                sleep(1.5)
                snake.reset((10, 10))
                break        
        redraw_window(window)
        
main()
