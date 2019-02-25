import gamemanager as gm
from cube import Cube
import pygame
import random
import numpy as np


class Snake():
    body = []
    turns = {}

    def __init__(self, color, pos):
        self.color = color
        self.head = Cube(pos, self.color)
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = -1
        self.grow()

    @property
    def is_dead(self):
        # Wall collision
        if self.colliding_bottom \
            or self.colliding_top \
            or self.colliding_left \
            or self.colliding_right:
            return True
        # Collision with own tail
        for x in range(len(self.body)):
            if self.body[x].pos in list(map(lambda z: z.pos, self.body[x +1:])):
                return True
        
        return False

    @property
    def body_length(self):
        return len(self.body)

    @property
    def pos_x(self):
        return self.body[0].pos[0]

    @property
    def pos_y(self):
        return self.body[0].pos[1]

    @property
    def going_up(self):
        return self.dirny < 0

    @property
    def going_down(self):
        return self.dirny > 0

    @property
    def going_left(self):
        return self.dirnx < 0

    @property
    def going_right(self):
        return self.dirnx > 0

    @property
    def colliding_top(self):
        return self.pos_y < 0

    @property
    def colliding_bottom(self):
        return self.pos_y >= gm.rows

    @property
    def colliding_left(self):
        return self.pos_x < 0

    @property
    def colliding_right(self):
        return self.pos_x >= gm.rows

    @property
    def tail_going_up(self):
        return self.body[-1].dirny < 0

    @property
    def tail_going_down(self):
        return self.body[-1].dirny > 0

    @property
    def tail_going_left(self):
        return self.body[-1].dirnx < 0

    @property
    def tail_going_right(self):
        return self.body[-1].dirnx > 0

    @property
    def obstacle_ahead(self):
        """ Returns true if the snake's own body or
            a game boundary is directly in front of its head
        """
        # coordinates of head
        x, y = self.body[0].pos
        # return true if raycast to new destination hits own body
        if self.dirnx == 0:
            direction = 1 if self.dirny > 0 else -1
            check_pos = (x, y + direction)
            # return (check_pos[1] >= gm.rows or check_pos[1] < 0) or (check_pos in self.body)
        elif self.dirny == 0:
            direction = 1 if self.dirnx > 0 else -1
            check_pos = (x + direction, y)
            # return (check_pos[1] >= gm.rows or check_pos[0] < 0) or (check_pos in self.body)
        
        check_x, check_y = check_pos
        # Wall collision
        if check_x < 0 or check_x >= gm.rows or check_y < 0 or check_y >= gm.rows:
            return True
        # Body collision
        for cube in self.body:
            if check_pos == cube.pos:
                return True
        return False

    @property
    def obstacle_left_right(self):
        """ Returns a tuple of bools indicating if the snake's own
            body or a game noundary is directly to the right/left of the snake's head
        """
        # coordinates of head
        x, y = self.body[0].pos
        if self.dirnx == 0:
            direction = 1 if self.dirny > 0 else -1
            check_right = (x - direction, y)
            check_left = (x + direction, y)

        elif self.dirny == 0:
            direction = 1 if self.dirnx > 0 else -1
            check_right = (x, y + direction)
            check_left = (x, y - direction)
        else:
            print("Warning: obstacle_left_right cannot determine direction!")

        # return check_left in self.body, check_right in self.body
        left, right = False, False
        for cube in self.body:
            if check_left == cube.pos:
                left = True
            if check_right == cube.pos:
                right = True

        # in addition, check if the wall is on the left or right
        left_x, left_y = check_left
        if left_x < 0 or left_x >= gm.rows or left_y < 0 or left_y >= gm.rows:
            left = True
        right_x, right_y = check_right
        if right_x < 0 or right_x >= gm.rows or right_y < 0 or right_y >= gm.rows:
            right = True
        
        return left, right
    

    def has_eaten(self, position):
        """ Returns true if the head is in the same position as parameter position.
        """
        return self.body[0].pos == position

    def move(self, move_vec=None):

        if gm.auto_movement:
            if move_vec is None:
                raise ValueError("Cannot move automatically if move_vec is None.")
            self._auto_movement(move_vec)
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
                cube.move(cube.dirnx, cube.dirny)
            #     # Check if we keep moving or switch sides
            #     if cube.pos[0] < 0: cube.pos = (cube.rows - 1, cube.pos[1])
            #     elif cube.pos[0] > cube.rows - 1: cube.pos = (0, cube.pos[1])
            #     elif cube.pos[1] > cube.rows - 1: cube.pos = (cube.pos[0], 0)
            #     elif cube.pos[1] < 0: cube.pos = (cube.pos[0], cube.rows - 1)
            #     else: cube.move(cube.dirnx, cube.dirny)
            

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.turn_left()
        if keys[pygame.K_RIGHT]: self.turn_right()
        if keys[pygame.K_UP]: self.turn_up()
        if keys[pygame.K_DOWN]: self.turn_down()

    def _auto_movement(self, move_vector):
        """ Controls the snake's movement using a 3-state variable.
            :param move_vector: Tuple of size 3. A 1 indicates move in a certain direction.
                                (1, 0, 0) move to left
                                (0, 1, 0) move straight
                                (0, 0, 1) move to right
        """        
        dirx, diry = self.dirnx, self.dirny
        if move_vector[0] == 1:
            if diry == 0: # horz right-turn
                dirx, diry = 0, -dirx
            elif dirx == 0: # vert right-turn
                diry, dirx = 0, diry
            self.turns[self.head.pos[:]] = [dirx, diry]
        elif move_vector[2] == 1:
            if diry == 0: # horz left-turn
                dirx, diry = 0, dirx
            elif dirx == 0: # vert left-turn
                diry, dirx = 0, -diry
            self.turns[self.head.pos[:]] = [dirx, diry]
        self.dirnx, self.dirny = dirx, diry
        # self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
        

    def grow(self, by=1):
        for _ in range(by):
            tail = self.body[-1]
            dx, dy = tail.dirnx, tail.dirny

            if self.tail_going_right:
                self.body.append(Cube((tail.pos[0] - 1, tail.pos[1]), self.color))
            elif self.tail_going_left:
                self.body.append(Cube((tail.pos[0] + 1, tail.pos[1]), self.color))
            elif self.tail_going_down:
                self.body.append(Cube((tail.pos[0], tail.pos[1] - 1), self.color))
            elif self.tail_going_up:
                self.body.append(Cube((tail.pos[0], tail.pos[1] + 1), self.color))

            self.body[-1].dirnx = dx
            self.body[-1].dirny = dy

    def reset(self, pos):
        self.head = Cube(pos, self.color)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = -1
        self.grow()

    def draw(self, surface):
        for i, cube in enumerate(self.body):
            if i == 0:
                cube.draw(surface, eyes=True)
            else:
                cube.draw(surface)

    def turn_left(self):
        if not self.dirnx > 0:
            self.dirnx = -1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
    
    def turn_right(self):
        if not self.dirnx < 0:
            self.dirnx = 1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
    
    def turn_up(self):
        if not self.dirny > 0:
            self.dirnx = 0
            self.dirny = -1
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
    
    def turn_down(self):
        if not self.dirny < 0:
            self.dirnx = 0
            self.dirny = 1
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
