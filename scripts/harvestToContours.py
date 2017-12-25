#!/usr/bin/env python

# harvestToContours.py #################
#
# An attempt to unify contour production so we don't have a million attempts to reinvent a broken wheel...
#
# Reads in a harvest list from the HF output in either text file or json formats (but c'mon.. use json.. what are you doing?)
# Then the CLs values are interpreted as p-values and converted to significances and then interpolated
# Interpolation of significance surface can be configured to e.g. nn, linear, cubic (options from mpl)
#
# By: Larry Lee - Dec 2017


# You'll have to have matplotlib and root setup side-by-side
# In an ATLAS environment, you can do that with:
#> localSetupSFT --cmtConfig=x86_64-slc6-gcc48-opt releases/LCG_79/pytools/1.9_python2.7,releases/LCG_79/pyanalysis/1.5_python2.7
#> lsetup root


import ROOT, json, argparse, math, sys, os

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

parser.add_argument("--logX", help="use log10 of x variable", action="store_true", default=False)
parser.add_argument("--logY", help="use log10 of y variable", action="store_true", default=False)

parser.add_argument("--fixedParamsFile","-f", type=str, help="give a json file with key=variable and value=value. e.g. use for pinning down third parameter in harvest list", default="")
parser.add_argument("--forbiddenFunction","-l", type=str, help="""a ROOT TF1 definition for a forbidden line e.g. kinematically forbidden regions. (for diagonal, use `-l "x"` )""", default="")
parser.add_argument("--ignoreUncertainty","-u", help="""Don't care about uncertainty bands!""", action="store_true", default=False)

args = parser.parse_args()

if not args.useROOT:
	try:
		import matplotlib.pyplot as plt
		import numpy as np
		import scipy.interpolate
	except:
		print ">>> You need matplotlib to be available to run in mpl mode."
		print ">>> Either use the ROOT interpolator with the option -r or set up mpl"
		print ">>> In an ATLAS environment, you can..."
		print ">>> > localSetupSFT --cmtConfig=x86_64-slc6-gcc48-opt releases/LCG_79/pytools/1.9_python2.7,releases/LCG_79/pyanalysis/1.5_python2.7"
		print ">>> > lsetup root"
		print ">>> "
		print ">>> Do you want me to try to set it up for you (in ATLAS env)? (y/n)"
		choice = raw_input().lower()
		if choice[0] == "y":
			try:
				os.system("localSetupSFT --cmtConfig=x86_64-slc6-gcc48-opt releases/LCG_79/pytools/1.9_python2.7,releases/LCG_79/pyanalysis/1.5_python2.7")
				os.system("lsetup root")
			except:
				print ">>> ... Setup didn't work for some reason!"
		else:
			print ">>> Quitting -- You don't have matplotlib/numpy setup and you requested mpl-based interpolation"
			sys.exit(1)


if args.ignoreUncertainty:
	listOfContours = ["CLs","CLsexp"]
else:
	listOfContours = ["CLs","CLsexp","clsu1s","clsu2s","clsd1s","clsd2s"]




