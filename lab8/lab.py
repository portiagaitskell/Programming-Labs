'''
Portia Gaitskell
Spring 2020

'''

"""6.009 Lab 8: carlae Interpreter Part 2"""

# REPLACE THIS FILE WITH YOUR lab.py FROM LAB 7, WHICH SHOULD BE THE STARTING
# POINT FOR THIS LAB.  YOU SHOULD ALSO ADD: import sys
import doctest
import sys
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

    # searches for first environment that references key
    # if none found, raise name error
    def search(self, key):
        if key in self.variables:
            return self
        elif self.parent:
            return self.parent.search(key)
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


class Pair:
    """
    Class representing cons cell and lists
    - car: represents the first element in the pair
    - cdr: represents the second element in the pair, int for cons cell, either None or Pair object for lists

    """
    # initialize car and ccr
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    # return the length of linked list object
    def __len__(self):
        # if no more elements in linked list, return 1
        if self.cdr is None:
            return 1
        # recursively find length of rest of list
        else:
            return 1 + len(self.cdr)

    # find element at index, if index==0 return car
    # else: recursively find element, decrease index by 1
    def __getitem__(self, index):
        if index == 0:
            return self.car
        else:
            return self.cdr[index-1]

    # copies Pair instances
    # copies car, recursively copies self.cdr
    def copy(self):
        self_copy = Pair(self.car, None)
        if self.cdr is None:
            return self_copy
        else:
            new_cdr = self.cdr.copy()
            self_copy.cdr = new_cdr
            return self_copy

    # concatenates self and next_list
    # takes one list as parameter
    def concat(self, next_list):
        # if cdr is None, add next_list here
        if self.cdr is None:
            self.cdr = next_list
            return self
        # recursively update self.cdr
        # return self
        else:
            self.cdr = self.cdr.concat(next_list)
            return self

    # maps function to each element in pair
    # find new_car, create new list
    # recursively find new_cdr
    def map(self, fn):
        new_car = fn([self.car])
        new_list = Pair(new_car, None)
        if self.cdr is None:
            return new_list
        else:
            new_cdr = self.cdr.map(fn)
            new_list.cdr = new_cdr
            return new_list

    # applies function to elements in list, only returns elements that return True
    def filter(self, fn):
        first_elt = fn([self.car])
        # if first_elt is True, add it as car of new list
        if first_elt:
            new_list = Pair(self.car, None)
            if self.cdr is None:
                return new_list
            else:
                new_cdr = self.cdr.filter(fn)
                new_list.cdr = new_cdr
                return new_list
        # if first element is false and cdr not None, run filter on cdr
        elif self.cdr is not None:
            return self.cdr.filter(fn)
        # else return None
        else:
            return None

    # combines elements of list using function, starting with initval
    # calculate new val, if self.cdr is None, return new_val
    # else recursive on self.cdr using function and new_val
    def reduce(self, fn, initval):
        new_val = fn([initval, self.car])
        if self.cdr is None:
            return new_val
        else:
            return self.cdr.reduce(fn, new_val)

    def __str__(self):
        return str(self.car) + ', ' + str(self.cdr)


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


# list of args passed as parameters
def cons(args):
    """
    Constructs new objects, is used to make ordered pairs as Pair objects
    Takes list of two objects, raise EvaluationError is not length(2)
    """
    if len(args) == 2:
        return Pair(args[0], args[1])

    else:
        raise EvaluationError


def car(arg):
    """
    Takes cons cell (instance Pair class) as argument
    Returns the first element in the pair.
    If arg not a cons cell, raise  EvaluationError.
    """
    if len(arg) == 1 and isinstance(arg[0], Pair):
        return arg[0].car
    else:
        raise EvaluationError


def cdr(arg):
    """
    Takes cons cell (instance Pair class) as argument
    Returns the second element in the pair.
    If arg not a cons cell, raise  EvaluationError.
    """
    if len(arg) == 1 and isinstance(arg[0], Pair):
        return arg[0].cdr
    else:
        raise EvaluationError


