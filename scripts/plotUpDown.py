#!/usr/bin/env python

from histfitter.plotting.systematicsplotter import SystematicsPlotter

import argparse
import os
import sys

# Example usage:
# ./plotUpDown.py --output-dir /tmp --filename /Users/gbesjes/work/inputs/data/MyMonob.root --sample Zjets --sample Wjets --region SRM --systematic VjetsTHSyst1 --systematic VjetsTHSyst2 --systematic VjetsTHSyst3

def checkArgs(args):
    if args.filename is None:
        print("Can't work without an input file!")
        sys.exit()

    if not os.path.exists(args.filename):
        print("Input file {0} doesn't exist!".format(args.filename))
        sys.exit()

    if not os.path.isfile(args.filename):
        print("Input file {0} is not a file!".format(args.filename))
        sys.exit()

    if not os.path.exists(args.output_dir):
        print("Output directory {0} doesn't exist!".format(args.output_dir))
        sys.exit()

    if not os.path.isdir(args.output_dir):
        print("Output directory {0} is not a directory!".format(args.output_dir))
        sys.exit()

    if args.sample == []:
        print("No input samples given!")
        sys.exit()

    if args.region == []:
        print("No input regions given!")
        sys.exit()

    if args.systematic == []:
        print("No input systematics given!")
        sys.exit()

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", default=None, type=str)
parser.add_argument("-o", "--output-dir", default=os.getcwd(), type=str, help="output dir of the plots")
parser.add_argument("-s", "--sample", default=[], action="append", help="samples to use (can specify multiple); e.g. Zjets")
parser.add_argument("-S", "--systematic", default=[], action="append", help="systematics to plot (can specify multiple); e.g. JER")
parser.add_argument("-r", "--region", default=[], action="append", help="input regions (can specify multiple); e.g. SRA")
parser.add_argument("-v", "--variable", default="cuts", type=str, help="variable the input is binned in; e.g. meffInc")
args = parser.parse_args()

p = SystematicsPlotter(filename=args.filename,
                       samples=args.sample,
                       regions=args.region,
                       systematics=args.systematic,
                       variable=args.variable)

p.outputDir = args.output_dir
p.writePlots()
