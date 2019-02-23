import gamemanager as gm
import pygame

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
