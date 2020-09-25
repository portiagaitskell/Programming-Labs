#!/usr/bin/env python3
import os
import lab
import sys
import json
import unittest

TEST_DIRECTORY = os.path.dirname(__file__)

class NotImplemented:
    def __eq__(self, other):
        return False

try:
    nil_rep = lab.result_and_env(lab.parse(['nil']))[0]
except:
    nil_rep = NotImplemented()

def list_from_ll(ll):
    if isinstance(ll, lab.Pair):
        if ll.cdr == nil_rep:
            return [list_from_ll(ll.car)]
        return [list_from_ll(ll.car)] + list_from_ll(ll.cdr)
    elif ll == nil_rep:
        return []
    elif isinstance(ll, (float, int)):
        return ll
    else:
        return 'SOMETHING'


class LispTest(unittest.TestCase):
    @staticmethod
    def _test_file(fname, num):
        try:
            out = lab.evaluate_file(os.path.join(TEST_DIRECTORY, 'test_files', fname))
            out = list_from_ll(out)
            out = {'ok': True, 'output': out}
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            out = {'ok': False, 'type': exc_type.__name__}
        with open(os.path.join(TEST_DIRECTORY, 'test_outputs', f'{num}.json')) as f:
            expected = json.load(f)
        msg = LispTest._test_file_msg(fname, num)
        return out, expected, msg

    @staticmethod
    def make_tester(func):
        """
        Helper to wrap a function so that, when called, it produces a
        dictionary instead of its normal result.  If the function call works
        without raising an exception, then the results are included.
        Otherwise, the dictionary includes information about the exception that
        was raised.
        """
        def _tester(*args):
            try:
                return {'ok': True, 'output': func(*args)}
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                return {'ok': False, 'type': exc_type.__name__}
        return _tester

    @staticmethod
    def load_test_values(n):
        """
        Helper function to load test inputs/outputs
        """
        with open(os.path.join(TEST_DIRECTORY, 'test_inputs', f'{n:02d}.json')) as f:
            inputs = json.load(f)
        with open(os.path.join(TEST_DIRECTORY, 'test_outputs', f'{n:02d}.json')) as f:
            outputs = json.load(f)
        return inputs, outputs

    @staticmethod
    def run_continued_evaluations(ins):
        """
        Helper to evaluate a sequence of expressions in an environment.
        """
        env = None
        outs = []
        try:
            t = LispTest.make_tester(lab.result_and_env)
        except:
            t = LispTest.make_tester(lab.evaluate)
        for i in ins:
            if env is None:
                args = (i, )
            else:
                args = (i, env)
            out = t(*args)
            if out['ok']:
                env = out['output'][1]
            if out['ok']:
                try:
                    typecheck = (int, float, lab.Pair)
                    func = list_from_ll
                except:
                    typecheck = (int, float)
                    func = lambda x: x if isinstance(x, typecheck) else 'SOMETHING'
                out['output'] = func(out['output'][0])
            outs.append(out)
        return outs

    def _compare_outputs(self, x, y, msg):
        if x['ok']:
            self.assertTrue(y['ok'], msg=msg + f'\n\nExpected an exception ({y.get("type", None)}), not {x.get("output", None)}')
            if isinstance(x['output'], (int, float)):
                self.assertEqual(type(x['output']), type(y['output']), msg=msg + f'\n\nOutput has incorrect type (expected {type(y.get("output", None))} but got {type(x.get("output", None))}')
                self.assertAlmostEqual(x['output'], y['output'], msg=msg + f'\n\nOutput has incorrect value (expected {y.get("output", None)!r} but got {x.get("output", None)!r})')
            else:
                self.assertEqual(x['output'], y['output'], msg=msg + f'\n\nOutput has incorrect value (expected {y.get("output", None)!r} but got {x.get("output", None)!r})')
        else:
            self.assertFalse(y['ok'], msg=msg + f'\n\nDid not expect an exception (got {x.get("type", None)}, expected {y.get("output", None)!r})')
            self.assertEqual(x['type'], y['type'], msg=msg + f'\n\nExpected {y.get("type", None)} to be raised, not {x.get("type", None)}')

    def _test_continued_evaluations(self, n):
        """
        Test that the results from running continued evaluations in the same
        environment match the expected values.
        """
        inp, out = self.load_test_values(n)
        msg = self._test_num_msg(n)
        results = self.run_continued_evaluations(inp)
        for result, expected in zip(results, out):
            self._compare_outputs(result, expected, msg)

    def _test_raw_continued_evaluations(self, n):
        """
        Test that the results from running continued evaluations in the same
        environment match the expected values.
        """
        with open(os.path.join(TEST_DIRECTORY, 'test_outputs', f'{n:02d}.json')) as f:
            expected = json.load(f)
        msg = "for test_inputs/%02d.carlae" % n
        env = None
        results = []
        try:
            t = LispTest.make_tester(lab.result_and_env)
        except:
            t = LispTest.make_tester(lab.evaluate)
        with open(os.path.join(TEST_DIRECTORY, 'test_inputs', f'{n:02d}.carlae')) as f:
            for line in iter(f.readline, ''):
                #print(line.strip())
                parsed = lab.parse(lab.tokenize(line.strip()))
                #print(parsed)
                #print('')
                out = t(*((parsed, ) if env is None else (parsed, env)))
                if out['ok']:
                    env = out['output'][1]
                if out['ok']:
                    try:
                        typecheck = (int, float, lab.Pair)
                        func = list_from_ll
                    except:
                        typecheck = (int, float)
                        func = lambda x: x if isinstance(x, typecheck) else 'SOMETHING'
                    out['output'] = func(out['output'][0])
                results.append(out)
        #print(results)
        for result, exp in zip(results, expected):
            #print('RESULT' + str(result))
            #print('EXP: ' + str(exp))
            self._compare_outputs(result, exp, msg=msg)


    def run_test_number(self, n, func):
        tester = self.make_tester(func)
        inp, out = self.load_test_values(n)
        msg = self._test_num_msg(n)
        for i, o in zip(inp, out):
            self._compare_outputs(tester(i), o, msg)

    @staticmethod
    def _test_num_msg(n):
        msg = "\nfor test_inputs/"+str(n)+".json"
        try:
            with open(os.path.join(TEST_DIRECTORY, 'carlae_code', '{n:02d}.carlae')) as f:
                code = f.read()
            msg += " and carlae_code/"+str(n)+".carlae"
        except Exception as e:
            with open(os.path.join(TEST_DIRECTORY, 'test_inputs', f'{n:02d}.json')) as f:
                code = str(json.load(f))
        msg += " that begins with\n"
        msg += code if len(code) < 80 else code[:80]+'...'
        return msg

    @staticmethod
    def _test_file_msg(fname, n):
        msg = "\nwhile running test_files/"+fname+" that begins with\n"
        with open(os.path.join(TEST_DIRECTORY, 'test_files', fname)) as f:
            code = f.read()
        msg += code if len(code) < 80 else code[:80]+'...'
        return msg



