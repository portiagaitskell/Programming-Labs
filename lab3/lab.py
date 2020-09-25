'''
Portia Gaitskell
Spring 2020

'''

#!/usr/bin/env python3

from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}


DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}


# Creates a tuple of 3 dictionaries
# Dict 1 (nodes): key = parent, values = set of children
# Dict 2 (dist): key = node, values = (lat, lon)
# Dict 3 (speed): key = tuple of connected nodes, value = speed along this path
def build_auxiliary_structures(nodes_filename, ways_filename):
    """
    Create any auxiliary structures you are interested in, by reading the data
    from the given filenames (using read_osm_data)
    """
    # initialize empty dictionaries
    nodes_dict = {}
    dist_dict = {}
    speed_dict = {}
    speed = 0

    # read each way from file
    for way in read_osm_data(ways_filename):
        # check for 'highway' and allowed highway type
        if 'highway' in way['tags'] and way['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
            # find speed along specific way
            if 'maxspeed_mph' in way['tags']:
                speed = way['tags']['maxspeed_mph']
            else:
                speed = DEFAULT_SPEED_LIMIT_MPH[way['tags']['highway']]

            # cycle through each node for this way
            for i in range(len(way['nodes'])):
                n = way['nodes'][i]

                if n not in nodes_dict:
                    nodes_dict[n] = set()
                if n not in dist_dict:
                    dist_dict[n] = ()
                # add node adjacent to the right as a child
                if i != len(way['nodes'])-1:
                    n_plus = way['nodes'][i+1]
                    nodes_dict[n].add(n_plus)

                    # create tuple of n and n+1 as key
                    # always sort pair in ascending order - consistent throughout search
                    pair = sorted_tuple(n, n_plus)

                    # set value of tuple nodes equal to speed along way
                    # reset value if a higher speed is found
                    if pair not in speed_dict:
                        speed_dict[pair] = speed
                    else:
                        if speed_dict[pair] < speed:
                            speed_dict[pair] = speed

                # check for oneway before adding nodes adjacent to the left
                if i != 0 and not ('oneway' in way['tags'] and way['tags']['oneway'] == 'yes'):
                    n_minus = way['nodes'][i-1]
                    nodes_dict[n].add(n_minus)

                    # repeat process above for speed dict and pair of n and n-1
                    pair = sorted_tuple(n, n_minus)

                    if pair not in speed_dict:
                        speed_dict[pair] = speed
                    else:
                        if speed_dict[pair] < speed:
                            speed_dict[pair] = speed

    # populate dist_dict with lat and lon of all valid nodes
    for node in read_osm_data(nodes_filename):
        if node['id'] in nodes_dict:
            id = node['id']
            lat = node['lat']
            lon = node['lon']
            dist_dict[id] = (lat, lon)

    return nodes_dict, dist_dict, speed_dict

# sorts two values into a tuple
def sorted_tuple(x, y):
    l = [x,y]
    l.sort()
    return tuple(l)


# uses find_path, with short = True
def find_short_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """
    return find_path(aux_structures, loc1, loc2, short=True)


# uses find_path, with short = False
def find_fast_path(aux_structures, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        aux_structures: the result of calling build_auxiliary_structures
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """
    return find_path(aux_structures, loc1, loc2, short=False)


# MAIN PATH FINDING ALGORITHM
# finds the min path (short or fast) between two locations
# Builds agenda, find min cost node, append children with updated cost, remove parent, check if parent is n2
# Short vs fast: heuristic for short, min distance for short vs. min time for fast
def find_path(aux_structures, loc1, loc2, short=True):
    nodes = aux_structures[0]
    dist = aux_structures[1]
    speed = aux_structures[2]

    # find nearest nodes
    n1, n2 = find_nearest_loc(aux_structures, loc1, loc2)

    if n1 == n2:
        return dist[n1]

    # initialize agenda, checked, parents
    # agenda is dictionary: key = node (current terminal node), value = cost
    # checked: set of all nodes REMOVED from agenda
    # parents: keeps track of min cost path to each node
    agenda = {n1: 0}
    checked = set()
    parents = {n1: None}

    while agenda:
        # set current node = min cost node from agenda
        # if short, use heuristic, otherwise not
        if short:
            parent = min_cost_heuristic(agenda, dist, n2)
        else:
            parent = min_cost(agenda)

        # use node dict to find all children
        for child in nodes[parent]:
            # find associated cost to each child through current node
            new_cost = agenda[parent] + cost_between(dist, speed, parent, child, short)

            # if child already in agenda, check for new shorter path through parent
            # else if not already checked, add to agenda with new_cost
            if child in agenda:
                if new_cost < agenda[child]:
                    agenda[child] = new_cost
                    parents[child] = parent
            elif child not in checked:
                agenda[child] = new_cost
                parents[child] = parent
        # add parent to checked and remove from agenda
        checked.add(parent)
        del agenda[parent]

        # if goal node has been removed (added to checked) shortest cost path has been found
        # use parents to return traced path
        if n2 in checked:
            return trace_path(parents, n2, dist)


# HELPER FUNCTIONS
# returns path from end node through parents
# returns path list of (lat, lon) tuples for each node
def trace_path(parents, node, dist):
    path = []
    while node is not None:
        path.append(dist[node])
        node = parents[node]

    path.reverse()

    return path


# returns key of min value in dictionary
# min function in python using key parameter
# min function acts on agenda.values() and responds the corresponding key
def min_cost(agenda):
    return min(agenda.keys(), key=(lambda k: agenda[k]))


# returns node of min cost with additional heuristic
# heuristic is distance from current node to goal
def min_cost_heuristic(agenda, dist, goal):
    min_cost = None
    min_node = None

    for node in agenda:
        cost = agenda[node] + great_circle_distance(dist[goal], dist[node])
        if min_cost is None:
            min_cost = cost
            min_node = node
        else:
            if cost < min_cost:
                min_cost = cost
                min_node = node
    return min_node


# finds the nearest location to locations in the dataset
# returns two tuples (lat and lon of a node), each corresponding to the given location
def find_nearest_loc(aux, loc1, loc2):
    dist = aux[1]

    # find n1 and n2 (nearest nodes to the given loc1 and loc2)
    d1 = None
    n1 = None

    d2 = None
    n2 = None

    for n in dist:
        if d1 is None:
            d1 = great_circle_distance(dist[n], loc1)
            n1 = n
            d2 = great_circle_distance(dist[n], loc2)
            n2 = n
        else:
            if great_circle_distance((dist[n]), loc1) < d1:
                d1 = great_circle_distance(dist[n], loc1)
                n1 = n
            if great_circle_distance((dist[n]), loc2) < d2:
                d2 = great_circle_distance(dist[n], loc2)
                n2 = n
    return n1, n2


# for short path - return great circle distance between nodes
# for fast - return great circle distance/speed from speed dictionary
def cost_between(dist, speed, n1, n2, short=True):
    d = great_circle_distance(dist[n1], dist[n2])
    if short:
        return d
    else:
        pair = sorted_tuple(n1, n2)
        s = speed[pair]
        return d / s


if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.

    '''
    # print 77 Mass Ave id
    for node in read_osm_data('resources/cambridge.nodes'):
        if node['tags'] != {} and 'name' in node['tags']:
            if node['tags']['name'] == '77 Massachusetts Ave':
                print('FOUND')
                print(node['id'])
                
    # count number of one ways in .ways
    count = 0
    for way in read_osm_data('resources/cambridge.ways'):
        print(type(way))
        if 'oneway' in way['tags'] and way['tags']['oneway'] == 'yes':
            print(way['nodes'])
            count+=1
    print(count)
    
    loc1 = (42.363745, -71.100999)
    loc2 = (42.361283, -71.239677)
    print(great_circle_distance(loc1, loc2))
    # calculate distance between two ID nodes
    node1 = None
    node2 = None
    for node in read_osm_data('resources/midwest.nodes'):
        if node['id'] == 233941454:
            node1 = node
        if node['id'] == 233947199:
            node2 = node
    print(great_circle_distance((node1['lat'],node1['lon']),(node2['lat'],node2['lon'])))
    '''
    '''
    way1 = None
    for way in read_osm_data('resources/midwest.ways'):
        if way['id'] == 21705939:
            #print(way)
            path = way['nodes']
            break
    nodes = [0]*len(path)
    
    for node in read_osm_data('resources/midwest.nodes'):
        if node['id'] in path:
            nodes[path.index(node['id'])] = node
    dist=0
    for i in range(len(nodes)-1):
        node1 = nodes[i]
        node2 = nodes[i+1]
        dist+=great_circle_distance((node1['lat'],node1['lon']),(node2['lat'],node2['lon']))
    print(dist)
    '''
    '''

    loc = (41.4452463, -89.3161394)
    min_dist = None
    min_node = None

    valid_nodes = set()
    for way in read_osm_data('resources/midwest.ways'):
        if 'highway' in way['tags'] and way['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
            valid_nodes.update(way['nodes'])

    total = 0
    allowed = 0
    for node in read_osm_data('resources/midwest.nodes'):
        total+= 1
        if node['id'] in valid_nodes:
            allowed+=1
    print(total)
    print(allowed)
    '''

    '''
    for node in read_osm_data('resources/midwest.nodes'):
        if min_dist is None and node['id'] in valid_nodes:
            min_dist = great_circle_distance((node['lat'],node['lon']),loc)
            min_node = node
            print('FIRST')
        elif node['id'] in valid_nodes and great_circle_distance((node['lat'],node['lon']),loc) < min_dist:
            min_dist = great_circle_distance((node['lat'],node['lon']),loc)
            min_node = node
    print(min_node['id'])
    '''


    #a = {'id': 0, 'children': (1,2,3,4), 'loc': (20,15)}
    #b = {'id': 1, 'children': (3,4),'loc': (10,2)}

    #nodes = (a,b)
    #for x in nodes:
        #if x['id'] == 0:
            #print(x['children'])
    # construct a dictionary of allowed nodes and each of each children, take note of one ways
    # second dictionary of allowed


    #aux = build_auxiliary_structures('resources/cambridge.nodes','resources/cambridge.ways')

    #print(find_nearest_loc(aux, (42.3592, -71.0932), (42.3575,  -71.0956)))

    # Find distance between (42.3858, -71.0783),(42.5465, -71.1787)
    # Checked size w/o heuristics = 372625
    # Checked size = 45928
    # print(find_short_path(aux, (42.3858, -71.0783),(42.5465, -71.1787)))

    for way in read_osm_data('resources/mit.ways'):
        print(way)

    for node in read_osm_data('resources/mit.nodes'):
        print(node)
    print(build_auxiliary_structures('resources/mit.nodes','resources/mit.ways'))


    pass
