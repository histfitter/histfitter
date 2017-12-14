#!/usr/bin/env python

# harvestToContours.py #################
#
# An attempt to unify contour production so we don't have a million attempts to reinvent a broken wheel...
#
# Reads in a harvest list from the HF output in either text file or json formats (but c'mon.. use json.. what are you doing?)
# Then the CLs values are interpreted as p-values and converted to significances and then interpolated
# Interpolation of significance surface can be configured to e.g. nn, linear, cubic (options from mpl)
#
# By: Larry Lee


# You'll have to have matplotlib and root setup side-by-side
# In an ATLAS environment, you can do that with:
#> localSetupSFT --cmtConfig=x86_64-slc6-gcc48-opt releases/LCG_79/pytools/1.9_python2.7,releases/LCG_79/pyanalysis/1.5_python2.7
#> lsetup root


import ROOT, json, argparse, math, sys

ROOT.gROOT.SetBatch()

parser = argparse.ArgumentParser()
parser.add_argument("--inputFile","-i",  type=str, help="input harvest file", default = "test.json")
parser.add_argument("--outputFile","-o", type=str, help="output ROOT file", default = "outputGraphs.root")
parser.add_argument("--interpolation",   type=str, help="type of interpolation for scipy. e.g. linear, cubic, nearest. NOTE: Anything other than linear seems buggy", default = "linear")
parser.add_argument("--level",           type=float, help="contour level output. Default to 95% CL", default = ROOT.RooStats.PValueToSignificance( 0.05 ))
parser.add_argument("--useROOT","-r", help="use the root interpolation engine instead of mpl", action="store_true", default=False)
parser.add_argument("--debug","-d", help="print extra debugging info", action="store_true", default=False)

parser.add_argument("--sigmax",          type=float, help="maximum significance in sigmas", default = 5.0)

parser.add_argument("--xVariable","-x",  type=str, default = "mg" )
parser.add_argument("--yVariable","-y",  type=str, default = "mlsp" )

parser.add_argument("--xResolution", type=int, default = 100 )
parser.add_argument("--yResolution", type=int, default = 100 )

parser.add_argument("--fixedParamsFile","-f", type=str, help="give a json file with key=variable and value=value. e.g. use for pinning down third parameter in harvest list", default="")

args = parser.parse_args()

if not args.useROOT:

	import matplotlib.pyplot as plt
	import numpy as np
	import scipy.interpolate

	import matplotlib.mlab


listOfContours = ["CLs","CLsexp","clsu1s","clsu2s","clsd1s","clsd2s"]



def main():
	"""Main function for driving the whole thing..."""

	print ">>> Welcome to harvestToContours!"
	for setting in dir(args):
		if not setting[0]=="_":
			print ">>> ... Setting: {: >20} {: >20}".format(setting, eval("args.%s"%setting) )

	f = ROOT.TFile(args.outputFile,"recreate")

	# Step 1 - Read in harvest list in either text or json format and dump it into a dictionary
	tmpdict = harvestToDict( args.inputFile )

	# Step 2 - Interpolate the fit results
	print ">>> Interpolating surface"
	outputGraphs = interpolateSurface( tmpdict , args.interpolation , args.useROOT)

	print ">>> Writing contours out"
	# Step 3 - get TGraph contours
	for whichContour in listOfContours:

		try:
			for iSubGraph,subGraph in enumerate(outputGraphs[whichContour]):
				subGraph.Write("%s_Contour_%d"%(whichContour,iSubGraph))
		except:
			print ">>> ... Well that one's no good. You might want to check on that... - %s"%whichContour
			if len(outputGraphs[whichContour]):
				print ">>> ... It appears this has no contours..."

	if args.debug:
		canvas = ROOT.TCanvas("FinalCurves","FinalCurves")
		try:
			outputGraphs["CLs"][0].Draw("AL")
			for whichContour in ["CLsexp","clsu1s","clsd1s"]:
				outputGraphs[whichContour][0].SetLineStyle(7)
				outputGraphs[whichContour][0].Draw("L")
			canvas.SaveAs("DebugFinalCurves.pdf")
		except:
			print ">>> ... Something broke. You don't seem to have a contour."


	print ">>> Closing file"

	f.Write()
	f.Close()


