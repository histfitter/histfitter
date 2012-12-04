from fitConfig import fitConfig
from logger import Logger

log = Logger('TopLevelXML')

def TopLevelXML(*args, **kwargs):
    log.warn("TopLevelXML has been deprecated in favour of fitConfig")
    return fitConfig(*args, **kwargs)