class Test1_OldBehaviors(LispTest):
    def tests_01_to_29_oldbehaviors(self):
        self.run_test_number(1, lab.tokenize)
        self.run_test_number(2, lab.parse)
        self.run_test_number(3, lambda i: lab.parse(lab.tokenize(i)))
        self.run_test_number(4, lab.evaluate)
        self.run_test_number(5, lab.evaluate)
        self._test_continued_evaluations(6)
        self._test_continued_evaluations(7)
        self._test_continued_evaluations(8)
        self._test_continued_evaluations(9)
        self._test_continued_evaluations(10)
        self._test_continued_evaluations(11)
        self._test_continued_evaluations(12)
        self._test_raw_continued_evaluations(13)
        self._test_raw_continued_evaluations(14)
        self._test_raw_continued_evaluations(15)
        self._test_raw_continued_evaluations(16)
        self._test_raw_continued_evaluations(17)
        self._test_raw_continued_evaluations(18)
        self._test_raw_continued_evaluations(19)
        self._test_raw_continued_evaluations(20)
        self._test_raw_continued_evaluations(21)
        self._test_raw_continued_evaluations(22)
        self._test_raw_continued_evaluations(23)
        self._test_raw_continued_evaluations(24)
        self._test_raw_continued_evaluations(25)
        self._test_raw_continued_evaluations(26)
        self._test_raw_continued_evaluations(27)
        self._test_raw_continued_evaluations(28)
        self._test_raw_continued_evaluations(29)


