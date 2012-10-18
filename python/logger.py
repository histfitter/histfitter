from ROOT import TMsgLogger

# maps 1-on-1 to names used in TMsgLogger.h
VERBOSE = 1
DEBUG   = 2
INFO    = 3
WARNING = 4
ERROR   = 5
FATAL   = 6
ALWAYS  = 7

_levelNames = {
    VERBOSE: 'VERBOSE', 
    DEBUG: 'DEBUG', 
    INFO: 'INFO', 
    WARNING: 'WARNING', 
    ERROR: 'ERROR', 
    FATAL: 'FATAL', 
    ALWAYS: 'ALWAYS',
    'VERBOSE': VERBOSE,
    'DEBUG': DEBUG,
    'INFO': INFO,
    'WARNING': WARNING,
    'ERROR': ERROR,
    'FATAL': FATAL,
    'ALWAYS': ALWAYS
}

def getLevelName(level):
    return _levelNames.get(level, ("%s" % level)) 

def _checkLevel(level):
    if isinstance(level, int):
        rv = level
    elif str(level) == level:
        if level not in _levelNames:
            raise ValueError("Unknown level: %r" % level)
        rv = _levelNames[level]
    else:
        raise TypeError("Level not an integer or a valid string: %r" % level)
    return rv

class Logger(object):

    def __init__(self,name):
        self.mlogger = TMsgLogger()
        self.mlogger.SetSource(name)
        self.mlogger.SetMinLevel(INFO)

    def setLevel(self, level):
        self.mlogger.SetMinLevel(_checkLevel(level))
        self.always("Log level set to %s " % getLevelName(level) )

    def verbose(self, msg):
        self.mlogger.writeLogMessage(VERBOSE, msg)
    
    def debug(self, msg):
        self.mlogger.writeLogMessage(DEBUG, msg)
    
    def info(self, msg):
        self.mlogger.writeLogMessage(INFO, msg)
    
    def warning(self, msg):
        self.mlogger.writeLogMessage(WARNING, msg)
    
    def error(self, msg):
        self.mlogger.writeLogMessage(ERROR, msg)
    
    def fatal(self, msg):
        self.mlogger.writeLogMessage(FATAL, msg)
    
    def always(self, msg):
        self.mlogger.writeLogMessage(ALWAYS, msg)

