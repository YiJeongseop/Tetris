import pygame
from pygame.locals import *
from pygame import mixer
import random
import time
import sqlite3
import os


score = 0
gameover = False
average_speed = 0 # 블록을 놓는 평균 속도
block_count = 0 # 만들어진 블록 개수
total_time = 0 # 블록을 놓는데 걸린 시간들의 합
start_time = 0 # 블록이 처음 생겼을 때의 시간

class BackgroundBlock:
    def __init__(self, x, y, number, done):
        super().__init__()
        self.x = x
        self.y = y
        self.number = number # 0-블록 X   1~7-블록 O   8-경계
        self.done = done # 경계 블록 또는 놓인 블록인지?

class Block:
    def __init__(self, blockNumber):
        self.blockNumber = blockNumber
        self.nextBlockList = [] # 블록이 생길 자리의 배경 블록 리스트
        self.currentBlockList = [] # 현재 움직이는 블록 리스트
        self.current_ylist = [] # 현재 움직이는 블록들 y좌표 리스트
        self.current_xlist = [] # 현재 움직이는 블록들 x좌표 리스트
        self.state = 1 # 블록 모양 상태 (1 ~ 4)

    def start(self):
        global block_count
        block_count += 1

        global start_time
        start_time = time.time()

        global gameover

        if self.blockNumber == 1:
            self.nextBlockList.clear()
            for x in range(4, 8):
                self.nextBlockList.append(backgroundblock_group[0][x].number) # 처음 블록이 생길 자리의 배경 블록들 추가
            for i in range(1, 8): # 블록이 생길 위치에 다른 블록들이 있다면?
                if i in self.nextBlockList:
                    gameover = True # 게임 오버
                    return
            for x in range(4, 8): # 블록이 생길 위치에 다른 블록들이 없다면?
                backgroundblock_group[0][x].number = 1 # 블록을 생성한다.
                self.currentBlockList.append(backgroundblock_group[0][x]) # 현재 움직이는 블록 리스트들에 추가

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
        global average_speed, total_time
        self.nextBlockList.clear()
        for i in range(0, 4):
            self.nextBlockList.append(backgroundblock_group[(self.currentBlockList[i].y//32) + 1][(self.currentBlockList[i].x//32)]) # 블록이 이동할 자리의 배경 블록들 추가
            if self.nextBlockList[i].number in range(1, 9) and self.nextBlockList[i].done == True: # 밑에 이미 놓인 블록들이 있다면 블록들을 멈춘다.
                y_list = []
                for j in range(0, 4):
                    self.currentBlockList[j].done = True
                    y_list.append(self.currentBlockList[j].y)
                self.currentBlockList.clear()
                break_sound.play()
                end_time = time.time() - start_time
                total_time += end_time
                average_speed = total_time / block_count
                eraseLine(y_list)
                return y_list

        for i in range(0, 4): # 이동하기 전에 블록들 색을 지운다.
            self.currentBlockList[i].number = 0
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

        for i in range(0, 4): # 이동한다.
            self.currentBlockList[i] = self.nextBlockList[i]
            self.currentBlockList[i].number = self.blockNumber

    def goLeft(self):
        self.nextBlockList.clear()
        for i in range(0, 4):
            self.nextBlockList.append(backgroundblock_group[self.currentBlockList[i].y//32][(self.currentBlockList[i].x//32)-1])
            if self.nextBlockList[i].number in range(1, 9) and self.nextBlockList[i].done == True:
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
            if self.nextBlockList[i].number in range(1, 9) and self.nextBlockList[i].done == True:
                return

        for i in range (0, 4):
            self.currentBlockList[i].number = 0
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.currentBlockList[i].x, self.currentBlockList[i].y, 32, 32))

        for i in range(0, 4):
            self.currentBlockList[i] = self.nextBlockList[i]
            self.currentBlockList[i].number = self.blockNumber

    def turn(self):
        self.current_ylist.clear()
        self.current_xlist.clear()
        for i in range(0, 4): # 현재 블록들의 x, y 좌표 할당
            self.current_ylist.append(self.currentBlockList[i].y//32)
            self.current_xlist.append(self.currentBlockList[i].x//32)

        if self.blockNumber == 1:
            if self.state == 1:
                if self.current_ylist[0] == 0: 
                    return
                for x in range(0, 4):
                    if backgroundblock_group[self.current_ylist[0] - 1][self.current_xlist[0] + x].done == True:
                        return
                    if backgroundblock_group[self.current_ylist[0] + 1][self.current_xlist[0] + x].done == True:
                        return
                    if backgroundblock_group[self.current_ylist[0] + 2][self.current_xlist[0] + x].done == True:
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
                    if backgroundblock_group[self.current_ylist[3] + y][self.current_xlist[0] - 1].done == True:
                        return
                for y in range(0, 4):
                    if backgroundblock_group[self.current_ylist[3] + y][self.current_xlist[0] + 1].done == True:
                        return
                for y in range(0, 4):
                    if backgroundblock_group[self.current_ylist[3] + y][self.current_xlist[0] - 2].done == True:
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
                    if backgroundblock_group[self.current_ylist[0] + 1][self.current_xlist[0] - x].done == True:
                        return
                    if backgroundblock_group[self.current_ylist[0] - 1][self.current_xlist[0] - x].done == True:
                        return
                    if backgroundblock_group[self.current_ylist[0] - 2][self.current_xlist[0] - x].done == True:
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
                    if backgroundblock_group[self.current_ylist[0] + y][self.current_xlist[0] - 1].done == True:
                        return
                for y in range(0, 4):
                    if backgroundblock_group[self.current_ylist[0] + y][self.current_xlist[0] + 1].done == True:
                        return
                for y in range(0, 4):
                    if backgroundblock_group[self.current_ylist[0] + y][self.current_xlist[0] + 2].done == True:
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
                    if backgroundblock_group[self.current_ylist[1] + 1][self.current_xlist[1] + x].done == True:
                        return
                for x in range(0, 2):   
                    if backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] + 1 + x].done == True:
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
                    if backgroundblock_group[self.current_ylist[1] + y][self.current_xlist[1] - 1].done == True:
                        return
                for x in range(0, 2):   
                    if backgroundblock_group[self.current_ylist[0] + 1 + y][self.current_xlist[0]].done == True:
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
                    if backgroundblock_group[self.current_ylist[1] - 1][self.current_xlist[1] - x].done == True:
                        return
                for x in range(0, 2):   
                    if backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] - 1 + x].done == True:
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
                    if backgroundblock_group[self.current_ylist[3] + y][self.current_xlist[1] + 1].done == True:
                        return
                for x in range(0, 2):   
                    if backgroundblock_group[self.current_ylist[0] - 2 + y][self.current_xlist[0]].done == True:
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
                    if backgroundblock_group[self.current_ylist[0] + 1][self.current_xlist[0] + x].done == True:
                        return
                for x in range(0, 2):   
                    if backgroundblock_group[self.current_ylist[3]][self.current_xlist[3] - 2 + x].done == True:
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
                    if backgroundblock_group[self.current_ylist[0] + y][self.current_xlist[0] - 1].done == True:
                        return
                for y in range(0, 2):   
                    if backgroundblock_group[self.current_ylist[0] + y][self.current_xlist[0] + 1].done == True:
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
                    if backgroundblock_group[self.current_ylist[2] - 1][self.current_xlist[2] + x].done == True:
                        return
                for x in range(0, 2):   
                    if backgroundblock_group[self.current_ylist[3]][self.current_xlist[3] + 1 + x].done == True:
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
                    if backgroundblock_group[self.current_ylist[2] + y][self.current_xlist[0] + 1].done == True:
                        return
                for y in range(0, 2):   
                    if backgroundblock_group[self.current_ylist[3] + 1 + y][self.current_xlist[3]].done == True:
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
                    if backgroundblock_group[self.current_ylist[2] - 1][self.current_xlist[0] + x].done == True:
                        return
                if backgroundblock_group[self.current_ylist[0] - 1][self.current_xlist[0]].done == True:
                    return
                if backgroundblock_group[self.current_ylist[1]][self.current_xlist[1] + 1].done == True:
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
                    if backgroundblock_group[self.current_ylist[0] + y][self.current_xlist[2] + 1].done == True:
                        return
                if backgroundblock_group[self.current_ylist[1] + 1][self.current_xlist[1]].done == True:
                    return
                if backgroundblock_group[self.current_ylist[2] - 1][self.current_xlist[2]].done == True:
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
                    if backgroundblock_group[self.current_ylist[2] + 1][self.current_xlist[3] + x].done == True:
                        return
                if backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] - 2].done == True:
                    return
                if backgroundblock_group[self.current_ylist[2]][self.current_xlist[0]].done == True:
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
                    if backgroundblock_group[self.current_ylist[0] - y][self.current_xlist[2] - 1].done == True:
                        return
                if backgroundblock_group[self.current_ylist[1] - 1][self.current_xlist[1]].done == True:
                    return
                if backgroundblock_group[self.current_ylist[2] + 1][self.current_xlist[2]].done == True:
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
                    if backgroundblock_group[self.current_ylist[1] + 1][self.current_xlist[1] + x].done == True:
                        return
                if backgroundblock_group[self.current_ylist[0]][self.current_xlist[1]].done == True:
                    return
                if backgroundblock_group[self.current_ylist[0]][self.current_xlist[3]].done == True:
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
                    if backgroundblock_group[self.current_ylist[1] + y][self.current_xlist[1] - 1].done == True:
                        return
                if backgroundblock_group[self.current_ylist[0] - 1][self.current_xlist[0]].done == True:
                    return
                if backgroundblock_group[self.current_ylist[0] + 1][self.current_xlist[0]].done == True:
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
                    if backgroundblock_group[self.current_ylist[1] - 1][self.current_xlist[3] + x].done == True:
                        return
                if backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] - 1].done == True:
                    return
                if backgroundblock_group[self.current_ylist[0]][self.current_xlist[0] + 1].done == True:
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
                    if backgroundblock_group[self.current_ylist[3] + y][self.current_xlist[1] + 1].done == True:
                        return
                if backgroundblock_group[self.current_ylist[0] - 1][self.current_xlist[0]].done == True:
                    return
                if backgroundblock_group[self.current_ylist[0] + 1][self.current_xlist[0]].done == True:
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
                    if backgroundblock_group[self.current_ylist[0] - 1][self.current_xlist[0] + x].done == True:
                        return
                if backgroundblock_group[self.current_ylist[0]][self.current_xlist[3]].done == True:
                    return
                if backgroundblock_group[self.current_ylist[2]][self.current_xlist[0]].done == True:
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
                    if backgroundblock_group[self.current_ylist[0] + y][self.current_xlist[0] + 1].done == True:
                        return
                if backgroundblock_group[self.current_ylist[0]][self.current_xlist[2]].done == True:
                    return
                if backgroundblock_group[self.current_ylist[3]][self.current_xlist[0]].done == True:
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
                    if backgroundblock_group[self.current_ylist[0] + 1][self.current_xlist[3] + x].done == True:
                        return
                if backgroundblock_group[self.current_ylist[0]][self.current_xlist[3]].done == True:
                    return
                if backgroundblock_group[self.current_ylist[2]][self.current_xlist[0]].done == True:
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
                    if backgroundblock_group[self.current_ylist[3] + y][self.current_xlist[0] - 1].done == True:
                        return
                if backgroundblock_group[self.current_ylist[0]][self.current_xlist[2]].done == True:
                    return
                if backgroundblock_group[self.current_ylist[3]][self.current_xlist[0]].done == True:
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
    maxy = max(y_list)//32 # 놓인 블록의 가장 큰 y 인덱스
    miny = min(y_list)//32 - 1 # 놓인 블록의 가장 작은 y 인덱스 - 1
    while(maxy > miny):
        count = 0
        for x in range(1, 11):
            if backgroundblock_group[maxy][x].done == False: # 가로 10개 블록 중 하나라도 비어있으면 루프를 나간다.
                break
            count += 1
            if count == 10: # 가로 10개 블록이 모두 차있으면?
                plusScore(maxy) # 100점을 더하고 한 줄을 지우고 한 줄씩 내리는 함수 실행
                maxy+=1
                miny+=1
        maxy-=1 

