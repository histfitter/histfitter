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
import os
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--inputFiles","-i",  type=str, help="input files json (use wildcards)" , default = "inputJSON")
parser.add_argument("--outputFile","-o",  type=str, help="output json" , default = "outputJSON.json")
parser.add_argument("--figureOfMerit","-f",  type=str, help="figure of merit", default = "CLsexp")
parser.add_argument("--modelDef","-m",  type=str, help="comma separated list of variables that define a model", default = "mg,mlsp,tau,gentau")

args = parser.parse_args()


def main():

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
		if os.path.isfile(filename.replace("Nominal","Up")) and os.path.isfile(filename.replace("Nominal","Down")):
			with open(filename.replace("Nominal","Up")) as data_file:
				print ">>> >>> Adding input file: %s"%filename
				data = json.load(data_file)
				df = pd.DataFrame(data, columns=data[0].keys())
				databaseListTheoryUp.append(df)
			with open(filename.replace("Nominal","Down")) as data_file:
				print ">>> >>> Adding input file: %s"%filename
				data = json.load(data_file)
				df = pd.DataFrame(data, columns=data[0].keys())
				databaseListTheoryDown.append(df)
		else:
			print ">>> ... Can't find theory variation inputs. Skipping..."

	database = pd.concat(databaseList)
	databaseTheoryUp   = pd.concat(databaseListTheoryUp)
	databaseTheoryDown = pd.concat(databaseListTheoryDown)

	# cleaning up the bad stuff!
	database = database[(database.CLsexp != 0) & database.failedstatus==0]

	listOfModels = df[args.modelDef.split(",")].drop_duplicates()

	print ">>> Number of signal models considered: %s"%len(listOfModels)

	outputDB = doTheMuxing(database,listOfModels)


	# Handle the theory variation databses using the optimization from the nominal...



	print ">>> Writing output json: %s"%args.outputFile

	with open(args.outputFile, 'w') as f:
		f.write( outputDB.to_json(orient = "records") )

	return

def doTheMuxing(database,listOfModels):

	outputDatabaseList = []

	for index, model in listOfModels.iterrows():

		tmpDatabase = database

		# Select for only those rows that correspond to my model point
		for item in list(model.index):
			tmpDatabase = tmpDatabase.loc[tmpDatabase[item] == model[item]]

		# Now I've filtered out so I'm only looking at statements for this specific model!

		bestRow = tmpDatabase.loc[[tmpDatabase[args.figureOfMerit].idxmin()]]

		outputDatabaseList.append(bestRow)

	return pd.concat(outputDatabaseList)


if __name__ == "__main__":
	main()
