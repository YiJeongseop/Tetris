import random
import time
from enum import Enum

import pygame
from pygame import mixer

from db_and_time import DB, Time
from settings import SCREEN, BLACK, WHITE, SKY_BLUE, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED, DESCENT_SPEED

Move = Enum("Move", ["LEFT", "RIGHT", "DOWN"])

background_blocks = [[0 for j in range(0, 12)] for i in range(0, 21)]  # Game Screen consisting of 12 x 21 blocks


class BackgroundBlock:
    def __init__(self, x: int, y: int, number: int, not_block: bool):
        """
        Every block has a number.
        0 is not block, 1 to 7 is block, 8 is boundary.
        not_block shows whether this block is a boundary or an installed block.
        """
        super().__init__()
        self.x = x
        self.y = y
        self.number = number 
        self.not_block = not_block


class Tetris:
    score = 0
    gameover = False
    number_of_blocks = 0  # How many blocks were made?

    def __init__(self, block_number: int):
        self.block_number = block_number
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

    def start(self, ti: Time):
        Tetris.number_of_blocks += 1
        ti.start_time = time.time()

        def currentIter(block_number, blocks):
            for block in iter(blocks):  # What if there are no other blocks where they will be?
                block.number = block_number  # Create the blocks on the game screen
                yield block

        self.next_blocks.clear()

        # A lazily-evaluated map of background blocks. Used to fetch and place one in next_blocks.
        fetch_blocks_map = [
            lambda group: group[0][4:8],  # Block 1
            lambda group: [group[0][4], *group[1][4:7]],  # Block 2
            lambda group: [*group[1][4:7], group[0][6]],  # Block 3
            lambda group: [block for blocks in group[0:2] for block in blocks[5:7]],  # Block 4
            lambda group: [*group[1][4:6], *group[0][5:7]],  # Block 5
            lambda group: [group[0][5], *group[1][4:7]],  # Block 6
            lambda group: [*group[0][4:6], *group[1][5:7]],  # Block 7
        ]
        fetcher = fetch_blocks_map[self.block_number - 1]
        blocks = fetcher(background_blocks)
        self.next_blocks.extend(block.number for block in blocks)
        Tetris.gameover = self.gameover_state()
        if Tetris.gameover:
            return
        self.current_blocks.extend(currentIter(self.block_number, blocks))

    def go(self, move: Enum, ti: Time, break_sound: mixer.Sound, erase_sound: mixer.Sound):
        self.next_blocks.clear()

        if move in (Move.LEFT, Move.RIGHT):
            if move == Move.LEFT:
                adjust = -1
            else:
                adjust = 1
            for i in range(0, 4):
                self.next_blocks.append(background_blocks[self.current_blocks[i].y//32][(self.current_blocks[i].x//32)+adjust])
                if self.next_blocks[i].number in range(1, 9) and self.next_blocks[i].not_block:
                    return
        elif move == Move.DOWN:
            for i in range(0, 4):
                self.next_blocks.append(background_blocks[(self.current_blocks[i].y//32) + 1][(self.current_blocks[i].x//32)])  
                # Add background blocks in where the blocks are moving
                
                if self.next_blocks[i].number in range(1, 9) and self.next_blocks[i].not_block:  
                    # If there are blocks down there, stop
                    y_list = []
                    for j in range(0, 4):
                        self.current_blocks[j].not_block = True
                        y_list.append(self.current_blocks[j].y)
                    self.current_blocks.clear()
                    break_sound.play()
                    ti.update_time(time.time(), Tetris.number_of_blocks)
                    self.erase_line_plus_score(y_list, erase_sound)
                    return y_list

        self.clear()  # The block is now moving! Remove the background blocks color beforehand.
        for i in range(0, 4):
            self.current_blocks[i] = self.next_blocks[i]
            self.current_blocks[i].number = self.block_number

    def clear(self):
        for i in range(0, 4):
            self.current_blocks[i].number = 0
            pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_blocks[i].x, self.current_blocks[i].y, 32, 32))

    def turn(self):
        """
        Blocks check if there are blocks around them based on their location.
        Turn if there are no blocks around.
        """
        self.current_y_list.clear()
        self.current_x_list.clear()
        for i in range(0, 4):
            self.current_y_list.append(self.current_blocks[i].y//32)
            self.current_x_list.append(self.current_blocks[i].x//32)
    
    def erase_line_plus_score(self, y_list: list, erase_sound: mixer.Sound):
        """
        max_y is largest y-index of placed blocks.
        min_y is smallest y-index of placed blocks minus 1.
        Check that all horizontal lines are full.
        """
        max_y = max(y_list)//32 
        min_y = min(y_list)//32 - 1 
        while(max_y > min_y):
            count = 0
            for x in range(1, 11):
                if background_blocks[max_y][x].not_block is False:  # If any of the 10 blocks is empty
                    break
                count += 1
                if count == 10: 
                    erase_sound.play()
                    for x in range(1, 11):
                        background_blocks[max_y][x].not_block = False
                        background_blocks[max_y][x].number = 0
                        pygame.draw.rect(SCREEN, BLACK, pygame.Rect(background_blocks[max_y][x].x, background_blocks[max_y][x].y, 32, 32))

                    for y2 in range(max_y, 0, -1):
                        for x in range(1, 11):
                            background_blocks[y2][x].not_block = background_blocks[y2-1][x].not_block
                            background_blocks[y2][x].number = background_blocks[y2-1][x].number
                            background_blocks[y2-1][x].not_block = False
                            background_blocks[y2-1][x].number = 0
                            pygame.draw.rect(SCREEN, BLACK, pygame.Rect(background_blocks[y2-1][x].x, background_blocks[y2-1][x].y, 32, 32))

                    Tetris.score += 100
                    max_y += 1
                    min_y += 1
            max_y -= 1


class Block1(Tetris):
    def __init__(self):
        super().__init__(1)

    def turn(self):
        super().turn()

        if self.state == 1:
            if self.current_y_list[0] == 0:
                return
            for x in range(0, 4):
                if background_blocks[self.current_y_list[0] - 1][self.current_x_list[0] + x].not_block:
                    return
                if background_blocks[self.current_y_list[0] + 1][self.current_x_list[0] + x].not_block:
                    return
                if background_blocks[self.current_y_list[0] + 2][self.current_x_list[0] + x].not_block:
                    return

            self.clear()
            for y in range(0, 4):
                background_blocks[self.current_y_list[2] + 2 - y][self.current_x_list[2]].number = self.block_number
                self.current_blocks[y] = background_blocks[self.current_y_list[2] + 2 - y][self.current_x_list[2]]

        elif self.state == 2:
            for y in range(0, 4):
                if background_blocks[self.current_y_list[3] + y][self.current_x_list[0] - 1].not_block:
                    return
            for y in range(0, 4):
                if background_blocks[self.current_y_list[3] + y][self.current_x_list[0] + 1].not_block:
                    return
            for y in range(0, 4):
                if background_blocks[self.current_y_list[3] + y][self.current_x_list[0] - 2].not_block:
                    return

            self.clear()
            for x in range(0, 4):
                background_blocks[self.current_y_list[1]][self.current_x_list[1] + 1 - x].number = self.block_number
                self.current_blocks[x] = background_blocks[self.current_y_list[1]][self.current_x_list[1] + 1 - x]

        elif self.state == 3:
            for x in range(0, 4):
                if background_blocks[self.current_y_list[0] + 1][self.current_x_list[0] - x].not_block:
                    return
                if background_blocks[self.current_y_list[0] - 1][self.current_x_list[0] - x].not_block:
                    return
                if background_blocks[self.current_y_list[0] - 2][self.current_x_list[0] - x].not_block:
                    return

            self.clear()
            for y in range(0, 4):
                background_blocks[self.current_y_list[2] - 2 + y][self.current_x_list[2]].number = self.block_number
                self.current_blocks[y] = background_blocks[self.current_y_list[2] - 2 + y][self.current_x_list[2]]

        elif self.state == 4:
            for y in range(0, 4):
                if background_blocks[self.current_y_list[0] + y][self.current_x_list[0] - 1].not_block:
                    return
            for y in range(0, 4):
                if background_blocks[self.current_y_list[0] + y][self.current_x_list[0] + 1].not_block:
                    return
            for y in range(0, 4):
                if background_blocks[self.current_y_list[0] + y][self.current_x_list[0] + 2].not_block:
                    return

            self.clear()
            for x in range(0, 4):
                background_blocks[self.current_y_list[1]][self.current_x_list[1] - 1 + x].number = self.block_number
                self.current_blocks[x] = background_blocks[self.current_y_list[1]][self.current_x_list[1] - 1 + x]

        self.state += 1
        

class Block2(Tetris):
    def __init__(self):
        super().__init__(2)

    def turn(self):
        super().turn()

        if self.state == 1:
            for x in range(0, 3):
                if background_blocks[self.current_y_list[1] + 1][self.current_x_list[1] + x].not_block:
                    return
            for x in range(0, 2):
                if background_blocks[self.current_y_list[0]][self.current_x_list[0] + 1 + x].not_block:
                    return

            self.clear()
            background_blocks[self.current_y_list[0]][self.current_x_list[0] + 2].number = self.block_number
            self.current_blocks[0] = background_blocks[self.current_y_list[0]][self.current_x_list[0] + 2]
            for y in range(0, 3):
                background_blocks[self.current_y_list[2] - 1 + y][self.current_x_list[2]].number = self.block_number
                self.current_blocks[y + 1] = background_blocks[self.current_y_list[2] - 1 + y][self.current_x_list[2]]

        elif self.state == 2:
            for y in range(0, 3):
                if background_blocks[self.current_y_list[1] + y][self.current_x_list[1] - 1].not_block:
                    return
            for x in range(0, 2):
                if background_blocks[self.current_y_list[0] + 1 + y][self.current_x_list[0]].not_block:
                    return

            self.clear()
            background_blocks[self.current_y_list[0] + 2][self.current_x_list[0]].number = self.block_number
            self.current_blocks[0] = background_blocks[self.current_y_list[0] + 2][self.current_x_list[0]]
            for x in range(0, 3):
                background_blocks[self.current_y_list[0] + 1][self.current_x_list[0] - x].number = self.block_number
                self.current_blocks[x + 1] = background_blocks[self.current_y_list[0] + 1][self.current_x_list[0] - x]

        elif self.state == 3:
            for x in range(0, 3):
                if background_blocks[self.current_y_list[1] - 1][self.current_x_list[1] - x].not_block:
                    return
            for x in range(0, 2):
                if background_blocks[self.current_y_list[0]][self.current_x_list[0] - 1 + x].not_block:
                    return

            self.clear()
            background_blocks[self.current_y_list[0]][self.current_x_list[0] - 2].number = self.block_number
            self.current_blocks[0] = background_blocks[self.current_y_list[0]][self.current_x_list[0] - 2]
            for y in range(0, 3):
                background_blocks[self.current_y_list[2] + 1 - y][self.current_x_list[2]].number = self.block_number
                self.current_blocks[y + 1] = background_blocks[self.current_y_list[2] + 1 - y][self.current_x_list[2]]

        elif self.state == 4:
            for y in range(0, 3):
                if background_blocks[self.current_y_list[3] + y][self.current_x_list[1] + 1].not_block:
                    return
            for x in range(0, 2):
                if background_blocks[self.current_y_list[0] - 2 + y][self.current_x_list[0]].not_block:
                    return

            self.clear()
            background_blocks[self.current_y_list[0] - 2][self.current_x_list[0]].number = self.block_number
            self.current_blocks[0] = background_blocks[self.current_y_list[0] - 2][self.current_x_list[0]]
            for x in range(0, 3):
                background_blocks[self.current_y_list[0] - 1][self.current_x_list[0] + x].number = self.block_number
                self.current_blocks[x + 1] = background_blocks[self.current_y_list[0] - 1][self.current_x_list[0] + x]

        self.state += 1

        
class Block3(Tetris):
    def __init__(self):
        super().__init__(3)

    def turn(self):
        super().turn()

        if self.state == 1:
            for x in range(0, 3):
                if background_blocks[self.current_y_list[0] + 1][self.current_x_list[0] + x].not_block:
                    return
            for x in range(0, 2):
                if background_blocks[self.current_y_list[3]][self.current_x_list[3] - 2 + x].not_block:
                    return

            self.clear()
            for y in range(0, 3):
                background_blocks[self.current_y_list[1] - 1 + y][self.current_x_list[1]].number = self.block_number
                self.current_blocks[y] = background_blocks[self.current_y_list[1] - 1 + y][self.current_x_list[1]]
            background_blocks[self.current_y_list[2] + 1][self.current_x_list[2]].number = self.block_number
            self.current_blocks[3] = background_blocks[self.current_y_list[2] + 1][self.current_x_list[2]]

        elif self.state == 2:
            for y in range(0, 3):
                if background_blocks[self.current_y_list[0] + y][self.current_x_list[0] - 1].not_block:
                     return
            for y in range(0, 2):
                if background_blocks[self.current_y_list[0] + y][self.current_x_list[0] + 1].not_block:
                    return

            self.clear()
            for x in range(0, 3):
                background_blocks[self.current_y_list[1]][self.current_x_list[1] + 1 - x].number = self.block_number
                self.current_blocks[x] = background_blocks[self.current_y_list[1]][self.current_x_list[1] + 1 - x]
            background_blocks[self.current_y_list[2]][self.current_x_list[2] - 1].number = self.block_number
            self.current_blocks[3] = background_blocks[self.current_y_list[2]][self.current_x_list[2] - 1]

        elif self.state == 3:
            for x in range(0, 3):
                if background_blocks[self.current_y_list[2] - 1][self.current_x_list[2] + x].not_block:
                    return
            for x in range(0, 2):
                if background_blocks[self.current_y_list[3]][self.current_x_list[3] + 1 + x].not_block:
                    return

            self.clear()
            for y in range(0, 3):
                background_blocks[self.current_y_list[1] + 1 - y][self.current_x_list[1]].number = self.block_number
                self.current_blocks[y] = background_blocks[self.current_y_list[1] + 1 - y][self.current_x_list[1]]
            background_blocks[self.current_y_list[2] - 1][self.current_x_list[2]].number = self.block_number
            self.current_blocks[3] = background_blocks[self.current_y_list[2] - 1][self.current_x_list[2]]

        elif self.state == 4:
            for y in range(0, 3):
                if background_blocks[self.current_y_list[2] + y][self.current_x_list[0] + 1].not_block:
                    return
            for y in range(0, 2):
                if background_blocks[self.current_y_list[3] + 1 + y][self.current_x_list[3]].not_block:
                    return

            self.clear()
            for x in range(0, 3):
                background_blocks[self.current_y_list[1]][self.current_x_list[1] - 1 + x].number = self.block_number
                self.current_blocks[x] = background_blocks[self.current_y_list[1]][self.current_x_list[1] - 1 + x]
            background_blocks[self.current_y_list[2]][self.current_x_list[2] + 1].number = self.block_number
            self.current_blocks[3] = background_blocks[self.current_y_list[2]][self.current_x_list[2] + 1]

        self.state += 1
    

class Block4(Tetris):
    def __init__(self):
        super().__init__(4)
        

class Block5(Tetris):
    def __init__(self):
        super().__init__(5)

    def turn(self):
        super().turn()

        if self.state == 1:
            if self.current_y_list[2] == 0:
                return
            for x in range(0, 3):
                if background_blocks[self.current_y_list[2] - 1][self.current_x_list[0] + x].not_block:
                    return
            if background_blocks[self.current_y_list[0] - 1][self.current_x_list[0]].not_block:
                return
            if background_blocks[self.current_y_list[1]][self.current_x_list[1] + 1].not_block:
                return

            self.clear()
            for y in range(0, 2):
                background_blocks[self.current_y_list[0] - 2 + y][self.current_x_list[0]].number = self.block_number
                self.current_blocks[y] = background_blocks[self.current_y_list[0] - 2 + y][self.current_x_list[0]]
            for y in range(0, 2):
                background_blocks[self.current_y_list[1] - 1 + y][self.current_x_list[1]].number = self.block_number
                self.current_blocks[y + 2] = background_blocks[self.current_y_list[1] - 1 + y][self.current_x_list[1]]

        elif self.state == 2:
            for y in range(0, 3):
                if background_blocks[self.current_y_list[0] + y][self.current_x_list[2] + 1].not_block:
                    return
            if background_blocks[self.current_y_list[1] + 1][self.current_x_list[1]].not_block:
                return
            if background_blocks[self.current_y_list[2] - 1][self.current_x_list[2]].not_block:
                return

            self.clear()
            for x in range(0, 2):
                background_blocks[self.current_y_list[0]][self.current_x_list[0] + 2 - x].number = self.block_number
                self.current_blocks[x] = background_blocks[self.current_y_list[0]][self.current_x_list[0] + 2 - x]
            for x in range(0, 2):
                background_blocks[self.current_y_list[1]][self.current_x_list[1] + 1 - x].number = self.block_number
                self.current_blocks[x + 2] = background_blocks[self.current_y_list[1]][self.current_x_list[1] + 1 - x]

        elif self.state == 3:
            for x in range(0, 3):
                if background_blocks[self.current_y_list[2] + 1][self.current_x_list[3] + x].not_block:
                    return
            if background_blocks[self.current_y_list[0]][self.current_x_list[0] - 2].not_block:
                return
            if background_blocks[self.current_y_list[2]][self.current_x_list[0]].not_block:
                return

            self.clear()
            for y in range(0, 2):
                background_blocks[self.current_y_list[0] + 2 - y][self.current_x_list[0]].number = self.block_number
                self.current_blocks[y] = background_blocks[self.current_y_list[0] + 2 - y][self.current_x_list[0]]
            for y in range(0, 2):
                background_blocks[self.current_y_list[1] + 1 - y][self.current_x_list[1]].number = self.block_number
                self.current_blocks[y + 2] = background_blocks[self.current_y_list[1] + 1 - y][self.current_x_list[1]]

        elif self.state == 4:
            for y in range(0, 3):
                if background_blocks[self.current_y_list[0] - y][self.current_x_list[2] - 1].not_block:
                    return
            if background_blocks[self.current_y_list[1] - 1][self.current_x_list[1]].not_block:
                return
            if background_blocks[self.current_y_list[2] + 1][self.current_x_list[2]].not_block:
                return

            self.clear()
            for x in range(0, 2):
                background_blocks[self.current_y_list[0]][self.current_x_list[0] - 2 + x].number = self.block_number
                self.current_blocks[x] = background_blocks[self.current_y_list[0]][self.current_x_list[0] - 2 + x]
            for x in range(0, 2):
                background_blocks[self.current_y_list[1]][self.current_x_list[1] - 1 + x].number = self.block_number
                self.current_blocks[x + 2] = background_blocks[self.current_y_list[1]][self.current_x_list[1] - 1 + x]

        self.state += 1
        

class Block6(Tetris):
    def __init__(self):
        super().__init__(6)

    def turn(self):
        super().turn()

        if self.state == 1:
            for x in range(0, 3):
                if background_blocks[self.current_y_list[1] + 1][self.current_x_list[1] + x].not_block:
                    return
            if background_blocks[self.current_y_list[0]][self.current_x_list[1]].not_block:
                return
            if background_blocks[self.current_y_list[0]][self.current_x_list[3]].not_block:
                return

            self.clear()
            background_blocks[self.current_y_list[3]][self.current_x_list[3]].number = self.block_number
            self.current_blocks[0] = background_blocks[self.current_y_list[3]][self.current_x_list[3]]
            for y in range(0, 3):
                background_blocks[self.current_y_list[0] + y][self.current_x_list[0]].number = self.block_number
                self.current_blocks[y + 1] = background_blocks[self.current_y_list[0] + y][self.current_x_list[0]]

        elif self.state == 2:
            for y in range(0, 3):
                if background_blocks[self.current_y_list[1] + y][self.current_x_list[1] - 1].not_block:
                    return
            if background_blocks[self.current_y_list[0] - 1][self.current_x_list[0]].not_block:
                return
            if background_blocks[self.current_y_list[0] + 1][self.current_x_list[0]].not_block:
                return

            self.clear()
            background_blocks[self.current_y_list[3]][self.current_x_list[3]].number = self.block_number
            self.current_blocks[0] = background_blocks[self.current_y_list[3]][self.current_x_list[3]]
            for x in range(0, 3):
                background_blocks[self.current_y_list[0]][self.current_x_list[0] - x].number = self.block_number
                self.current_blocks[x + 1] = background_blocks[self.current_y_list[0]][self.current_x_list[0] - x]

        elif self.state == 3:
            for x in range(0, 3):
                if background_blocks[self.current_y_list[1] - 1][self.current_x_list[3] + x].not_block:
                    return
            if background_blocks[self.current_y_list[0]][self.current_x_list[0] - 1].not_block:
                return
            if background_blocks[self.current_y_list[0]][self.current_x_list[0] + 1].not_block:
                return

            self.clear()
            background_blocks[self.current_y_list[3]][self.current_x_list[3]].number = self.block_number
            self.current_blocks[0] = background_blocks[self.current_y_list[3]][self.current_x_list[3]]
            for y in range(0, 3):
                background_blocks[self.current_y_list[2] + 1 - y][self.current_x_list[0]].number = self.block_number
                self.current_blocks[y + 1] = background_blocks[self.current_y_list[2] + 1 - y][self.current_x_list[0]]

        elif self.state == 4:
            for y in range(0, 3):
                if background_blocks[self.current_y_list[3] + y][self.current_x_list[1] + 1].not_block:
                    return
            if background_blocks[self.current_y_list[0] - 1][self.current_x_list[0]].not_block:
                return
            if background_blocks[self.current_y_list[0] + 1][self.current_x_list[0]].not_block:
                return

            self.clear()
            background_blocks[self.current_y_list[3]][self.current_x_list[3]].number = self.block_number
            self.current_blocks[0] = background_blocks[self.current_y_list[3]][self.current_x_list[3]]
            for x in range(0, 3):
                background_blocks[self.current_y_list[0]][self.current_x_list[0] + x].number = self.block_number
                self.current_blocks[x + 1] = background_blocks[self.current_y_list[0]][self.current_x_list[0] + x]

        self.state += 1
        

class Block7(Tetris):
    def __init__(self):
        super().__init__(7)

    def turn(self):
        super().turn()

        if self.state == 1:
            if self.current_y_list[0] == 0:
                return
            for x in range(0, 3):
                if background_blocks[self.current_y_list[0] - 1][self.current_x_list[0] + x].not_block:
                    return
            if background_blocks[self.current_y_list[0]][self.current_x_list[3]].not_block:
                return
            if background_blocks[self.current_y_list[2]][self.current_x_list[0]].not_block:
                return

            self.clear()
            for y in range(0, 2):
                background_blocks[self.current_y_list[1] - 1 + y][self.current_x_list[1]].number = self.block_number
                self.current_blocks[y] = background_blocks[self.current_y_list[1] - 1 + y][self.current_x_list[1]]
            for y in range(0, 2):
                background_blocks[self.current_y_list[0] + y][self.current_x_list[0]].number = self.block_number
                self.current_blocks[y + 2] = background_blocks[self.current_y_list[0] + y][self.current_x_list[0]]

        elif self.state == 2:
            for y in range(0, 3):
                if background_blocks[self.current_y_list[0] + y][self.current_x_list[0] + 1].not_block:
                    return
            if background_blocks[self.current_y_list[0]][self.current_x_list[2]].not_block:
                return
            if background_blocks[self.current_y_list[3]][self.current_x_list[0]].not_block:
                return

            self.clear()
            for x in range(0, 2):
                background_blocks[self.current_y_list[1]][self.current_x_list[1] + 1 - x].number = self.block_number
                self.current_blocks[x] = background_blocks[self.current_y_list[1]][self.current_x_list[1] + 1 - x]
            for x in range(0, 2):
                background_blocks[self.current_y_list[0]][self.current_x_list[0] - x].number = self.block_number
                self.current_blocks[x + 2] = background_blocks[self.current_y_list[0]][self.current_x_list[0] - x]

        elif self.state == 3:
            for x in range(0, 3):
                if background_blocks[self.current_y_list[0] + 1][self.current_x_list[3] + x].not_block:
                    return
            if background_blocks[self.current_y_list[0]][self.current_x_list[3]].not_block:
                return
            if background_blocks[self.current_y_list[2]][self.current_x_list[0]].not_block:
                return

            self.clear()
            for y in range(0, 2):
                background_blocks[self.current_y_list[1] + 1 - y][self.current_x_list[1]].number = self.block_number
                self.current_blocks[y] = background_blocks[self.current_y_list[1] + 1 - y][self.current_x_list[1]]
            for y in range(0, 2):
                background_blocks[self.current_y_list[0] - y][self.current_x_list[0]].number = self.block_number
                self.current_blocks[y + 2] = background_blocks[self.current_y_list[0] - y][self.current_x_list[0]]

        elif self.state == 4:
            for y in range(0, 3):
                if background_blocks[self.current_y_list[3] + y][self.current_x_list[0] - 1].not_block:
                    return
            if background_blocks[self.current_y_list[0]][self.current_x_list[2]].not_block:
                return
            if background_blocks[self.current_y_list[3]][self.current_x_list[0]].not_block:
                return

            self.clear()
            for x in range(0, 2):
                background_blocks[self.current_y_list[1]][self.current_x_list[1] - 1 + x].number = self.block_number
                self.current_blocks[x] = background_blocks[self.current_y_list[1]][self.current_x_list[1] - 1 + x]
            for x in range(0, 2):
                background_blocks[self.current_y_list[0]][self.current_x_list[0] + x].number = self.block_number
                self.current_blocks[x + 2] = background_blocks[self.current_y_list[0]][self.current_x_list[0] + x]

        self.state += 1


def draw_block_to_wait(block_number: int):
    """
    Receive block_number as param.
    This number determines what the block will look like.
    Then, draw the next block in the waiting area.
    """
    if block_number == 1:
        for x in range(14, 18):
            pygame.draw.rect(SCREEN, SKY_BLUE, pygame.Rect(32 * x + 16, 32 * 12, 32, 32))

    elif block_number == 2:
        for x in range(15, 18):
            pygame.draw.rect(SCREEN, BLUE, pygame.Rect(32 * x, 32 * 12, 32, 32))
        pygame.draw.rect(SCREEN, BLUE, pygame.Rect(32 * 15, 32 * 11, 32, 32))

    elif block_number == 3:
        for x in range(15, 18):
            pygame.draw.rect(SCREEN, ORANGE, pygame.Rect(32 * x, 32 * 12, 32, 32))
        pygame.draw.rect(SCREEN, ORANGE, pygame.Rect(32 * 17, 32 * 11, 32, 32))

    elif block_number == 4:
        for x in range(15, 17):
            for y in range(11, 13):
                pygame.draw.rect(SCREEN, YELLOW, pygame.Rect(32 * x + 16, 32 * y, 32, 32))

    elif block_number == 5:
        for x in range(16, 18):
            pygame.draw.rect(SCREEN, GREEN, pygame.Rect(32 * x, 32 * 11, 32, 32))
        for x in range(15, 17):
            pygame.draw.rect(SCREEN, GREEN, pygame.Rect(32 * x, 32 * 12, 32, 32))

    elif block_number == 6:
        for x in range(15, 18):
            pygame.draw.rect(SCREEN, PURPLE, pygame.Rect(32 * x, 32 * 12, 32, 32))
        pygame.draw.rect(SCREEN, PURPLE, pygame.Rect(32 * 16, 32 * 11, 32, 32))

    elif block_number == 7:
        for x in range(15, 17):
            pygame.draw.rect(SCREEN, RED, pygame.Rect(32 * x, 32 * 11, 32, 32))
        for x in range(16, 18):
            pygame.draw.rect(SCREEN, RED, pygame.Rect(32 * x, 32 * 12, 32, 32))


def color_the_block(screen, coordinates: tuple, x: int, y: int):
    pygame.draw.rect(screen, coordinates, pygame.Rect(32 * x, 32 * y, 32, 32))
    pygame.draw.rect(screen, BLACK, pygame.Rect(32 * x, 32 * y, 32, 32), width=1)


def main():
    block_shape_list = [Block1, Block2, Block3, Block4, Block5, Block6, Block7]

    def check_and_go_down(ti: time, erase_sound: mixer.Sound, break_sound: mixer.Sound, current_block, next_block):  
        """
        Check if the block can go down and go down if possible.
        Return current_block and next_block,
        Because these are not global variables, they need to be updated.
        """
        if type(current_block.go(Move.DOWN, ti, erase_sound, break_sound)) == list:
            current_block = next_block
            next_block = random.choice(block_shape_list)() 
            current_block.start(ti)
        return current_block, next_block
    
    pygame.init()  # The coordinate (0, 0) is in the upper left.

    db = DB()
    score_list = db.fetch_highest_score()
    ti = Time()

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
    break_sound = mixer.Sound("resources/audio/202230__deraj__pop-sound.wav")
    break_sound.set_volume(0.2)
    gameover_sound = mixer.Sound("resources/audio/42349__irrlicht__game-over.wav")
    gameover_sound.set_volume(0.2)
    erase_sound = mixer.Sound("resources/audio/143607__dwoboyle__menu-interface-confirm-003.wav")
    erase_sound.set_volume(0.15)

    for y in range(0, 21):  # Create blocks that make up the game screen
        for x in range(0, 12):
            if x == 0 or x == 11 or y == 20:  # The blocks that make up the boundary
                background_blocks[y][x] = BackgroundBlock(32 * x, 32 * y, 8, True)
            else:
                background_blocks[y][x] = BackgroundBlock(32 * x, 32 * y, 0, False)

    descent_var = 0

    current_block = random.choice(block_shape_list)()  # Randomly select one of the seven types of blocks
    next_block = random.choice(block_shape_list)()
    current_block.start(ti)  # First block appears on the game screen

    running = True
    while running:
        SCREEN.fill(BLACK)  # Paint the SCREEN black before draw blocks on SCREEN
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if current_block.block_number != 4:  # Square block do not rotate.
                        current_block.turn()
                elif event.key == pygame.K_DOWN:
                    descent_var = 0
                    current_block, next_block = check_and_go_down(ti, erase_sound, break_sound, current_block, next_block)
                elif event.key == pygame.K_LEFT:
                    current_block.go(Move.LEFT, ti, erase_sound, break_sound)
                elif event.key == pygame.K_RIGHT:
                    current_block.go(Move.RIGHT, ti, erase_sound, break_sound)

        descent_var += 1
        if descent_var % DESCENT_SPEED == 0:
            current_block, next_block = check_and_go_down(ti, erase_sound, break_sound, current_block, next_block)  
            # The block automatically goes down If you don't press down key.

        text = font_score.render("Score : " + str(Tetris.score), True, WHITE)
        SCREEN.blit(text, (387, 15))
        text2 = font_average_time.render(f"Average time to put a block : {ti.avg_time:.2f}s", True, WHITE)
        SCREEN.blit(text2, (387, 55))
        text3 = font_best.render(f"Best : {score_list[0][0]} / {score_list[0][1]:.2f}", True, WHITE)
        SCREEN.blit(text3, (387, 635))

        pygame.draw.rect(SCREEN, (211, 211, 211), pygame.Rect(32 * 14, 32 * 10, 32*5, 32*4), width=3)  # Border

        draw_block_to_wait(next_block.block_number)  # Draw the next block to come out in the waiting area

        for x in range(1, 11):  # Color the boundaries of the blocks on the game screen
            for y in range(0, 20):
                pygame.draw.rect(SCREEN, (161, 145, 61), pygame.Rect(32 * x, 32 * y, 32, 32), width=1)

        for y in range(0, 21):  # Color the blocks on the game screen
            for x in range(0, 12):
                if background_blocks[y][x].number == 1:
                    color_the_block(SCREEN, SKY_BLUE, x, y)
                elif background_blocks[y][x].number == 2:
                    color_the_block(SCREEN, BLUE, x, y)
                elif background_blocks[y][x].number == 3:
                    color_the_block(SCREEN, ORANGE, x, y)
                elif background_blocks[y][x].number == 4:
                    color_the_block(SCREEN, YELLOW, x, y)
                elif background_blocks[y][x].number == 5:
                    color_the_block(SCREEN, GREEN, x, y)
                elif background_blocks[y][x].number == 6:
                    color_the_block(SCREEN, PURPLE, x, y)
                elif background_blocks[y][x].number == 7:
                    color_the_block(SCREEN, RED, x, y)
                elif background_blocks[y][x].number == 8:
                    pygame.draw.rect(SCREEN, (128, 128, 128), pygame.Rect(32 * x, 32 * y, 32, 32))

        if Tetris.gameover:
            pygame.draw.rect(SCREEN, BLACK, pygame.Rect(32 * 1, 32 * 3, 32 * 19, 32 * 15))
            pygame.draw.rect(SCREEN, WHITE, pygame.Rect(32 * 1, 32 * 3, 32 * 19, 32 * 15), width=3)
            gameover_text = font_game_over.render("GAME OVER!", True, WHITE)
            SCREEN.blit(gameover_text, (50, 220))
            text = font_score.render("Score : " + str(Tetris.score), True, WHITE)
            SCREEN.blit(text, (70, 360))
            text2 = font_average_time.render(f"Average time to put a block : {ti.avg_time:.2f}s", True, WHITE)
            SCREEN.blit(text2, (70, 400))
            gameover_sound.play()
            pygame.display.flip()
            db.save_highest_score(Tetris.score, ti.avg_time)
            pygame.time.wait(2000)
            running = False

        pygame.display.flip()  # It makes the screen to be updated continuously

        clock.tick(30)  # In main loop, it determine FPS

    pygame.quit()


if __name__ == "__main__":
    main()
