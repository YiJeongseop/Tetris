import itertools
import random
import time
from enum import Enum
from typing import Protocol

import pygame
from pygame import mixer, Surface

from db import DB
from time_tracking import TimeTracking
from settings import (
    SCREEN, BLACK, WHITE, SKY_BLUE, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED, DESCENT_SPEED, X_LENGTH, Y_LENGTH
)


class Move(Enum):
    """Movement options in the game."""
    UP = 0
    LEFT = 1
    RIGHT = 2
    DOWN = 3


class Block(Protocol):

    def turn(self) -> None:
        """Perform a turn action of the block in the game.

        The function checks if the current block can rotate without colliding with any other blocks.
        If it can, the function updates the positions of the current blocks accordingly.

        The position of the block depends also on the state of the block.
        """
        ...

    @staticmethod
    def draw() -> None:
        """Draw the block in the waiting area."""
        ...


class BackgroundBlock:
    def __init__(self, x: int, y: int, number: int, not_block: bool):
        """
        Every block has a number.
        0 is not block, 1 to 7 is block, 8 is boundary.
        not_block shows whether this block is a boundary or an installed block.
        """
        self.x = x
        self.y = y
        self.number = number 
        self.not_block = not_block

    @property
    def color(self) -> tuple:
        """Return the color related with each block type."""
        if self.number == 1:
            return SKY_BLUE
        elif self.number == 2:
            return BLUE
        elif self.number == 3:
            return ORANGE
        elif self.number == 4:
            return YELLOW
        elif self.number == 5:
            return GREEN
        elif self.number == 6:
            return PURPLE
        elif self.number == 7:
            return RED

    @staticmethod
    def color_the_block(screen: Surface, coordinates: tuple, x: int, y: int) -> None:
        pygame.draw.rect(screen, coordinates, pygame.Rect(32 * x, 32 * y, 32, 32))
        pygame.draw.rect(screen, BLACK, pygame.Rect(32 * x, 32 * y, 32, 32), width=1)


background_blocks = [[0 for j in range(X_LENGTH)] for i in range(Y_LENGTH)]  # Game Screen consisting of 12 × 21 blocks