class Test2_Conditionals(LispTest):
    def test_30_conditionals(self):
        self._test_raw_continued_evaluations(30)

    def test_31_abs(self):
        self._test_raw_continued_evaluations(31)

    def test_32_and(self):
        self._test_raw_continued_evaluations(32)

    def test_33_or(self):
        self._test_raw_continued_evaluations(33)

    def test_34_not(self):
        self._test_raw_continued_evaluations(34)

    def test_35_shortcircuit_1(self):
        self._test_raw_continued_evaluations(35)

    def test_36_shortcircuit_2(self):
        self._test_raw_continued_evaluations(36)

    def test_37_shortcircuit_3(self):
        self._test_raw_continued_evaluations(37)

    def test_38_shortcircuit_4(self):
        self._test_raw_continued_evaluations(38)

    def test_39_conditional_scoping(self):
        self._test_raw_continued_evaluations(39)

    def test_40_conditional_scoping_2(self):
        self._test_raw_continued_evaluations(40)


class Test3_Lists(LispTest):
    def test_41_cons_lists(self):
        self._test_raw_continued_evaluations(41)

    def test_42_car_cdr(self):
        self._test_raw_continued_evaluations(42)

    def test_43_car_cdr_2(self):
        self._test_raw_continued_evaluations(43)

    def test_44_length(self):
        self._test_raw_continued_evaluations(44)

    def test_45_indexing(self):
        self._test_raw_continued_evaluations(45)

    def test_46_concat(self):
        self._test_raw_continued_evaluations(46)

    def test_47_list_ops(self):
        self._test_raw_continued_evaluations(47)

    def test_48_map_builtin(self):
        self._test_raw_continued_evaluations(48)

    def test_49_map_carlaefunc(self):
        self._test_raw_continued_evaluations(49)

    def test_50_filter_builtin(self):
        self._test_raw_continued_evaluations(50)

    def test_51_filter_carlaefunc(self):
        self._test_raw_continued_evaluations(51)

    def test_52_reduce_builtin(self):
        self._test_raw_continued_evaluations(52)

    def test_53_reduce_carlaefunc(self):
        self._test_raw_continued_evaluations(53)

    def test_54_map_filter_reduce(self):
        self._test_raw_continued_evaluations(54)


class Test4_Begin(LispTest):
    def test_55_begin(self):
        self._test_raw_continued_evaluations(55)


class Test5_Files(LispTest):
    def test_56(self):
        self._compare_outputs(*self._test_file("small_test1.crl", 56))

    def test_57(self):
        self._compare_outputs(*self._test_file("small_test2.crl", 57))

    def test_58(self):
        self._compare_outputs(*self._test_file("small_test3.crl", 58))

    def test_59(self):
        self._compare_outputs(*self._test_file("small_test4.crl", 59))

    def test_60(self):
        self._compare_outputs(*self._test_file("small_test5.crl", 60))


class Test6_Let_SetBang(LispTest):
    def test_61_let(self):
        self._test_raw_continued_evaluations(61)

    def test_62_let_2(self):
        self._test_raw_continued_evaluations(62)

    def test_63_let_3(self):
        self._test_raw_continued_evaluations(63)

    def test_64_setbang(self):
        self._test_raw_continued_evaluations(64)

    def test_65_begin2(self):
        self._test_raw_continued_evaluations(65)


class Test7_DeepNesting(LispTest):
    def test_66(self):
        self._test_raw_continued_evaluations(66)

    def test_67(self):
        self._test_raw_continued_evaluations(67)

    def test_68(self):
        self._test_raw_continued_evaluations(68)


class Test8_RealPrograms(LispTest):
    def test_69_counters_oop(self):
        self._test_raw_continued_evaluations(69)

    def test_70_fizzbuzz(self):
        self._test_raw_continued_evaluations(70)

    def test_71_primes(self):
        self._test_raw_continued_evaluations(71)

    def test_72_averages_oop(self):
        self._test_raw_continued_evaluations(72)


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
