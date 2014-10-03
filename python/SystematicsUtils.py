"""
 **********************************************************************************
 * Project: HistFitter - A ROOT-based package for statistical data analysis       *
 * Package: HistFitter                                                            *
 * Namespace: SystematicsUtils                                                    *
 * Created: November 2012                                                         *
 *                                                                                *
 * Description:                                                                   *
 *             Functions for processing systematics                               *
 *                                                                                *
 * Authors:                                                                       *
 *      HistFitter group, CERN, Geneva                                            *
 *                                                                                *
 * Redistribution and use in source and binary forms, with or without             *
 * modification, are permitted according to the terms listed in the file          *
 * LICENSE.                                                                       *
 **********************************************************************************
"""

from systematic import Systematic
from configManager import configMgr
from ROOT import TMath
from copy import deepcopy


def matchName(aChan, chanList):
    for chan in chanList:
        if aChan.name == chan.name:
            return True
        pass
    return False


def appendIfMatchName(aChan, chanList):
    if aChan in chanList:
        print "WARNING instance of channel %s already in chanList. " \
              "Not the typical use case." % (aChan.name)
    if matchName(aChan, chanList):
        chanList.append(aChan)
        pass
    return


def addWeight(oldList, newWeight):
    newList = deepcopy(oldList)
    newList.append(newWeight)
    return newList



