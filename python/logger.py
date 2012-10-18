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
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger,cls).__new__(cls,*args,**kwargs)
        else:
            raise Exception("Class Logger allows only one instance")

        return cls._instance

    def __init__(self):
        self.TMsgLogger = TMsgLogger.getInstance()
        self.TMsgLogger.SetSource("HistFitter")
        self.TMsgLogger.SetMinLevel(INFO)

    def setLevel(self, level):
        self.TMsgLogger.SetMinLevel(_checkLevel(level))
        self.always("Log level set to %s " % getLevelName(level) )

    def verbose(self, msg):
        TMsgLogger.writeLogMessage(VERBOSE, msg)
    
    def debug(self, msg):
        TMsgLogger.writeLogMessage(DEBUG, msg)
    
    def info(self, msg):
        TMsgLogger.writeLogMessage(INFO, msg)
    
    def warning(self, msg):
        TMsgLogger.writeLogMessage(WARNING, msg)
    
    def error(self, msg):
        TMsgLogger.writeLogMessage(ERROR, msg)
    
    def fatal(self, msg):
        TMsgLogger.writeLogMessage(FATAL, msg)
    
    def always(self, msg):
        TMsgLogger.writeLogMessage(ALWAYS, msg)

#initialize singleton
log = Logger()
