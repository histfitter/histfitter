"""
 **********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *  
 * Package: HistFitter                                                            *
 * Class  : logger                                                                *
 *                                                                                *
 * Description:                                                                   *
 *      output logger class producing nicely formatted log messages, import       *
 *            from C++ counter-part.                                              *  
 *                                                                                *
 *      Adapted from TMVA:MsgLogger. Original authors:                            *
 *                                                                                *
 *      Attila Krasznahorkay  <Attila.Krasznahorkay@cern.ch> - CERN, Switzerland  *
 *      Andreas Hoecker       <Andreas.Hocker@cern.ch> - CERN, Switzerland        *
 *      Joerg Stelzer         <stelzer@cern.ch>        - DESY, Germany            *
 *      Eckhard v. Toerne     <evt@uni-bonn.de>        - U of Bonn, Germany       *
 *                                                                                *
 * Copyright (c) 2005-2011:                                                       *
 *      CERN, Switzerland                                                         *
 *      U. of Victoria, Canada                                                    *
 *      MPI-K Heidelberg, Germany                                                 *
 *      U. of Bonn, Germany                                                       *
 *                                                                                *
 *   http://root.cern.ch/root/htmldoc/src/TMVA__MsgLogger.h.html                  *
 *                                                                                *
 * (http://tmva.sourceforge.net/LICENSE)                                          *
 **********************************************************************************/
"""

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
    if isinstance(level, str):
        return level
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
        self._log = TMsgLogger()
        self._log.SetSource(name)
        self._log.SetMinLevel(INFO)
        self._levelLock = False

    def setLevel(self, level, lock=False):
        if(self._log.GetLevelLock() ):
            self.warning("Cannot set log level again, current setting is %s" % self._log.GetMinLevelStr())
            return

        self._log.SetMinLevel(_checkLevel(level), lock)
        self.always("Log level set to %s " % getLevelName(level) )
        if(lock):
            self.always("This log level is the final setting") 

    def verbose(self, msg):
        self._log.writeLogMessage(VERBOSE, msg)
    
    def debug(self, msg):
        self._log.writeLogMessage(DEBUG, msg)
    
    def info(self, msg):
        self._log.writeLogMessage(INFO, msg)
    
    def warning(self, msg):
        self._log.writeLogMessage(WARNING, msg)
    
    def error(self, msg):
        self._log.writeLogMessage(ERROR, msg)
    
    def fatal(self, msg):
        self._log.writeLogMessage(FATAL, msg)
    
    def always(self, msg):
        self._log.writeLogMessage(ALWAYS, msg)

