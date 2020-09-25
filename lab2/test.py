#!/usr/bin/env python3
import os
import lab
import sys
import pickle
import random
import unittest


TEST_DIRECTORY = os.path.dirname(__file__)


class TestTiny(unittest.TestCase):
    def setUp(self):
        """ Load actor/movie database """
        filename = 'resources/tiny.pickle'
        with open(filename, 'rb') as f:
            self.data = pickle.load(f)

    # tests acted_together function using randomly generated actors inside the set
    def test_a(self):
        randInt = random.randint(0, len(self.data)-1)
        actor_1 = self.data[randInt][0]
        actor_2 = self.data[randInt][1]
        self.assertTrue(lab.acted_together(self.data, actor_1, actor_2))

    # test for Bacon number 0
    def test_b(self):
        n = 0
        expected = {4724}

        result = lab.actors_with_bacon_number(self.data, n)
        self.assertTrue(isinstance(result, set))
        self.assertEqual(result, expected)

    # test for Bacon number 1
    def test_c(self):
        n = 1
        expected = {2876,1532}

        result = lab.actors_with_bacon_number(self.data, n)
        self.assertTrue(isinstance(result, set))
        self.assertEqual(result, expected)

    # test for Bacon number 2
    def test_d(self):
        n = 2
        expected = {1640}

        result = lab.actors_with_bacon_number(self.data, n)
        self.assertTrue(isinstance(result, set))
        self.assertEqual(result, expected)

    # test for Bacon number 3
    def test_e(self):
        n = 3
        expected = set()

        result = lab.actors_with_bacon_number(self.data, n)
        self.assertTrue(isinstance(result, set))
        self.assertEqual(result, expected)

    # test for Bacon path to id 1640
    def test_f(self):
        expected = [4724, 2876, 1640]
        actor_id = 1640
        result = lab.bacon_path(self.data, actor_id)

        self.assertEqual(result, expected)

    # test for actor_to_actor_path
    def test_g(self):
        expected = [4724, 2876, 1640]
        start_id = 4724
        end_id = 1640

        result = lab.actor_to_actor_path(self.data, start_id, end_id)
        self.assertEqual(result,expected)



class Test01_ActedTogether(unittest.TestCase):
    def setUp(self):
        """ Load actor/movie database """
        filename = 'resources/small.pickle'
        #filename = 'resources/large.pickle'
        with open(filename, 'rb') as f:
            self.data = pickle.load(f)

    def test_01(self):
        # Simple test, two actors who acted together
        actor1 = 4724
        actor2 = 9210
        self.assertTrue(lab.acted_together(self.data, actor1, actor2))

    def test_02(self):
        # Simple test, two actors who had not acted together
        actor1 = 4724
        actor2 = 16935
        self.assertFalse(lab.acted_together(self.data, actor1, actor2))

    def test_03(self):
        # Simple test, same actor
        actor1 = 4724
        actor2 = 4724
        self.assertTrue(lab.acted_together(self.data, actor1, actor2))


class Test02_BaconNumber(unittest.TestCase):
    def setUp(self):
        """ Load actor/movie database """
        filename = 'resources/small.pickle'
        with open(filename, 'rb') as f:
            self.data = pickle.load(f)

    def test_04(self):
        # Actors with Bacon number of 2
        n = 2
        expected = {1640, 1811, 2115, 2283, 2561, 2878, 3085, 4025, 4252, 4765,
                    6541, 9827, 11317, 14104, 16927, 16935, 19225, 33668, 66785,
                    90659, 183201, 550521, 1059002, 1059003, 1059004, 1059005,
                    1059006, 1059007, 1232763}

        first_result = lab.actors_with_bacon_number(self.data, n)
        self.assertTrue(isinstance(first_result, set))
        self.assertEqual(first_result, expected)

        second_result = lab.actors_with_bacon_number(self.data, n)
        self.assertTrue(isinstance(second_result, set))
        self.assertEqual(second_result, expected)

    def test_05(self):
        # Actors with Bacon number of 3
        n = 3
        expected = {52, 1004, 1248, 2231, 2884, 4887, 8979, 10500, 12521,
                    14792, 14886, 15412, 16937, 17488, 19119, 19207, 19363,
                    20853, 25972, 27440, 37252, 37612, 38351, 44712, 46866,
                    46867, 48576, 60062, 75429, 83390, 85096, 93138, 94976,
                    109625, 113777, 122599, 126471, 136921, 141458, 141459,
                    141460, 141461, 141495, 146634, 168638, 314092, 349956,
                    558335, 572598, 572599, 572600, 572601, 572602, 572603,
                    583590, 931399, 933600, 1086299, 1086300, 1168416, 1184797,
                    1190297, 1190298, 1190299, 1190300}
        first_result = lab.actors_with_bacon_number(self.data, n)
        self.assertTrue(isinstance(first_result, set))
        self.assertEqual(first_result, expected)

        second_result = lab.actors_with_bacon_number(self.data, n)
        self.assertTrue(isinstance(second_result, set))
        self.assertEqual(second_result, expected)

    def test_06(self):
        # random large Bacon number
        N = random.randint(50, 100)
        k = random.randint(7, 30)
        self.assertEqual(len(lab.actors_with_bacon_number(make_bacon_tree(N, k), N)), k)

    def test_07(self):
        # random graph, Bacon number with no people
        N = random.randint(5, 10)
        k = random.randint(4, 7)
        self.assertEqual(len(lab.actors_with_bacon_number(make_bacon_tree(N, k), int(1e20))), 0)
        self.assertEqual(len(lab.actors_with_bacon_number(make_bacon_tree(N, k), int(1e20))), 0)


