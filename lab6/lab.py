# NO ADDITIONAL IMPORTS!
from text_tokenize import tokenize_sentences


class Trie:
    def __init__(self):
        # value associated with sequence ending at this node
        self.value = None
        # dictionary mapping single-element sequences (length=1 strings, length-1 tuples)
        # to another trie node
        self.children = {}
        # type of keys
        self.type = None

    # set key to value
    # uses find_helper function
    def __setitem__(self, key, value):
        """
        Add a key with the given value to the trie, or reassign the associated
        value if it is already present in the trie.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is of
        the wrong type.
        """
        return self.find_helper(key, set_=value, get=None, del_=None)

    # get value for key
    # uses find_helper function
    def __getitem__(self, key):
        """
        Return the value for the specified prefix.  If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        """
        return self.find_helper(key, set_=None, get=True, del_=None)

    # deletes key from the trie
    # uses find_helper function
    def __delitem__(self, key):
        """
        Delete the given key from the trie if it exists. If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        """
        return self.find_helper(key, set_=None, get=None, del_=True)

    # function tries to get a key
    # if get function returns KeyError, return False
    # if no error, return True
    def __contains__(self, key):
        """
        Is key a key in the trie? return True or False.
        Try to get key from trie
        Except KeyError
        """
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True


    def __iter__(self, ongoing = None):
        """
        Generator of (key, value) pairs for all keys/values in this trie and
        its children.  Must be a generator!

        Recursive function:
            - Base Case: if the value is not None, yield cumulative word, value
            - Recursive case: continue to iterate over each child Trie in self.children
                Uses yield from: yield from __iter__ generator function
        Returns list of tuples of valid keys, values
        """
        # sets value of ongoing to appropriate type
        if ongoing is None:
            if self.type == type(''):
                ongoing = ''
            else:
                ongoing = ()

        # yield word, value if value is not None
        if self.value is not None:
            yield (ongoing, self.value)

        for ch, child in self.children.items():
            # for something in generator yield
            yield from child.__iter__(ongoing+ch)


    def find_helper(self, key, set_ = None, get = None, del_ = None):
        """
        Helper function used is __set__, __get__, __del__
        Function makes appropriate checks for type and key
        set_: value (if set) or None
        get : True or None
        del_: True or None

        Checks if key exists in children, if so, extract node element at key[0]
        If not, either raise key error (get_ or del_) or create new Trie object (set_)
        Base Case: If len(key) == 1:
            set_: set n.value = set_
            get: return n.value
            del_: set n.value = None, return None
        Else: recursive case (will call back to original function)
            set_: n[key[1:]] = value
            get: n[key[1:]]
            del_: del n[key[1:]]
        """
        # check for appropriate types for key
        if not isinstance(key, str) and not isinstance(key, tuple):
            raise TypeError
        # if type = None, set it to type(key
        # else, raise TypeError
        if not self.type and key:
            self.type = type(key)
        elif type(key) != self.type:
            raise TypeError

        # if key[0:1] in children, use existing node
        if key and key[0:1] in self.children:
            n = self.children[key[0:1]]

        # if not existing:
        else:
            if del_ or get:
                raise KeyError
            # create new Trie() object, add to children, set type
            elif set_:
                n = Trie()
                self.children[key[0:1]] = n
                n.type = self.type
        # base case
        if len(key) == 1:
            # set value
            if set_:
                n.value = set_
            # return or delete valid object
            elif n.value is not None:
                if get:
                    return n.value
                elif del_:
                    n.value = None
                    return
            else:
                raise KeyError
        # recursive case
        else:
            if set_:
                n[key[1:]] = set_
            elif get:
                return n[key[1:]]
            elif del_:
                del n[key[1:]]


def make_trie_helper(text, word = None, phrase = None):
    """
    Helper function for make_word_trie and make_phrase_trie
    Use tokenize_sentences to extract sentences
    For sentence in setences:
        - If word: split sentence into words, if word in trie, increment by 1, otherwise set to 1
        - If sentence: split into tuple of words, if sentence if trie, increment by 1, otherwise set to 1
    Return trie
    """
    t = Trie()
    sentences = tokenize_sentences(text)
    for sentence in sentences:
        if word:
            for word in sentence.split(' '):
                if word in t:
                    t[word] += 1
                else:
                    t[word] = 1
        elif phrase:
            sentence = tuple(sentence.split(' '))
            if sentence in t:
                t[sentence] += 1
            else:
                t[sentence] = 1
    return t


def make_word_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text
    """
    return make_trie_helper(text, word=True, phrase=None)


def make_phrase_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    sentences in the text (as tuples of individual words) and whose values are
    the number of times the associated sentence appears in the text.
    """
    return make_trie_helper(text, word=None, phrase=True)



def autocomplete_helper(trie, prefix):
    """
    Autocomplete helper
    If prefix is empty string or tuple, use entire trie
    Otherwise, use search_pref to find all instances of prefix
    Returns dictionary of keys to values (counts)
    """

    if type(prefix) != trie.type:
        raise TypeError

    def search_pref(t, pref):
        try:
            n = t.children[pref[0:1]]
        except KeyError:
            return []

        if len(pref) == 1:
            return n
        else:
            return search_pref(n, pref[1:])
    # prefix empty - use entire tree
    if prefix == '' or prefix == tuple():
        n = trie
    else:
        n = search_pref(trie, prefix)

    if not n:
        return n
    # create dictionary of keys and values (count)
    valid = {}
    for ch, child in n:
        valid[prefix+ch] = child

    # return dictionary
    return valid


