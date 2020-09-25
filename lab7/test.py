#!/usr/bin/env python3
import os
import lab
import sys
import json
import unittest

TEST_DIRECTORY = os.path.dirname(__file__)

class LispTest(unittest.TestCase):
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
        with open('test_inputs/%02d.json' % n) as f:
            inputs = json.load(f)
        with open('test_outputs/%02d.json' % n) as f:
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
                if isinstance(out['output'][0], (int, float)):
                    out['output'] = out['output'][0]
                else:
                    out['output'] = 'SOMETHING'
            outs.append(out)
        return outs

    def _compare_outputs(self, x, y, msg):
        if x['ok']:
            self.assertTrue(y['ok'], msg=msg + f'\n\nExpected an exception ({y.get("type", None)})')
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
        with open('test_outputs/%02d.json' % n) as f:
            expected = json.load(f)
        msg = "for test_inputs/%02d.carlae" % n
        env = None
        results = []
        try:
            t = LispTest.make_tester(lab.result_and_env)
        except:
            t = LispTest.make_tester(lab.evaluate)
        with open('test_inputs/%02d.carlae' % n) as f:
            for line in iter(f.readline, ''):
                parsed = lab.parse(lab.tokenize(line.strip()))
                print(parsed)
                print('')
                out = t(*((parsed, ) if env is None else (parsed, env)))
                if out['ok']:
                    env = out['output'][1]
                if out['ok']:
                    if isinstance(out['output'][0], (int, float)):
                        out['output'] = out['output'][0]
                    else:
                        out['output'] = 'SOMETHING'
                results.append(out)
        for result, exp in zip(results, expected):
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
            with open('carlae_code/%02d.carlae' % n) as f:
                code = f.read()
            msg += " and carlae_code/"+str(n)+".carlae"
        except Exception as e:
            with open('test_inputs/%02d.json' % n) as f:
                code = str(json.load(f))
        msg += " that begins with\n"
        msg += code if len(code) < 80 else code[:80]+'...'
        return msg


class Test1_Parse(LispTest):
    def test_01_tokenize(self):
        self.run_test_number(1, lab.tokenize)

    def test_02_parse(self):
        self.run_test_number(2, lab.parse)

    def test_03_tokenize_and_parse(self):
        self.run_test_number(3, lambda i: lab.parse(lab.tokenize(i)))


class Test2_Eval(LispTest):
    def test_04_calc(self):
        self.run_test_number(4, lab.evaluate)

    def test_05_mult_div(self):
        self.run_test_number(5, lab.evaluate)

    def test_06_simple_assignment(self):
        self._test_continued_evaluations(6)

    def test_07_simple_assignment(self):
        self._test_continued_evaluations(7)

    def test_08_bad_lookups(self):
        self._test_continued_evaluations(8)

    def test_09_rename_builtin(self):
        self._test_continued_evaluations(9)


class Test3_Func(LispTest):
    def test_10_simple_function(self):
        self._test_continued_evaluations(10)

    def test_11_inline_lambda(self):
        self._test_continued_evaluations(11)

    def test_12_closures(self):
        self._test_continued_evaluations(12)


class Test4_All(LispTest):
    def test_13_short_definition(self):
        self._test_raw_continued_evaluations(13)

    def test_14_dependent_definition(self):
        self._test_raw_continued_evaluations(14)

    def test_15_scoping_1(self):
        self._test_raw_continued_evaluations(15)

    def test_16_scoping_2(self):
        self._test_raw_continued_evaluations(16)

    def test_17_scoping_3(self):
        self._test_raw_continued_evaluations(17)

    def test_18_scoping_4(self):
        self._test_raw_continued_evaluations(18)

    def test_19_scoping_5(self):
        self._test_raw_continued_evaluations(19)

    def test_20_calling_errors(self):
        self._test_raw_continued_evaluations(20)

    def test_21_functionception(self):
        self._test_raw_continued_evaluations(21)

    def test_22_alias(self):
        self._test_raw_continued_evaluations(22)

    def test_23_big_scoping_1(self):
        self._test_raw_continued_evaluations(23)

    def test_24_big_scoping_2(self):
        self._test_raw_continued_evaluations(24)

    def test_25_big_scoping_3(self):
        self._test_raw_continued_evaluations(25)

    def test_26_big_scoping_4(self):
        self._test_raw_continued_evaluations(26)


class Test5_Additional(LispTest):
    def test_27_more_syntax(self):
        self._test_raw_continued_evaluations(27)

    def test_28_nested_defines(self):
        self._test_raw_continued_evaluations(28)

    def test_29_nested_defines(self):
        self._test_raw_continued_evaluations(29)


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