class Test03_BaconPath(unittest.TestCase):
    """ These tests check the actual path for validity, and to do so in a
    reasonable time requires a fast checking database. So this reveals
    both validate path and convert. It's probably better to put some
    subset of these into a web check only. Maybe to have a couple of
    tests here with a single unique path.
    """
    def setUp(self):
        """ Load actor/movie database """
        with open('resources/small.pickle', 'rb') as f:
            self.db_small = pickle.load(f)
        with open('resources/large.pickle', 'rb') as f:
            self.db_large = pickle.load(f)

    def test_08(self):
        # Bacon path, small database, path does not exist
        actor_id = 2876669
        expected = None

        first_result = lab.bacon_path(self.db_small, actor_id)
        self.assertEqual(first_result, expected)

        second_result = lab.bacon_path(self.db_small, actor_id)
        self.assertEqual(second_result, expected)

    def test_09(self):
        # Bacon path, small database, length of 3 (4 actors, 3 movies)
        actor_id = 46866
        len_expected = 3

        first_result = lab.bacon_path(self.db_small, actor_id)
        len_first_result = -1 if first_result is None else len(first_result)-1
        second_result = lab.bacon_path(self.db_small, actor_id)
        len_second_result = -1 if second_result is None else len(second_result)-1

        self.assertTrue(valid_path(self.db_small, first_result))
        self.assertEqual(len_first_result, len_expected)
        self.assertEqual(first_result[0], 4724)
        self.assertEqual(first_result[-1], actor_id)

        self.assertTrue(valid_path(self.db_small, second_result))
        self.assertEqual(len_second_result, len_expected)
        self.assertEqual(second_result[0], 4724)
        self.assertEqual(second_result[-1], actor_id)

    def test_10(self):
        # Bacon path, large database, length of 2 (3 actors, 2 movies)
        actor_id = 1204
        len_expected = 2
        result = lab.bacon_path(self.db_large, actor_id)
        len_result = -1 if result is None else len(result)-1
        self.assertTrue(valid_path(self.db_large, result))
        self.assertEqual(len_result, len_expected)
        self.assertEqual(result[0], 4724)
        self.assertEqual(result[-1], actor_id)

    def test_11(self):
        # Bacon path, large database, length of 4 (5 actors, 4 movies)
        actor_id = 197897
        len_expected = 4
        result = lab.bacon_path(self.db_large, actor_id)
        len_result = -1 if result is None else len(result)-1
        self.assertTrue(valid_path(self.db_large, result))
        self.assertEqual(len_result, len_expected)
        self.assertEqual(result[0], 4724)
        self.assertEqual(result[-1], actor_id)

    def test_12(self):
        # Bacon path, large database, length of 6 (7 actors, 6 movies)
        actor_id = 1345462
        len_expected = 6
        result = lab.bacon_path(self.db_large, actor_id)
        # here, we compute the result twice, to test for mutation of the db
        result = lab.bacon_path(self.db_large, actor_id)
        len_result = -1 if result is None else len(result)-1
        self.assertTrue(valid_path(self.db_large, result))
        self.assertEqual(len_result, len_expected)
        self.assertEqual(result[0], 4724)
        self.assertEqual(result[-1], actor_id)

    def test_13(self):
        # Bacon path, large database, does not exist
        actor_id = 1204555
        expected = None
        result = lab.bacon_path(self.db_large, actor_id)
        self.assertEqual(result, expected)