def harvestToDict( harvestInputFileName = "" ):
	"""This parses the input file into a dictionary object for simpler handling"""
	print ">>> Entering harvestToDict()"

	modelDict = {}

	harvestInput = open(harvestInputFileName,"r")

	constraintsDict = {}
	if args.fixedParamsFile:
		with open(args.fixedParamsFile) as inputFixedParamsFile:
			inputFixedParamsJSON = json.load(inputFixedParamsFile)
			# print inputFixedParamsJSON
			constraintsDict = inputFixedParamsJSON

	if ".json" in harvestInputFileName:
		print ">>> ... Interpreting json file %s"%harvestInputFileName

		with open(harvestInputFileName) as inputJSONFile:
			inputJSON = json.load(inputJSONFile)

			# print inputJSON

			for sample in inputJSON:

				## Allowing filtering of entries via a constraints file
				if args.fixedParamsFile:
					failConstraintCutList = [not sample[str(constrainedVar)]==constrainedVal for (constrainedVar, constrainedVal) in constraintsDict.iteritems()]
					if any(failConstraintCutList):
						continue

				sampleParams = (sample[args.xVariable],sample[args.yVariable])


				if ROOT.RooStats.PValueToSignificance( float(sample["CLsexp"]) ) < args.sigmax and not math.isinf(float(sample["CLsexp"])) :
					modelDict[sampleParams] = dict(zip(listOfContours,  [ROOT.RooStats.PValueToSignificance( float(sample["%s"%x]) ) for x in listOfContours] ) )

				else:
					if not sampleParams in modelDict:
						modelDict[sampleParams] = dict(zip(listOfContours,  [args.sigmax for x in listOfContours] ) )
				if(args.debug):
					print sampleParams, float(sample["CLs"]), ROOT.RooStats.PValueToSignificance( float(sample["CLs"])     )


	else:
		print ">>> ... Interpreting text file -- (This feature hasn't been fully tested)"
		print ">>> ... Also why aren't you just using JSON you fool"
		print ">>> ... Seriously -- HF now spits out a JSON, and if you're converting that back to a text file you deserve to have things not work..."

		try:
			from summary_harvest_tree_description import treedescription
			# from summary_harvest_tree_description_MEffRJRCombine import treedescription
			dummy,fieldNames = treedescription()
			fieldNames = fieldNames.split(':')
		except:
			print ">>> Crash and burn -- I need a harvest tree description file!"
			sys.exit(0)

		for model in harvestInput.readlines():
			values = model.split()
			values = dict(zip(fieldNames, values))

			massPoint = (float(values[args.xVariable]),float(values[args.yVariable]))

			## Allowing filtering of entries via a constraints file
			if args.fixedParamsFile:
				failConstraintCutList = [not values[str(constrainedVar)]==constrainedVal for (constrainedVar, constrainedVal) in constraintsDict.iteritems()]
				if any(failConstraintCutList):
					continue

			modelDict[massPoint] = dict(zip(listOfContours,  [ROOT.RooStats.PValueToSignificance( float(values["%s/F"%x]) ) for x in listOfContours] ) )


			print massPoint, ROOT.RooStats.PValueToSignificance( float(values["CLs/F"])     )

	return modelDict


