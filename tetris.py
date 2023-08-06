import os
import random
import sqlite3  # https://docs.python.org/3.8/library/sqlite3.html
import time

import pygame  # https://www.pygame.org/docs/
from pygame import mixer

from settings import DB_PATH, DB_NAME


class BackgroundBlock:
    def __init__(self, x, y, number, done):
        super().__init__()
        self.x = x
        self.y = y
        self.number = number  # 0 - Not block   1~7 - Block   8 - Boundary
        self.done = done  # Is this a boundary or installed blocks?


class Block:
    def __init__(self, blockNumber):
        self.blockNumber = blockNumber
        self.nextBlockList = []  # There will be the next block in the waiting area. It's a list of that background blocks.
        self.currentBlockList = []  # List of moving blocks
        self.current_ylist = []  # y-coordinate list of moving blocks
        self.current_xlist = []  # x-coordinate list of moving blocks
        self.state = 1  # You can turn the block four times. 1, 2, 3, 4

    def start(self):
        global block_count
        block_count += 1
        global start_time
        start_time = time.time()
        global gameover

        if self.blockNumber == 1:
            self.nextBlockList.clear()
            for x in range(4, 8):
                self.nextBlockList.append(backgroundblock_group[0][x].number)  # Add background blocks where the first block will be placed.. in nextBlockList.
            for i in range(1, 8):  # What if there are other blocks where they will be?
                if i in self.nextBlockList:
                    gameover = True
                    return
            for x in range(4, 8):  # What if there are no other blocks where they will be?
                backgroundblock_group[0][x].number = 1  # Create the blocks on the game screen
                self.currentBlockList.append(backgroundblock_group[0][x])

        elif self.blockNumber == 2:
            self.nextBlockList.clear()
            self.nextBlockList.append(backgroundblock_group[0][4].number)
            for x in range(4, 7):
                self.nextBlockList.append(backgroundblock_group[1][x].number)
            for i in range(1, 8):
                if i in self.nextBlockList:
                    gameover = True
                    return
            backgroundblock_group[0][4].number = 2
            self.currentBlockList.append(backgroundblock_group[0][4])
            for x in range(4, 7):
                backgroundblock_group[1][x].number = 2
                self.currentBlockList.append(backgroundblock_group[1][x])

        elif self.blockNumber == 3:
            self.nextBlockList.clear()
            for x in range(4, 7):
                self.nextBlockList.append(backgroundblock_group[1][x].number)
            self.nextBlockList.append(backgroundblock_group[0][6].number)
            for i in range(1, 8):
                if i in self.nextBlockList:
                    gameover = True
                    return
            for x in range(4, 7):
                backgroundblock_group[1][x].number = 3
                self.currentBlockList.append(backgroundblock_group[1][x])
            backgroundblock_group[0][6].number = 3
            self.currentBlockList.append(backgroundblock_group[0][6])

        elif self.blockNumber == 4:
            self.nextBlockList.clear()
            for y in range(0, 2):
                for x in range(5, 7):
                    self.nextBlockList.append(backgroundblock_group[y][x].number)
            for i in range(1, 8):
                if i in self.nextBlockList:
                    gameover = True
                    return
            for y in range(0, 2):
                for x in range(5, 7):
                    backgroundblock_group[y][x].number = 4
                    self.currentBlockList.append(backgroundblock_group[y][x])

        elif self.blockNumber == 5:
            self.nextBlockList.clear()
            for x in range(4, 6):
                self.nextBlockList.append(backgroundblock_group[1][x].number)
            for x in range(5, 7):
                self.nextBlockList.append(backgroundblock_group[0][x].number)
            for i in range(1, 8):
                if i in self.nextBlockList:
                    gameover = True
                    return
            for x in range(4, 6):
                backgroundblock_group[1][x].number = 5
                self.currentBlockList.append(backgroundblock_group[1][x])
            for x in range(5, 7):
                backgroundblock_group[0][x].number = 5
                self.currentBlockList.append(backgroundblock_group[0][x])

        elif self.blockNumber == 6:
            self.nextBlockList.clear()
            self.nextBlockList.append(backgroundblock_group[0][5].number)
            for x in range(4, 7):
                self.nextBlockList.append(backgroundblock_group[1][x].number)
            for i in range(1, 8):
                if i in self.nextBlockList:
                    gameover = True
                    return
            backgroundblock_group[0][5].number = 6
            self.currentBlockList.append(backgroundblock_group[0][5])
            for x in range(4, 7):
                backgroundblock_group[1][x].number = 6
                self.currentBlockList.append(backgroundblock_group[1][x])

        elif self.blockNumber == 7:
            self.nextBlockList.clear()
            for x in range(4, 6):
                self.nextBlockList.append(backgroundblock_group[0][x].number)
            for x in range(5, 7):
                self.nextBlockList.append(backgroundblock_group[1][x].number)
            for i in range(1, 8):
                if i in self.nextBlockList:
                    gameover = True
                    return
            for x in range(4, 6):
                backgroundblock_group[0][x].number = 7
                self.currentBlockList.append(backgroundblock_group[0][x])
            for x in range(5, 7):
                backgroundblock_group[1][x].number = 7
                self.currentBlockList.append(backgroundblock_group[1][x])

    def goDown(self):
        global average_time_to_put_a_block, total_time
        self.nextBlockList.clear()
        for i in range(0, 4):
            self.nextBlockList.append(backgroundblock_group[(self.currentBlockList[i].y//32) + 1][(self.currentBlockList[i].x//32)])  # Add background blocks in where the blocks are moving
            if self.nextBlockList[i].number in range(1, 9) and self.nextBlockList[i].done is True:  # If there are blocks down there, stop
                y_list = []
                for j in range(0, 4):
                    self.currentBlockList[j].done = True
                    y_list.append(self.currentBlockList[j].y)
                self.currentBlockList.clear()
                break_sound.play()
                end_time = time.time() - start_time
                total_time += end_time
                average_time_to_put_a_block = total_time / block_count
                eraseLine(y_list)
                return y_list

        for i in range(0, 4):  # The block can go down! Remove the background blocks color before moving.
            self.currentBlockList[i].number = 0
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

        for i in range(0, 4):
            self.currentBlockList[i] = self.nextBlockList[i]
            self.currentBlockList[i].number = self.blockNumber

    def goLeft(self):
        self.nextBlockList.clear()
        for i in range(0, 4):
            self.nextBlockList.append(backgroundblock_group[self.currentBlockList[i].y//32][(self.currentBlockList[i].x//32)-1])
            if self.nextBlockList[i].number in range(1, 9) and self.nextBlockList[i].done is True:
                return

        for i in range (0, 4):
            self.currentBlockList[i].number = 0
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

        for i in range(0, 4):
            self.currentBlockList[i] = self.nextBlockList[i]
            self.currentBlockList[i].number = self.blockNumber

    def goRight(self):
        self.nextBlockList.clear()
        for i in range(0, 4):
            self.nextBlockList.append(backgroundblock_group[self.currentBlockList[i].y//32][(self.currentBlockList[i].x//32)+1])
            if self.nextBlockList[i].number in range(1, 9) and self.nextBlockList[i].done is True:
                return

        for i in range (0, 4):
            self.currentBlockList[i].number = 0
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

        for i in range(0, 4):
            self.currentBlockList[i] = self.nextBlockList[i]
            self.currentBlockList[i].number = self.blockNumber

    def turn(self):  # There are so many codes. I am sad that I am not able to reduce this.
        self.current_ylist.clear()
        self.current_xlist.clear()
        for i in range(0, 4):
            self.current_ylist.append(self.currentBlockList[i].y//32)
            self.current_xlist.append(self.currentBlockList[i].x//32)

        if self.blockNumber == 1:
            if self.state == 1:
                if self.current_ylist[0] == 0:
                    return
                for x in range(0, 4):
                    if backgroundblock_group[self.current_ylist[0] - 1][self.current_xlist[0] + x].done is True:
                        return
                    if backgroundblock_group[self.current_ylist[0] + 1][self.current_xlist[0] + x].done is True:
                        return
                    if backgroundblock_group[self.current_ylist[0] + 2][self.current_xlist[0] + x].done is True:
                        return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                for y in range(0, 4):
                    backgroundblock_group[self.current_ylist[2] + 2 - y][self.current_xlist[2]].number = self.blockNumber
                    self.currentBlockList[y] = backgroundblock_group[self.current_ylist[2] + 2 - y][self.current_xlist[2]]

                self.state = 2

            elif self.state == 2:
                for y in range(0, 4):
                    if backgroundblock_group[self.current_ylist[3] + y][self.current_xlist[0] - 1].done is True:
                        return
                for y in range(0, 4):
                    if backgroundblock_group[self.current_ylist[3] + y][self.current_xlist[0] + 1].done is True:
                        return
                for y in range(0, 4):
                    if backgroundblock_group[self.current_ylist[3] + y][self.current_xlist[0] - 2].done is True:
                        return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                for x in range(0, 4):
                    backgroundblock_group[self.current_ylist[1]][self.current_xlist[1] + 1 - x].number = self.blockNumber
                    self.currentBlockList[x] = backgroundblock_group[self.current_ylist[1]][self.current_xlist[1] + 1 - x]

                self.state = 3

            elif self.state == 3:
                for x in range(0, 4):
                    if backgroundblock_group[self.current_ylist[0] + 1][self.current_xlist[0] - x].done is True:
                        return
                    if backgroundblock_group[self.current_ylist[0] - 1][self.current_xlist[0] - x].done is True:
                        return
                    if backgroundblock_group[self.current_ylist[0] - 2][self.current_xlist[0] - x].done is True:
                        return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                for y in range(0, 4):
                    backgroundblock_group[self.current_ylist[2] - 2 + y][self.current_xlist[2]].number = self.blockNumber
                    self.currentBlockList[y] = backgroundblock_group[self.current_ylist[2] - 2 + y][self.current_xlist[2]]

                self.state = 4

            elif self.state == 4:
                for y in range(0, 4):
                    if backgroundblock_group[self.current_ylist[0] + y][self.current_xlist[0] - 1].done is True:
                        return
                for y in range(0, 4):
                    if backgroundblock_group[self.current_ylist[0] + y][self.current_xlist[0] + 1].done is True:
                        return
                for y in range(0, 4):
                    if backgroundblock_group[self.current_ylist[0] + y][self.current_xlist[0] + 2].done is True:
                        return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                for x in range(0, 4):
                    backgroundblock_group[self.current_ylist[1]][self.current_xlist[1] - 1 + x].number = self.blockNumber
                    self.currentBlockList[x] = backgroundblock_group[self.current_ylist[1]][self.current_xlist[1] - 1 + x]

                self.state = 1

        elif self.blockNumber == 2:
            if self.state == 1:
                for x in range(0, 3):
                    if backgroundblock_group[self.current_ylist[1] + 1][self.current_xlist[1] + x].done is True:
                        return
                for x in range(0, 2):
                    if backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] + 1 + x].done is True:
                        return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] + 2].number = self.blockNumber
                self.currentBlockList[0] = backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] + 2]
                for y in range(0, 3):
                    backgroundblock_group[self.current_ylist[2] - 1 + y][self.current_xlist[2]].number = self.blockNumber
                    self.currentBlockList[y + 1] = backgroundblock_group[self.current_ylist[2] - 1 + y][self.current_xlist[2]]

                self.state = 2

            elif self.state == 2:
                for y in range(0, 3):
                    if backgroundblock_group[self.current_ylist[1] + y][self.current_xlist[1] - 1].done is True:
                        return
                for x in range(0, 2):
                    if backgroundblock_group[self.current_ylist[0] + 1 + y][self.current_xlist[0]].done is True:
                        return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                backgroundblock_group[self.current_ylist[0] + 2][self.current_xlist[0]].number = self.blockNumber
                self.currentBlockList[0] = backgroundblock_group[self.current_ylist[0] + 2][self.current_xlist[0]]
                for x in range(0, 3):
                    backgroundblock_group[self.current_ylist[0] + 1][self.current_xlist[0] - x].number = self.blockNumber
                    self.currentBlockList[x + 1] = backgroundblock_group[self.current_ylist[0] + 1][self.current_xlist[0] - x]

                self.state = 3

            elif self.state == 3:
                for x in range(0, 3):
                    if backgroundblock_group[self.current_ylist[1] - 1][self.current_xlist[1] - x].done is True:
                        return
                for x in range(0, 2):
                    if backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] - 1 + x].done is True:
                        return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] - 2].number = self.blockNumber
                self.currentBlockList[0] = backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] - 2]
                for y in range(0, 3):
                    backgroundblock_group[self.current_ylist[2] + 1 - y][self.current_xlist[2]].number = self.blockNumber
                    self.currentBlockList[y + 1] = backgroundblock_group[self.current_ylist[2] + 1 - y][self.current_xlist[2]]

                self.state = 4

            elif self.state == 4:
                for y in range(0, 3):
                    if backgroundblock_group[self.current_ylist[3] + y][self.current_xlist[1] + 1].done is True:
                        return
                for x in range(0, 2):
                    if backgroundblock_group[self.current_ylist[0] - 2 + y][self.current_xlist[0]].done is True:
                        return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                backgroundblock_group[self.current_ylist[0] - 2][self.current_xlist[0]].number = self.blockNumber
                self.currentBlockList[0] = backgroundblock_group[self.current_ylist[0] - 2][self.current_xlist[0]]
                for x in range(0, 3):
                    backgroundblock_group[self.current_ylist[0] - 1][self.current_xlist[0] + x].number = self.blockNumber
                    self.currentBlockList[x + 1] = backgroundblock_group[self.current_ylist[0] - 1][self.current_xlist[0] + x]

                self.state = 1

        elif self.blockNumber == 3:
            if self.state == 1:
                for x in range(0, 3):
                    if backgroundblock_group[self.current_ylist[0] + 1][self.current_xlist[0] + x].done is True:
                        return
                for x in range(0, 2):
                    if backgroundblock_group[self.current_ylist[3]][self.current_xlist[3] - 2 + x].done is True:
                        return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                for y in range(0, 3):
                    backgroundblock_group[self.current_ylist[1] - 1 + y][self.current_xlist[1]].number = self.blockNumber
                    self.currentBlockList[y] = backgroundblock_group[self.current_ylist[1] - 1 + y][self.current_xlist[1]]
                backgroundblock_group[self.current_ylist[2] + 1][self.current_xlist[2]].number = self.blockNumber
                self.currentBlockList[3] = backgroundblock_group[self.current_ylist[2] + 1][self.current_xlist[2]]

                self.state = 2

            elif self.state == 2:
                for y in range(0, 3):
                    if backgroundblock_group[self.current_ylist[0] + y][self.current_xlist[0] - 1].done is True:
                        return
                for y in range(0, 2):
                    if backgroundblock_group[self.current_ylist[0] + y][self.current_xlist[0] + 1].done is True:
                        return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                for x in range(0, 3):
                    backgroundblock_group[self.current_ylist[1]][self.current_xlist[1] + 1 - x].number = self.blockNumber
                    self.currentBlockList[x] = backgroundblock_group[self.current_ylist[1]][self.current_xlist[1] + 1 - x]
                backgroundblock_group[self.current_ylist[2]][self.current_xlist[2] - 1].number = self.blockNumber
                self.currentBlockList[3] = backgroundblock_group[self.current_ylist[2]][self.current_xlist[2] - 1]

                self.state = 3

            elif self.state == 3:
                for x in range(0, 3):
                    if backgroundblock_group[self.current_ylist[2] - 1][self.current_xlist[2] + x].done is True:
                        return
                for x in range(0, 2):
                    if backgroundblock_group[self.current_ylist[3]][self.current_xlist[3] + 1 + x].done is True:
                        return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                for y in range(0, 3):
                    backgroundblock_group[self.current_ylist[1] + 1 - y][self.current_xlist[1]].number = self.blockNumber
                    self.currentBlockList[y] = backgroundblock_group[self.current_ylist[1] + 1 - y][self.current_xlist[1]]
                backgroundblock_group[self.current_ylist[2] - 1][self.current_xlist[2]].number = self.blockNumber
                self.currentBlockList[3] = backgroundblock_group[self.current_ylist[2] - 1][self.current_xlist[2]]

                self.state = 4

            elif self.state == 4:
                for y in range(0, 3):
                    if backgroundblock_group[self.current_ylist[2] + y][self.current_xlist[0] + 1].done is True:
                        return
                for y in range(0, 2):
                    if backgroundblock_group[self.current_ylist[3] + 1 + y][self.current_xlist[3]].done is True:
                        return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                for x in range(0, 3):
                    backgroundblock_group[self.current_ylist[1]][self.current_xlist[1] - 1 + x].number = self.blockNumber
                    self.currentBlockList[x] = backgroundblock_group[self.current_ylist[1]][self.current_xlist[1] - 1 + x]
                backgroundblock_group[self.current_ylist[2]][self.current_xlist[2] + 1].number = self.blockNumber
                self.currentBlockList[3] = backgroundblock_group[self.current_ylist[2]][self.current_xlist[2] + 1]

                self.state = 1

        elif self.blockNumber == 5:
            if self.state == 1:
                if self.current_ylist[2] == 0:
                    return
                for x in range(0, 3):
                    if backgroundblock_group[self.current_ylist[2] - 1][self.current_xlist[0] + x].done is True:
                        return
                if backgroundblock_group[self.current_ylist[0] - 1][self.current_xlist[0]].done is True:
                    return
                if backgroundblock_group[self.current_ylist[1]][self.current_xlist[1] + 1].done is True:
                    return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                for y in range(0, 2):
                    backgroundblock_group[self.current_ylist[0] - 2 + y][self.current_xlist[0]].number = self.blockNumber
                    self.currentBlockList[y] = backgroundblock_group[self.current_ylist[0] - 2 + y][self.current_xlist[0]]
                for y in range(0, 2):
                    backgroundblock_group[self.current_ylist[1] - 1 + y][self.current_xlist[1]].number = self.blockNumber
                    self.currentBlockList[y + 2] = backgroundblock_group[self.current_ylist[1] - 1 + y][self.current_xlist[1]]

                self.state = 2

            elif self.state == 2:
                for y in range(0, 3):
                    if backgroundblock_group[self.current_ylist[0] + y][self.current_xlist[2] + 1].done is True:
                        return
                if backgroundblock_group[self.current_ylist[1] + 1][self.current_xlist[1]].done is True:
                    return
                if backgroundblock_group[self.current_ylist[2] - 1][self.current_xlist[2]].done is True:
                    return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                for x in range(0, 2):
                    backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] + 2 - x].number = self.blockNumber
                    self.currentBlockList[x] = backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] + 2 - x]
                for x in range(0, 2):
                    backgroundblock_group[self.current_ylist[1]][self.current_xlist[1] + 1 - x].number = self.blockNumber
                    self.currentBlockList[x + 2] = backgroundblock_group[self.current_ylist[1]][self.current_xlist[1] + 1 - x]

                self.state = 3

            elif self.state == 3:
                for x in range(0, 3):
                    if backgroundblock_group[self.current_ylist[2] + 1][self.current_xlist[3] + x].done is True:
                        return
                if backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] - 2].done is True:
                    return
                if backgroundblock_group[self.current_ylist[2]][self.current_xlist[0]].done is True:
                    return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                for y in range(0, 2):
                    backgroundblock_group[self.current_ylist[0] + 2 - y][self.current_xlist[0]].number = self.blockNumber
                    self.currentBlockList[y] = backgroundblock_group[self.current_ylist[0] + 2 - y][self.current_xlist[0]]
                for y in range(0, 2):
                    backgroundblock_group[self.current_ylist[1] + 1 - y][self.current_xlist[1]].number = self.blockNumber
                    self.currentBlockList[y + 2] = backgroundblock_group[self.current_ylist[1] + 1 - y][self.current_xlist[1]]

                self.state = 4

            elif self.state == 4:
                for y in range(0, 3):
                    if backgroundblock_group[self.current_ylist[0] - y][self.current_xlist[2] - 1].done is True:
                        return
                if backgroundblock_group[self.current_ylist[1] - 1][self.current_xlist[1]].done is True:
                    return
                if backgroundblock_group[self.current_ylist[2] + 1][self.current_xlist[2]].done is True:
                    return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                for x in range(0, 2):
                    backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] - 2 + x].number = self.blockNumber
                    self.currentBlockList[x] = backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] - 2 + x]
                for x in range(0, 2):
                    backgroundblock_group[self.current_ylist[1]][self.current_xlist[1] - 1 + x].number = self.blockNumber
                    self.currentBlockList[x + 2] = backgroundblock_group[self.current_ylist[1]][self.current_xlist[1] - 1 + x]

                self.state = 1

        elif self.blockNumber == 6:
            if self.state == 1:
                for x in range(0, 3):
                    if backgroundblock_group[self.current_ylist[1] + 1][self.current_xlist[1] + x].done is True:
                        return
                if backgroundblock_group[self.current_ylist[0]][self.current_xlist[1]].done is True:
                    return
                if backgroundblock_group[self.current_ylist[0]][self.current_xlist[3]].done is True:
                    return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                backgroundblock_group[self.current_ylist[3]][self.current_xlist[3]].number = self.blockNumber
                self.currentBlockList[0] = backgroundblock_group[self.current_ylist[3]][self.current_xlist[3]]
                for y in range(0, 3):
                    backgroundblock_group[self.current_ylist[0] + y][self.current_xlist[0]].number = self.blockNumber
                    self.currentBlockList[y + 1] = backgroundblock_group[self.current_ylist[0] + y][self.current_xlist[0]]

                self.state = 2

            elif self.state == 2:
                for y in range(0, 3):
                    if backgroundblock_group[self.current_ylist[1] + y][self.current_xlist[1] - 1].done is True:
                        return
                if backgroundblock_group[self.current_ylist[0] - 1][self.current_xlist[0]].done is True:
                    return
                if backgroundblock_group[self.current_ylist[0] + 1][self.current_xlist[0]].done is True:
                    return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                backgroundblock_group[self.current_ylist[3]][self.current_xlist[3]].number = self.blockNumber
                self.currentBlockList[0] = backgroundblock_group[self.current_ylist[3]][self.current_xlist[3]]
                for x in range(0, 3):
                    backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] - x].number = self.blockNumber
                    self.currentBlockList[x + 1] = backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] - x]

                self.state = 3

            elif self.state == 3:
                for x in range(0, 3):
                    if backgroundblock_group[self.current_ylist[1] - 1][self.current_xlist[3] + x].done is True:
                        return
                if backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] - 1].done is True:
                    return
                if backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] + 1].done is True:
                    return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                backgroundblock_group[self.current_ylist[3]][self.current_xlist[3]].number = self.blockNumber
                self.currentBlockList[0] = backgroundblock_group[self.current_ylist[3]][self.current_xlist[3]]
                for y in range(0, 3):
                    backgroundblock_group[self.current_ylist[2] + 1 - y][self.current_xlist[0]].number = self.blockNumber
                    self.currentBlockList[y + 1] = backgroundblock_group[self.current_ylist[2] + 1 - y][self.current_xlist[0]]

                self.state = 4

            elif self.state == 4:
                for y in range(0, 3):
                    if backgroundblock_group[self.current_ylist[3] + y][self.current_xlist[1] + 1].done is True:
                        return
                if backgroundblock_group[self.current_ylist[0] - 1][self.current_xlist[0]].done is True:
                    return
                if backgroundblock_group[self.current_ylist[0] + 1][self.current_xlist[0]].done is True:
                    return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                backgroundblock_group[self.current_ylist[3]][self.current_xlist[3]].number = self.blockNumber
                self.currentBlockList[0] = backgroundblock_group[self.current_ylist[3]][self.current_xlist[3]]
                for x in range(0, 3):
                    backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] + x].number = self.blockNumber
                    self.currentBlockList[x + 1] = backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] + x]

                self.state = 1

        elif self.blockNumber == 7:
            if self.state == 1:
                if self.current_ylist[0] == 0:
                    return
                for x in range(0, 3):
                    if backgroundblock_group[self.current_ylist[0] - 1][self.current_xlist[0] + x].done is True:
                        return
                if backgroundblock_group[self.current_ylist[0]][self.current_xlist[3]].done is True:
                    return
                if backgroundblock_group[self.current_ylist[2]][self.current_xlist[0]].done is True:
                    return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                for y in range(0, 2):
                    backgroundblock_group[self.current_ylist[1] - 1 + y][self.current_xlist[1]].number = self.blockNumber
                    self.currentBlockList[y] = backgroundblock_group[self.current_ylist[1] - 1 + y][self.current_xlist[1]]
                for y in range(0, 2):
                    backgroundblock_group[self.current_ylist[0] + y][self.current_xlist[0]].number = self.blockNumber
                    self.currentBlockList[y + 2] = backgroundblock_group[self.current_ylist[0] + y][self.current_xlist[0]]

                self.state = 2

            elif self.state == 2:
                for y in range(0, 3):
                    if backgroundblock_group[self.current_ylist[0] + y][self.current_xlist[0] + 1].done is True:
                        return
                if backgroundblock_group[self.current_ylist[0]][self.current_xlist[2]].done is True:
                    return
                if backgroundblock_group[self.current_ylist[3]][self.current_xlist[0]].done is True:
                    return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                for x in range(0, 2):
                    backgroundblock_group[self.current_ylist[1]][self.current_xlist[1] + 1 - x].number = self.blockNumber
                    self.currentBlockList[x] = backgroundblock_group[self.current_ylist[1]][self.current_xlist[1] + 1 - x]
                for x in range(0, 2):
                    backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] - x].number = self.blockNumber
                    self.currentBlockList[x + 2] = backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] - x]

                self.state = 3

            elif self.state == 3:
                for x in range(0, 3):
                    if backgroundblock_group[self.current_ylist[0] + 1][self.current_xlist[3] + x].done is True:
                        return
                if backgroundblock_group[self.current_ylist[0]][self.current_xlist[3]].done is True:
                    return
                if backgroundblock_group[self.current_ylist[2]][self.current_xlist[0]].done is True:
                    return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                for y in range(0, 2):
                    backgroundblock_group[self.current_ylist[1] + 1 - y][self.current_xlist[1]].number = self.blockNumber
                    self.currentBlockList[y] = backgroundblock_group[self.current_ylist[1] + 1 - y][self.current_xlist[1]]
                for y in range(0, 2):
                    backgroundblock_group[self.current_ylist[0] - y][self.current_xlist[0]].number = self.blockNumber
                    self.currentBlockList[y + 2] = backgroundblock_group[self.current_ylist[0] - y][self.current_xlist[0]]

                self.state = 4

            elif self.state == 4:
                for y in range(0, 3):
                    if backgroundblock_group[self.current_ylist[3] + y][self.current_xlist[0] - 1].done is True:
                        return
                if backgroundblock_group[self.current_ylist[0]][self.current_xlist[2]].done is True:
                    return
                if backgroundblock_group[self.current_ylist[3]][self.current_xlist[0]].done is True:
                    return

                for i in range(0, 4):
                    self.currentBlockList[i].number = 0
                    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

                for x in range(0, 2):
                    backgroundblock_group[self.current_ylist[1]][self.current_xlist[1] - 1 + x].number = self.blockNumber
                    self.currentBlockList[x] = backgroundblock_group[self.current_ylist[1]][self.current_xlist[1] - 1 + x]
                for x in range(0, 2):
                    backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] + x].number = self.blockNumber
                    self.currentBlockList[x + 2] = backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] + x]

                self.state = 1