class Test04_ActorPath(unittest.TestCase):
    def setUp(self):
        """ Load actor/movie database """
        with open('resources/small.pickle', 'rb') as f:
            self.db_small = pickle.load(f)
        with open('resources/large.pickle', 'rb') as f:
            self.db_large = pickle.load(f)

    def test_14(self):
        # Actor path, large database, length of 7 (8 actors, 7 movies)
        actor_1 = 1345462
        actor_2 = 89614
        len_expected = 7

        first_result = lab.actor_to_actor_path(self.db_large, actor_1, actor_2)
        len_first_result = -1 if first_result is None else len(first_result)-1
        self.assertTrue(valid_path(self.db_large, first_result))
        self.assertEqual(len_first_result, len_expected)
        self.assertEqual(first_result[0], actor_1)
        self.assertEqual(first_result[-1], actor_2)

        second_result = lab.actor_to_actor_path(self.db_large, actor_1, actor_2)
        len_second_result = -1 if second_result is None else len(second_result)-1
        self.assertTrue(valid_path(self.db_large, second_result))
        self.assertEqual(len_second_result, len_expected)
        self.assertEqual(second_result[0], actor_1)
        self.assertEqual(second_result[-1], actor_2)

    def test_15(self):
        # Actor path, large database, length of 4 (5 actors, 4 movies)
        actor_1 = 100414
        actor_2 = 57082
        len_expected = 4
        result = lab.actor_to_actor_path(self.db_large, actor_1, actor_2)
        len_result = -1 if result is None else len(result)-1
        self.assertTrue(valid_path(self.db_large, result))
        self.assertEqual(len_result, len_expected)
        self.assertEqual(result[0], actor_1)
        self.assertEqual(result[-1], actor_2)

    def test_16(self):
        # Bacon path, large database, length of 7 (8 actors, 7 movies)
        actor_1 = 43011
        actor_2 = 1379833
        len_expected = 7
        result = lab.actor_to_actor_path(self.db_large, actor_1, actor_2)
        len_result = -1 if result is None else len(result)-1
        self.assertTrue(valid_path(self.db_large, result))
        self.assertEqual(len_result, len_expected)
        self.assertEqual(result[0], actor_1)
        self.assertEqual(result[-1], actor_2)

    def test_17(self):
        # Bacon path, large database, does not exist
        actor_1 = 43011
        actor_2 = 1204555
        expected = None
        result = lab.actor_to_actor_path(self.db_large, actor_1, actor_2)
        self.assertEqual(result, expected)

    def test_18(self):
        # actor path that exists
        x = 1372398
        y = 62597
        p = lab.actor_to_actor_path(self.db_large, x, y)
        e = [1372398, 7056, 4566, 540, 100567, 62597]
        self.assertTrue(valid_path(self.db_large, p))
        self.assertEqual(len(p), len(e))
        self.assertEqual(p[0], x)
        self.assertEqual(p[-1], y)

    def test_19(self):
        # actor path that exists
        e = [184581, 27111, 11086, 170882]
        x = e[0]
        y = e[-1]
        p = lab.actor_to_actor_path(self.db_large, x, y)
        self.assertTrue(valid_path(self.db_large, p))
        self.assertEqual(len(p), len(e))
        self.assertEqual(p[0], x)
        self.assertEqual(p[-1], y)

    def test_20(self):
        # actor path that exists
        e = list(range(700))
        random.shuffle(e)
        data = [(i, j, 0) for i,j in zip(e, e[1:])]
        random.shuffle(data)
        x = e[0]
        y = e[-1]
        p = lab.actor_to_actor_path(data, x, y)
        self.assertTrue(valid_path(data, p))
        self.assertEqual(len(p), len(e))
        self.assertEqual(p[0], x)
        self.assertEqual(p[-1], y)

    def test_21(self):
        x = 1234567890
        y = 1234567898
        data = self.db_large[:]
        data.append((x, y, 0))
        p = lab.actor_to_actor_path(data, 4724, y)
        self.assertEqual(p, None)