def linked_list(args, en = None):
    """
    Takes argument as list of numbers following list
    If not args passed, return empty list
    If only one arg passed, evaluate created list using cons and nil
    If multiple passed, create list using 'list' keyword, evaluate
    """
    if len(args) == 0:
        return None
    elif len(args) == 1:
        return evaluate(['cons', args[0], 'nil'], en)
    else:
        ll = ['list']+args[1:]
        return evaluate(['cons', args[0], ll], en)


def length(args):
    """
    Takes a linked list element (nested Pair object)
    If no argument passed, return 0
    Use class function 'len' to find length
    """
    if args[0] is None:
        return 0
    try:
        length = len(args[0])
        return length
    except:
        raise EvaluationError


def eltatindex(args):
    """
    Takes list and a nonnegative index, returns the element at the given index in the given list
    Checks for two elements in args, runs __getitem__
    """
    try:
        ll, i = args
        return ll[i]
    except:
        raise EvaluationError


def is_list(arg):
    """
    Checks to see if args is a linked list
    Returns True if: arg is None OR (arg and arg.cdr are instances of Pair)
    Else: return False
    """
    if arg is None:
        return True
    else:
        # if instance of Pair and arg.cdr is instance of list
        if isinstance(arg, Pair) and is_list(arg.cdr):
            return True
        else:
            return False


def concat(args):
    """
    Takes arbitrary num of lists as args
    Returns a new list representing the concatenation of these lists.
    If exactly one list is passed in, it should return a copy of that list.
    If concat is called with no arguments, it should produce an empty list.
    Calling concat on any elements that are not lists should result in an EvaluationError.
    """
    # initialize first elt
    ll_1 = None

    # find first non empty linked list
    # ll_1 remains None is len(args) == 0
    for i, elt in enumerate(args):
        if elt is not None:
            try:
                #copy first element
                ll_1 = elt.copy()
                break
            except:
                raise EvaluationError

    if ll_1 is None:
        return None
    # if first element is not a list, raise EvaluationError
    elif not is_list(ll_1):
        raise EvaluationError

    # go through each element after first
    for ll in args[i+1:]:
        # if None, do nothing
        if ll is None:
            continue
        # if not a list, raise error
        elif not is_list(ll):
            raise EvaluationError
        try:
            # use concat method to add to ll_1
            ll_1 = ll_1.concat(ll.copy())
        except:
            raise EvaluationError

    return ll_1

def map_list(args):
    """
    (map FUNCTION LIST)
    Takes a function and a list as arguments
    Returns a new list w/ results of applying function to each element of list
    Uses map function of Pair class
    """
    try:
        fn, ll = args
    except:
        raise EvaluationError

    if ll is None:
        return None
    if not is_list(ll):
        raise EvaluationError

    else:
        try:
            mapping = ll.map(fn)
            return mapping
        except:
            EvaluationError


def filter_list(args):
    """
    (filter FUNCTION LIST)
    Takes function and a list as arguments
    Returns a new list containing only the elements of the given list
        for which the given function returns true.
    """
    try:
        fn, ll = args
    except:
        raise EvaluationError
    if ll is None:
        return None
    if not is_list(ll):
        raise EvaluationError
    else:
        try:
            # use Pair method .filter
            filtered = ll.filter(fn)
            return filtered
        except:
            raise EvaluationError

def reduce(args):
    """
    (reduce FUNCTION LIST INITVAL)
    Takes function, list, and initial value as inputs.
    Returns output by successively applying the given function to the elements in the list,
        maintaining a ongoing val
    """
    try:
        fn, ll, i = args
    except:
        EvaluationError

    if not is_list(ll):
        raise EvaluationError
    elif ll is None:
        return i
    else:
        try:
            # use .reduce Pair function
            reduced = ll.reduce(fn, i)
            return reduced
        except:
            EvaluationError


