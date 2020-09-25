#!/usr/bin/env python3
import os
import lab
import sys
import pickle
import doctest
import unittest
from copy import deepcopy

sys.setrecursionlimit(20000)

TEST_DIRECTORY = os.path.dirname(__file__)

TESTDOC_FLAGS = doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE
TESTDOC_SKIP = ['lab']


class Test00_DocTests(unittest.TestCase):
    def test_doctests_run(self):
        """ Checking to see if all lab doctests run successfully """
        results = doctest.testmod(lab, optionflags=TESTDOC_FLAGS, report=False)
        self.assertEqual(results[0], 0)

    def test_all_doc_strings_exist(self):
        """ Checking if docstrings have been written for everything in lab.py """
        tests = doctest.DocTestFinder(exclude_empty=False).find(lab)
        for test in tests:
            if test.name in TESTDOC_SKIP:
                continue
            if not test.docstring:
                missing = "Oh no, '{}' has no docstring!".format(test.name)
                self.fail(missing)


class Test01_2dNewGame(unittest.TestCase):
    def test_newsmallgame(self):
        result = lab.new_game_2d(10, 8, [(7, 3), (2, 6), (8, 7), (4, 4), (3, 5),
                                         (4, 6), (6, 2), (9, 4), (4, 2), (4, 0),
                                         (8, 6), (9, 7), (8, 5), (5, 0), (7, 2),
                                         (5, 3)])
        expected = {"board": [[0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 1, 1, 1],
                              [0, 0, 0, 0, 1, 2, ".", 1],
                              [1, 2, 1, 2, 2, ".", 3, 2],
                              [".", 3, ".", 3, ".", 3, ".", 1],
                              [".", 4, 3, ".", 2, 2, 1, 1],
                              [1, 3, ".", 4, 2, 0, 0, 0],
                              [0, 2, ".", ".", 2, 2, 3, 2],
                              [0, 1, 2, 3, 3, ".", ".", "."],
                              [0, 0, 0, 1, ".", 3, 4, "."]],
                    "dimensions": (10, 8),
                    "mask": [[False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False],
                             [False, False, False, False, False, False, False, False]],
                    "state": "ongoing"}
        for name in expected:
            self.assertEqual(result[name], expected[name])

    def test_newmediumgame(self):
        result = lab.new_game_2d(30, 16, [(16, 6), (17, 7), (14, 4), (13, 4),
                                          (0, 7), (21, 6), (2, 5), (5, 5), (6, 10),
                                          (12, 6), (24, 14), (14, 1), (24, 1),
                                          (26, 12), (8, 15), (9, 3), (16, 0),
                                          (19, 13), (15, 14), (13, 10), (18, 10),
                                          (21, 15), (28, 15), (29, 14), (11, 15),
                                          (14, 8), (17, 8), (24, 8), (25, 5),
                                          (2, 1), (10, 3), (27, 2), (17, 6),
                                          (7, 15), (15, 0), (21, 8), (20, 0),
                                          (1, 10), (10, 4), (14, 6), (1, 0),
                                          (4, 11), (27, 0), (9, 13), (23, 5),
                                          (14, 12), (20, 15), (3, 15), (26, 14),
                                          (4, 8), (10, 15), (7, 11), (18, 1),
                                          (25, 4), (26, 3), (22, 14), (28, 2),
                                          (13, 2), (19, 6), (1, 4), (21, 4),
                                          (1, 9), (8, 7), (23, 1), (22, 11),
                                          (19, 5), (18, 7), (0, 6), (26, 4),
                                          (3, 4), (5, 9), (24, 13), (20, 8),
                                          (19, 0), (0, 3), (21, 13), (3, 3),
                                          (28, 9), (11, 1), (12, 10), (24, 10),
                                          (18, 13), (0, 0), (21, 0), (3, 13),
                                          (27, 13), (5, 15), (26, 9), (17, 4),
                                          (7, 9), (19, 9), (24, 7), (22, 5),
                                          (3, 8), (27, 8), (9, 5), (23, 13),
                                          (5, 2), (10, 2)])
        with open('test_outputs/test2d_newmediumgame.pickle', 'rb') as f:
            expected = pickle.load(f)
        for name in expected:
            self.assertEqual(result[name], expected[name])


    def test_newlargegame(self):
        with open('test_outputs/test2d_newlargegame.pickle', 'rb') as f:
            expected = pickle.load(f)
        with open('test_inputs/test2d_newlargegame.pickle', 'rb') as f:
            inputs = pickle.load(f)
        result = lab.new_game_2d(inputs['num_rows'], inputs['num_cols'],
                             inputs['bombs'])
        for name in expected:
            self.assertEqual(result[name], expected[name])


class Test02_2dDig(unittest.TestCase):
    def test_dig(self):
        for t in ('complete', 'mine', 'small'):
            with self.subTest(test=t):
                with open('test_outputs/test2d_dig%s.pickle' % t, 'rb') as f:
                    expected = pickle.load(f)
                with open('test_inputs/test2d_dig%s.pickle' % t, 'rb') as f:
                    inputs = pickle.load(f)
                game = inputs['game']
                revealed = lab.dig_2d(game, inputs['row'], inputs['col'])
                self.assertEqual(revealed, expected['revealed'])
                for name in expected['game']:
                    self.assertEqual(game[name], expected['game'][name])


