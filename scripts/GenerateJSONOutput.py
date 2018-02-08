#!/usr/bin/env python

# GenerateJSONOutput.py #################
#
# Command-line interface for turning output root files into JSON files for further processing.
#
# By: Larry Lee - Dec 2017


import argparse, sys, os

parser = argparse.ArgumentParser()
parser.add_argument('--inputFiles','-i', type=str, nargs='+', help="input ROOT files -- if you give me just the nominal, I'll try to find the theory variations and the upper limit automatically", required=True)
parser.add_argument("--format","-f",          type=str, help="format of object names", default = "hypo_SU_%f_%f_0_10")
parser.add_argument("--interpretation","-p",  type=str, help="interpretation of object name", default = "m0:m12")
parser.add_argument("--cut","-c",  type=str, help="cut string", default = "1")
parser.add_argument("--noAddTabs","-n",  help = "don't convert JSON to human readable file", action="store_true", default=False)

args = parser.parse_args()


# Print out the settings
for setting in dir(args):
	if not setting[0]=="_":
		print ">>> ... Setting: {: >20} {: >40}".format(setting, eval("args.%s"%setting) )
print ""


import ROOT
ROOT.gSystem.Load("libSusyFitter.so")

ROOT.gROOT.SetBatch()


def main():


	for filename in args.inputFiles:

		processFile(filename)

		if "Nominal" in filename:
			print ">>> Attempting to find theory variation files"

			try:
				processFile(filename.replace("Nominal","Up"))
			except:
				print ">>> WARNING: Can't find file: %s"%filename.replace("Nominal","Up")

			try:
				processFile(filename.replace("Nominal","Down"))
			except:
				print ">>> WARNING: Can't find file: %s"%filename.replace("Nominal","Down")

			try:
				processFile(filename.replace("_fixSigXSecNominal_hypotest","_upperlimit"))
			except:
				print ">>> WARNING: Can't find file: %s"%filename.replace("_fixSigXSecNominal_hypotest","_upperlimit")

	if not args.noAddTabs:
		cleanUpJSON()

	print ">>>"
	print ">>> Done!"
	print ">>>"

	return

def processFile(file):

	print ""
	if os.path.isfile(file):
		ROOT.CollectAndWriteHypoTestResults( file, args.format, args.interpretation, args.cut )
	else:
		print ">>> ERROR: File does not exist: %s"%file
		sys.exit(1)
	print ""
	return

def cleanUpJSON():
	import json
	import glob
	for file in glob.glob("./*json"):
		print ">>> Making file human readable: %s"%file
		data = json.load(open(file))
		with open(file, 'w') as f:
			f.write( json.dumps(data, indent=4) )
	return



if __name__ == "__main__":
	main()