class Tetris:
    mixer.init()
    break_sound = mixer.Sound("resources/audio/202230__deraj__pop-sound.wav")
    break_sound.set_volume(0.2)
    erase_sound = mixer.Sound("resources/audio/143607__dwoboyle__menu-interface-confirm-003.wav")
    erase_sound.set_volume(0.15)

    def __init__(self):
        self.score = 0
        self.gameover = False
        self.number_of_blocks = 0  # How many blocks were made?
        self.block_number = 0
        self.next_blocks = []  # The background blocks where moving blocks will be placed.
        self.current_blocks = []  # The background blocks where moving blocks are placed.
        self.current_y_list = []  # y-coordinate list of moving blocks
        self.current_x_list = []  # x-coordinate list of moving blocks
        self._state = 1  # You can turn the block four times. 1, 2, 3, 4

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if self._state != 4:
            self._state = value
        else:
            self._state = 1

    def gameover_state(self):
        # What if there are other blocks where they will be?
        return any(i in self.next_blocks for i in range(1, 8))

    def start(self, ti: TimeTracking, current_block: Block):
        self.block_number = current_block.number
        self.number_of_blocks += 1
        ti.start_time = time.time()

        def current_iter(block_number, blocks):
            for block in iter(blocks):  # What if there are no other blocks where they will be?
                block.number = block_number  # Create the blocks on the game screen
                yield block

        self.next_blocks.clear()

        # A lazily-evaluated map of background blocks. Used to fetch and place one in next_blocks.
        fetch_blocks_map = [
            lambda group: group[0][4:8],  # Block I (1)
            lambda group: [group[0][4], *group[1][4:7]],  # Block J (2)
            lambda group: [*group[1][4:7], group[0][6]],  # Block L (3)
            lambda group: [block for blocks in group[0:2] for block in blocks[5:7]],  # Block O (4)
            lambda group: [*group[1][4:6], *group[0][5:7]],  # Block S (5)
            lambda group: [group[0][5], *group[1][4:7]],  # Block T (6)
            lambda group: [*group[0][4:6], *group[1][5:7]],  # Block Z (7)
        ]
        fetcher = fetch_blocks_map[self.block_number - 1]
        blocks = fetcher(background_blocks)
        self.next_blocks.extend(block.number for block in blocks)
        self.gameover = self.gameover_state()
        if self.gameover:
            return
        self.current_blocks.extend(current_iter(self.block_number, blocks))
        self._state = 1 

    def go(self, move: Enum, ti: TimeTracking):
        self.next_blocks.clear()

        if move in (Move.LEFT, Move.RIGHT):
            if move == Move.LEFT:
                adjust = -1
            else:
                adjust = 1
            for i in range(4):
                self.next_blocks.append(
                    background_blocks[self.current_blocks[i].y//32][(self.current_blocks[i].x//32)+adjust]
                )
                if self.next_blocks[i].number in range(1, 9) and self.next_blocks[i].not_block:
                    return
        elif move == Move.DOWN:
            for i in range(4):
                self.next_blocks.append(
                    background_blocks[(self.current_blocks[i].y//32) + 1][(self.current_blocks[i].x//32)]
                )
                # Add background blocks in where the blocks are moving
                
                if self.next_blocks[i].number in range(1, 9) and self.next_blocks[i].not_block:  
                    # If there are blocks down there, stop
                    y_list = []
                    for j in range(4):
                        self.current_blocks[j].not_block = True
                        y_list.append(self.current_blocks[j].y)
                    self.current_blocks.clear()
                    self.break_sound.play()
                    ti.update_time(time.time(), self.number_of_blocks)
                    self.erase_line_plus_score(y_list, self.erase_sound)
                    return y_list

        self.clear()  # The block is now moving! Remove the background blocks color beforehand.
        for i in range(4):
            self.current_blocks[i] = self.next_blocks[i]
            self.current_blocks[i].number = self.block_number

    def clear(self):
        for i in range(4):
            self.current_blocks[i].number = 0
            pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_blocks[i].x, self.current_blocks[i].y, 32, 32))

    def erase_line_plus_score(self, y_list: list, erase_sound: mixer.Sound):
        """
        max_y is largest y-index of placed blocks.
        min_y is smallest y-index of placed blocks minus 1.
        Check that all horizontal lines are full.
        """
        max_y = max(y_list)//32 
        min_y = min(y_list)//32 - 1 
        while max_y > min_y:
            count = 0
            for x in range(1, 11):
                if not background_blocks[max_y][x].not_block:  # If any of the 10 blocks is empty
                    break
                count += 1
                if count == 10: 
                    erase_sound.play()
                    for x in range(1, 11):
                        background_blocks[max_y][x].not_block = False
                        background_blocks[max_y][x].number = 0
                        pygame.draw.rect(
                            SCREEN, BLACK, pygame.Rect(background_blocks[max_y][x].x, background_blocks[max_y][x].y, 32, 32)  # noqa
                        )

                    for y2 in range(max_y, 0, -1):
                        for x in range(1, 11):
                            background_blocks[y2][x].not_block = background_blocks[y2-1][x].not_block
                            background_blocks[y2][x].number = background_blocks[y2-1][x].number
                            background_blocks[y2-1][x].not_block = False
                            background_blocks[y2-1][x].number = 0
                            pygame.draw.rect(
                                SCREEN, BLACK, pygame.Rect(background_blocks[y2-1][x].x, background_blocks[y2-1][x].y, 32, 32)  # noqa
                            )

                    self.score += 100
                    max_y += 1
                    min_y += 1
            max_y -= 1


class BlockI(): 
    def __init__(self, tetris: Tetris):
        self.number = 1
        self.tetris = tetris
        self.current_list_coords = [
            (0, 0),
            (0, 3),
            (0, 0),
            (0, 0),
        ]
        self.background_list_coords = [
            (2, 2),
            (1, 1),
            (2, 2),
            (1, 1),
        ]

    @property
    def current_coord(self):
        y, x = self.current_list_coords[self.tetris.state - 1]
        return (self.tetris.current_y_list[y], self.tetris.current_x_list[x])

    @property
    def background_coord(self):
        y, x = self.background_list_coords[self.tetris.state - 1]
        return (self.tetris.current_y_list[y], self.tetris.current_x_list[x])

    def turn(self):
        self.tetris.current_y_list.clear()
        self.tetris.current_x_list.clear()
        for i in range(4):
            self.tetris.current_y_list.append(self.tetris.current_blocks[i].y//32)
            self.tetris.current_x_list.append(self.tetris.current_blocks[i].x//32)

        if self.tetris.state == 1:
            if self.tetris.current_y_list[0] == 0:
                return
            checking_coords = ((y, x) for x in range(4) for y in [-1, 1, 2])
            turning_coords = ((2 - y, 0) for y in range(4))

        elif self.tetris.state == 2:
            checking_coords = itertools.chain(
                ((y, -1) for y in range(4)),
                ((y, 1) for y in range(4)),
                ((y, -2) for y in range(4)),
            )
            turning_coords = ((0, 1 - x) for x in range(4))

        elif self.tetris.state == 3:
            checking_coords = ((y, -x) for x in range(4) for y in [1, -1, -2])
            turning_coords = ((y - 2, 0) for y in range(4))

        elif self.tetris.state == 4:
            checking_coords = itertools.chain(
                ((y, -1) for y in range(4)),
                ((y, 1) for y in range(4)),
                ((y, 2) for y in range(4)),
            )
            turning_coords = ((0, x - 1) for x in range(4))

        current_y, current_x = self.current_coord
        background_y, background_x = self.background_coord
        is_not_turnable = any(
            background_blocks[current_y + y][current_x + x].not_block for y, x in checking_coords
        )
        if is_not_turnable:
            return
        self.tetris.clear()
        blocks_to_render = (
            background_blocks[background_y + y][background_x + x]
            for y, x in turning_coords
        )
        for i, block in enumerate(blocks_to_render):
            block.number = self.tetris.block_number
            self.tetris.current_blocks[i] = block
        self.tetris.state += 1

    @staticmethod
    def draw():
        for x in range(14, 18):
            pygame.draw.rect(SCREEN, SKY_BLUE, pygame.Rect(32 * x + 16, 32 * 12, 32, 32))


class BlockJ(): 
    def __init__(self, tetris: Tetris):
        self.number = 2
        self.tetris = tetris
        self.background_list_coords = [
            [(0, 0), (2, 2)],
            [(0, 0), (0, 0)],
            [(0, 0), (2, 2)],
            [(0, 0), (0, 0)],
        ]


    def render_background_blocks(self, offset, offset_loop_func):
        (y1, x1), (y2, x2) = self.background_list_coords[self.tetris.state - 1]

        current_y = self.tetris.current_y_list[y1]
        current_x = self.tetris.current_x_list[x1]
        block = background_blocks[current_y + offset[0]][current_x + offset[1]]
        block.number = self.tetris.block_number
        self.tetris.current_blocks[0] = block

        current_y = self.tetris.current_y_list[y2]
        current_x = self.tetris.current_x_list[x2]
        for i in range(3):
            y, x = offset_loop_func(i)
            block = background_blocks[current_y + y][current_x + x]
            block.number = self.tetris.block_number
            self.tetris.current_blocks[i + 1] = block


    def turn(self):
        self.tetris.current_y_list.clear()
        self.tetris.current_x_list.clear()
        for i in range(4):
            self.tetris.current_y_list.append(self.tetris.current_blocks[i].y//32)
            self.tetris.current_x_list.append(self.tetris.current_blocks[i].x//32)

        if self.tetris.state == 1:
            for x in range(3):
                if background_blocks[self.tetris.current_y_list[1] + 1][self.tetris.current_x_list[1] + x].not_block:
                    return
            for x in range(2):
                if background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[0] + 1 + x].not_block:
                    return

            self.tetris.clear()
            self.render_background_blocks((0, 2), lambda y: (y - 1, 0))

        elif self.tetris.state == 2:
            for y in range(3):
                if background_blocks[self.tetris.current_y_list[1] + y][self.tetris.current_x_list[1] - 1].not_block:
                    return
            for x in range(2):
                if background_blocks[self.tetris.current_y_list[0] + 1 + y][self.tetris.current_x_list[0]].not_block:
                    return

            self.tetris.clear()
            self.render_background_blocks((2, 0), lambda x: (1, -x))

        elif self.tetris.state == 3:
            for x in range(3):
                if background_blocks[self.tetris.current_y_list[1] - 1][self.tetris.current_x_list[1] - x].not_block:
                    return
            for x in range(2):
                if background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[0] - 1 + x].not_block:
                    return

            self.tetris.clear()
            self.render_background_blocks((0, -2), lambda y: (1 - y, 0))

        elif self.tetris.state == 4:
            for y in range(3):
                if background_blocks[self.tetris.current_y_list[3] + y][self.tetris.current_x_list[1] + 1].not_block:
                    return
            for x in range(2):
                if background_blocks[self.tetris.current_y_list[0] - 2 + y][self.tetris.current_x_list[0]].not_block:
                    return

            self.tetris.clear()
            self.render_background_blocks((-2, 0), lambda x: (-1, x))

        self.tetris.state += 1

    @staticmethod
    def draw():
        for x in range(15, 18):
            pygame.draw.rect(SCREEN, BLUE, pygame.Rect(32 * x, 32 * 12, 32, 32))
        pygame.draw.rect(SCREEN, BLUE, pygame.Rect(32 * 15, 32 * 11, 32, 32))

        
class BlockL():
    def __init__(self, tetris: Tetris):
        self.number = 3
        self.tetris = tetris

    def turn(self):
        self.tetris.current_y_list.clear()
        self.tetris.current_x_list.clear()
        for i in range(4):
            self.tetris.current_y_list.append(self.tetris.current_blocks[i].y//32)
            self.tetris.current_x_list.append(self.tetris.current_blocks[i].x//32)

        if self.tetris.state == 1:
            for x in range(3):
                if background_blocks[self.tetris.current_y_list[0] + 1][self.tetris.current_x_list[0] + x].not_block:
                    return
            for x in range(2):
                if background_blocks[self.tetris.current_y_list[3]][self.tetris.current_x_list[3] - 2 + x].not_block:
                    return

            self.tetris.clear()
            for y in range(3):
                background_blocks[self.tetris.current_y_list[1] - 1 + y][self.tetris.current_x_list[1]].number = self.tetris.block_number
                self.tetris.current_blocks[y] = background_blocks[self.tetris.current_y_list[1] - 1 + y][self.tetris.current_x_list[1]]
            background_blocks[self.tetris.current_y_list[2] + 1][self.tetris.current_x_list[2]].number = self.tetris.block_number
            self.tetris.current_blocks[3] = background_blocks[self.tetris.current_y_list[2] + 1][self.tetris.current_x_list[2]]

        elif self.tetris.state == 2:
            for y in range(3):
                if background_blocks[self.tetris.current_y_list[0] + y][self.tetris.current_x_list[0] - 1].not_block:
                     return
            for y in range(2):
                if background_blocks[self.tetris.current_y_list[0] + y][self.tetris.current_x_list[0] + 1].not_block:
                    return

            self.tetris.clear()
            for x in range(3):
                background_blocks[self.tetris.current_y_list[1]][self.tetris.current_x_list[1] + 1 - x].number = self.tetris.block_number
                self.tetris.current_blocks[x] = background_blocks[self.tetris.current_y_list[1]][self.tetris.current_x_list[1] + 1 - x]
            background_blocks[self.tetris.current_y_list[2]][self.tetris.current_x_list[2] - 1].number = self.tetris.block_number
            self.tetris.current_blocks[3] = background_blocks[self.tetris.current_y_list[2]][self.tetris.current_x_list[2] - 1]

        elif self.tetris.state == 3:
            for x in range(3):
                if background_blocks[self.tetris.current_y_list[2] - 1][self.tetris.current_x_list[2] + x].not_block:
                    return
            for x in range(2):
                if background_blocks[self.tetris.current_y_list[3]][self.tetris.current_x_list[3] + 1 + x].not_block:
                    return

            self.tetris.clear()
            for y in range(3):
                background_blocks[self.tetris.current_y_list[1] + 1 - y][self.tetris.current_x_list[1]].number = self.tetris.block_number
                self.tetris.current_blocks[y] = background_blocks[self.tetris.current_y_list[1] + 1 - y][self.tetris.current_x_list[1]]
            background_blocks[self.tetris.current_y_list[2] - 1][self.tetris.current_x_list[2]].number = self.tetris.block_number
            self.tetris.current_blocks[3] = background_blocks[self.tetris.current_y_list[2] - 1][self.tetris.current_x_list[2]]

        elif self.tetris.state == 4:
            for y in range(3):
                if background_blocks[self.tetris.current_y_list[2] + y][self.tetris.current_x_list[0] + 1].not_block:
                    return
            for y in range(2):
                if background_blocks[self.tetris.current_y_list[3] + 1 + y][self.tetris.current_x_list[3]].not_block:
                    return

            self.tetris.clear()
            for x in range(3):
                background_blocks[self.tetris.current_y_list[1]][self.tetris.current_x_list[1] - 1 + x].number = self.tetris.block_number
                self.tetris.current_blocks[x] = background_blocks[self.tetris.current_y_list[1]][self.tetris.current_x_list[1] - 1 + x]
            background_blocks[self.tetris.current_y_list[2]][self.tetris.current_x_list[2] + 1].number = self.tetris.block_number
            self.tetris.current_blocks[3] = background_blocks[self.tetris.current_y_list[2]][self.tetris.current_x_list[2] + 1]

        self.tetris.state += 1

    @staticmethod
    def draw():
        for x in range(15, 18):
            pygame.draw.rect(SCREEN, ORANGE, pygame.Rect(32 * x, 32 * 12, 32, 32))
        pygame.draw.rect(SCREEN, ORANGE, pygame.Rect(32 * 17, 32 * 11, 32, 32))


class BlockO():
    def __init__(self, tetris: Tetris):
        self.number = 4
        self.tetris = tetris

    def turn(self):
        pass

    @staticmethod
    def draw():
        for x in range(15, 17):
            for y in range(11, 13):
                pygame.draw.rect(SCREEN, YELLOW, pygame.Rect(32 * x + 16, 32 * y, 32, 32))


class BlockS():
    def __init__(self, tetris: Tetris):
        self.number = 5
        self.tetris = tetris

    def turn(self):
        self.tetris.current_y_list.clear()
        self.tetris.current_x_list.clear()
        for i in range(4):
            self.tetris.current_y_list.append(self.tetris.current_blocks[i].y//32)
            self.tetris.current_x_list.append(self.tetris.current_blocks[i].x//32)

        if self.tetris.state == 1:
            if self.tetris.current_y_list[2] == 0:
                return
            for x in range(3):
                if background_blocks[self.tetris.current_y_list[2] - 1][self.tetris.current_x_list[0] + x].not_block:
                    return
            if background_blocks[self.tetris.current_y_list[0] - 1][self.tetris.current_x_list[0]].not_block:
                return
            if background_blocks[self.tetris.current_y_list[1]][self.tetris.current_x_list[1] + 1].not_block:
                return

            self.tetris.clear()
            for y in range(2):
                background_blocks[self.tetris.current_y_list[0] - 2 + y][self.tetris.current_x_list[0]].number = self.tetris.block_number
                self.tetris.current_blocks[y] = background_blocks[self.tetris.current_y_list[0] - 2 + y][self.tetris.current_x_list[0]]
            for y in range(2):
                background_blocks[self.tetris.current_y_list[1] - 1 + y][self.tetris.current_x_list[1]].number = self.tetris.block_number
                self.tetris.current_blocks[y + 2] = background_blocks[self.tetris.current_y_list[1] - 1 + y][self.tetris.current_x_list[1]]

        elif self.tetris.state == 2:
            for y in range(3):
                if background_blocks[self.tetris.current_y_list[0] + y][self.tetris.current_x_list[2] + 1].not_block:
                    return
            if background_blocks[self.tetris.current_y_list[1] + 1][self.tetris.current_x_list[1]].not_block:
                return
            if background_blocks[self.tetris.current_y_list[2] - 1][self.tetris.current_x_list[2]].not_block:
                return

            self.tetris.clear()
            for x in range(2):
                background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[0] + 2 - x].number = self.tetris.block_number
                self.tetris.current_blocks[x] = background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[0] + 2 - x]
            for x in range(2):
                background_blocks[self.tetris.current_y_list[1]][self.tetris.current_x_list[1] + 1 - x].number = self.tetris.block_number
                self.tetris.current_blocks[x + 2] = background_blocks[self.tetris.current_y_list[1]][self.tetris.current_x_list[1] + 1 - x]

        elif self.tetris.state == 3:
            for x in range(3):
                if background_blocks[self.tetris.current_y_list[2] + 1][self.tetris.current_x_list[3] + x].not_block:
                    return
            if background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[0] - 2].not_block:
                return
            if background_blocks[self.tetris.current_y_list[2]][self.tetris.current_x_list[0]].not_block:
                return

            self.tetris.clear()
            for y in range(2):
                background_blocks[self.tetris.current_y_list[0] + 2 - y][self.tetris.current_x_list[0]].number = self.tetris.block_number
                self.tetris.current_blocks[y] = background_blocks[self.tetris.current_y_list[0] + 2 - y][self.tetris.current_x_list[0]]
            for y in range(2):
                background_blocks[self.tetris.current_y_list[1] + 1 - y][self.tetris.current_x_list[1]].number = self.tetris.block_number
                self.tetris.current_blocks[y + 2] = background_blocks[self.tetris.current_y_list[1] + 1 - y][self.tetris.current_x_list[1]]

        elif self.tetris.state == 4:
            for y in range(3):
                if background_blocks[self.tetris.current_y_list[0] - y][self.tetris.current_x_list[2] - 1].not_block:
                    return
            if background_blocks[self.tetris.current_y_list[1] - 1][self.tetris.current_x_list[1]].not_block:
                return
            if background_blocks[self.tetris.current_y_list[2] + 1][self.tetris.current_x_list[2]].not_block:
                return

            self.tetris.clear()
            for x in range(2):
                background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[0] - 2 + x].number = self.tetris.block_number
                self.tetris.current_blocks[x] = background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[0] - 2 + x]
            for x in range(2):
                background_blocks[self.tetris.current_y_list[1]][self.tetris.current_x_list[1] - 1 + x].number = self.tetris.block_number
                self.tetris.current_blocks[x + 2] = background_blocks[self.tetris.current_y_list[1]][self.tetris.current_x_list[1] - 1 + x]

        self.tetris.state += 1

    @staticmethod
    def draw():
        for x in range(16, 18):
            pygame.draw.rect(SCREEN, GREEN, pygame.Rect(32 * x, 32 * 11, 32, 32))
        for x in range(15, 17):
            pygame.draw.rect(SCREEN, GREEN, pygame.Rect(32 * x, 32 * 12, 32, 32))


class BlockT():
    def __init__(self, tetris: Tetris):
        self.number = 6
        self.tetris = tetris

    def turn(self):
        self.tetris.current_y_list.clear()
        self.tetris.current_x_list.clear()
        for i in range(4):
            self.tetris.current_y_list.append(self.tetris.current_blocks[i].y//32)
            self.tetris.current_x_list.append(self.tetris.current_blocks[i].x//32)

        if self.tetris.state == 1:
            for x in range(3):
                if background_blocks[self.tetris.current_y_list[1] + 1][self.tetris.current_x_list[1] + x].not_block:
                    return
            if background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[1]].not_block:
                return
            if background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[3]].not_block:
                return

            self.tetris.clear()
            background_blocks[self.tetris.current_y_list[3]][self.tetris.current_x_list[3]].number = self.tetris.block_number
            self.tetris.current_blocks[0] = background_blocks[self.tetris.current_y_list[3]][self.tetris.current_x_list[3]]
            for y in range(3):
                background_blocks[self.tetris.current_y_list[0] + y][self.tetris.current_x_list[0]].number = self.tetris.block_number
                self.tetris.current_blocks[y + 1] = background_blocks[self.tetris.current_y_list[0] + y][self.tetris.current_x_list[0]]

        elif self.tetris.state == 2:
            for y in range(3):
                if background_blocks[self.tetris.current_y_list[1] + y][self.tetris.current_x_list[1] - 1].not_block:
                    return
            if background_blocks[self.tetris.current_y_list[0] - 1][self.tetris.current_x_list[0]].not_block:
                return
            if background_blocks[self.tetris.current_y_list[0] + 1][self.tetris.current_x_list[0]].not_block:
                return

            self.tetris.clear()
            background_blocks[self.tetris.current_y_list[3]][self.tetris.current_x_list[3]].number = self.tetris.block_number
            self.tetris.current_blocks[0] = background_blocks[self.tetris.current_y_list[3]][self.tetris.current_x_list[3]]
            for x in range(3):
                background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[0] - x].number = self.tetris.block_number
                self.tetris.current_blocks[x + 1] = background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[0] - x]

        elif self.tetris.state == 3:
            for x in range(3):
                if background_blocks[self.tetris.current_y_list[1] - 1][self.tetris.current_x_list[3] + x].not_block:
                    return
            if background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[0] - 1].not_block:
                return
            if background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[0] + 1].not_block:
                return

            self.tetris.clear()
            background_blocks[self.tetris.current_y_list[3]][self.tetris.current_x_list[3]].number = self.tetris.block_number
            self.tetris.current_blocks[0] = background_blocks[self.tetris.current_y_list[3]][self.tetris.current_x_list[3]]
            for y in range(3):
                background_blocks[self.tetris.current_y_list[2] + 1 - y][self.tetris.current_x_list[0]].number = self.tetris.block_number
                self.tetris.current_blocks[y + 1] = background_blocks[self.tetris.current_y_list[2] + 1 - y][self.tetris.current_x_list[0]]

        elif self.tetris.state == 4:
            for y in range(3):
                if background_blocks[self.tetris.current_y_list[3] + y][self.tetris.current_x_list[1] + 1].not_block:
                    return
            if background_blocks[self.tetris.current_y_list[0] - 1][self.tetris.current_x_list[0]].not_block:
                return
            if background_blocks[self.tetris.current_y_list[0] + 1][self.tetris.current_x_list[0]].not_block:
                return

            self.tetris.clear()
            background_blocks[self.tetris.current_y_list[3]][self.tetris.current_x_list[3]].number = self.tetris.block_number
            self.tetris.current_blocks[0] = background_blocks[self.tetris.current_y_list[3]][self.tetris.current_x_list[3]]
            for x in range(3):
                background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[0] + x].number = self.tetris.block_number
                self.tetris.current_blocks[x + 1] = background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[0] + x]

        self.tetris.state += 1
        
    @staticmethod
    def draw():
        for x in range(15, 18):
            pygame.draw.rect(SCREEN, PURPLE, pygame.Rect(32 * x, 32 * 12, 32, 32))
        pygame.draw.rect(SCREEN, PURPLE, pygame.Rect(32 * 16, 32 * 11, 32, 32))


