'''
Portia Gaitskell
Spring 2020

'''

#!/usr/bin/env python3

import pickle
# NO ADDITIONAL IMPORTS ALLOWED!

# Note that part of your checkoff grade for lab 2 will be based on the
# style/clarity of your code.  As you are working through the lab, be on the
# lookout for things that would be made clearer by comments/docstrings, and for
# opportunities to rearrange aspects of your code to avoid repetition (for
# example, by introducing helper functions).


# function that takes a data set and returns boolean of whether actors have acted together
# checks every data point
def acted_together(data, actor_id_1, actor_id_2):
    for x in data:
        if (x[0] == actor_id_1 and x[1] == actor_id_2) or (x[1] == actor_id_1 and x[0] == actor_id_2):
            return True
    return False


# constructs tree from given data
# tree returns dictionary for each bacon number
def actors_with_bacon_number(data, n):
    tree = construct_tree(data, 4724)
    final = set()

    for id in tree.keys():
        if tree[id] == n:
            final.add(id)

    return final


# constructs tree from given data with start_id as the center node
# can also be used to construct a tree from any other start_id and find path to any end_id
# change path parameter to True to print out path
# add in end_set parameter if construct_tree is being used to find the shortest path to any actor in a list
def construct_tree(data, start_id=4724, end_id=0, path = False, end_set=set()):
    connected_actors = dictionary_links(data)

    # if searching for path and end_set does not exist - return None
    if path and (end_id not in connected_actors) and not end_set:
        return None

    bacon_number_dict = {}

    working_set = {start_id}
    checked = set()
    n = 0

    # if returning parent path - define appropriate vars
    if path:
        parents = {start_id: None}
        found = False

    # move through list until working set is empty
    while working_set:

        new_set = set()

        for actor in working_set:
            bacon_number_dict[actor] = n

            if path:
                for a in connected_actors[actor]:
                    if a not in parents:
                        parents[a] = actor
                        # used for actors_connecting_films, the first end actor path found is returned
                        if len(end_set) > 0 and a in end_set:
                            return trace_path(parents, a)
                        # if specific end_id is found, return path to it
                        if a == end_id:
                            found = True
                            return trace_path(parents, end_id)

            new_set |= connected_actors[actor]

        checked |= working_set

        new_set -= checked

        working_set = new_set.copy()

        n += 1
    # if no path is found
    if path and not found:
        return None

    return bacon_number_dict


# retrace path of given actor
def trace_path(parents, actor):
    path = []
    while actor is not None:
        path.append(actor)
        actor = parents[actor]

    path.reverse()

    return path


# HELPER FUNCTION: returns dictionary of all connected actors
def dictionary_links(data):
    connected_actors = {}

    for x in data:
        if x[0] not in connected_actors:
            connected_actors[x[0]] = set()
        if x[1] not in connected_actors:
            connected_actors[x[1]] = set()

        connected_actors[x[0]].add(x[1])
        connected_actors[x[1]].add(x[0])
    return connected_actors


# Use construct tree with start id at Bacon and moving to desired end actor
# Path is true - returning path list
def bacon_path(data, actor_id):
    start_id = 4724
    return construct_tree(data, start_id, actor_id, path=True)


# use construct tree and pather = True
# only pass end set if checking for shortest path to a set of actors
def actor_to_actor_path(data, actor_id_1, actor_id_2, end_set=set()):
    return construct_tree(data, actor_id_1, actor_id_2, path=True, end_set=end_set)


# find shortest movie path between two actors
# use actor_to_actor_path to find shortest path
def movie_path(data, actor_id_1, actor_id_2):
    path = actor_to_actor_path(data, actor_id_1, actor_id_2)

    mov = []
    # for each edge in the path, find a movie that connects them
    # break early to prevent adding multiple movies per pair
    for i in range(len(path) - 1):
        for x in data:
            if x[0] == path[i] and x[1] == path[i + 1] or x[1] == path[i] and x[0] == path[i + 1]:
                mov.append(x[2])
                break
    return mov