def interpolateSurface(modelDict = {}, interpolationFunction = "linear", useROOT=False):
	"""The actual interpolation"""

	modelPoints = modelDict.keys()
	modelPointsValues = modelDict.values()

	x0 =   list( zip( *modelPoints )[0] )
	y0 =   list( zip( *modelPoints )[1] )

	zValues = {} # entry x points
	x={} # entry x points
	y={} # entry x points

	graphs = {}


	for whichContour in listOfContours:
		zValues[whichContour] = [ tmpEntry[whichContour] for tmpEntry in modelPointsValues]
		x[whichContour]       = [ a for a in x0 ];
		y[whichContour]       = [ a for a in y0 ];

	# remove inf point in each entry
	for whichContour in listOfContours:

		while any([math.isinf(tmp) for tmp in zValues[whichContour]  ]):#  np.isinf( zValues[whichContour]  ).any():
			myindex = [math.isinf(tmp) for tmp in zValues[whichContour] ].index(True)
			if (args.debug):
				print ">>> ... Remove Inf at i=%d x=%d y=%d" % (myindex,x[whichContour][myindex],y[whichContour][myindex])
			x[whichContour].pop(myindex)
			y[whichContour].pop(myindex)
			zValues[whichContour].pop(myindex)
			pass;

		if any([math.isinf(tmp) for tmp in zValues[whichContour]  ]):
			print ">>> ... Still infs in %s!! This is a problem... Exiting." % whichContour
			sys.exit(0)

	if useROOT:
		print ">>> ... Using ROOT's internal interpolation scheme (triangular)."
		print ">>> ... If you like your plot to look like a dinosaur's back or an escalator, then you're entitled to that.."


		canvas = ROOT.TCanvas("c1","c1",800,600);
		h2D    = ROOT.TH2D("h","h",200,min(x0),max(x0),200,min(y0),max(y0) );

		for whichContour in listOfContours:
			graphs[whichContour] = createGraphsFromArrays(x[whichContour],y[whichContour],zValues[whichContour],whichContour)

		# print graphs
		return graphs

	else:
		print ">>> ... Using scipy interpolate scheme."

		if args.interpolation in ["cubic","nearest"]:
			print ">>> WARNING: cubic and nearest interpolation modes seem to give unreliable results in tests!"

		xi = {}
		yi = {}
		zi = {}
		for whichContour in listOfContours:
			print ">>> ... Interpolating %s"%whichContour;
			xArray = np.array(x[whichContour]);
			yArray = np.array(y[whichContour]);
			xyArray = np.array( zip(x[whichContour],y[whichContour]) )
			zValuesArray = np.array( zValues[whichContour] );

			# get xi, yi
			xi[whichContour], yi[whichContour] = np.linspace(xArray.min(), xArray.max(), args.xResolution), np.linspace(yArray.min(), yArray.max(), args.yResolution);
			xi[whichContour], yi[whichContour] = np.meshgrid(xi[whichContour], yi[whichContour]);

			# zi[whichContour] = matplotlib.mlab.griddata(xArray, yArray, zValuesArray, xi[whichContour], yi[whichContour], interp=interpolationFunction)
			zi[whichContour] = scipy.interpolate.griddata( xyArray , zValuesArray, (xi[whichContour], yi[whichContour]) , method=interpolationFunction)

			contourList = getContourPoints(xi[whichContour],yi[whichContour],zi[whichContour], args.level)

			graphs[whichContour] = []
			for contour in contourList:
				graph = ROOT.TGraph(len(contour[0]), contour[0].flatten('C'), contour[1].flatten('C') )
				graphs[whichContour].append(graph)
		return graphs


def createGraphsFromArrays(x,y,z,label):

	if args.debug:
		print ">>> ... In createGraphsFromArrays for %s"%label

	from array import array

	gr = ROOT.TGraph2D(len(x),
		array('f',x),
		array('f',y),
		array('f',z) )

	hist = gr.GetHistogram().Clone(label)

	if label=="CLsexp":
		hist.Write("CLsexp_hist")

	hist.SetContour(1)
	hist.SetContourLevel(0,args.level)
	ROOT.SetOwnership(hist,0)
	hist.Draw("CONT LIST")
	ROOT.gPad.Update()
	outputContours = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
	maxIntegral = 0
	biggestGraph = 0
	allGraphs = []
	for contour in outputContours.At(0):
		l = contour.Clone()
		ROOT.SetOwnership(l,0)
		l.Draw("ALP")
		if contour.Integral() > maxIntegral:
			maxIntegral = contour.Integral()
			biggestGraph = contour.Clone()
		allGraphs.append(l)
		# print contour.GetN()
	if biggestGraph and args.debug:
		biggestGraph.Draw("ALP")
		# canvas.SaveAs("gr_%s.pdf"%label)
	# return biggestGraph

	if args.debug:
		print ">>> ... ... Number of graphs %d"%len(allGraphs)
		# print allGraphs

	return allGraphs



def getContourPoints(xi,yi,zi,level ):

	c = plt.contour(xi,yi,zi, [level])
	contour = c.collections[0]

	contourList = []

	for i in xrange( len(contour.get_paths() ) ):
		v = contour.get_paths()[i].vertices

		x = v[:,0]
		y = v[:,1]

		contourList.append( (x,y) )

	return contourList




if __name__ == "__main__":
	main()