class BlockZ():
    def __init__(self, tetris: Tetris):
        self.number = 7
        self.tetris = tetris

    def turn(self):
        self.tetris.current_y_list.clear()
        self.tetris.current_x_list.clear()
        for i in range(4):
            self.tetris.current_y_list.append(self.tetris.current_blocks[i].y//32)
            self.tetris.current_x_list.append(self.tetris.current_blocks[i].x//32)

        if self.tetris.state == 1:
            if self.tetris.current_y_list[0] == 0:
                return
            for x in range(3):
                if background_blocks[self.tetris.current_y_list[0] - 1][self.tetris.current_x_list[0] + x].not_block:
                    return
            if background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[3]].not_block:
                return
            if background_blocks[self.tetris.current_y_list[2]][self.tetris.current_x_list[0]].not_block:
                return

            self.tetris.clear()
            for y in range(2):
                background_blocks[self.tetris.current_y_list[1] - 1 + y][self.tetris.current_x_list[1]].number = self.tetris.block_number
                self.tetris.current_blocks[y] = background_blocks[self.tetris.current_y_list[1] - 1 + y][self.tetris.current_x_list[1]]
            for y in range(2):
                background_blocks[self.tetris.current_y_list[0] + y][self.tetris.current_x_list[0]].number = self.tetris.block_number
                self.tetris.current_blocks[y + 2] = background_blocks[self.tetris.current_y_list[0] + y][self.tetris.current_x_list[0]]

        elif self.tetris.state == 2:
            for y in range(3):
                if background_blocks[self.tetris.current_y_list[0] + y][self.tetris.current_x_list[0] + 1].not_block:
                    return
            if background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[2]].not_block:
                return
            if background_blocks[self.tetris.current_y_list[3]][self.tetris.current_x_list[0]].not_block:
                return

            self.tetris.clear()
            for x in range(2):
                background_blocks[self.tetris.current_y_list[1]][self.tetris.current_x_list[1] + 1 - x].number = self.tetris.block_number
                self.tetris.current_blocks[x] = background_blocks[self.tetris.current_y_list[1]][self.tetris.current_x_list[1] + 1 - x]
            for x in range(2):
                background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[0] - x].number = self.tetris.block_number
                self.tetris.current_blocks[x + 2] = background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[0] - x]

        elif self.tetris.state == 3:
            for x in range(3):
                if background_blocks[self.tetris.current_y_list[0] + 1][self.tetris.current_x_list[3] + x].not_block:
                    return
            if background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[3]].not_block:
                return
            if background_blocks[self.tetris.current_y_list[2]][self.tetris.current_x_list[0]].not_block:
                return

            self.tetris.clear()
            for y in range(2):
                background_blocks[self.tetris.current_y_list[1] + 1 - y][self.tetris.current_x_list[1]].number = self.tetris.block_number
                self.tetris.current_blocks[y] = background_blocks[self.tetris.current_y_list[1] + 1 - y][self.tetris.current_x_list[1]]
            for y in range(2):
                background_blocks[self.tetris.current_y_list[0] - y][self.tetris.current_x_list[0]].number = self.tetris.block_number
                self.tetris.current_blocks[y + 2] = background_blocks[self.tetris.current_y_list[0] - y][self.tetris.current_x_list[0]]

        elif self.tetris.state == 4:
            for y in range(3):
                if background_blocks[self.tetris.current_y_list[3] + y][self.tetris.current_x_list[0] - 1].not_block:
                    return
            if background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[2]].not_block:
                return
            if background_blocks[self.tetris.current_y_list[3]][self.tetris.current_x_list[0]].not_block:
                return

            self.tetris.clear()
            for x in range(2):
                background_blocks[self.tetris.current_y_list[1]][self.tetris.current_x_list[1] - 1 + x].number = self.tetris.block_number
                self.tetris.current_blocks[x] = background_blocks[self.tetris.current_y_list[1]][self.tetris.current_x_list[1] - 1 + x]
            for x in range(2):
                background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[0] + x].number = self.tetris.block_number
                self.tetris.current_blocks[x + 2] = background_blocks[self.tetris.current_y_list[0]][self.tetris.current_x_list[0] + x]

        self.tetris.state += 1

    @staticmethod
    def draw():
        for x in range(15, 17):
            pygame.draw.rect(SCREEN, RED, pygame.Rect(32 * x, 32 * 11, 32, 32))
        for x in range(16, 18):
            pygame.draw.rect(SCREEN, RED, pygame.Rect(32 * x, 32 * 12, 32, 32))


