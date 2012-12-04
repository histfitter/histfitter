from channel import Channel
from logger import Logger

log = Logger("ChannelXML")

def ChannelXML(*args, **kwargs):
    log.warn("ChannelXML has been deprecated in favour of Channel")
    return Channel(*args, **kwargs)

