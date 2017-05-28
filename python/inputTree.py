class InputTree(object):
    def __init__(self, filename, treename):
        # if the file doesn't exist, that's OK. A file without a treename is not.

        if treename == "":
            raise ValueError("Cannot initialize InputTree without treename")

        self.filename = filename
        self.treename = treename

    def __repr__(self):
        return "InputTree(%s, %s)" % (self.filename, self.treename)

    def __eq__(self, other):
        if isinstance(other, InputTree):
            return ((self.filename == other.filename) and (self.treename == other.treename))
        else:
            return False

    def __hash__(self):
        return hash(self.__repr__())
