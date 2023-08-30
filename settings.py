import os
import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_NAME = "HighestScore.sqlite"
DB_PATH = os.path.join(BASE_DIR, DB_NAME)

SCREEN = pygame.display.set_mode((672, 672))  # Screen consisting of 21 x 21 blocks, the size of one block is 32 x 32
DESCENT_SPEED = 20  # Adjust the descent speed. 1 = Drops fastest.

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKY_BLUE = (80, 188, 223)
BLUE = (0, 0, 255)
ORANGE = (255, 127, 0)
YELLOW = (255, 212, 0)
GREEN = (129, 193, 71)
PURPLE = (153, 0, 255)
RED = (255, 0, 0)

X_LENGTH = 12
Y_LENGTH = 21