def main():
    block_shape_list = [BlockI, BlockJ, BlockL, BlockO, BlockS, BlockT, BlockZ]

    def check_and_go_down(ti: TimeTracking, current_block: Block, next_block: Block):
        """Check if the block can go down and do it if it is possible.

        Args:
            ti (Time): Current time
            current_block (Tetris): Current block
            next_block (Tetris): Next block

        Returns:
            current_block, next_block: the updated blocks if the movement was possible, the same blocks otherwise.
        """
        if type(tetris.go(Move.DOWN, ti)) == list:
            current_block = next_block
            next_block = random.choice(block_shape_list)(tetris)
            tetris.start(ti, current_block)
        return current_block, next_block
    
    pygame.init()  # The coordinate (0, 0) is in the upper left.

    tetris = Tetris()
    db = DB()
    score_list = db.fetch_highest_score()
    ti = TimeTracking()

    font_score = pygame.font.SysFont("consolas", 30)  
    font_game_over = pygame.font.SysFont("ebrima", 100)  
    font_best = pygame.font.SysFont("consolas", 20) 
    font_average_time = pygame.font.SysFont("consolas", 15)  

    pygame.display.set_caption("Tetris")  # Title
    pygame.key.set_repeat(120)  # Control how held keys are repeated
    clock = pygame.time.Clock()  # Create an object to help track time

    mixer.init()
    mixer.music.load("resources/audio/580898__bloodpixelhero__in-game.wav")
    mixer.music.set_volume(0.04)
    mixer.music.play()

    for y in range(Y_LENGTH):  # Create blocks that make up the game screen
        for x in range(X_LENGTH):
            if x in [0, 11] or y == 20:  # The blocks that make up the boundary
                background_blocks[y][x] = BackgroundBlock(32 * x, 32 * y, 8, True)
            else:
                background_blocks[y][x] = BackgroundBlock(32 * x, 32 * y, 0, False)

    descent_var = 0

    current_block = random.choice(block_shape_list)(tetris)  # Randomly select one of the seven types of blocks
    next_block = random.choice(block_shape_list)(tetris)
    tetris.start(ti, current_block) # First block appears on the game screen

    running = True
    while running:
        SCREEN.fill(BLACK)  # Paint the SCREEN black before draw blocks on SCREEN
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    current_block.turn()
                elif event.key == pygame.K_DOWN:
                    descent_var = 0
                    current_block, next_block = check_and_go_down(ti, current_block, next_block)
                elif event.key == pygame.K_LEFT:
                    tetris.go(Move.LEFT, ti)
                elif event.key == pygame.K_RIGHT:
                    tetris.go(Move.RIGHT, ti)

        descent_var += 1
        if descent_var % DESCENT_SPEED == 0:
            current_block, next_block = check_and_go_down(ti, current_block, next_block)
            # The block automatically goes down If you don't press down key.

        score_info = font_score.render("Score : " + str(tetris.score), True, WHITE)
        SCREEN.blit(score_info, (387, 15))
        avg_time_info = font_average_time.render(f"Average time to put a block : {ti.avg_time:.2f}s", True, WHITE)
        SCREEN.blit(avg_time_info, (387, 55))
        best_time_info = font_best.render(f"Best : {score_list[0][0]} / {score_list[0][1]:.2f}", True, WHITE)
        SCREEN.blit(best_time_info, (387, 635))

        pygame.draw.rect(SCREEN, (211, 211, 211), pygame.Rect(32 * 14, 32 * 10, 32*5, 32*4), width=3)  # Border

        next_block.draw()  # Draw the next block to come out in the waiting area

        for x in range(1, 11):  # Color the boundaries of the blocks on the game screen
            for y in range(20):
                pygame.draw.rect(SCREEN, (161, 145, 61), pygame.Rect(32 * x, 32 * y, 32, 32), width=1)

        for y in range(Y_LENGTH):  # Color the blocks on the game screen
            for x in range(X_LENGTH):
                if background_blocks[y][x].number in range(1, 8):
                    BackgroundBlock.color_the_block(SCREEN, background_blocks[y][x].color, x, y)
                elif background_blocks[y][x].number == 8:
                    pygame.draw.rect(SCREEN, (128, 128, 128), pygame.Rect(32 * x, 32 * y, 32, 32))

        if tetris.gameover:
            pygame.draw.rect(SCREEN, BLACK, pygame.Rect(32 * 1, 32 * 3, 32 * 19, 32 * 15))
            pygame.draw.rect(SCREEN, WHITE, pygame.Rect(32 * 1, 32 * 3, 32 * 19, 32 * 15), width=3)
            gameover_text = font_game_over.render("GAME OVER!", True, WHITE)
            SCREEN.blit(gameover_text, (50, 220))
            score_info = font_score.render("Score : " + str(tetris.score), True, WHITE)
            SCREEN.blit(score_info, (70, 360))
            avg_time_info = font_average_time.render(f"Average time to put a block : {ti.avg_time:.2f}s", True, WHITE)
            SCREEN.blit(avg_time_info, (70, 400))
            gameover_sound = mixer.Sound("resources/audio/42349__irrlicht__game-over.wav")
            gameover_sound.set_volume(0.2)
            gameover_sound.play()
            pygame.display.flip()
            db.save_highest_score(tetris.score, ti.avg_time)
            pygame.time.wait(2000)
            running = False

        pygame.display.flip()  # It makes the screen to be updated continuously

        clock.tick(30)  # In main loop, it determine FPS

    pygame.quit()


if __name__ == "__main__":
    main()
