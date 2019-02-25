import gamemanager as gm
import numpy as np
import pygame
import sys


class Cube:

    def __init__(self, start, color=(255,0,0)):
        self.pos = start
        self.dirnx = 0
        self.dirny = -1
        self.color = color
        self.rows = gm.rows

    @property
    def pos_x(self):
        return self.pos[0]

    @property
    def pos_y(self):
        return self.pos[1]

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)

    def draw(self, surface, eyes=False):
        dis = gm.window_width // self.rows
        row, col = self.pos[:]
        pygame.draw.rect(surface, self.color, (row * dis + 1, col * dis + 1, dis - 2, dis - 2))
        if eyes:
            centre = dis // 2
            radius = 3
            circleMid = (row * dis + centre - radius, col * dis + 8)
            circleMid2 = (row * dis + centre + radius, col * dis + 8)
            pygame.draw.circle(surface, (0, 0, 0), circleMid, radius)
            pygame.draw.circle(surface, (0, 0, 0), circleMid2, radius)

    def get_angle_to_point(self, x, y, norm=True):
        """ Returns a normalized angle [-1;1] from 
            the snake's direction towards the point (x, y). 
            If norm is True, result will be between 0 and 1.
        """
        if x >= self.pos_x and y <= self.pos_y:
            a = abs(self.pos_y - y)
            b = abs(self.pos_x - x)
            c = np.sqrt(a ** 2 + b ** 2)
            sin_a = np.sin(a / c)
            alpha = np.degrees(np.arcsin(sin_a))
        elif x < self.pos_x and y <= self.pos_y:
            a = abs(self.pos_x - x)
            b = abs(self.pos_y - y)
            c = np.sqrt(a ** 2 + b ** 2)
            sin_a = np.sin(a / c)
            alpha = 90 + np.degrees(np.arcsin(sin_a))
        elif x < self.pos_x and y > self.pos_y:
            a = abs(self.pos_y - y)
            b = abs(self.pos_x - x)
            c = np.sqrt(a ** 2 + b ** 2)
            sin_a = np.sin(a / c)
            alpha = 180 + np.degrees(np.arcsin(sin_a))
        else:
            a = abs(self.pos_y - y)
            b = abs(self.pos_x - x)
            c = np.sqrt(a ** 2 + b ** 2)
            sin_a = np.sin(a / c)
            alpha = 360 - np.degrees(np.arcsin(sin_a))
        if norm:
            alpha = alpha / 360
        if c == 0:
            print("Division by zero in get_angle_to_point!")
            sys.exit("PROGRAM STOPPED")
        return alpha