def nextBlockDraw(blockNumber):
    if blockNumber == 1:
        for x in range(14, 18):
            pygame.draw.rect(screen, (80, 188, 223), pygame.Rect(32 * x + 16, 32 * 12, 32, 32))

    elif blockNumber == 2:
        for x in range(15, 18):
            pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(32 * x, 32 * 12, 32, 32))
        pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(32 * 15, 32 * 11, 32, 32))

    elif blockNumber == 3:
        for x in range(15, 18):
            pygame.draw.rect(screen, (255, 127, 0), pygame.Rect(32 * x, 32 * 12, 32, 32))
        pygame.draw.rect(screen, (255, 127, 0), pygame.Rect(32 * 17, 32 * 11, 32, 32))

    elif blockNumber == 4:
        for x in range(15, 17):
            for y in range(11, 13):
                pygame.draw.rect(screen, (255, 212, 0), pygame.Rect(32 * x + 16, 32 * y, 32, 32))

    elif blockNumber == 5:
        for x in range(16, 18):
            pygame.draw.rect(screen, (129, 193, 71), pygame.Rect(32 * x, 32 * 11, 32, 32))
        for x in range(15, 17):
            pygame.draw.rect(screen, (129, 193, 71), pygame.Rect(32 * x, 32 * 12, 32, 32))

    elif blockNumber == 6:
        for x in range(15, 18):
            pygame.draw.rect(screen, (139, 0, 255), pygame.Rect(32 * x, 32 * 12, 32, 32))
        pygame.draw.rect(screen, (139, 0, 255), pygame.Rect(32 * 16, 32 * 11, 32, 32))

    elif blockNumber == 7:
        for x in range(15, 17):
            pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(32 * x, 32 * 11, 32, 32))
        for x in range(16, 18):
            pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(32 * x, 32 * 12, 32, 32))