def main():
	"""Main function for driving the whole thing..."""


	print ">>> Welcome to harvestToContours!"

	# Print out the settings
	for setting in dir(args):
		if not setting[0]=="_":
			print ">>> ... Setting: {: >20} {: >40}".format(setting, eval("args.%s"%setting) )

	f = ROOT.TFile(args.outputFile,"recreate")

	############################################################
	# Step 1 - Read in harvest list in either text or json format and dump it into a dictionary

	tmpdict = harvestToDict( args.inputFile )

	############################################################
	# Step 1.5 - If there's a function for a kinematically forbidden region, add zeros to dictionary

	if args.forbiddenFunction:
		addZerosToDict(tmpdict,args.forbiddenFunction)

	############################################################
	# Step 2 - Interpolate the fit results

	print ">>> Interpolating surface"

	outputGraphs = interpolateSurface( tmpdict , args.interpolation , args.useROOT)

	############################################################
	# Step 3 - get TGraph contours

	print ">>> Writing contours out"

	f.mkdir("SubGraphs"); f.cd("SubGraphs")
	for whichContour in listOfContours:

		try:
			for iSubGraph,subGraph in enumerate(outputGraphs[whichContour]):
				subGraph.Write("%s_Contour_%d"%(whichContour,iSubGraph))
		except:
			print ">>> ... Well that one's no good. You might want to check on that... - %s"%whichContour
			if len(outputGraphs[whichContour]):
				print ">>> ... It appears this has no contours..."

	f.cd()

	############################################################
	# Step 4 - Make pretty curves (and bands) or try to...

	if not args.ignoreUncertainty:
		for icurve,(curve1,curve2) in enumerate(zip(outputGraphs["clsu1s"],outputGraphs["clsd1s"]) ):
			band_1s = createBandFromContours( curve1, curve2 )
			band_1s.SetFillColorAlpha(ROOT.TColor.GetColor("#ffd700"), 0.75)
			band_1s.Write("Band_1s_%d"%icurve)
		for icurve,(curve1,curve2) in enumerate(zip(outputGraphs["clsu2s"],outputGraphs["clsd2s"]) ):
			band_2s = createBandFromContours( curve1, curve2 )
			band_2s.SetFillColorAlpha(ROOT.TColor.GetColor("#115000"), 0.5)
			band_2s.Write("Band_2s_%d"%icurve)

	for icurve,obsCurve in enumerate(outputGraphs["CLs"]):
		obsCurve.SetLineWidth(2)
		obsCurve.SetLineColorAlpha(ROOT.TColor.GetColor("#800000"), 0.9 )
		obsCurve.Write("Obs_%s"%icurve)
	for icurve,expCurve in enumerate(outputGraphs["CLsexp"]):
		expCurve.SetLineStyle(7)
		expCurve.Write("Exp_%s"%icurve)


	############################################################
	# Step 5 - Write out a pretty canvas for further editing

	canvas = ROOT.TCanvas("FinalCurves","FinalCurves")
	if not args.ignoreUncertainty:
		for iGraph in xrange(len(outputGraphs["clsu1s"]) ):
			f.Get("Band_1s_%d"%iGraph).Draw("ALF" if iGraph==0 else "LF")
	else:
		f.Get("Exp_0").Draw("AL")
	for iGraph in xrange(len(outputGraphs["CLsexp"]) ):
		f.Get("Exp_%d"%iGraph).Draw("L")
	for iGraph in xrange(len(outputGraphs["CLs"]) ):
		f.Get("Obs_%d"%iGraph).Draw("L")
	ROOT.gPad.RedrawAxis()
	canvas.Write()

	if args.debug:
		canvas.SaveAs("DebugFinalCurves.pdf")

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

				try:
					sampleParams = (float(sample[args.xVariable]),float(sample[args.yVariable]) )
				except:
					print ">>> ... Error: %s or %s doesn't exist as an entry in the input file"%(args.xVariable,args.yVariable)
					print ">>> ... Use cmd line options -x and -y to point to variables that exist in the input"
					sys.exit(1)

				sampleParamsList = list(sampleParams)
				if args.logX:
					sampleParamsList[0] = math.log10(sampleParamsList[0])
				if args.logY:
					sampleParamsList[1] = math.log10(sampleParamsList[1])
				sampleParams = tuple(sampleParamsList)

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

			sampleParams = (float(values[args.xVariable]),float(values[args.yVariable]))

			sampleParamsList = list(sampleParams)
			if args.logX:
				sampleParamsList[0] = math.log10(sampleParamsList[0])
			if args.logY:
				sampleParamsList[1] = math.log10(sampleParamsList[1])
			sampleParams = tuple(sampleParamsList)

			## Allowing filtering of entries via a constraints file
			if args.fixedParamsFile:
				failConstraintCutList = [not values[str(constrainedVar)]==constrainedVal for (constrainedVar, constrainedVal) in constraintsDict.iteritems()]
				if any(failConstraintCutList):
					continue

			modelDict[sampleParams] = dict(zip(listOfContours,  [ROOT.RooStats.PValueToSignificance( float(values["%s/F"%x]) ) for x in listOfContours] ) )


			print sampleParams, ROOT.RooStats.PValueToSignificance( float(values["CLs/F"])     )

	return modelDict


def addZerosToDict(inputDict, function, numberOfZeros = 100):
	"""This takes in a TF1 and dots zero points along that function, and adds to the dict"""

	tmpListOfXValues = [entry[0] for entry in inputDict.keys()]
	lowerLimit = 0
	upperLimit = max(tmpListOfXValues)
	forbiddenFunction = ROOT.TF1("forbiddenFunction",args.forbiddenFunction,lowerLimit,upperLimit)
	forbiddenFunction.Write("forbiddenFunction")

	for xValue in [lowerLimit + x*(upperLimit-lowerLimit)/float(numberOfZeros) for x in range(numberOfZeros)]:
		inputDict[(xValue,forbiddenFunction.Eval(xValue))] = dict(zip(listOfContours,  [0.0 for x in listOfContours] ) )
	return

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

		return graphs

	else:
		print ">>> ... Using scipy interpolate scheme."

		if args.interpolation in ["nearest"]:
			print ">>> WARNING: nearest interpolation mode seems to give unreliable results in tests!"

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
		gr.Write("CLexp_gr")

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

def createBandFromContours(contour1,contour2):

	outputSize = contour1.GetN()+contour2.GetN()+1
	outputGraph = ROOT.TGraph(outputSize)
	tmpx, tmpy = ROOT.Double(), ROOT.Double()
	for iPoint in xrange(contour2.GetN()):
		contour2.GetPoint(iPoint,tmpx,tmpy)
		outputGraph.SetPoint(iPoint,tmpx,tmpy)
	for iPoint in xrange(contour1.GetN()):
		contour1.GetPoint(contour1.GetN()-1-iPoint,tmpx,tmpy)
		outputGraph.SetPoint(contour2.GetN()+iPoint,tmpx,tmpy)
	contour2.GetPoint(0,tmpx,tmpy)
	outputGraph.SetPoint(contour1.GetN()+contour2.GetN(),tmpx,tmpy)

	outputGraph.SetFillStyle(1001);
	outputGraph.SetLineWidth(1)

	return outputGraph

if __name__ == "__main__":
	main()