def plusScore(y):
    global score
    erase_sound.play()

    for x in range(1, 11): # 한 줄을 비운다.
        backgroundblock_group[y][x].done = False
        backgroundblock_group[y][x].number = 0
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(backgroundblock_group[y][x].x, backgroundblock_group[y][x].y, 32, 32))

    for y2 in range(y, 0, -1): # 한 줄씩 내린다.
        for x in range(1, 11):
            backgroundblock_group[y2][x].done = backgroundblock_group[y2-1][x].done
            backgroundblock_group[y2][x].number = backgroundblock_group[y2-1][x].number
            backgroundblock_group[y2-1][x].done = False
            backgroundblock_group[y2-1][x].number = 0
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(backgroundblock_group[y2-1][x].x, backgroundblock_group[y2-1][x].y, 32, 32))

    score += 100

pygame.init()

PATH = './best.sqlite'
if os.path.isfile(PATH) != True:
    con = sqlite3.connect("best.sqlite")
    cur = con.cursor()
    cur.execute("CREATE TABLE best (Score, AverageSpeed)")
    cur.execute("INSERT INTO best (Score, AverageSpeed) VALUES (0, 0)")
    con.commit()
else:
    con = sqlite3.connect("best.sqlite")
    cur = con.cursor()

cur.execute("SELECT * FROM best ORDER BY Score DESC")
score_list = cur.fetchall()