def eraseLine(y_list):
    max_y = max(y_list)//32  # Largest y-index of a placed block
    min_y = min(y_list)//32 - 1  # Smallest y-index of a placed block - 1
    while(max_y > min_y):
        count = 0
        for x in range(1, 11):
            if backgroundblock_group[max_y][x].done is False:  # If any of the 10 blocks is empty, leave the loop
                break
            count += 1
            if count == 10:  # A line is full
                plusScore(max_y)  # Let's add points, erase one line, and Drop on every other line
                max_y += 1
                min_y += 1
        max_y -= 1


def plusScore(y):
    global score
    erase_sound.play()

    for x in range(1, 11):
        backgroundblock_group[y][x].done = False  # Change the status of the background blocks
        backgroundblock_group[y][x].number = 0
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(backgroundblock_group[y][x].x, backgroundblock_group[y][x].y, 32, 32))

    for y2 in range(y, 0, -1):  # Drop on every other line
        for x in range(1, 11):
            backgroundblock_group[y2][x].done = backgroundblock_group[y2-1][x].done
            backgroundblock_group[y2][x].number = backgroundblock_group[y2-1][x].number
            backgroundblock_group[y2-1][x].done = False
            backgroundblock_group[y2-1][x].number = 0
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(backgroundblock_group[y2-1][x].x, backgroundblock_group[y2-1][x].y, 32, 32))

    score += 100