class Test05_Path(unittest.TestCase):
    def setUp(self):
        """ Load actor/movie database """
        with open('resources/large.pickle', 'rb') as f:
            self.db_large = pickle.load(f)

    def test_22(self):
        result = lab.actor_path(self.db_large, 975260, lambda p: False)
        self.assertEqual(result, None)

    def test_23(self):
        result = lab.actor_path(self.db_large, 975260, lambda p: True)
        self.assertEqual(result, [975260])

        result2 = lab.actor_path(self.db_large, 975260, lambda p: p == 975260)
        self.assertEqual(result2, [975260])

    def test_24(self):
        ppl = {536472, 44795, 240045, 19534}
        result1 = lab.actor_path(self.db_large, 10526, lambda p: p in ppl)
        self.assertNotEqual(result1, None)
        self.assertEqual(len(result1), 4)
        self.assertTrue(valid_path(self.db_large, result1))
        self.assertEqual(result1[0], 10526)
        self.assertEqual(result1[-1], 19534)

        result2 = lab.actor_path(self.db_large, 10526, lambda p: p in ppl and p > 19534)
        self.assertNotEqual(result2, None)
        self.assertEqual(len(result2), 5)
        self.assertTrue(valid_path(self.db_large, result2))
        self.assertEqual(result2[0], 10526)
        self.assertIn(result2[-1], {536472, 44795})

    def test_25(self):
        result = lab.actor_path(self.db_large, 152597, lambda p: p in {129507, 1400266, 1355798})
        self.assertNotEqual(result, None)
        self.assertEqual(len(result), 7)
        self.assertTrue(valid_path(self.db_large, result))
        self.assertEqual(result[0], 152597)
        self.assertIn(result[-1], {1400266, 1355798})

    def test_26(self):
        result = lab.actor_path(self.db_large, 26473, lambda p: p in {105656, 118946})
        self.assertNotEqual(result, None)
        self.assertEqual(len(result), 2)
        self.assertTrue(valid_path(self.db_large, result))
        self.assertEqual(result[0], 26473)
        self.assertEqual(result[-1], 118946)

    def test_27(self):
        result = lab.actor_path(self.db_large, 129507, lambda p: p == 152597)
        self.assertNotEqual(result, None)
        self.assertEqual(len(result), 8)
        self.assertTrue(valid_path(self.db_large, result))
        self.assertEqual(result[0], 129507)
        self.assertEqual(result[-1], 152597)


class Test06_ActorsConnectingFilms(unittest.TestCase):
    expected_lengths = {
        (18860, 75181): 2,
        (142416, 44521): 5,
    }

    def setUp(self):
        """ Load actor/movie database """
        with open('resources/large.pickle', 'rb') as f:
            self.db_large = pickle.load(f)

    def check_connected_movie_path(self, m1, m2):
        m1a = set()
        m2a = set()
        for a, b, c in self.db_large:
            if c == m1:
                s = m1a
            elif c == m2:
                s = m2a
            else:
                continue
            s.add(a)
            s.add(b)
        result = lab.actors_connecting_films(self.db_large, m1, m2)
        self.assertNotEqual(result, None)
        self.assertEqual(len(result), self.expected_lengths[(m1, m2)])
        self.assertIn(result[0], m1a)
        self.assertIn(result[-1], m2a)
        self.assertTrue(valid_path(self.db_large, result))

    def test_28(self):
        self.check_connected_movie_path(18860, 75181)

    def test_29(self):
        self.check_connected_movie_path(142416, 44521)


def random_number_list(L, i=1):
    o = list(range(i*100000, i*100000+L))
    random.shuffle(o)
    return o


def valid_path(d, p):
    x = {frozenset(i[:-1]) for i in d}
    return all(frozenset(i) in x for i in zip(p, p[1:]))


def make_bacon_tree(L, n=10):
    id_set = 2
    path = [4724] + random_number_list(L, i=1)
    n -= 1
    out = set((i,j) for i,j in zip(path, path[1:]))
    while n > 0:
        point = random.choice(range(len(path)-1))
        d = L - point
        if d == 0:
            continue
        newpath = random_number_list(d, i=id_set)
        p = [path[point]] + newpath
        out |= set((i,j) for i,j in zip(p, p[1:]))
        id_set += 1
        n -= 1
    return [(i, j, 0) for i,j in out]


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