def autocomplete(trie, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is of an inappropriate type for the
    trie.
    """
    if max_count == 0:
        return []

    # use helper function to generate dictionary of keys with prefix to their count
    valid = autocomplete_helper(trie, prefix)
    if not valid:
        return []

    # valid = sorted list (sorted by value), returns list of greatest to least occurance
    valid = sorted(valid, key=valid.get, reverse=True)

    # if len(valid) > max_count - splice valid
    if max_count and max_count <= len(valid):
        return valid[0:max_count]

    return valid


def autocorrect(trie, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    # Use autocomplete to get list of autocompletes
    valid = autocomplete(trie, prefix, max_count)
    if not valid:
        return []

    # if max_count is a number and enough elements were generated, return autocomplete
    if max_count and len(valid) == max_count:
        return valid

    seen = set(valid)

    alph = 'abcdefghijklmnopqrstuvwxyz'

    # 4 GENERATOR FUNCTIONS
    # run function on string, only yield if prefix/edit is in trie and has not been seen

    # Replace one character in string
    def single_replace():
        for c in alph:
            for x in prefix:
                edit = prefix
                edit = edit.replace(x, c)
                if edit in trie and edit not in seen:
                    seen.add(edit)
                    yield edit

    # Insert one character at all possible locations
    def single_insert():
        for c in alph:
            for i in range(len(prefix) + 1):
                edit = prefix
                edit = edit[:i] + c + edit[i:]
                if edit in trie and edit not in seen:
                    seen.add(edit)
                    yield edit

    # Delete one character at all possible locations
    def single_delete():
        for c in prefix:
            edit = prefix.replace(c, '')
            if edit in trie and edit not in seen:
                seen.add(edit)
                yield edit

    # Swap any two adjacent characters
    def single_transpose():
        for i in range(len(prefix) - 1):
            edit = list(prefix)
            edit[i], edit[i + 1] = edit[i + 1], edit[i]
            edit = ''.join(edit)
            if edit in trie and edit not in seen:
                seen.add(edit)
                yield edit

    edits = {}
    # for each generator in the list, add generated prefix and count
    for gen in [single_replace(), single_insert(), single_delete(), single_transpose()]:
        for pref in gen:
            edits[pref] = trie[pref]

    # remove any redundant elements in the dictionary
    for elt in set(valid):
        if elt in edits:
            del edits[elt]

    # sort dictionary from high to low of count
    edits = sorted(edits, key=edits.get, reverse=True)

    # if max_count is not None
    # splice edits up to max_count-len(valid)
    if max_count:
        edits = edits[0:max_count-len(valid)]

    # return combined list
    return valid + list(edits)


def word_filter(trie, pattern):
    """
    Return list of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """

    # function removes all consecutive '*' in the pattern
    def clean_pattern(p):
        p = list(p)
        for i in range( len(p) - 1, 0, -1):
            if p[i] == '*' and p[i-1] == '*':
                del p[i]
        return ''.join(p)

    # recursive helper function
    # Base Case:
    #   1. Not pattern - if trie.value, return set {word, value}
    #   2. Not trie.children - if pattern == '*' and value exists, return {word, value}
    #   3. Otherwise, return nothing
    # Recursive case:
    #   1. '?': run recursion on each valid letter in trie.children, move pattern by 1
    #   2. '*': run recursion on each valid letter, do not move pattern AND run on same tree, move pattern by 1
    #   3. letter: check if letter is valid, run recursion on child it points to
    # Append each result to a set, return final set
    def world_filter_helper(trie, pattern, word=''):
        final = set()
        # Base Cases
        if not pattern:
            if trie.value:
                return {(word, trie.value)}
            return set()
        elif not trie.children:
            if pattern == '*' and trie.value:
                return {(word, trie.value)}
            return set()

        # recursive cases
        else:
            if pattern[0] == '?':
                for ch, child in trie.children.items():
                    final |= world_filter_helper(child, pattern[1:], word + ch)
            elif pattern[0] == '*':
                final |= world_filter_helper(trie, pattern[1:], word)
                for ch, child in trie.children.items():
                    final |= world_filter_helper(child, pattern, word + ch)
            else:
                if pattern[0] in trie.children:
                    child = trie.children[pattern[0]]
                    final |= world_filter_helper(child, pattern[1:], word+pattern[0])
        return final

    pattern = clean_pattern(pattern)
    return list(world_filter_helper(trie, pattern))


# you can include test cases of your own in the block below.
if __name__ == '__main__':

    trie = make_word_trie("man mat mattress map me met a man a a a map man met")
    result = word_filter(trie, '*')
    print(result)

    # Q2: print(autocomplete(t, 'gre', 6))
    # Q3

    #with open("meta.txt", encoding="utf-8") as f:
    #    text = f.read()

    #t = make_word_trie(text)
    #print(word_filter(t, 'c*h'))

    #with open("meta.txt", encoding="utf-8") as f:
    #    text = f.read()

    #t = make_word_trie(text)
    #print(word_filter(t, 'c*h'))

    '''
    #with open("alice.txt", encoding="utf-8") as f:
        text = f.read()

    t = make_phrase_trie(text)
    print(len(autocomplete(t, tuple())))
    total = 0
    for elt in t:
        total += elt[1]

    print(total)

    '''