pygame.key.set_repeat(80) # 키보드 키의 연속 동작

font = pygame.font.SysFont("consolas", 30)
font2 = pygame.font.SysFont("ebrima", 100)
font3 = pygame.font.SysFont("consolas", 20)

pygame.display.set_caption("Tetris")  
screen = pygame.display.set_mode((672, 672)) # 32x32 칸이 21x21  

clock = pygame.time.Clock()  

mixer.init()
mixer.music.load("580898__bloodpixelhero__in-game.wav")
mixer.music.set_volume(0.04)
mixer.music.play()

break_sound = mixer.Sound("202230__deraj__pop-sound.wav")
break_sound.set_volume(0.2)

gameover_sound = mixer.Sound("42349__irrlicht__game-over.wav")
gameover_sound.set_volume(0.2)

erase_sound = mixer.Sound("143607__dwoboyle__menu-interface-confirm-003.wav")
erase_sound.set_volume(0.15)

backgroundblock_group = [[0 for j in range(0, 12)] for i in range(0, 21)] # 12 x 21 게임판 배경 블록 리스트

for y in range(0, 21):  
    for x in range(0, 12):
        if x == 0 or x == 11 or y == 20:
            backgroundblock_group[y][x] = BackgroundBlock(32 * x, 32 * y, 8, True)
        else:
            backgroundblock_group[y][x] = BackgroundBlock(32 * x, 32 * y, 0, False)

