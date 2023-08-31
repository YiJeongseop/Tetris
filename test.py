import pygame
import unittest
import tetris
from pygame import mixer
from settings import SCREEN, BLACK, SKY_BLUE
from time_tracking import TimeTracking


class TestTetris(unittest.TestCase):
    def setUp(self):
        pygame.init()
        mixer.init()
        mixer.music.load("resources/audio/580898__bloodpixelhero__in-game.wav")
        mixer.music.set_volume(0.04)
        mixer.music.play()
        self.break_sound = mixer.Sound("resources/audio/202230__deraj__pop-sound.wav")
        self.break_sound.set_volume(0.2)
        self.erase_sound = mixer.Sound("resources/audio/143607__dwoboyle__menu-interface-confirm-003.wav")
        self.erase_sound.set_volume(0.15)
        self.test_block = tetris.BlockJ()
        for y in range(0, 21): 
            for x in range(0, 12):
                if x == 0 or x == 11 or y == 20: 
                    tetris.background_blocks[y][x] = tetris.BackgroundBlock(32 * x, 32 * y, 8, True)
                else:
                    tetris.background_blocks[y][x] = tetris.BackgroundBlock(32 * x, 32 * y, 0, False)
    
    def test_start(self):
        self.test_block.start(TimeTracking())
        self.assertEqual(tetris.background_blocks[0][4].number, 2)

    def test_go(self):
        self.test_block.start(TimeTracking())
        self.test_block.go(tetris.Move.DOWN, TimeTracking())
        self.assertEqual(tetris.background_blocks[2][4].number, 2)

    def test_turn(self):
        self.test_block.start(TimeTracking())
        self.test_block.turn()
        self.assertEqual(self.test_block.state, 2)

    def test_color_the_block(self):
        tetris.BackgroundBlock.color_the_block(SCREEN, SKY_BLUE, 0, 0)
        self.assertEqual(SCREEN.get_at((0, 0)), BLACK)
        self.assertEqual(SCREEN.get_at((1, 1)), SKY_BLUE)


if __name__ == '__main__':
    unittest.main()
