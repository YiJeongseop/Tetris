import pygame
import unittest
import tetris
from pygame import mixer
from settings import SCREEN, BLACK, SKY_BLUE, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED
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
        self.tetris = tetris.Tetris()
        self.test_block_i = tetris.BlockI(self.tetris)
        self.test_block_j = tetris.BlockJ(self.tetris)
        self.test_block_l = tetris.BlockL(self.tetris)
        self.test_block_o = tetris.BlockO(self.tetris)
        self.test_block_s = tetris.BlockS(self.tetris)
        self.test_block_t = tetris.BlockT(self.tetris)
        self.test_block_z = tetris.BlockZ(self.tetris)
        self.time_tracking = TimeTracking()
        self._turns = (1, 2, 3, 0)
        for y in range(21): 
            for x in range(12):
                if x in (0, 11) or y == 20: 
                    tetris.background_blocks[y][x] = tetris.BackgroundBlock(32 * x, 32 * y, 8, True)
                else:
                    tetris.background_blocks[y][x] = tetris.BackgroundBlock(32 * x, 32 * y, 0, False)
    
    def test_start(self):
        self.tetris.start(self.time_tracking, self.test_block_j)
        self.assertEqual(tetris.background_blocks[0][4].number, 2)

    def test_go_down(self):
        self.tetris.start(self.time_tracking, self.test_block_j)
        self.tetris.go(tetris.Move.DOWN, self.time_tracking)
        self.assertEqual(tetris.background_blocks[2][4].number, 2)

    def test_stop(self):
        self.tetris.start(self.time_tracking, self.test_block_j)
        for i in range(18):
            self.tetris.go(tetris.Move.DOWN, self.time_tracking)
        self.assertEqual(type(self.tetris.go(tetris.Move.DOWN, self.time_tracking)), list)

    def test_go_left(self):
        self.tetris.start(self.time_tracking, self.test_block_j)
        self.tetris.go(tetris.Move.LEFT, self.time_tracking)
        self.assertEqual(tetris.background_blocks[0][3].number, 2)

    def test_go_right(self):
        self.tetris.start(self.time_tracking, self.test_block_j)
        self.tetris.go(tetris.Move.RIGHT, self.time_tracking)
        self.assertEqual(tetris.background_blocks[0][5].number, 2)

    def test_turn_i(self):
        self.tetris.start(self.time_tracking, self.test_block_i)
        self.tetris.go(tetris.Move.DOWN, self.time_tracking)
        for state in self._turns:
            self.test_block_i.turn()
            self.assertEqual(self.tetris.state, state)

    def test_turn_j(self):
        self.tetris.start(self.time_tracking, self.test_block_j)
        self.tetris.go(tetris.Move.DOWN, self.time_tracking)
        for state in self._turns:
            self.test_block_j.turn()
            self.assertEqual(self.tetris.state, state)
        
    def test_turn_l(self):
        self.tetris.start(self.time_tracking, self.test_block_l)
        self.tetris.go(tetris.Move.DOWN, self.time_tracking)
        for state in self._turns:
            self.test_block_l.turn()
            self.assertEqual(self.tetris.state, state)
        
    def test_turn_s(self):
        self.tetris.start(self.time_tracking, self.test_block_s)
        self.tetris.go(tetris.Move.DOWN, self.time_tracking)
        for state in self._turns:
            self.test_block_s.turn()
            self.assertEqual(self.tetris.state, state)
        
    def test_turn_t(self):
        self.tetris.start(self.time_tracking, self.test_block_t)
        self.tetris.go(tetris.Move.DOWN, self.time_tracking)
        for state in self._turns:
            self.test_block_t.turn()
            self.assertEqual(self.tetris.state, state)
        
    def test_turn_z(self):
        self.tetris.start(self.time_tracking, self.test_block_z)
        self.tetris.go(tetris.Move.DOWN, self.time_tracking)
        for state in self._turns:
            self.test_block_z.turn()
            self.assertEqual(self.tetris.state, state)

    def test_i_draw(self):
        self.test_block_i.draw()
        self.assertEqual(SCREEN.get_at((464, 384)), SKY_BLUE)
        
    def test_j_draw(self):
        self.test_block_j.draw()
        self.assertEqual(SCREEN.get_at((480, 352)), BLUE)
        
    def test_l_draw(self):
        self.test_block_l.draw()
        self.assertEqual(SCREEN.get_at((544, 352)), ORANGE)
        
    def test_o_draw(self):
        self.test_block_o.draw()
        self.assertEqual(SCREEN.get_at((496, 352)), YELLOW)
        
    def test_s_draw(self):
        self.test_block_s.draw()
        self.assertEqual(SCREEN.get_at((480, 384)), GREEN)
        
    def test_t_draw(self):
        self.test_block_t.draw()
        self.assertEqual(SCREEN.get_at((512, 352)), PURPLE)
        
    def test_z_draw(self):
        self.test_block_z.draw()
        self.assertEqual(SCREEN.get_at((512, 384)), RED)
        
    def test_color_the_block(self):
        tetris.BackgroundBlock.color_the_block(SCREEN, SKY_BLUE, 0, 0)
        self.assertEqual(SCREEN.get_at((0, 0)), BLACK)
        self.assertEqual(SCREEN.get_at((1, 1)), SKY_BLUE)


if __name__ == '__main__':
    unittest.main()
