'''
Portia Gaitskell
Spring 2020

'''

#!/usr/bin/env python3
"""6.009 Lab 7: carlae Interpreter"""

import doctest
# NO ADDITIONAL IMPORTS!


class EvaluationError(Exception):
    """
    Exception to be raised if there is an error during evaluation other than a
    NameError.
    """
    pass


class Environment:
    """
    Environment objects that represent current environment
    Hold parent Environment object and variables defined within the environment
    Functions:
        - set: sets variable in current environment
        - get: searches current and all parent environments for key
    """
    def __init__(self, parent, args=None):
        # parent environment object
        self.parent = parent
        # holds all variables defined in environment
        self.variables = {}
        # args is dictionary
        if args:
            self.variables = args

    def __setitem__(self, key, value):
        self.variables[key] = value

    def __getitem__(self, key):
        # if key in current environment, return
        if key in self.variables:
            return self.variables[key]
        # if parent exists, check parent for key
        elif self.parent:
            return self.parent[key]
        # does not exist anywhere
        else:
            raise NameError


class Function:
    """
    Function objects contain the parameters, body, and environment created in of new functions
    Function: call
        - syntax: Function(args)
        Checks if args length = params length
        Creates new environment, sets params = args in new environment
        Runs evaluate using expression in new environment
    """
    def __init__(self, en_created, params, expr):
        self.en_created = en_created
        # list of parameters
        self.params = params
        # list to be evaluate
        self.expr = expr

    def __call__(self, args):
        # create new environment for function to run in
        # parent environment in environment created in
        en = Environment(self.en_created)
        # check if valid length of args
        if len(self.params) != len(args):
            raise EvaluationError
        else:
            # set each param = respective arg
            for i in range(len(args)):
                en[self.params[i]] = args[i]
            # use evaluate on self.expr in new environment
            return evaluate(self.expr, en)


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a carlae
                      expression
    """
    # helper function used to split parenthesis from word
    def parenthesis_split(word):
        out = []
        ongoing = ''
        # for each char in word
        for char in word:
            # if parenthesis, append ongoing and parenthesis, reset ongoing
            if char == '(' or char == ')':
                if ongoing:
                    out.append(ongoing)
                out.append(char)
                ongoing = ''
            # else append next char to ongoing
            else:
                ongoing += char
        if ongoing:
            out.append(ongoing)
        # return list
        return out

    # split source into lines to extract
    lines = source.splitlines()
    # final tokenized list
    final = []
    # for each line
    for line in lines:
        # get index of comment, -1 if not comment
        # splice list if comment
        comment = line.find(';')
        if comment != -1:
            line = line[0: comment]

        # split line into words
        line = line.split()
        for elt in line:
            # check for parenthesis and run helper function
            if '(' in elt or ')' in elt:
                out = parenthesis_split(elt)
                final += out
            # else just append entire word
            else:
                final.append(elt)
    # returns list of strings
    return final


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    tokens = tokens

    # helper function - converts a word into its correct type
    # if str, return str
    def convert(word):
        try:
            word = int(word)
        except ValueError:
            try:
                word = float(word)
            except ValueError:
                pass
        return word

    # recursive parse helper function
    def parse_expression(index):
        final = []
        # get token at current index
        token = tokens[index]
        # if open paren (should always be '(' at start of S-expression)
        if token == '(':
            # continue while objects in tokens still left to consider
            while index < len(tokens) - 1:
                # increment index
                index += 1
                token = tokens[index]
                # if ')', break and end S-expression
                if token == ')':
                    break
                # if '(' - add layer of recursion, return terminating index
                elif token == '(':
                    temp, index = parse_expression(index)
                    final.append(temp)
                # else, append given element to final
                else:
                    final.append(convert(token))
            return final, index
        else:
            raise SyntaxError

    # if single object, return converted object
    if len(tokens) == 1:
        return convert(tokens[0])

    # if num open != num closed --> SyntaxError
    if tokens.count('(') != tokens.count(')'):
        raise SyntaxError

    # return output[0] of helper function
    return parse_expression(0)[0]


# builtin functions
carlae_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': lambda args: args[0] if len(args) == 1 else (args[0] * carlae_builtins['*'](args[1:])),
    '/': lambda args: args[0] if len(args) == 1 else (args[0] / carlae_builtins['*'](args[1:]))
}


def evaluate(tree, en=None):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
        en (class Environment): if not passed, create new global envrionment
    """
    # initialize en if None
    if not en:
        # initialize builtin environment
        # set builtin variables
        builtin = Environment(None, carlae_builtins)
        # initialize global environment
        en = Environment(builtin)

    # if tree is single object (not a list)
    if not isinstance(tree, list):
        if isinstance(tree, int) or isinstance(tree, float):
            return tree
        else:
            # lookup variable in environment
            return en[tree]

    # if first word is 'define', create variables within global frame
    # (define (NAME) (params) (expr)) --> always 3 or 4 elements long
    if tree[0] == 'define':
        if len(tree) > 4:
            raise EvaluationError
        # if NAME is an S-expression
        if isinstance(tree[1], list):
            var = tree[1][0]
            # value ['lambda', [params], [expr]]
            val = ['lambda'] + [tree[1][1:]] + tree[2:]
            # evaluate, set equal, return
            evaluated_val = evaluate(val, en)
            en[var] = evaluated_val
            return evaluated_val

        else:
            # name of variable to be stored in environment
            var = tree[1]
            # can be individual object or list
            val = tree[2]
            evaluated_val = evaluate(val, en)
            en[var] = evaluated_val
            return evaluated_val

    # if first element is 'lambda'
    elif tree[0] == 'lambda':
        # create function object and return
        fn = Function(en, tree[1], tree[2])
        return fn

    # Evaluate branch
    else:
        fn = evaluate(tree[0], en)
        # fn must not be int or float
        if isinstance(fn, int) or isinstance(fn, float):
            raise EvaluationError
        # evaluate every element inside tree[1:]
        new = []
        for elt in tree[1:]:
            new.append(evaluate(elt, en))

        return fn(new)


def result_and_env(tree, en = None):
    """
    Function used for testing
    Creates global environment, if not given
    Call evaluate and returns value and environment
    """
    if not en:
        # initialize builtin environment
        # set builtin variables
        builtin = Environment(None, carlae_builtins)
        # initialize global environment
        en = Environment(builtin)

    # return evaluate and updated environment
    return evaluate(tree, en), en


def REPL():
    # creates environment
    en = Environment(Environment(None, carlae_builtins))
    # initialize input
    inp = ''
    while inp != 'QUIT':
        inp = input('in> ')
        # try to print result, catch exceptions
        try:
            inp = parse(tokenize(inp))
            out, en = result_and_env(inp, en)
            print('out> ' + str(out))
        except Exception as e:
            print(type(e))



if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    s = '(define (five) (+ 2 3))'
    s2 = '(define five (lambda () (+ 2 3)))'
    s3 = '(define (square x) (* x x))'
    s4 = '(define square (lambda (x) (* x x)))'
    #print(parse(tokenize(s3)))
    #print(parse(tokenize(s4)))
    REPL()