# generalizes actor_to_actor for a given list of end goal actors
# run actor_to_actor for each actor in list
def actor_path(data, actor_id_1, goal_test_function):
    # get list of all actors in dictionary
    # if test_function returns true, add actor to list
    # use actor_to_actor_path to test valid path

    if goal_test_function(0) or goal_test_function(actor_id_1):
        return [actor_id_1]

    full_dict = dictionary_links(data)
    search_list = []
    for actor in full_dict:
        if goal_test_function(actor):
            search_list.append(actor)

    paths = []

    for actor in search_list:
        path = actor_to_actor_path(data, actor_id_1, actor)
        if path != None:
            paths.append(path)

    if len(paths) > 0:
        shortest = paths[0]
        for p in paths:
            if len(p) < len(shortest):
                shortest = p
        return shortest


# HELPER FUNCTION to create dictionary of movies and actors in them
def movie_dictionary(data):
    movs = {}
    for x in data:
        if x[2] not in movs:
            movs[x[2]] = set()
        movs[x[2]].update({x[0], x[1]})
    return movs


# returns the shortest path of actors connecting two films
# creates dictionary
# finds two sets: 1) actors in film1 2) actors in film2
# use actor_to_actor_path to find every possible combination of paths
# for each given set, actor path function will return the path to the first node found
# return shortest overall path
def actors_connecting_films(data, film1, film2):
    movs = movie_dictionary(data)

    actors1 = movs[film1]
    actors2 = movs[film2]

    all_paths = []
    for actor in actors1:
        all_paths.append(actor_to_actor_path(data, actor, 0, end_set = actors2))

    if len(all_paths) > 0:
        shortest = all_paths[0]
        for p in all_paths:
            if p is not None and len(p) < len(shortest):
                shortest = p
        return shortest


# HELPER FUNCTIONS FOR TESTING
def id_to_name(names_, id):
    for name, num in names_.items():
        if num == id:
            return name


def name_to_id(names_, name):
    for n, id in names_.items():
        if n == name:
            return id


if __name__ == '__main__':
    with open('resources/small.pickle', 'rb') as f:
        smalldb = pickle.load(f)

    with open('resources/names.pickle', 'rb') as f:
        names = pickle.load(f)

    #print(names)

    ''' 
     2.2 Questions
     
    print(names)
    print(names['Jeff East'])
    for name, id in names.items():
        if id == 65422:
            print(name)
    '''

    with open('resources/movies.pickle', 'rb') as f:
        movies = pickle.load(f)
    #print(movies)

    with open('resources/tiny.pickle', 'rb') as f:
        tiny = pickle.load(f)
    print(tiny)

    '''

    actor1 = names['Tony Shalhoub']
    actor2 = names['Francois Perier']
    actor3 = names['Jennifer Pisana']
    actor4 = names['Melina Kanakaredes']
    print(acted_together(smalldb,actor1,actor2))
    print(acted_together(smalldb,actor3,actor4))
    '''

    with open('resources/large.pickle', 'rb') as f:
        large = pickle.load(f)

    #print(tiny)
    #print(len(large))
    #print(actors_with_bacon_number(tiny,6))


    #set_ = actors_with_bacon_number(large,6)

    #six = set()

    #for id in set_:
        #six.add(id_to_name(names, id))

    #rint(six)

    #print(bacon_path(large, 1204))

    # CODE FOR MOVIE PATH

    name1 = names['Christopher Guest']
    name2 = names['Vjeran Tin Turk']


    '''
    path = actor_to_actor_path(large, name1, name2)
    list = []
    for p in path:
        list.append(id_to_name(names, p))
    #print(path)
    #print(list)

    for key,value in names.items():
        if value == 975260:
            print(key)

    print(construct_tree(large, 975260))
    '''

    print(tiny)
    print(actor_to_actor_path(tiny, 4724, 1640))




    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    pass
