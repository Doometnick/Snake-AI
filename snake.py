import gamemanager as gm
from cube import Cube
import pygame
import random


class Snake():
    body = []
    turns = {}

    def __init__(self, color, pos):
        self.color = color
        self.head = Cube(pos, self.color)
        self.body.append(self.head)
        self.grow()
        self.dirnx = 0
        self.dirny = -1

    def move(self):

        if gm.auto_movement:
            #self._auto_movement()
            pass
        else:
            self._handle_input()

        for i, cube, in enumerate(self.body):
            p = cube.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                cube.move(turn[0], turn[1])
                if i == len(self.body) - 1:
                    self.turns.pop(p)
            else:
                # Check if we keep moving or switch sides
                if cube.dirnx == -1 and cube.pos[0] <= 0: cube.pos = (cube.rows - 1, cube.pos[1])
                elif cube.dirnx == 1 and cube.pos[0] >= cube.rows - 1: cube.pos = (0, cube.pos[1])
                elif cube.dirny == 1 and cube.pos[1] >= cube.rows - 1: cube.pos = (cube.pos[0], 0)
                elif cube.dirny == -1 and cube.pos[1] <= 0: cube.pos = (cube.pos[0], cube.rows - 1)
                else: cube.move(cube.dirnx, cube.dirny)

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.turn_left()
        if keys[pygame.K_RIGHT]: self.turn_right()
        if keys[pygame.K_UP]: self.turn_up()
        if keys[pygame.K_DOWN]: self.turn_down()

    def _auto_movement(self, move_vector: tuple):
        """ Controls the snake's movement using a 3-state variable.
            :param move_vector: Tuple of size 3. A 1 indicates move in a certain direction.
                                (1, 0, 0) move to left
                                (0, 1, 0) move straight
                                (0, 0, 1) move to right
        """
        
        dirx, diry = self.dirnx, self.dirny
        if move_vector == (1, 0, 0):
            if diry == 0: # horz right-turn
                dirx, diry = 0, -dirx
            elif dirx == 0: # vert right-turn
                diry, dirx = 0, diry
        elif move_vector == (0, 0, 1):
            if diry == 0: # horz left-turn
                dirx, diry = 0, dirx
            elif dirx == 0: # vert left-turn
                diry, dirx = 0, -diry
        self.dirnx, self.dirny = dirx, diry
        self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
        

    def grow(self, by=1):
        for _ in range(by):
            tail = self.body[-1]
            dx, dy = tail.dirnx, tail.dirny

            if self.isGoingRight:
                self.body.append(Cube((tail.pos[0] - 1, tail.pos[1]), self.color))
            elif self.isGoingLeft:
                self.body.append(Cube((tail.pos[0] + 1, tail.pos[1]), self.color))
            elif self.isGoingDown:
                self.body.append(Cube((tail.pos[0], tail.pos[1] - 1), self.color))
            elif self.isGoingUp:
                self.body.append(Cube((tail.pos[0], tail.pos[1] + 1), self.color))

            self.body[-1].dirnx = dx
            self.body[-1].dirny = dy

    def reset(self, pos):
        self.head = Cube(pos, self.color)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1

    def draw(self, surface):
        for i, cube in enumerate(self.body):
            if i == 0:
                cube.draw(surface, eyes=True)
            else:
                cube.draw(surface)

    def turn_left(self):
        if self.dirnx != 1:
            self.dirnx = -1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
    
    def turn_right(self):
        if self.dirnx != -1:
            self.dirnx = 1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
    
    def turn_up(self):
        if self.dirny != 1:
            self.dirnx = 0
            self.dirny = -1
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
    
    def turn_down(self):
        if self.dirny != -1:
            self.dirnx = 0
            self.dirny = 1
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

    @property
    def isGoingRight(self):
        if self.body[-1].dirnx == 1:
            return True
        return False

    @property
    def isGoingLeft(self):
        if self.body[-1].dirnx == -1:
            return True
        return False
    
    @property
    def isGoingUp(self):
        if self.body[-1].dirny == -1:
            return True
        return False
    
    @property
    def isGoingDown(self):
        if self.body[-1].dirny == 1:
            return True
        return False