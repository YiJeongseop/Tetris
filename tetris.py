import os
import random
import sqlite3  # https://docs.python.org/3.8/library/sqlite3.html
import time
import pygame  # https://www.pygame.org/docs/
from pygame import mixer
from enum import Enum
from settings import DB_PATH, DB_NAME, SCREEN, BLACK, WHITE, SKY_BLUE, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED, DESCENT_SPEED

Move = Enum("Move", ["LEFT", "RIGHT", "DOWN"])


class BackgroundBlock:
    def __init__(self, x: int, y: int, number: int, done: bool):
        super().__init__()
        self.x = x
        self.y = y
        self.number = number  # 0 - Not block   1~7 - Block   8 - Boundary
        self.done = done  # Is this a boundary or installed blocks?


class Block:
    def __init__(self, block_number: int):
        self.block_number = block_number
        self.next_block_list = []  # There will be the next block in the waiting area. It's a list of that background blocks.
        self.current_block_list = []  # List of moving blocks
        self.current_y_list = []  # y-coordinate list of moving blocks
        self.current_x_list = []  # x-coordinate list of moving blocks
        self.state = 1  # You can turn the block four times. 1, 2, 3, 4

    def gameover_state(self):
        # What if there are other blocks where they will be?
        return any(i in self.next_block_list for i in range(1, 8))

    def start(self):
        global block_count
        block_count += 1
        global start_time
        start_time = time.time()
        global gameover

        def currentIter(block_number, blocks):
            for block in iter(blocks):  # What if there are no other blocks where they will be?
                block.number = block_number  # Create the blocks on the game SCREEN
                yield block

        self.next_block_list.clear()

        # A lazily-evaluated map of background blocks. Used to fetch and place one in next_block_list.
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
        blocks = fetcher(background_block_group)
        self.next_block_list.extend(block.number for block in blocks)
        gameover = self.gameover_state()
        if gameover:
            return
        self.current_block_list.extend(currentIter(self.block_number, blocks))

    def go(self, move: Enum):
        global average_time_to_put_a_block, total_time
        self.next_block_list.clear()

        if move in (Move.LEFT, Move.RIGHT):
            if move == Move.LEFT:
                adjust = -1
            else:
                adjust = 1
            for i in range(0, 4):
                self.next_block_list.append(background_block_group[self.current_block_list[i].y//32][(self.current_block_list[i].x//32)+adjust])
                if self.next_block_list[i].number in range(1, 9) and self.next_block_list[i].done:
                    return
        elif move == Move.DOWN:
            for i in range(0, 4):
                self.next_block_list.append(background_block_group[(self.current_block_list[i].y//32) + 1][(self.current_block_list[i].x//32)])  # Add background blocks in where the blocks are moving
                if self.next_block_list[i].number in range(1, 9) and self.next_block_list[i].done:  # If there are blocks down there, stop
                    y_list = []
                    for j in range(0, 4):
                        self.current_block_list[j].done = True
                        y_list.append(self.current_block_list[j].y)
                    self.current_block_list.clear()
                    break_sound.play()
                    end_time = time.time() - start_time
                    total_time += end_time
                    average_time_to_put_a_block = total_time / block_count
                    erase_line(y_list)
                    return y_list

        for i in range(0, 4):  # The block is now moving! Remove the background blocks color beforehand.
            self.current_block_list[i].number = 0
            pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

        for i in range(0, 4):
            self.current_block_list[i] = self.next_block_list[i]
            self.current_block_list[i].number = self.block_number

    def turn(self):  # There are so many codes. I am sad that I am not able to reduce this.
        self.current_y_list.clear()
        self.current_x_list.clear()
        for i in range(0, 4):
            self.current_y_list.append(self.current_block_list[i].y//32)
            self.current_x_list.append(self.current_block_list[i].x//32)

        if self.block_number == 1:
            if self.state == 1:
                if self.current_y_list[0] == 0:
                    return
                for x in range(0, 4):
                    if background_block_group[self.current_y_list[0] - 1][self.current_x_list[0] + x].done is True:
                        return
                    if background_block_group[self.current_y_list[0] + 1][self.current_x_list[0] + x].done is True:
                        return
                    if background_block_group[self.current_y_list[0] + 2][self.current_x_list[0] + x].done is True:
                        return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                for y in range(0, 4):
                    background_block_group[self.current_y_list[2] + 2 - y][self.current_x_list[2]].number = self.block_number
                    self.current_block_list[y] = background_block_group[self.current_y_list[2] + 2 - y][self.current_x_list[2]]

                self.state = 2

            elif self.state == 2:
                for y in range(0, 4):
                    if background_block_group[self.current_y_list[3] + y][self.current_x_list[0] - 1].done is True:
                        return
                for y in range(0, 4):
                    if background_block_group[self.current_y_list[3] + y][self.current_x_list[0] + 1].done is True:
                        return
                for y in range(0, 4):
                    if background_block_group[self.current_y_list[3] + y][self.current_x_list[0] - 2].done is True:
                        return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                for x in range(0, 4):
                    background_block_group[self.current_y_list[1]][self.current_x_list[1] + 1 - x].number = self.block_number
                    self.current_block_list[x] = background_block_group[self.current_y_list[1]][self.current_x_list[1] + 1 - x]

                self.state = 3

            elif self.state == 3:
                for x in range(0, 4):
                    if background_block_group[self.current_y_list[0] + 1][self.current_x_list[0] - x].done is True:
                        return
                    if background_block_group[self.current_y_list[0] - 1][self.current_x_list[0] - x].done is True:
                        return
                    if background_block_group[self.current_y_list[0] - 2][self.current_x_list[0] - x].done is True:
                        return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                for y in range(0, 4):
                    background_block_group[self.current_y_list[2] - 2 + y][self.current_x_list[2]].number = self.block_number
                    self.current_block_list[y] = background_block_group[self.current_y_list[2] - 2 + y][self.current_x_list[2]]

                self.state = 4

            elif self.state == 4:
                for y in range(0, 4):
                    if background_block_group[self.current_y_list[0] + y][self.current_x_list[0] - 1].done is True:
                        return
                for y in range(0, 4):
                    if background_block_group[self.current_y_list[0] + y][self.current_x_list[0] + 1].done is True:
                        return
                for y in range(0, 4):
                    if background_block_group[self.current_y_list[0] + y][self.current_x_list[0] + 2].done is True:
                        return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                for x in range(0, 4):
                    background_block_group[self.current_y_list[1]][self.current_x_list[1] - 1 + x].number = self.block_number
                    self.current_block_list[x] = background_block_group[self.current_y_list[1]][self.current_x_list[1] - 1 + x]

                self.state = 1

        elif self.block_number == 2:
            if self.state == 1:
                for x in range(0, 3):
                    if background_block_group[self.current_y_list[1] + 1][self.current_x_list[1] + x].done is True:
                        return
                for x in range(0, 2):
                    if background_block_group[self.current_y_list[0]][self.current_x_list[0] + 1 + x].done is True:
                        return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                background_block_group[self.current_y_list[0]][self.current_x_list[0] + 2].number = self.block_number
                self.current_block_list[0] = background_block_group[self.current_y_list[0]][self.current_x_list[0] + 2]
                for y in range(0, 3):
                    background_block_group[self.current_y_list[2] - 1 + y][self.current_x_list[2]].number = self.block_number
                    self.current_block_list[y + 1] = background_block_group[self.current_y_list[2] - 1 + y][self.current_x_list[2]]

                self.state = 2

            elif self.state == 2:
                for y in range(0, 3):
                    if background_block_group[self.current_y_list[1] + y][self.current_x_list[1] - 1].done is True:
                        return
                for x in range(0, 2):
                    if background_block_group[self.current_y_list[0] + 1 + y][self.current_x_list[0]].done is True:
                        return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                background_block_group[self.current_y_list[0] + 2][self.current_x_list[0]].number = self.block_number
                self.current_block_list[0] = background_block_group[self.current_y_list[0] + 2][self.current_x_list[0]]
                for x in range(0, 3):
                    background_block_group[self.current_y_list[0] + 1][self.current_x_list[0] - x].number = self.block_number
                    self.current_block_list[x + 1] = background_block_group[self.current_y_list[0] + 1][self.current_x_list[0] - x]

                self.state = 3

            elif self.state == 3:
                for x in range(0, 3):
                    if background_block_group[self.current_y_list[1] - 1][self.current_x_list[1] - x].done is True:
                        return
                for x in range(0, 2):
                    if background_block_group[self.current_y_list[0]][self.current_x_list[0] - 1 + x].done is True:
                        return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                background_block_group[self.current_y_list[0]][self.current_x_list[0] - 2].number = self.block_number
                self.current_block_list[0] = background_block_group[self.current_y_list[0]][self.current_x_list[0] - 2]
                for y in range(0, 3):
                    background_block_group[self.current_y_list[2] + 1 - y][self.current_x_list[2]].number = self.block_number
                    self.current_block_list[y + 1] = background_block_group[self.current_y_list[2] + 1 - y][self.current_x_list[2]]

                self.state = 4

            elif self.state == 4:
                for y in range(0, 3):
                    if background_block_group[self.current_y_list[3] + y][self.current_x_list[1] + 1].done is True:
                        return
                for x in range(0, 2):
                    if background_block_group[self.current_y_list[0] - 2 + y][self.current_x_list[0]].done is True:
                        return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                background_block_group[self.current_y_list[0] - 2][self.current_x_list[0]].number = self.block_number
                self.current_block_list[0] = background_block_group[self.current_y_list[0] - 2][self.current_x_list[0]]
                for x in range(0, 3):
                    background_block_group[self.current_y_list[0] - 1][self.current_x_list[0] + x].number = self.block_number
                    self.current_block_list[x + 1] = background_block_group[self.current_y_list[0] - 1][self.current_x_list[0] + x]

                self.state = 1

        elif self.block_number == 3:
            if self.state == 1:
                for x in range(0, 3):
                    if background_block_group[self.current_y_list[0] + 1][self.current_x_list[0] + x].done is True:
                        return
                for x in range(0, 2):
                    if background_block_group[self.current_y_list[3]][self.current_x_list[3] - 2 + x].done is True:
                        return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                for y in range(0, 3):
                    background_block_group[self.current_y_list[1] - 1 + y][self.current_x_list[1]].number = self.block_number
                    self.current_block_list[y] = background_block_group[self.current_y_list[1] - 1 + y][self.current_x_list[1]]
                background_block_group[self.current_y_list[2] + 1][self.current_x_list[2]].number = self.block_number
                self.current_block_list[3] = background_block_group[self.current_y_list[2] + 1][self.current_x_list[2]]

                self.state = 2

            elif self.state == 2:
                for y in range(0, 3):
                    if background_block_group[self.current_y_list[0] + y][self.current_x_list[0] - 1].done is True:
                        return
                for y in range(0, 2):
                    if background_block_group[self.current_y_list[0] + y][self.current_x_list[0] + 1].done is True:
                        return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                for x in range(0, 3):
                    background_block_group[self.current_y_list[1]][self.current_x_list[1] + 1 - x].number = self.block_number
                    self.current_block_list[x] = background_block_group[self.current_y_list[1]][self.current_x_list[1] + 1 - x]
                background_block_group[self.current_y_list[2]][self.current_x_list[2] - 1].number = self.block_number
                self.current_block_list[3] = background_block_group[self.current_y_list[2]][self.current_x_list[2] - 1]

                self.state = 3

            elif self.state == 3:
                for x in range(0, 3):
                    if background_block_group[self.current_y_list[2] - 1][self.current_x_list[2] + x].done is True:
                        return
                for x in range(0, 2):
                    if background_block_group[self.current_y_list[3]][self.current_x_list[3] + 1 + x].done is True:
                        return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                for y in range(0, 3):
                    background_block_group[self.current_y_list[1] + 1 - y][self.current_x_list[1]].number = self.block_number
                    self.current_block_list[y] = background_block_group[self.current_y_list[1] + 1 - y][self.current_x_list[1]]
                background_block_group[self.current_y_list[2] - 1][self.current_x_list[2]].number = self.block_number
                self.current_block_list[3] = background_block_group[self.current_y_list[2] - 1][self.current_x_list[2]]

                self.state = 4

            elif self.state == 4:
                for y in range(0, 3):
                    if background_block_group[self.current_y_list[2] + y][self.current_x_list[0] + 1].done is True:
                        return
                for y in range(0, 2):
                    if background_block_group[self.current_y_list[3] + 1 + y][self.current_x_list[3]].done is True:
                        return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                for x in range(0, 3):
                    background_block_group[self.current_y_list[1]][self.current_x_list[1] - 1 + x].number = self.block_number
                    self.current_block_list[x] = background_block_group[self.current_y_list[1]][self.current_x_list[1] - 1 + x]
                background_block_group[self.current_y_list[2]][self.current_x_list[2] + 1].number = self.block_number
                self.current_block_list[3] = background_block_group[self.current_y_list[2]][self.current_x_list[2] + 1]

                self.state = 1

        elif self.block_number == 5:
            if self.state == 1:
                if self.current_y_list[2] == 0:
                    return
                for x in range(0, 3):
                    if background_block_group[self.current_y_list[2] - 1][self.current_x_list[0] + x].done is True:
                        return
                if background_block_group[self.current_y_list[0] - 1][self.current_x_list[0]].done is True:
                    return
                if background_block_group[self.current_y_list[1]][self.current_x_list[1] + 1].done is True:
                    return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                for y in range(0, 2):
                    background_block_group[self.current_y_list[0] - 2 + y][self.current_x_list[0]].number = self.block_number
                    self.current_block_list[y] = background_block_group[self.current_y_list[0] - 2 + y][self.current_x_list[0]]
                for y in range(0, 2):
                    background_block_group[self.current_y_list[1] - 1 + y][self.current_x_list[1]].number = self.block_number
                    self.current_block_list[y + 2] = background_block_group[self.current_y_list[1] - 1 + y][self.current_x_list[1]]

                self.state = 2

            elif self.state == 2:
                for y in range(0, 3):
                    if background_block_group[self.current_y_list[0] + y][self.current_x_list[2] + 1].done is True:
                        return
                if background_block_group[self.current_y_list[1] + 1][self.current_x_list[1]].done is True:
                    return
                if background_block_group[self.current_y_list[2] - 1][self.current_x_list[2]].done is True:
                    return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                for x in range(0, 2):
                    background_block_group[self.current_y_list[0]][self.current_x_list[0] + 2 - x].number = self.block_number
                    self.current_block_list[x] = background_block_group[self.current_y_list[0]][self.current_x_list[0] + 2 - x]
                for x in range(0, 2):
                    background_block_group[self.current_y_list[1]][self.current_x_list[1] + 1 - x].number = self.block_number
                    self.current_block_list[x + 2] = background_block_group[self.current_y_list[1]][self.current_x_list[1] + 1 - x]

                self.state = 3

            elif self.state == 3:
                for x in range(0, 3):
                    if background_block_group[self.current_y_list[2] + 1][self.current_x_list[3] + x].done is True:
                        return
                if background_block_group[self.current_y_list[0]][self.current_x_list[0] - 2].done is True:
                    return
                if background_block_group[self.current_y_list[2]][self.current_x_list[0]].done is True:
                    return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                for y in range(0, 2):
                    background_block_group[self.current_y_list[0] + 2 - y][self.current_x_list[0]].number = self.block_number
                    self.current_block_list[y] = background_block_group[self.current_y_list[0] + 2 - y][self.current_x_list[0]]
                for y in range(0, 2):
                    background_block_group[self.current_y_list[1] + 1 - y][self.current_x_list[1]].number = self.block_number
                    self.current_block_list[y + 2] = background_block_group[self.current_y_list[1] + 1 - y][self.current_x_list[1]]

                self.state = 4

            elif self.state == 4:
                for y in range(0, 3):
                    if background_block_group[self.current_y_list[0] - y][self.current_x_list[2] - 1].done is True:
                        return
                if background_block_group[self.current_y_list[1] - 1][self.current_x_list[1]].done is True:
                    return
                if background_block_group[self.current_y_list[2] + 1][self.current_x_list[2]].done is True:
                    return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                for x in range(0, 2):
                    background_block_group[self.current_y_list[0]][self.current_x_list[0] - 2 + x].number = self.block_number
                    self.current_block_list[x] = background_block_group[self.current_y_list[0]][self.current_x_list[0] - 2 + x]
                for x in range(0, 2):
                    background_block_group[self.current_y_list[1]][self.current_x_list[1] - 1 + x].number = self.block_number
                    self.current_block_list[x + 2] = background_block_group[self.current_y_list[1]][self.current_x_list[1] - 1 + x]

                self.state = 1

        elif self.block_number == 6:
            if self.state == 1:
                for x in range(0, 3):
                    if background_block_group[self.current_y_list[1] + 1][self.current_x_list[1] + x].done is True:
                        return
                if background_block_group[self.current_y_list[0]][self.current_x_list[1]].done is True:
                    return
                if background_block_group[self.current_y_list[0]][self.current_x_list[3]].done is True:
                    return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                background_block_group[self.current_y_list[3]][self.current_x_list[3]].number = self.block_number
                self.current_block_list[0] = background_block_group[self.current_y_list[3]][self.current_x_list[3]]
                for y in range(0, 3):
                    background_block_group[self.current_y_list[0] + y][self.current_x_list[0]].number = self.block_number
                    self.current_block_list[y + 1] = background_block_group[self.current_y_list[0] + y][self.current_x_list[0]]

                self.state = 2

            elif self.state == 2:
                for y in range(0, 3):
                    if background_block_group[self.current_y_list[1] + y][self.current_x_list[1] - 1].done is True:
                        return
                if background_block_group[self.current_y_list[0] - 1][self.current_x_list[0]].done is True:
                    return
                if background_block_group[self.current_y_list[0] + 1][self.current_x_list[0]].done is True:
                    return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                background_block_group[self.current_y_list[3]][self.current_x_list[3]].number = self.block_number
                self.current_block_list[0] = background_block_group[self.current_y_list[3]][self.current_x_list[3]]
                for x in range(0, 3):
                    background_block_group[self.current_y_list[0]][self.current_x_list[0] - x].number = self.block_number
                    self.current_block_list[x + 1] = background_block_group[self.current_y_list[0]][self.current_x_list[0] - x]

                self.state = 3

            elif self.state == 3:
                for x in range(0, 3):
                    if background_block_group[self.current_y_list[1] - 1][self.current_x_list[3] + x].done is True:
                        return
                if background_block_group[self.current_y_list[0]][self.current_x_list[0] - 1].done is True:
                    return
                if background_block_group[self.current_y_list[0]][self.current_x_list[0] + 1].done is True:
                    return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                background_block_group[self.current_y_list[3]][self.current_x_list[3]].number = self.block_number
                self.current_block_list[0] = background_block_group[self.current_y_list[3]][self.current_x_list[3]]
                for y in range(0, 3):
                    background_block_group[self.current_y_list[2] + 1 - y][self.current_x_list[0]].number = self.block_number
                    self.current_block_list[y + 1] = background_block_group[self.current_y_list[2] + 1 - y][self.current_x_list[0]]

                self.state = 4

            elif self.state == 4:
                for y in range(0, 3):
                    if background_block_group[self.current_y_list[3] + y][self.current_x_list[1] + 1].done is True:
                        return
                if background_block_group[self.current_y_list[0] - 1][self.current_x_list[0]].done is True:
                    return
                if background_block_group[self.current_y_list[0] + 1][self.current_x_list[0]].done is True:
                    return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                background_block_group[self.current_y_list[3]][self.current_x_list[3]].number = self.block_number
                self.current_block_list[0] = background_block_group[self.current_y_list[3]][self.current_x_list[3]]
                for x in range(0, 3):
                    background_block_group[self.current_y_list[0]][self.current_x_list[0] + x].number = self.block_number
                    self.current_block_list[x + 1] = background_block_group[self.current_y_list[0]][self.current_x_list[0] + x]

                self.state = 1

        elif self.block_number == 7:
            if self.state == 1:
                if self.current_y_list[0] == 0:
                    return
                for x in range(0, 3):
                    if background_block_group[self.current_y_list[0] - 1][self.current_x_list[0] + x].done is True:
                        return
                if background_block_group[self.current_y_list[0]][self.current_x_list[3]].done is True:
                    return
                if background_block_group[self.current_y_list[2]][self.current_x_list[0]].done is True:
                    return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                for y in range(0, 2):
                    background_block_group[self.current_y_list[1] - 1 + y][self.current_x_list[1]].number = self.block_number
                    self.current_block_list[y] = background_block_group[self.current_y_list[1] - 1 + y][self.current_x_list[1]]
                for y in range(0, 2):
                    background_block_group[self.current_y_list[0] + y][self.current_x_list[0]].number = self.block_number
                    self.current_block_list[y + 2] = background_block_group[self.current_y_list[0] + y][self.current_x_list[0]]

                self.state = 2

            elif self.state == 2:
                for y in range(0, 3):
                    if background_block_group[self.current_y_list[0] + y][self.current_x_list[0] + 1].done is True:
                        return
                if background_block_group[self.current_y_list[0]][self.current_x_list[2]].done is True:
                    return
                if background_block_group[self.current_y_list[3]][self.current_x_list[0]].done is True:
                    return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                for x in range(0, 2):
                    background_block_group[self.current_y_list[1]][self.current_x_list[1] + 1 - x].number = self.block_number
                    self.current_block_list[x] = background_block_group[self.current_y_list[1]][self.current_x_list[1] + 1 - x]
                for x in range(0, 2):
                    background_block_group[self.current_y_list[0]][self.current_x_list[0] - x].number = self.block_number
                    self.current_block_list[x + 2] = background_block_group[self.current_y_list[0]][self.current_x_list[0] - x]

                self.state = 3

            elif self.state == 3:
                for x in range(0, 3):
                    if background_block_group[self.current_y_list[0] + 1][self.current_x_list[3] + x].done is True:
                        return
                if background_block_group[self.current_y_list[0]][self.current_x_list[3]].done is True:
                    return
                if background_block_group[self.current_y_list[2]][self.current_x_list[0]].done is True:
                    return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                for y in range(0, 2):
                    background_block_group[self.current_y_list[1] + 1 - y][self.current_x_list[1]].number = self.block_number
                    self.current_block_list[y] = background_block_group[self.current_y_list[1] + 1 - y][self.current_x_list[1]]
                for y in range(0, 2):
                    background_block_group[self.current_y_list[0] - y][self.current_x_list[0]].number = self.block_number
                    self.current_block_list[y + 2] = background_block_group[self.current_y_list[0] - y][self.current_x_list[0]]

                self.state = 4

            elif self.state == 4:
                for y in range(0, 3):
                    if background_block_group[self.current_y_list[3] + y][self.current_x_list[0] - 1].done is True:
                        return
                if background_block_group[self.current_y_list[0]][self.current_x_list[2]].done is True:
                    return
                if background_block_group[self.current_y_list[3]][self.current_x_list[0]].done is True:
                    return

                for i in range(0, 4):
                    self.current_block_list[i].number = 0
                    pygame.draw.rect(SCREEN, BLACK, pygame.Rect(self.current_block_list[i].x, self.current_block_list[i].y, 32, 32))

                for x in range(0, 2):
                    background_block_group[self.current_y_list[1]][self.current_x_list[1] - 1 + x].number = self.block_number
                    self.current_block_list[x] = background_block_group[self.current_y_list[1]][self.current_x_list[1] - 1 + x]
                for x in range(0, 2):
                    background_block_group[self.current_y_list[0]][self.current_x_list[0] + x].number = self.block_number
                    self.current_block_list[x + 2] = background_block_group[self.current_y_list[0]][self.current_x_list[0] + x]

                self.state = 1


def next_block_draw(block_number: int):
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


def erase_line(y_list: list):
    max_y = max(y_list)//32  # Largest y-index of a placed block
    min_y = min(y_list)//32 - 1  # Smallest y-index of a placed block - 1
    while(max_y > min_y):
        count = 0
        for x in range(1, 11):
            if background_block_group[max_y][x].done is False:  # If any of the 10 blocks is empty, leave the loop
                break
            count += 1
            if count == 10:  # A line is full
                plus_score(max_y)  # Let's add points, erase one line, and Drop on every other line
                max_y += 1
                min_y += 1
        max_y -= 1


def plus_score(y: int):
    global score
    erase_sound.play()

    for x in range(1, 11):
        background_block_group[y][x].done = False  # Change the status of the background blocks
        background_block_group[y][x].number = 0
        pygame.draw.rect(SCREEN, BLACK, pygame.Rect(background_block_group[y][x].x, background_block_group[y][x].y, 32, 32))

    for y2 in range(y, 0, -1):  # Drop on every other line
        for x in range(1, 11):
            background_block_group[y2][x].done = background_block_group[y2-1][x].done
            background_block_group[y2][x].number = background_block_group[y2-1][x].number
            background_block_group[y2-1][x].done = False
            background_block_group[y2-1][x].number = 0
            pygame.draw.rect(SCREEN, BLACK, pygame.Rect(background_block_group[y2-1][x].x, background_block_group[y2-1][x].y, 32, 32))

    score += 100


def check_and_go_down():  # Check if the block can go down and go down if possible
    global current_block, next_block
    if type(current_block.go(Move.DOWN)) == list:
        current_block = next_block
        next_block = Block(random.randint(1, 7))
        current_block.start()


def color_the_block(screen, coordinates: tuple, x: int, y: int):
    pygame.draw.rect(screen, coordinates, pygame.Rect(32 * x, 32 * y, 32, 32))
    pygame.draw.rect(screen, BLACK, pygame.Rect(32 * x, 32 * y, 32, 32), width=1)


score = 0
gameover = False
average_time_to_put_a_block = 0
block_count = 0  # How many blocks were made?
total_time = 0  # Total time it took to put a block
start_time = 0  # Time when the block was first created
current_block = Block(random.randint(1, 7))  # Randomly select one of the seven types of blocks
next_block = Block(random.randint(1, 7))

background_block_group = [[0 for j in range(0, 12)] for i in range(0, 21)]  # Game SCREEN consisting of 12 x 21 blocks
for y in range(0, 21):  # Create blocks that make up the game SCREEN
    for x in range(0, 12):
        if x == 0 or x == 11 or y == 20:  # The blocks that make up the boundary
            background_block_group[y][x] = BackgroundBlock(32 * x, 32 * y, 8, True)
        else:
            background_block_group[y][x] = BackgroundBlock(32 * x, 32 * y, 0, False)

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

def main():
    pygame.init()  # The coordinate (0, 0) is in the upper left.

    autotime_down = 0  # Variable to control block down speed

    if os.path.isfile(DB_PATH) is not True:
        con = sqlite3.connect(DB_NAME)  # Create Connection Object
        cur = con.cursor()  # You must create a Cursor Object before execute() can be called.
        cur.execute("CREATE TABLE HighestScore (Score, AverageTimeToPutABlock)")  # Since the file does not exist, create a table
        cur.execute("INSERT INTO HighestScore (Score, AverageTimeToPutABlock) VALUES (0, 0)")  # and insert 0, 0
        con.commit()  # Save (commit) the changes
    else:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

    cur.execute("SELECT * FROM HighestScore ORDER BY Score DESC")
    score_list = cur.fetchall()  # Fetches all (remaining) rows of a query result, returning a list

    pygame.key.set_repeat(120)  # Control how held keys are repeated

    font_score = pygame.font.SysFont("consolas", 30) # "Score"
    font_game_over = pygame.font.SysFont("ebrima", 100) # "GAME OVER"
    font_best = pygame.font.SysFont("consolas", 20) # "Best"
    font_average_time = pygame.font.SysFont("consolas", 15) # "Average time to put a block"

    pygame.display.set_caption("Tetris")  # Title

    clock = pygame.time.Clock()  # Create an object to help track time

    current_block.start()  # First block appears on the game SCREEN!

    running = True
    while running:  # Main loop
        SCREEN.fill(BLACK)  # Paint the SCREEN black before draw blocks on SCREEN
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if current_block.block_number != 4:  # Square blocks do not rotate.
                        current_block.turn()
                elif event.key == pygame.K_DOWN:
                    autotime_down = 0
                    check_and_go_down()
                elif event.key == pygame.K_LEFT:
                    current_block.go(Move.LEFT)
                elif event.key == pygame.K_RIGHT:
                    current_block.go(Move.RIGHT)

        autotime_down += 1
        if autotime_down % DESCENT_SPEED == 0:
            check_and_go_down()  # The block automatically goes down If you don't press down key.

        text = font_score.render("Score : " + str(score), True, WHITE)
        SCREEN.blit(text, (387, 15))
        text2 = font_average_time.render(f"Average time to put a block : {average_time_to_put_a_block:.2f}s", True, WHITE)
        SCREEN.blit(text2, (387, 55))
        text3 = font_best.render(f"Best : {score_list[0][0]} / {score_list[0][1]:.2f}", True, WHITE)
        SCREEN.blit(text3, (387, 635))

        pygame.draw.rect(SCREEN, (211, 211, 211), pygame.Rect(32 * 14, 32 * 10, 32*5, 32*4), width=3)  # Border where the next block waits

        next_block_draw(next_block.block_number)  # Draw the next block to come out in the waiting area

        for x in range(1, 11):  # Color the boundaries of the blocks on the game SCREEN
            for y in range(0, 20):
                pygame.draw.rect(SCREEN, (161, 145, 61), pygame.Rect(32 * x, 32 * y, 32, 32), width=1)

        for y in range(0, 21):  # Color the blocks on the game SCREEN
            for x in range(0, 12):
                if background_block_group[y][x].number == 1:
                    color_the_block(SCREEN, SKY_BLUE, x, y)
                elif background_block_group[y][x].number == 2:
                    color_the_block(SCREEN, BLUE, x, y)
                elif background_block_group[y][x].number == 3:
                    color_the_block(SCREEN, ORANGE, x, y)
                elif background_block_group[y][x].number == 4:
                    color_the_block(SCREEN, YELLOW, x, y)
                elif background_block_group[y][x].number == 5:
                    color_the_block(SCREEN, GREEN, x, y)
                elif background_block_group[y][x].number == 6:
                    color_the_block(SCREEN, PURPLE, x, y)
                elif background_block_group[y][x].number == 7:
                    color_the_block(SCREEN, RED, x, y)
                elif background_block_group[y][x].number == 8:
                    pygame.draw.rect(SCREEN, (128, 128, 128), pygame.Rect(32 * x, 32 * y, 32, 32))

        if gameover is True:
            pygame.draw.rect(SCREEN, BLACK, pygame.Rect(32 * 1, 32 * 3, 32 * 19, 32 * 15))
            pygame.draw.rect(SCREEN, WHITE, pygame.Rect(32 * 1, 32 * 3, 32 * 19, 32 * 15), width=3)
            gameover_text = font_game_over.render("GAME OVER!", True, WHITE)
            SCREEN.blit(gameover_text, (50, 220))
            text = font_score.render("Score : " + str(score), True, WHITE)
            SCREEN.blit(text, (70, 360))
            text2 = font_average_time.render(f"Average time to put a block : {average_time_to_put_a_block:.2f}s", True, WHITE)
            SCREEN.blit(text2, (70, 400))
            gameover_sound.play()
            pygame.display.flip()
            cur.execute(f"INSERT INTO HighestScore VALUES ({score}, {average_time_to_put_a_block})")
            con.commit()
            pygame.time.wait(2000)
            running = False

        pygame.display.flip()  # It makes the SCREEN to be updated continuously

        clock.tick(30)  # In main loop, it determine FPS

    pygame.quit()


if __name__ == "__main__":
    main()