def checkAndGoDown():  # Check if the block can go down and go down if possible
    global current_block, next_block
    if type(current_block.goDown()) == list:
        current_block = next_block
        next_block = Block(random.randint(1, 7))
        current_block.start()


def colorTheBlock(screen, coordinates, x, y):
    pygame.draw.rect(screen, coordinates, pygame.Rect(32 * x, 32 * y, 32, 32))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(32 * x, 32 * y, 32, 32), width=1)


score = 0
gameover = False
average_time_to_put_a_block = 0
block_count = 0  # How many blocks were made?
total_time = 0  # Total time it took to put a block
start_time = 0  # Time when the block was first created
current_block = Block(random.randint(1, 7))  # Randomly select one of the seven types of blocks
next_block = Block(random.randint(1, 7))
autotime_down = 0  # Variable to control block down speed

pygame.init()  # The coordinate (0, 0) is in the upper left.

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

font = pygame.font.SysFont("consolas", 30)
font2 = pygame.font.SysFont("ebrima", 100)
font3 = pygame.font.SysFont("consolas", 20)
font4 = pygame.font.SysFont("consolas", 15)

pygame.display.set_caption("Tetris")  # Title
screen = pygame.display.set_mode((672, 672))  # Full screen consisting of 21 x 21 blocks, the size of one block is 32 x 32

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

