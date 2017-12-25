#!/usr/bin/env python

# GenerateJSONOutput.py #################
#
# Command-line interface for turning output root files into JSON files for further processing.
#
# By: Larry Lee - Dec 2017

from ROOT import gROOT,gSystem,gDirectory
gSystem.Load("libSusyFitter.so")

import argparse

gROOT.SetBatch()

parser = argparse.ArgumentParser()
parser.add_argument("--inputFile" ,"-i",  type=str, help="input ROOT file" , default = "test.root")
parser.add_argument("--format","-f",          type=str, help="format of object names", default = "hypo_SU_%f_%f_0_10")
parser.add_argument("--interpretation","-p",  type=str, help="interpretation of object name", default = "m0:m12")
parser.add_argument("--cut","-c",  type=str, help="cut string", default = "1")

args = parser.parse_args()

CollectAndWriteHypoTestResults( args.inputFile, args.format, args.interpretation, args.cut )
