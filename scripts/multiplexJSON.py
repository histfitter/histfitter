#!/usr/bin/env python

# multiplexJSON.py #################
#
# A "multiplexer" to combine many JSON files (like for different SRs) and outputs
# a single JSON with the "best" SR written out. Default figure of merit is expected CLs
# but is configurable.
#
# By: Larry Lee - Jan 2018

import json
import argparse
import glob
import os,sys

parser = argparse.ArgumentParser()
parser.add_argument("--inputFiles","-i",  type=str, help="input files json (use wildcards)" , default = "inputJSON")
parser.add_argument("--outputFile","-o",  type=str, help="output json" , default = "outputJSON.json")
parser.add_argument("--figureOfMerit","-f",  type=str, help="figure of merit", default = "CLsexp")
parser.add_argument("--modelDef","-m",  type=str, help="comma separated list of variables that define a model", default = "mg,mlsp,tau,gentau")

args = parser.parse_args()


try:
	import pandas as pd
except:
	print ">>> You need pandas to be available."
	print ">>> In an ATLAS environment, you can..."
	print ">>> > localSetupSFT --cmtConfig=x86_64-slc6-gcc48-opt releases/LCG_79/pytools/1.9_python2.7,releases/LCG_79/pyanalysis/1.5_python2.7"
	print ">>> "
	print ">>> Do you want me to try to set it up for you (in ATLAS env)? (y/n)"
	choice = raw_input().lower()
	if choice[0] == "y":
		try:
			os.system("localSetupSFT --cmtConfig=x86_64-slc6-gcc48-opt releases/LCG_79/pytools/1.9_python2.7,releases/LCG_79/pyanalysis/1.5_python2.7")
			import pandas as pd
		except:
			print ">>> ... Setup didn't work for some reason!"
	else:
		print ">>> Quitting -- You don't have pandas set up!"
		sys.exit(1)



def main():

	print ">>>"
	print ">>> Welcome to multiplexJSON!"

	# Print out the settings
	for setting in dir(args):
		if not setting[0]=="_":
			print ">>> ... Setting: {: >20}:  {}".format(setting, eval("args.%s"%setting) )

	print ">>> "

	databaseList = []

	databaseListTheoryUp = []
	databaseListTheoryDown = []

	for filename in glob.glob(args.inputFiles):
		print ">>> Adding input file: %s"%filename
		with open(filename) as data_file:
			data = json.load(data_file)
			df = pd.DataFrame(data, columns=data[0].keys())
			databaseList.append(df)

		print ">>> Looking for theory variation files"
		if "Nominal" in filename and os.path.isfile(filename.replace("Nominal","Up")) and os.path.isfile(filename.replace("Nominal","Down")):
			with open(filename.replace("Nominal","Up")) as data_file:
				print ">>> >>> Adding input file for theory up variation"
				data = json.load(data_file)
				df = pd.DataFrame(data, columns=data[0].keys())
				databaseListTheoryUp.append(df)
			with open(filename.replace("Nominal","Down")) as data_file:
				print ">>> >>> Adding input file for theory down variation"
				data = json.load(data_file)
				df = pd.DataFrame(data, columns=data[0].keys())
				databaseListTheoryDown.append(df)
		else:
			print ">>> ... Can't find theory variation inputs. Skipping..."

	database = pd.concat(databaseList)
	if len(databaseListTheoryUp):
		databaseTheoryUp   = pd.concat(databaseListTheoryUp)
		databaseTheoryDown = pd.concat(databaseListTheoryDown)

	# cleaning up the bad stuff!
	database = database[(database.CLsexp != 0) & database.failedstatus==0]

	try:
		listOfModels = df[args.modelDef.split(",")].drop_duplicates()
	except:
		print ">>> Problem! The model definition variables don't seem to exist! Quitting."
		sys.exit(1)

	print ">>> Number of signal models considered: %s"%len(listOfModels)

	outputDB = doTheMuxing(database,listOfModels)

	# Handle the theory variation databses using the optimization from the nominal...

	if len(databaseListTheoryUp):
		outputDBTheoryUp   = doTheMuxing(databaseTheoryUp,listOfModels, outputDB)
		outputDBTheoryDown = doTheMuxing(databaseTheoryDown,listOfModels, outputDB)

	print ">>> Writing output json: %s"%args.outputFile

	with open(args.outputFile, 'w') as f:
		f.write( outputDB.to_json(orient = "records") )


	if len(databaseListTheoryUp):
		print ">>> Writing output json for theory variations *_[Up/Down].json "
		with open(args.outputFile.replace(".json","")+"_Up.json", 'w') as f:
			f.write( outputDBTheoryUp.to_json(orient = "records") )
		with open(args.outputFile.replace(".json","")+"_Down.json", 'w') as f:
			f.write( outputDBTheoryDown.to_json(orient = "records") )

	print ">>> Done!"
	print ">>>"

	return

def doTheMuxing(database,listOfModels, nominalDatabase=0):

	outputDatabaseList = []

	for index, model in listOfModels.iterrows():

		tmpDatabase = database

		# Select for only those rows that correspond to my model point
		for item in list(model.index):
			tmpDatabase = tmpDatabase.loc[tmpDatabase[item] == model[item]]

		# Now I've filtered out so I'm only looking at statements for this specific model!

		# Use figure of merit to do optimization
		if type(nominalDatabase)==int:
			bestRow = tmpDatabase.loc[[tmpDatabase[args.figureOfMerit].idxmin()]]

		# Use nominalDatabase that has already been optimized for choosing best row
		else:

			tmpNominalDatabase = nominalDatabase
			# Select for only those rows that correspond to my model point
			for item in list(model.index):
				tmpNominalDatabase = tmpNominalDatabase.loc[tmpNominalDatabase[item] == model[item]]

			# print tmpNominalDatabase.fID
			bestRow = tmpDatabase.loc[tmpDatabase["fID"]==tmpNominalDatabase.fID]

		outputDatabaseList.append(bestRow)

	return pd.concat(outputDatabaseList)



if __name__ == "__main__":
	main()
