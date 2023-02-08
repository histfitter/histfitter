"""
 **********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Class  : TopLevelXml                                                           *
 * Created: November 2012                                                         *
 *                                                                                *
 * Description:                                                                   *
 *      Class to define a TopLevelXMl (HistFactory class) - DEPRECATED            *
 *                           in favour of fitConfig                               *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************
"""

from fitConfig import fitConfig
from logger import Logger

log = Logger('TopLevelXML')

def TopLevelXML(*args, **kwargs):
    """
    @deprecated Deprecated in favour of fitConfig
    """
    log.warn("TopLevelXML has been deprecated in favour of fitConfig")
    return fitConfig(*args, **kwargs)

