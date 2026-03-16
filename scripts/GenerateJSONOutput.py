#!/usr/bin/env python

# GenerateJSONOutput.py
#
# Command-line interface for turning output root files into JSON files for further processing.
#
# By: Larry Lee - Dec 2017


import argparse
import sys
import os
import ROOT
import json
import glob
import re

ROOT.gSystem.Load(f"libHistFitter.so")

ROOT.gROOT.SetBatch()

parser = argparse.ArgumentParser()
parser.add_argument(
    "--inputFiles",
    "-i",
    type=str,
    nargs="+",
    help="input ROOT files -- if you give me just the nominal, I'll try to find the theory variations and the upper limit automatically",
    required=True,
)
parser.add_argument(
    "--format",
    "-f",
    type=str,
    help="format of object names",
    default="hypo_SU_%f_%f_0_10",
)
parser.add_argument(
    "--interpretation",
    "-p",
    type=str,
    help="interpretation of object name",
    default="m0:m12",
)
parser.add_argument(
    "--addCoordinates",
    "-a",
    type=str,
    help="add additional coordinates to json using a python dictionary {existing json value name and math : new value name}",
    default='{"m0":"x","m12":"y"}',
)
parser.add_argument("--cut", "-c", type=str, help="cut string", default="1")
parser.add_argument(
    "--noAddTabs",
    "-n",
    help="don't convert JSON to human readable file",
    action="store_true",
    default=False,
)

args = parser.parse_args()

# Print out the settings
for arg in vars(args):
    user_input = getattr(args, arg)
    print(f">>> ... Setting: {arg: >20} {str(user_input): >40}")
print("")

def main():

    for filename in args.inputFiles:

        processFile(filename)
        if args.addCoordinates != "":
            addCoordinates(filename, args.addCoordinates)

        if "Nominal" in filename:
            print(">>> Attempting to find theory variation files")

            try:
                newfilename = filename.replace("Nominal", "Up")
                if newfilename == filename:
                    raise
                processFile(newfilename)
                if args.addCoordinates != "":
                    addCoordinates(newfilename, args.addCoordinates)
            except:
                print(
                    ">>> WARNING: Can't find file: %s"
                    % filename.replace("Nominal", "Up")
                )

            try:
                newfilename = filename.replace("Nominal", "Down")
                if newfilename == filename:
                    raise
                processFile(newfilename)
                if args.addCoordinates != "":
                    addCoordinates(newfilename, args.addCoordinates)
            except:
                print(
                    ">>> WARNING: Can't find file: %s"
                    % filename.replace("Nominal", "Down")
                )

            try:
                newfilename = filename.replace(
                    "_fixSigXSecNominal_hypotest", "_upperlimit"
                )
                if newfilename == filename:
                    raise
                processFile(newfilename)
                if args.addCoordinates != "":
                    addCoordinates(newfilename, args.addCoordinates)
            except:
                print(
                    ">>> WARNING: Can't find file: %s"
                    % filename.replace("_fixSigXSecNominal_hypotest", "_upperlimit")
                )
            try:
                newfilename = filename.replace("_Nominal", "_upperlimit")
                if newfilename == filename:
                    raise
                processFile(newfilename)
                if args.addCoordinates != "":
                    addCoordinates(newfilename, args.addCoordinates)
            except:
                print(
                    ">>> WARNING: Can't find file: %s"
                    % filename.replace("_fixSigXSecNominal_hypotest", "_upperlimit")
                )

    if not args.noAddTabs:
        cleanUpJSON()

    print(">>>")
    print(">>> Done!")
    print(">>>")

    return


def processFile(file):

    print("")
    if os.path.isfile(file):
        ROOT.hf.CollectAndWriteHypoTestResults(
            file, args.format, args.interpretation, args.cut
        )
    else:
        print(">>> ERROR: File does not exist: %s" % file)
        sys.exit(1)
    print("")
    return


def cleanUpJSON():

    for file in glob.glob("./*json"):
        if os.isdir(file):
            continue
        print(">>> Making file human readable: %s" % file)
        data = json.load(open(file))
        with open(file, "w") as f:
            f.write(json.dumps(data, indent=4))
    return


def addCoordinates(fileName, coordString):

    coordDict = json.loads(coordString)

    jsonFileName = fileName.split("/")[-1]  # grab just the filename
    jsonFileName = jsonFileName.replace(".root", "__1_harvest_list.json")

    data = json.load(open(jsonFileName))

    for i, hypo_test in enumerate(data):  # an entry is one hypo test result
        for key in coordDict:  # each item of the result
            # parse input arguments, thanks to Larry for regex suggestions
            total = eval(re.sub(r"\b([a-zA-Z]+[0-9]*)\b", r'hypo_test["\g<1>"]', key))

            # assign new key to value
            hypo_test[coordDict[key]] = total

    with open(jsonFileName, "w") as f:
        f.write(json.dumps(data))


if __name__ == "__main__":
    main()
