'''
Portia Gaitskell
Spring 2020

'''

#!/usr/bin/env python3
"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """

    return main_recursive(formula, {})


def main_recursive(formula, solution):
    """
    Main recursive function used
    1) Checks for any single units - if any are found, runs recursively until none are found
        Updates formula, and collapses it accordingly
        Updates solution accordingly
    2) Makes a guess of the first variable found - uses given value to inform guess
        If no errors, continue down this path, guessing on each next variable until solution is found
            or it returns None
        If error, guess opposite of given, and follow same procedures
        If both return None, return None

    :param formula: formula in CNF form
    :param solution: dictionary matching variables (key), to a boolean (True or False)
    :return: valid solution or None
    """

    if not formula:
        return solution

    unit_flag = False

    for line in formula:
        # equals empty list within formula - error and return None
        if len(line) == 0:
            return None

        # unit found - flag causes recursion
        if len(line) == 1:
            unit_flag = True

            # if unit not in solution, add to solution
            if line[0][0] not in solution:
                solution[line[0][0]] = line[0][1]
                # remove individual line
                formula.remove(line)
            # if unit in solution,
            elif line[0][0] in solution:
                # if solution's don't match - error and return None
                if solution[line[0][0]] != line[0][1]:
                    # contradiction
                    return None
                else:
                    formula.remove(line)

    # if single statement has been found, trigger recursion
    if unit_flag:
        # update formula using updated solution
        formula = simplify_formula(formula, solution)
        # output new solution by rerunning main_recursion
        # do not need to copy as no "guesses" have been made
        solution = main_recursive(formula, solution)
        return solution

    else:
        # try first variable found with boolean given in formula
        solution[formula[0][0][0]] = formula[0][0][1]
        # create copy of formula and update - if fails, original formula used below
        f1 = simplify_formula(formula, solution)
        # create copy of solution
        s1 = solution.copy()
        s1 = main_recursive(f1, s1)

        # if s1 is not None, solution found, return s1
        if s1:
            return s1
        else:
            # try other bool option
            solution[formula[0][0][0]] = not formula[0][0][1]
            # simplify and update formula
            formula = simplify_formula(formula, solution)
            # return output of main_recursion - either None or valid solution
            return main_recursive(formula, solution)


def simplify_formula(formula, solution):
    """
    Copies the formula and returns a shortened version
    Runs from the end to the beginning
    If a variable is in solution and bool matches, delete the entire line
    If variable does not match, delete tuple
    Any empty lists are caught by main_recursion

    :param formula: Formula in CNF
    :param solution: dictionary of variables and corresponding booleans
    :return: Simplified formula removing any redundencies or given solutions, returns in CNF form
    """

    f = []
    for x in formula:
        f.append(x.copy())

    for i in range(len(f) - 1, -1, -1):
        for j in range(len(f[i])-1, -1, -1):
            if f[i][j][0] in solution:
                if solution[f[i][j][0]] != f[i][j][1]:
                    f[i].remove(f[i][j])
                elif solution[f[i][j][0]] == f[i][j][1]:
                    del f[i]
                    break
    return f


def boolify_scheduling_problem(student_preferences, session_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of session names (strings) that work for that student
    session_capacities: a dictionary mapping each session name to a positive
                        integer for how many students can fit in that session

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up
    We assume no student or session names contain underscores.
    """
    rule1 = desired_rooms((student_preferences, session_capacities))
    rule2 = one_room((student_preferences, session_capacities))
    rule3 = oversubscription((student_preferences, session_capacities))

    return rule1+rule2+rule3


def desired_rooms(x):
    """
    For each student, we need to guarantee that they are given a room that
     they selected as one of their preferences
    """
    rule = []
    for p in x[0]:
        line = []
        for r in x[0][p]:
            var = str(p) + '_' + str(r)
            line.append((var, True))
        rule.append(line)
    return rule


def one_room(x):
    """
    each student must be in at least one session, and
    each student must be in at most one session
    """
    rule = []
    for p in x[0]:
        all_comb = []
        for r in x[1]:
            all_comb.append(str(p) + '_' +str(r))
        subsets = list(all_subsets(all_comb))
        for s in subsets:
            if len(s) == 2:
                s = list(s)
                rule.append([(str(s[0]),False),(str(s[1]),False)])
    return rule


def oversubscription(x):
    """
    if a given room can contain N students, then in every possible group of N+1 there
    must be at least one student who is not in the given room

    """
    rule = []

    num_people = len(x[0])

    for r in x[1]:
        size = x[1][r]
        if size < num_people:
            all_p = []
            for p in x[0]:
                all_p.append(str(p) + '_' + str(r))
            subsets = list(all_subsets(all_p))
            for s in subsets:
                if len(s) == size+1:
                    s = list(s)
                    sub_rule = []
                    for i in range(len(s)):
                        sub_rule.append((str(s[i]),False))

                    rule.append(sub_rule)
    return rule


def all_subsets(l):
    """
    Generator function that produces all combinations of a given list
    Outputs a set of sets
    """
    if len(l) == 0:
        yield set()
    else:
        first = {l[0]}
        for s in all_subsets(l[1:]):
            yield s
            yield first | s



if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