# builtin functions
carlae_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    '*': lambda args: args[0] if len(args) == 1 else (args[0] * carlae_builtins['*'](args[1:])),
    '/': lambda args: args[0] if len(args) == 1 else (args[0] / carlae_builtins['*'](args[1:])),
    '#t': True,
    '#f': False,
    '=?': lambda args: True if len(args) == 1 else (False if args[0] != args[1] else carlae_builtins['=?'](args[1:])),
    '>': lambda args: True if len(args) == 1 else (False if args[0] <= args[1] else carlae_builtins['>'](args[1:])),
    '>=': lambda args: True if len(args) == 1 else (False if args[0] < args[1] else carlae_builtins['>='](args[1:])),
    '<': lambda args: True if len(args) == 1 else (False if args[0] >= args[1] else carlae_builtins['<'](args[1:])),
    '<=': lambda args: True if len(args) == 1 else (False if args[0] > args[1] else carlae_builtins['<='](args[1:])),
    'not': lambda arg: True if not arg[0] else False,
    'cons': cons,
    'car': car,
    'cdr': cdr,
    'nil': None,
    'length': length,
    'elt-at-index': eltatindex,
    'concat': concat,
    'map': map_list,
    'filter': filter_list,
    'reduce': reduce
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

    # catches is passed in elt is empty
    if len(tree) == 0:
        raise EvaluationError

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

    # if first element is 'and'
    elif tree[0] == 'and':
        for elt in tree[1:]:
            # if any arg evaluates to False, immediately return False
            if not evaluate(elt, en):
                return False
        return True

    # if first element is 'or'
    elif tree[0] == 'or':
        for elt in tree[1:]:
            # if any arg evaluates to True, immediately return True
            if evaluate(elt, en):
                return True
        return False

    # if first element is 'if'
    # if tree[1] is tree evluate true expression (tree[2])
    # else evaluate false expression (tree[3])
    elif tree[0] == 'if':
        if evaluate(tree[1], en):
            return evaluate(tree[2], en)
        else:
            return evaluate(tree[3], en)

    # if 'list' call list function
    elif tree[0] == 'list':
        return linked_list(tree[1:], en)

    # if 'begin' evaluate up to last element, only return last evaluate
    elif tree[0] == 'begin':
        args = tree[1:]
        for i in range(len(args)-1):
            evaluate(args[i], en)
        return evaluate(args[-1], en)

    # if 'let', create new Envt
    # extract expression and body, for each var and val in expression
    # add variable and value to new environment by evaluating in existing envt
    # evaluate body of function in new envt
    elif tree[0] == 'let':
        new_en = Environment(en)
        expression, body = tree[1], tree[2]
        for var, val in expression:
            new_en[var] = evaluate(val, en)
        return evaluate(body, new_en)

    # extract variable and expression
    # set evaluate variable in envt
    # create a new envt by searching for variable in nearest ent
    # set variable in found envt to evaluate value
    elif tree[0] == 'set!':
        variable, expression = tree[1], tree[2]
        eval_var = evaluate(expression, en)
        new_en = en.search(variable)
        new_en[variable] = eval_var
        return eval_var

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


def evaluate_file(filename, en=None, return_en = False):
    """
    Runs evaluate expression from a file, optional environment
    """
    with open(filename, 'rt') as file:
        data = file.read()

    inp = data
    #return evaluate(parse(tokenize(inp)), en)
    if not return_en:
        return evaluate(parse(tokenize(inp)), en)
    else:
        return result_and_env(parse(tokenize(inp)), en)


def REPL(en = None):
    # creates environment
    #if not en:
        #en = Environment(Environment(None, carlae_builtins))
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
    en = Environment(Environment(None, carlae_builtins))
    # if file name is passed in, len(sys.argv) > 1
    if len(sys.argv) > 1:
        files = sys.argv[1:]
        en = Environment(Environment(None, carlae_builtins))
        for f in files:
            res, en = evaluate_file(f, en, return_en=True)
    REPL(en)
    #else:
        #REPL()


