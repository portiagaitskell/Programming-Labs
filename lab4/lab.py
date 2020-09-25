'''
Portia Gaitskell
Spring 2020

'''

#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

# NO IMPORTS ALLOWED!

def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION


def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, False, False, False]
        [False, False, False, False]
    state: ongoing

    # REFACTORED CODE
    board = create_2d_array(num_rows, num_cols, bombs)
    mask = create_2d_array(num_rows, num_cols)
    for r in range(num_rows):
        for c in range(num_cols):
            if board[r][c] == 0:
                neighbor_bombs = 0
                adj = get_adjacent(num_rows, num_cols, (r, c))
                for x in adj:
                    if x in bombs:
                        neighbor_bombs += 1
                board[r][c] = neighbor_bombs
    return {
        'dimensions': (num_rows, num_cols),
        'board': board,
        'mask': mask,
        'state': 'ongoing'}
    """

    return new_game_nd((num_rows,num_cols), bombs)



def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['mask'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['mask'][bomb_location] ==
    True), 'victory' when all safe squares (squares that do not contain a bomb)
    and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, True, True, True]
        [False, False, True, True]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    mask:
        [True, True, False, False]
        [False, False, False, False]
    state: defeat


    ## REFACTORED CODE
    if game['state'] == 'defeat' or game['state'] == 'victory':
        return 0

    if game['board'][row][col] == '.':
        game['mask'][row][col] = True
        game['state'] = 'defeat'
        return 1

    # already revealed square return 0, otherwise initialize revealed
    if not game['mask'][row][col]:
        game['mask'][row][col] = True
        revealed = 1
    else:
        return 0

    if game['board'][row][col] == 0:
        num_rows, num_cols = game['dimensions']
        adj = get_adjacent(num_rows, num_cols, (row, col))
        if adj:
            for loc in adj:
                if game['board'][loc[0]][loc[1]] != '.' and not game['mask'][loc[0]][loc[1]]:
                    revealed += dig_2d(game, loc[0], loc[1])

    for r in range(game['dimensions'][0]):
        # for each r,
        for c in range(game['dimensions'][1]):
        #for each c,
            if game['board'][r][c] != '.' and not game['mask'][r][c]:
                game['state'] = 'ongoing'
                return revealed
    game['state'] = 'victory'
    return revealed
    """
    return dig_nd(game, (row,col))


def render_2d(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring bombs).
    game['mask'] indicates which squares should be visible.  If xray is True (the
    default is False), game['mask'] is ignored and all cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A 2D array (list of lists)

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]


    ## ORGINAL CODE
    render = []
    # copy game board
    for x in game['board']:
        row = []
        for y in x:
            row.append(y)
        render.append(row)

    mask = game['mask']
    r, c = game['dimensions']

    # if 0, set to ' '
    # if mask = False, set to '_'
    # otherwise, show value
    for i in range(r):
        for j in range(c):
            if render[i][j] == 0:
                render[i][j] = ' '
            else:
                render[i][j] = str(render[i][j])
    if not xray:
        for i in range(r):
            for j in range(c):
                if not mask[i][j]:
                    render[i][j] = '_'
    return render
    """

    return render_nd(game, xray)


def render_ascii(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function 'render_2d(game)'.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A string-based representation of game

    >>> print(render_ascii({'dimensions': (2, 4),
    ...                     'state': 'ongoing',
    ...                     'board': [['.', 3, 1, 0],
    ...                               ['.', '.', 1, 0]],
    ...                     'mask':  [[True, True, True, False],
    ...                               [False, False, True, False]]}))
    .31_
    __1_
    """
    render = render_2d(game, xray)
    asc = []
    for r in render:
        row_str = ''.join(r)
        asc.append(row_str)
    end = "\n".join(asc)
    return end

    return asc
    '''
    render = render_2d(game, xray)
    asc = ''
    for r in range(len(render)):
        for c in render[r]:
            asc += c
        if r != len(render) - 1:
            asc += "\n"
    return asc
    '''


# 2D HELPER FUNCTIONS
# NO LONGER NEEDED

def create_2d_array(rows, cols, bombs=None):
    """
    NO LONGER NEEDED WITH ND
    Creates 2d array of given dims: (row, col)
    Used to create board and mask array

    Parameters:
        rows: num rows
        cols: num cols
        bombs: tuple of locations
    Returns: Populated array of given dimensions

    """
    if not bombs:
        return [[False for _ in range(cols)] for _ in range(rows)]
    else:
        board = [[0 for _ in range(cols)] for _ in range(rows)]
        for b in bombs:
            if 0 <= b[0] < rows and 0 <= b[1] < cols:
                board[b[0]][b[1]] = '.'
        return board


def get_adjacent(rows, cols, current):
    """
    Finds adjacent squares to current coordinate in 2D array
    No longer needed with get_nd_adjacent
    Parameters:
        rows: num rows of board
        cols: num cols of board
        current: current coordinate
    Returns: returns list of tuples of adjacent pixels

    """
    r = current[0]
    c = current[1]
    adjacent = []

    for i in range(-1, 2):
        if 0 <= r + i < rows:
            if 0 <= c - 1 < cols:
                adjacent.append((r + i, c - 1))
            if 0 <= c < cols:
                adjacent.append((r + i, c))
            if 0 <= c + 1 < cols:
                adjacent.append((r + i, c + 1))
    adjacent.remove(current)
    return adjacent