current_block = Block(random.randint(1, 7))
next_block = Block(random.randint(1, 7))
current_block.start()

autotime_down = 0 # 블록이 내려가는 속도를 조절하는 변수

running = True
while running:

    screen.fill((0, 0, 0))  

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if current_block.blockNumber != 4:
                    current_block.turn()
            elif event.key == pygame.K_DOWN:
                autotime_down = 0
                if type(current_block.goDown()) == list:
                    current_block = next_block
                    next_block = Block(random.randint(1, 7))
                    current_block.start()
            elif event.key == pygame.K_LEFT:
                current_block.goLeft()
            elif event.key == pygame.K_RIGHT:
                current_block.goRight()

    autotime_down += 1
    if autotime_down % 30 == 0:
        if type(current_block.goDown()) == list:
            current_block = next_block
            next_block = Block(random.randint(1, 7))
            current_block.start()

    text = font.render("Score : " + str(score), True, (255, 255, 255))
    screen.blit(text, (400, 15))

    text2 = font3.render(f"Average Speed : {average_speed:.2f}", True, (255, 255, 255))
    screen.blit(text2, (400, 55))

    text3 = font3.render(f"Best : {score_list[0][0]} / {score_list[0][1]:.2f}", True, (255, 255, 255))
    screen.blit(text3, (400, 635))
    
    pygame.draw.rect(screen, (211, 211, 211), pygame.Rect(32 * 14, 32 * 10, 32*5, 32*4), width = 3)

    nextBlockDraw(next_block.blockNumber)

    for x in range(0, 12): 
        for y in range(0, 21):
            pygame.draw.rect(screen, (161, 145, 61), pygame.Rect(32 * x, 32 * y, 32, 32), width=1)

    for y in range(0, 21): # 배경 블록에 할당된 색에 따라 색칠을 한다.
        for x in range(0, 12):
            if backgroundblock_group[y][x].number == 1:
                pygame.draw.rect(screen, (80, 188, 223), pygame.Rect(32 * x, 32 * y, 32, 32))
                pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(32 * x, 32 * y, 32, 32), width = 1)
            elif backgroundblock_group[y][x].number == 2:
                pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(32 * x, 32 * y, 32, 32))
                pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(32 * x, 32 * y, 32, 32), width = 1)
            elif backgroundblock_group[y][x].number == 3:
                pygame.draw.rect(screen, (255, 127, 0), pygame.Rect(32 * x, 32 * y, 32, 32))
                pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(32 * x, 32 * y, 32, 32), width = 1)
            elif backgroundblock_group[y][x].number == 4:
                pygame.draw.rect(screen, (255, 212, 0), pygame.Rect(32 * x, 32 * y, 32, 32))
                pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(32 * x, 32 * y, 32, 32), width = 1)
            elif backgroundblock_group[y][x].number == 5:
                pygame.draw.rect(screen, (129, 193, 71), pygame.Rect(32 * x, 32 * y, 32, 32))
                pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(32 * x, 32 * y, 32, 32), width = 1)
            elif backgroundblock_group[y][x].number == 6:
                pygame.draw.rect(screen, (139, 0, 255), pygame.Rect(32 * x, 32 * y, 32, 32))
                pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(32 * x, 32 * y, 32, 32), width = 1)
            elif backgroundblock_group[y][x].number == 7:
                pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(32 * x, 32 * y, 32, 32))
                pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(32 * x, 32 * y, 32, 32), width = 1)
            elif backgroundblock_group[y][x].number == 8:
                pygame.draw.rect(screen, (128, 128, 128), pygame.Rect(32 * x, 32 * y, 32, 32))

    if gameover == True:
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(32 * 1, 32 * 3, 32 * 19, 32 * 15))
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(32 * 1, 32 * 3, 32 * 19, 32 * 15), width = 3)
        gameover_text = font2.render("GAME OVER!", True, (255, 255, 255))
        screen.blit(gameover_text, (50, 220))
        text = font.render("Score : " + str(score), True, (255, 255, 255))
        screen.blit(text, (70, 360))
        text2 = font3.render(f"Average Speed : {average_speed:.2f}", True, (255, 255, 255))
        screen.blit(text2, (70, 400))
        gameover_sound.play()
        pygame.display.flip()
        cur.execute(f"INSERT INTO best VALUES ({score}, {average_speed})")
        con.commit()
        pygame.time.wait(2000)
        running = False

    pygame.display.flip()  

    clock.tick(30)  

pygame.quit()
