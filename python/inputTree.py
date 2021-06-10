from logger import Logger

log = Logger('InputTree')

class InputTree:
    def __init__(self, filename, treename, friends=[]):
        # if the file doesn't exist, that's OK. A file without a treename is not.

        if treename == "":
            raise ValueError("Cannot initialize InputTree without treename")

        log.verbose(f"Initialising input tree with filename='{filename}' and treename='{treename}'")

        self.filename = filename
        self._treename = treename

        self.isFriend = False # 
        self.friends = [] # a list of friends to add

        for friend in friends:
            self.addFriend(friend[0], friend[1])

    def getTreename(self, suffix=""):
        return f"{self._treename}{suffix}"
   
    # NOTE: no @property because of the default argument
    treename = property(getTreename)

    def addFriend(self, filename, treename):
        if self.isFriend:
            raise ValueError("Cannot add friend tree to a tree that is already a friend")

        t = InputTree(filename, treename)
        t.isFriend = True
        self.friends.append(t)

    def __repr__(self):
        return f"InputTree({self.filename}, {self.treename})"

    def __eq__(self, other):
        if isinstance(other, InputTree):
            return ((self.filename == other.filename) and (self.treename == other.treename))
        else:
            return False

    def __hash__(self):
        return hash(self.__repr__())