# N-D IMPLEMENTATION

def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: ongoing
    """
    board = nd_array(dimensions, 0)
    mask = nd_array(dimensions, False)

    for b in bombs:
        board = mod_loc(board, b, '.')

        adj = get_nd_adjacent(dimensions, b)
        for x in adj:
            val = find_loc(board, x)
            if val != '.':
                board = mod_loc(board, x, val+1)

    return {
        'dimensions': dimensions,
        'board': board,
        'mask': mask,
        'state': 'ongoing'}


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the mask to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: defeat
    """
    if game['state'] == 'defeat' or game['state'] == 'victory':
        return 0

    if find_loc(game['board'],coordinates) == '.':
        game['mask'] = mod_loc(game['mask'], coordinates, True)
        game['state'] = 'defeat'
        return 1

    game, revealed = rec_nd(game, coordinates, 0)

    for p in find_all_points(game['dimensions']):
        if find_loc(game['board'], p) != '.' and not find_loc(game['mask'], p):
            game['state'] = 'ongoing'
            return revealed
    game['state'] = 'victory'
    return revealed


def rec_nd(game, current, r):
    '''
    Recursive helper function called within dig_nd
    Performs all actions after one click

    Returns modified game (updates mask) and number of revealed squares
    Call rec_nd until no squares == 0 and not mask

    :param game: Current game
    :param current: clicked point
    :return: Updated game, number of revealed squares
    '''

    if not find_loc(game['mask'], current):
        game['mask'] = mod_loc(game['mask'], current, True)
        revealed = 1
    else:
        return game, 0

    if find_loc(game['board'], current) == 0:
        dims = game['dimensions']
        adj = get_nd_adjacent(dims, current)
        if adj:
            for loc in adj:
                if find_loc(game['board'], loc) != '.' and not find_loc(game['mask'], loc):
                    revealed += rec_nd(game, loc, revealed)[1]

    return game, revealed



def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares
    neighboring bombs).  The mask indicates which squares should be
    visible.  If xray is True (the default is False), the mask is ignored
    and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    the mask

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [True, True], [True, True]],
    ...               [[False, False], [False, False], [True, True], [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    render = nd_array(game['dimensions'], 0)
    for p in find_all_points(game['dimensions']):
        val = find_loc(game['board'], p)
        if val == 0:
            mod_loc(render, p, ' ')
        else:
            mod_loc(render, p, str(val))

        if not xray:
            if not find_loc(game['mask'], p):
                mod_loc(render, p, '_')
    return render


# ND HELPER FUNCTIONS

def nd_array(dims, val):
    """
    Creates an array (nested list) of the given dimensions. Populates list with the given val

    Recursive function, each time removes first element of dimensions
    and searches until last dimension is reached

    :param dims: dimensions of array
    :param val: value to pass into array
    :return: array of given dimensions with value
    """
    if len(dims) == 1:
        return [val for _ in range(dims[0])]
    arr = [nd_array(dims[1:], val) for _ in range(dims[0])]
    return arr


def find_loc(arr, loc):
    """
    Given ND array and location, return value at that location
    Recursive function, searches through each dimension of location until last dim is reached
    Return value

    :param arr: Array to be checked
    :param loc: tuple of coordinates
    :return: value at given coordinates
    """

    if len(loc) == 1:
        return arr[loc[0]]
    return find_loc(arr[loc[0]], loc[1:])


def mod_loc(arr, loc, val):
    """
    Modifies ND arr at location to value
    Recursively passes through each dimension of array until location is reached
    Change value, return array

    :param arr: ND array
    :param loc: tuple of coordinates
    :param val: new value to be modified
    :return: updated array with changed value
    """
    if len(loc) == 1:
        arr[loc[0]] = val
        return arr
    mod_loc(arr[loc[0]], loc[1:], val)
    return arr


def find_all_points(dims):
    """
    Returns a list of tuples of coordinates of all possible points in the given dimensions
    Recursively passes through each dimension to find all permutations of coordinates

    :param dims: dimensions of ND array
    :return: list of tuples of coordinates
    """
    final = []
    if len(dims) == 1:
        coords = []
        for i in range(dims[0]):
            coords.append((i,))
        return coords
    for i in range(dims[0]):
        for j in find_all_points(dims[1:]):
            final.append((i,) + j)
    return final


def get_nd_adjacent(dims, current):
    """
    Returns all adjacent points to the current point
    Recursively moves through each dimension, checks for valid coordinates (not out of range),
    appends all combinations of valid points

    :param dims: dimensions of ND array
    :param current: current coordinate
    :return: list of tuples of coordinates
    """
    final = []
    coords = []

    for i in range(-1,2):
        if 0 <= current[0] + i < dims[0]:
            val = current[0] + i
            coords.append((val,))
    if len(dims) == 1:
        return coords

    for x in coords:
        for y in get_nd_adjacent(dims[1:],current[1:]):
            final.append(x + y)

    return final

if __name__ == "__main__":

    pass

    '''
    # Test with doctests. Helpful to debug individual lab.py functions.
    import doctest
    doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags) #runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d or any other function you might want.  To do so, comment
    # out the above line, and uncomment the below line of code. This may be
    # useful as you write/debug individual doctests or functions.  Also, the
    # verbose flag can be set to True to see all test results, including those
    # that pass.
    #
    #doctest.run_docstring_examples(render_2d, globals(), optionflags=_doctest_flags, verbose=False)
    '''

