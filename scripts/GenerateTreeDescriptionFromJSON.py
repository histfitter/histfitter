#!/usr/bin/env python

# Generates old-fashioned summary_harvest_tree_description files from JSON output

import argparse
import json
import os
import string
import sys

from collections import OrderedDict

scriptName = os.path.basename(__file__)

def checkArgs(args):
    if not os.path.exists(args.filename):
        print "%s: input file %s does not exist!" % (scriptName, args.filename)
        sys.exit()

    if not args.filename.endswith(".json") and (args.output_filename is None or args.output_filename == ""):
        print "%s: input file %s does NOT end in .json. Cannot autogenerate output filename; specify a path yourself" % (scriptName, args.filename)
        sys.exit()

    if args.output_filename is None or args.output_filename == "":
        args.output_filename = args.filename.replace(".json", "")
    
    print "%s: will write output to %s" % (scriptName, args.output_filename)

def generateHeaderFiles(keys):
    print "%s: generating header files" % (scriptName)

def sanitizeData(data):
    # 'NaN' is a string in JSON. Fix it. 
    for d in data[0]:
        for key in d:
            if isinstance(d[key], float): continue
            if key == "fID": continue # fID may contain strings
            d[key] = float(d[key])

    return data

def readInputFile(filename):
    data = []
    with open(filename) as f:
        for line in f:
            data.append(json.loads(line))

    print "%s: read input data" % (scriptName)
    return sanitizeData(data)

def getKeys(data):
    first = True
    keys = []
    for d in data[0]:
        if first: 
            keys = list(d.keys())
            first = False
        else:
            # sanity check. if this goes wrong you messed up the file yourself.
            assert list(d.keys()) == keys

    print "%s: read keys: %s" % (scriptName, ":".join(keys) )
    return keys

def pythonHeaderTemplate():
    s = ( "#!/usr/bin/env python\n\n"
          "import os, sys, ROOT\n"
          "#from ROOT import TTree, TString\n\n"
          "ROOT.gROOT.SetBatch(True)\n"
          "ROOT.PyConfig.IgnoreCommandLineOptions = True\n\n"
          "def treedescription():\n"
          "  filename = \"$outfile\"\n"
          "  description = \"$description\"\n"
          "  return filename, description\n\n"
          "def harvesttree(textfile='$outfile'):\n"
          "  filename, description=treedescription()\n"
          "  tree = ROOT.TTree('tree','data from ascii file')\n"
          "  if len(textfile)>0:\n"
          "    nlines = tree.ReadFile(textfile,description)\n"
          "  elif len(filename)>0:\n"
          "    nlines = tree.ReadFile(filename,description)\n"
          "  else:\n"
          "    print 'WARNING: file name is empty. No tree is read.'\n\n"
          "  tree.SetMarkerStyle(8)\n"
          "  tree.SetMarkerSize(0.5)\n\n"
          "  return tree\n\n" ) 
    return s

def cppHeaderTemplate():
    includes  = ("\n#include \"TTree.h\"\n"
                 "#include \"TFile.h\"\n"
                 "#include <iostream>\n"
                 "using namespace std;\n")

    harvesttree = ("\nTTree* harvesttree(const char* textfile=0) {\n"
                   "  const char* filename    = \"$outfile\";\n"
                   "  const char* description = \"$description\";\n"
                   "  TTree* tree = new TTree(\"tree\",\"data from ascii file\");\n"
                   "  Long64_t nlines(0);\n"
                   "  if (textfile!=0) {\n"
                   "    nlines = tree->ReadFile(textfile,description);\n"
                   "  } else if (filename!=0) {\n"
                   "    nlines = tree->ReadFile(filename,description);\n"
                   "  } else {\n"
                   "    cout << \"WARNING: file name is empty. No tree is read.\" << endl;\n"
                   "  }\n"
                   "  tree->SetMarkerStyle(8);\n"
                   "  tree->SetMarkerSize(0.5);\n"
                   "  return tree;\n"
                   "}\n")

    writetree  = ("\nvoid writetree() {\n"
                  "  TTree* tree = (TTree *)gDirectory->Get(\"tree\");\n"
                  "  if (tree==0) {\n"
                  "    tree = harvesttree();\n"
                  "    if (tree==0) return;\n"
                  "  }\n"
                  "  TFile* file = TFile::Open(\"$outfile.root\",\"RECREATE\");\n"
                  "  file->cd();\n"
                  "  tree->Write();\n"
                  "  file->Close();\n"
                  "}\n")

    main  = ("\nvoid summary_harvest_tree_description() {\n"
             "  TTree* tree = harvesttree();\n"
             "  gDirectory->Add(tree);\n"
             "}\n")

    return includes + harvesttree + writetree + main 

def treeType(key):
    if key == "fID": return "C"
    return "F"

def writeHeaderFiles(keys, inputFilename, outputFilename):
    types = {k: "{0}/F".format(k) for k in keys}
    types = OrderedDict([(k, "{0}/{1}".format(k, treeType(k))) for k in keys])

    description = ":".join(types.values())

    t = string.Template(pythonHeaderTemplate())
    pythonHeader = t.substitute({"outfile": os.path.abspath(outputFilename), "description": description })
    
    t = string.Template(cppHeaderTemplate())
    cppHeader = t.substitute({"outfile": os.path.abspath(outputFilename), "description": description })

    # will have to go in same dir as input filename
    outputDir = os.path.dirname(os.path.abspath(inputFilename))
    
    # write the python header
    headerFilename = "%s/summary_harvest_tree_description.py" % outputDir
    f = open(headerFilename, "w+")
    f.write(pythonHeader)
    f.close()

    print "%s: wrote summary_harvest_tree_description.py" % scriptName

    # write the C++ header
    headerFilename = "%s/summary_harvest_tree_description.h" % outputDir
    f = open(headerFilename, "w+")
    f.write(cppHeader)
    f.close()
    
    print "%s: wrote summary_harvest_tree_description.h" % scriptName

    pass

def typeForVar(key):
    if key == "fID": 
        return "%s"
    
    return "%e"

def writeOutputFile(data, filename):
    f = open(filename, "w+")
    for d in data[0]:
        f.write(" ".join([typeForVar(k) % v for (k, v) in d.items()]))
        f.write("\n")
    f.close()
    
    print "%s: wrote %s" % (scriptName, filename)
    pass

def writeListFile(inputFilename, outputFilename):
    # can be used when importing this script
    data = readInputFile(inputFilename)
    keys = getKeys(data)

    writeHeaderFiles(keys, inputFilename, outputFilename)
    writeOutputFile(data, outputFilename)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', metavar='FILE', dest='filename', help='input filename', required=True, type=str)
    parser.add_argument('-o', '--output', metavar='FILE', dest='output_filename', required=False, type=str, help="default output filename strips .json off the extension")
    args = parser.parse_args()

    checkArgs(args)
    writeListFile(args.filename, args.output_filename)