backgroundblock_group = [[0 for j in range(0, 12)] for i in range(0, 21)]  # Game screen consisting of 12 x 21 blocks
for y in range(0, 21):  # Create blocks that make up the game screen
    for x in range(0, 12):
        if x == 0 or x == 11 or y == 20:  # The blocks that make up the boundary
            backgroundblock_group[y][x] = BackgroundBlock(32 * x, 32 * y, 8, True)
        else:
            backgroundblock_group[y][x] = BackgroundBlock(32 * x, 32 * y, 0, False)

current_block.start()  # First block appears on the game screen!

running = True
while running:  # Main loop
    screen.fill((0, 0, 0))  # Paint the screen black before draw blocks on screen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if current_block.blockNumber != 4:  # Square blocks do not rotate.
                    current_block.turn()
            elif event.key == pygame.K_DOWN:
                autotime_down = 0
                checkAndGoDown()
            elif event.key == pygame.K_LEFT:
                current_block.goLeft()
            elif event.key == pygame.K_RIGHT:
                current_block.goRight()

    autotime_down += 1
    if autotime_down % 30 == 0:
        checkAndGoDown()  # The block automatically goes down If you don't press down key.

    text = font.render("Score : " + str(score), True, (255, 255, 255))
    screen.blit(text, (387, 15))
    text2 = font4.render(f"Average time to put a block : {average_time_to_put_a_block:.2f}s", True, (255, 255, 255))
    screen.blit(text2, (387, 55))
    text3 = font3.render(f"Best : {score_list[0][0]} / {score_list[0][1]:.2f}", True, (255, 255, 255))
    screen.blit(text3, (387, 635))

    pygame.draw.rect(screen, (211, 211, 211), pygame.Rect(32 * 14, 32 * 10, 32*5, 32*4), width=3)  # Border where the next block waits

    nextBlockDraw(next_block.blockNumber)  # Draw the next block to come out in the waiting area

    for x in range(1, 11):  # Color the boundaries of the blocks on the game screen
        for y in range(0, 20):
            pygame.draw.rect(screen, (161, 145, 61), pygame.Rect(32 * x, 32 * y, 32, 32), width=1)

    for y in range(0, 21):  # Color the blocks on the game screen
        for x in range(0, 12):
            if backgroundblock_group[y][x].number == 1:
                colorTheBlock(screen, (80, 188, 223), x, y)
            elif backgroundblock_group[y][x].number == 2:
                colorTheBlock(screen, (0, 0, 255), x, y)
            elif backgroundblock_group[y][x].number == 3:
                colorTheBlock(screen, (255, 127, 0), x, y)
            elif backgroundblock_group[y][x].number == 4:
                colorTheBlock(screen, (255, 212, 0), x, y)
            elif backgroundblock_group[y][x].number == 5:
                colorTheBlock(screen, (129, 193, 71), x, y)
            elif backgroundblock_group[y][x].number == 6:
                colorTheBlock(screen, (139, 0, 255), x, y)
            elif backgroundblock_group[y][x].number == 7:
                colorTheBlock(screen, (255, 0, 0), x, y)
            elif backgroundblock_group[y][x].number == 8:
                pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(32 * x, 32 * y, 32, 32))

    if gameover is True:
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(32 * 1, 32 * 3, 32 * 19, 32 * 15))
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(32 * 1, 32 * 3, 32 * 19, 32 * 15), width=3)
        gameover_text = font2.render("GAME OVER!", True, (255, 255, 255))
        screen.blit(gameover_text, (50, 220))
        text = font.render("Score : " + str(score), True, (255, 255, 255))
        screen.blit(text, (70, 360))
        text2 = font4.render(f"Average time to put a block : {average_time_to_put_a_block:.2f}s", True, (255, 255, 255))
        screen.blit(text2, (70, 400))
        gameover_sound.play()
        pygame.display.flip()
        cur.execute(f"INSERT INTO HighestScore VALUES ({score}, {average_time_to_put_a_block})")
        con.commit()
        pygame.time.wait(2000)
        running = False

    pygame.display.flip()  # It makes the screen to be updated continuously

    clock.tick(30)  # In main loop, it determine FPS

pygame.quit()