class Test03_2dRender(unittest.TestCase):
    def test_render(self):
        """ Testing render on a small board """
        with open('test_inputs/test2d_render.pickle', 'rb') as f:
            inp = pickle.load(f)
        result = lab.render_2d(inp)
        expected = [[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                    [' ', ' ', ' ', ' ', ' ', '1', '1', '1'],
                    [' ', ' ', ' ', ' ', '1', '2', '_', '_'],
                    ['1', '2', '1', '2', '2', '_', '_', '_'],
                    ['_', '_', '_', '_', '_', '_', '_', '_'],
                    ['_', '_', '_', '_', '_', '_', '_', '_'],
                    ['_', '_', '_', '_', '_', '_', '_', '_'],
                    ['_', '_', '_', '_', '_', '_', '_', '_'],
                    ['_', '_', '_', '_', '_', '_', '_', '_'],
                    ['_', '_', '_', '_', '_', '_', '_', '_']]
        self.assertEqual(result, expected)

class Test04_RenderASCII(unittest.TestCase):
    def test_asciismall(self):
        """ Testing render_ascii on a small 2d board """
        with open('test_inputs/test2d_asciismall.pickle', 'rb') as f:
            inp = pickle.load(f)
        result = lab.render_ascii(inp)
        expected = ('        \n'
                    '     111\n'
                    '    12__\n'
                    '12122___\n'
                    '________\n'
                    '________\n'
                    '________\n'
                    '________\n'
                    '________\n'
                    '________')
        self.assertEqual(result, expected)

    def test_asciixray(self):
        """ Testing render_ascii on a small 2d board with xray """
        with open('test_inputs/test2d_asciixray.pickle', 'rb') as f:
            inputs = pickle.load(f)
        result = lab.render_ascii(inputs['game'], True)
        expected = ('        \n'
                    '     111\n'
                    '    12.1\n'
                    '12122.32\n'
                    '.3.3.3.1\n'
                    '.43.2211\n'
                    '13.42   \n'
                    ' 2..2232\n'
                    ' 1233...\n'
                    '   1.34.')
        self.assertEqual(result, expected)


class Test05_2dIntegration(unittest.TestCase):
    def run_integration_test(self, t):
        """ dig, render, and render_ascii on boards """
        with open('test_outputs/test2d_integration%d.pickle' % t, 'rb') as f:
            expected = pickle.load(f)
        with open('test_inputs/test2d_integration%s.pickle' % t, 'rb') as f:
            inputs = pickle.load(f)
        results = []
        game = inputs['game']
        for coord in inputs['coords']:
            results.append((('dig', lab.dig_2d(game, *coord)),
                            ('game', game),
                            ('render', lab.render_2d(game)),
                            ('render/xray', lab.render_2d(game, True)),
                            ('render_ascii', lab.render_ascii(game)),
                            ('render_ascii/xray', lab.render_ascii(game, True))))
        self.assertEqual(results, expected)

    def test_integration_1(self):
        self.run_integration_test(1)

    def test_integration_2(self):
        self.run_integration_test(2)

    def test_integration_3(self):
        self.run_integration_test(3)


class Test06_NdNewGame(unittest.TestCase):
    def test_newsmall6dgame(self):
        """ Testing new_game on a small 6-D board """
        with open('test_outputs/testnd_newsmall6dgame.pickle', 'rb') as f:
            expected = pickle.load(f)
        with open('test_inputs/testnd_newsmall6dgame.pickle', 'rb') as f:
            inputs = pickle.load(f)
        result = lab.new_game_nd(inputs['dimensions'], inputs['bombs'])
        for i in ('dimensions', 'board', 'mask', 'state'):
            self.assertEqual(result[i], expected[i])


    def test_newlarge4dgame(self):
        """ Testing new_game on a large 4-D board """
        with open('test_outputs/testnd_newlarge4dgame.pickle', 'rb') as f:
            expected = pickle.load(f)
        with open('test_inputs/testnd_newlarge4dgame.pickle', 'rb') as f:
            inputs = pickle.load(f)
        result = lab.new_game_nd(inputs['dimensions'], inputs['bombs'])
        for i in ('dimensions', 'board', 'mask', 'state'):
            self.assertEqual(result[i], expected[i])


class Test07_NdIntegration(unittest.TestCase):
    def _test_integration(self, n):
        with open('test_outputs/testnd_integration%s.pickle' % n, 'rb') as f:
            expected = pickle.load(f)
        with open('test_inputs/testnd_integration%s.pickle' % n, 'rb') as f:
            inputs = pickle.load(f)
        g = lab.new_game_nd(inputs['dimensions'], inputs['bombs'])
        for location, results in zip(inputs['digs'], expected):
            squares_revealed, game, rendered, rendered_xray = results
            res = lab.dig_nd(g, location)
            self.assertEqual(res, squares_revealed)
            for i in ('dimensions', 'board', 'mask', 'state'):
                self.assertEqual(g[i], game[i])
            self.assertEqual(lab.render_nd(g), rendered)
            self.assertEqual(lab.render_nd(g, True), rendered_xray)

    def test_integration1(self):
        """ dig and render, repeatedly, on a large board"""
        self._test_integration(1)

    def test_integration2(self):
        """ dig and render, repeatedly, on a large board"""
        self._test_integration(2)

    def test_integration3(self):
        """ dig and render, repeatedly, on a large board"""
        self._test_integration(3)


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
