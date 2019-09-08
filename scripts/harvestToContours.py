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


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import ROOT, json, argparse, math, sys, os, pickle, copy

ROOT.gROOT.SetBatch()


parser = argparse.ArgumentParser()
parser.add_argument("--inputFile","-i",  type = str, help="input harvest file", default = "test.json")
parser.add_argument("--outputFile","-o", type = str, help="output ROOT file", default = "outputGraphs.root")
parser.add_argument("--interpolation",   type = str, help="type of interpolation for scipy (RBF). e.g. linear, cubic, gaussian, multiquadric.", default = "multiquadric")
parser.add_argument("--interpolationEpsilon", type=float, help="scipy (RBF) epsilon parameter", default = 0)
parser.add_argument("--level",           type = float, help="contour level output. Default to 95%% CL", default = 1.64485362695)
parser.add_argument("--useROOT","-r",    help = "use the root interpolation engine instead of mpl", action="store_true", default=False)
parser.add_argument("--debug","-d",      help = "print extra debugging info", action="store_true", default=False)
parser.add_argument("--sigmax",          type = float, help="maximum significance in sigmas", default = 5.0)
parser.add_argument("--xVariable","-x",  type = str, default = "mg" )
parser.add_argument("--yVariable","-y",  type = str, default = "mlsp" )
parser.add_argument("--xResolution",     type = int, default = 100 )
parser.add_argument("--yResolution",     type = int, default = 100 )

parser.add_argument("--xMin", type=float, default = None )
parser.add_argument("--yMin", type=float, default = None )
parser.add_argument("--xMax", type=float, default = None )
parser.add_argument("--yMax", type=float, default = None )

parser.add_argument("--logX", help="use log10 of x variable", action="store_true", default=False)
parser.add_argument("--logY", help="use log10 of y variable", action="store_true", default=False)

parser.add_argument("--fixedParamsFile","-f",   type=str, help="give a json file with key=variable and value=value. e.g. use for pinning down third parameter in harvest list", default="")
parser.add_argument("--forbiddenFunction","-l", type=str, help="""a ROOT TF1 definition for a forbidden line e.g. kinematically forbidden regions. (defaults to diagonal, i.e. -l 'x'). Set to 'None' to turn off.""", default="x")
parser.add_argument("--ignoreUncertainty","-u", help="""Don't care about uncertainty bands!""", action="store_true", default=False)

parser.add_argument("--areaThreshold","-a",     type = float, help="Throw away contours with areas less than threshold", default=0)
parser.add_argument("--smoothing",    "-s",     type = str, help="smoothing option. For ROOT, use {k5a, k5b, k3a}. For scipy, uses smoothing from RBF.", default="0.1")
parser.add_argument("--noSig","-n",      help = "don't convert CLs to significance -- don't use this option unless you know what you're doing!", action="store_true", default=False)

parser.add_argument("--nominalLabel",      help = "keyword in filename to look for nominal sig XS", type=str, default="Nominal")

parser.add_argument("--useUpperLimit", help="use upper limit information instead of CLs. Automatically turns off significance transform.", action="store_true", default=False)

parser.add_argument("--closedBands","-b",      help = "if contours are closed shapes in this space, this can help with stitching issues if you're seeing weird effects", action="store_true", default=False)

args = parser.parse_args()


## If I need to use scipy, please let me have scipy. I'll even help you out!
try:
	import matplotlib as mpl
	mpl.use('Agg')
	import matplotlib.pyplot as plt
	import numpy as np
	import scipy.interpolate
except:
	print( ">>>" )
	print( ">>> You need scipy/matplotlib to run this. And you had to have run harvestToContours in scipy mode [default]" )
	print( ">>> In an ATLAS environment, you can..." )
	print( '>>> > lsetup "lcgenv -p LCG_93 x86_64-slc6-gcc62-opt pyanalysis" "lcgenv -p LCG_93 x86_64-slc6-gcc62-opt pytools" "lcgenv -p LCG_93 x86_64-slc6-gcc62-opt pygraphics" "lcgenv -p LCG_93 x86_64-slc6-gcc62-opt ROOT" ' )
	print( ">>> " )
	print( ">>> Try that and then run this again!" )
	sys.exit(1)


if args.useUpperLimit:

	print( ">>> ")
	print( ">>> INFO: You've asked for interpolation of an upper limit plane. So I'll also turn off the significance transform (--noSig) for you. And setting level to 1.")
	print( ">>> ")

	args.noSig = True
	args.level = 1.0

	if args.ignoreUncertainty:
		listOfContours = ["upperLimit","expectedUpperLimit"]
	else:
		listOfContours = ["upperLimit","expectedUpperLimit","expectedUpperLimitPlus1Sig","expectedUpperLimitPlus2Sig","expectedUpperLimitMinus1Sig","expectedUpperLimitMinus2Sig"]
	listOfContours_OneSigma = ["expectedUpperLimitPlus1Sig","expectedUpperLimitMinus1Sig"]
	listOfContours_TwoSigma = ["expectedUpperLimitPlus2Sig","expectedUpperLimitMinus2Sig"]
	expectedContour = "expectedUpperLimit"
	observedContour = "upperLimit"
else:
	if args.ignoreUncertainty:
		listOfContours = ["CLs","CLsexp","upperLimit","expectedUpperLimit"]
	else:
		listOfContours = ["CLs","CLsexp","clsu1s","clsu2s","clsd1s","clsd2s","upperLimit","expectedUpperLimit"]
	listOfContours_OneSigma = ["clsu1s","clsd1s"]
	listOfContours_TwoSigma = ["clsu2s","clsd2s"]
	expectedContour = "CLsexp"
	observedContour = "CLs"



def main():
	"""Main function for driving the whole thing..."""

	print( ">>> Welcome to harvestToContours!" )

	# Print out the settings
	for setting in dir(args):
		if not setting[0]=="_":
			print( ">>> ... Setting: {: >20} {: >40}".format(setting, eval("args.%s"%setting) ) )


	if args.xMin == None:
		print ("")
		print (">>> ******************** WARNING ***************************")
		print (">>> ** You haven't defined --xMin, --xMax, --yMin, --yMax **")
		print (">>> ** If you're going to later use multiplexContours.py  **")
		print (">>> ** to combine contours, and if your inputs don't have **")
		print (">>> ** exactly the same signal points, you're gonna have  **")
		print (">>> ** a bad time. To be safe, define these.              **")
		print (">>> ********************************************************")
		print ("")

	if args.forbiddenFunction == "x":
		print ("")
		print (">>> ******************** WARNING ***************************")
		print (">>> ** The default kinematically forbidden line is y=x    **")
		print (">>> ** If you have no kinematically forbidden region,     **")
		print (">>> ** use the option --forbiddenFunction ""              **")
		print (">>> ** or feel free to use another function! Just beware  **")
		print (">>> ** of the default if you see funky results            **")
		print (">>> ********************************************************")
		print ("")


	f = ROOT.TFile(args.outputFile,"recreate")

	processInputFile(inputFile = args.inputFile, outputFile = f, label = "")

	if args.nominalLabel in args.inputFile:
		print (">>> Handling theory variations...")
		try:
			processInputFile(inputFile = args.inputFile.replace(args.nominalLabel,"Up")  , outputFile = f, label = "_Up")
			processInputFile(inputFile = args.inputFile.replace(args.nominalLabel,"Down"), outputFile = f, label = "_Down")
		except:
			print (">>> ... Can't find theory variation files. Skipping.")

		print (">>> Handling upper limit file")

		try:
			processInputFile(inputFile = args.inputFile.replace(args.nominalLabel,"UpperLimit")  , outputFile = f, label = "_UL")
			print (">>>")
			print (">>> *********************************************************")
			print (">>> FYI: This is just for putting upper limit values as")
			print (">>> ... little grey numbers on your final plot. This is")
			print (">>> ... not for making contours from. It'll write out a")
			print (">>> ... TGraph2D with those numbers")
			print (">>> *********************************************************")
			print (">>>")
		except:
			print (">>>")
			print (">>> ... Can't find upper limit file. Skipping.")
			print (">>> ... (This is only used for little grey numbers")
			print (">>> ... on the final plot so if you're not interested")
			print (">>> ... in that right now, you can ignore this!)")
			print (">>>")

	print (">>> ")
	print (">>> Closing file")

	f.Write()
	f.Close()

	print (">>> ")
	print (">>> All done! Have a beautiful day -- You're an inspiration you wonderful person you!")

	return

def processInputFile(inputFile, outputFile, label = ""):
	"""Do actual processing of a given input file"""

	############################################################
	# Step 1 - Read in harvest list in either text or json format and dump it into a dictionary

	resultsDict = harvestToDict( inputFile )

	if len(resultsDict)<3:
		print (">>> WARNING: You have fewer than three valid model points in your input. I can't interpolate that in 2D! You've given me %d valid points!"%( len(resultsDict) ) )
		return -1

	if label=="": #Only do this for the nominal signal XS
		for whichContour in listOfContours:
			tmpGraph = createTGraphFromDict(resultsDict,whichContour)
			tmpGraph.Write( "%s_gr"%(whichContour) )

		listOfFIDs = createListOfFIDs(resultsDict,ROOT.gDirectory)
		if len(listOfFIDs):
			tmpGraph = createTGraphFromDict(resultsDict,"fID",listOfFIDs)
			tmpGraph.Write( "fID_gr" )

	if label=="_UL":
		for whichEntry in ["upperLimit","expectedUpperLimit"]:
			tmpGraph = createTGraphFromDict(resultsDict,whichEntry)
			tmpGraph.Write( "%s_gr"%(whichEntry) )

	if label!="_UL":
		truncateSignificances( resultsDict , args.sigmax )

	############################################################
	# Step 1.5 - If there's a function for a kinematically forbidden region, add zeros to dictionary

	if "none" not in args.forbiddenFunction.lower():
		resultsDict = addValuesToDict(resultsDict, args.forbiddenFunction, numberOfPoints=100 ,value = "mirror" )

	############################################################
	# Step 2 - Interpolate the fit results

	print (">>> Interpolating surface")

	if label=="_UL":
		# Now I want to interpolate the UL surface if it exists so I can write out a detailed 2D surface
		upperLimitSurface = interpolateSurface( resultsDict, args.interpolation, args.useROOT, outputSurfaceTGraph=True, tmpListOfContours=["upperLimit"] )
		upperLimitSurface.Write("upperLimit_Surface")
		if args.debug:
			canvas = ROOT.TCanvas("upperLimitSurface","upperLimitSurface")
			upperLimitSurface.Draw("cont4z")
			ROOT.gPad.SetRightMargin(0.15)
			ROOT.gPad.SetLogz()
			ROOT.gPad.RedrawAxis()
			canvas.SaveAs("upperLimitSurface.pdf")
		return

	outputGraphs = interpolateSurface( resultsDict , args.interpolation , args.useROOT , outputSurface=True if label=="" else False)

	############################################################
	# Step 3 - get TGraph contours

	print (">>> Writing contours out")

	outputFile.mkdir("SubGraphs"); outputFile.cd("SubGraphs")
	for whichContour in listOfContours:

		try:
			for iSubGraph,subGraph in enumerate(outputGraphs[whichContour]):
				subGraph.Write("%s_Contour_%d%s"%(whichContour,iSubGraph,label))
		except:
			print (">>> ... Well that one's no good. You might want to check on that... - %s"%whichContour)
			if len(outputGraphs[whichContour]):
				print (">>> ... It appears this has no contours...")

	outputFile.cd()

	############################################################
	# Step 4 - Make pretty curves (and bands) or try to...

	if not args.ignoreUncertainty and label=="":
		if len(outputGraphs[listOfContours_OneSigma[0] ])==0 and len(outputGraphs[listOfContours_OneSigma[1] ])>0:
			print (">>>")
			print (">>> WARNING: You don't have +1 sigma sensitivity,")
			print (">>> ... but you do have -1 sigma reach. Making a ")
			print (">>> ... +/-1 sigma band from only the -1 side.")
			print (">>> ")
			for icurve,curve1 in enumerate(outputGraphs[listOfContours_OneSigma[1] ]):
				band_1s = createBandFromContours( curve1 )
				band_1s.SetFillColorAlpha(ROOT.TColor.GetColor("#ffd700"), 0.75)
				band_1s.Write("Band_1s_%d"%icurve)
		for icurve,(curve1,curve2) in enumerate(zip(outputGraphs[listOfContours_OneSigma[0] ],outputGraphs[listOfContours_OneSigma[1] ]) ):
			band_1s = createBandFromContours( curve1, curve2 )
			band_1s.SetFillColorAlpha(ROOT.TColor.GetColor("#ffd700"), 0.75)
			band_1s.Write("Band_1s_%d"%icurve)
		for icurve,(curve1,curve2) in enumerate(zip(outputGraphs[listOfContours_TwoSigma[0] ],outputGraphs[listOfContours_TwoSigma[1] ]) ):
			band_2s = createBandFromContours( curve1, curve2 )
			band_2s.SetFillColorAlpha(ROOT.TColor.GetColor("#115000"), 0.5)
			band_2s.Write("Band_2s_%d"%icurve)


	for icurve,obsCurve in enumerate(outputGraphs[observedContour]):
		obsCurve.SetLineWidth(2)
		obsCurve.SetLineColorAlpha(ROOT.TColor.GetColor("#800000"), 0.9 )
		obsCurve.Write("Obs_%s%s"%(icurve,label) )
	for icurve,expCurve in enumerate(outputGraphs[expectedContour]):
		expCurve.SetLineStyle(7)
		expCurve.Write("Exp_%s%s"%(icurve,label) )


	############################################################
	# Step 5 - Write out a pretty canvas for further editing

	if label=="":
		canvas = ROOT.TCanvas("FinalCurves","FinalCurves")
		try:
			if not args.ignoreUncertainty and outputFile.Get("Band_1s_0"):
				for iGraph in xrange(  len(outputGraphs[listOfContours_OneSigma[1] ])   ):
						outputFile.Get("Band_1s_%d"%iGraph).Draw("ALF" if iGraph==0 else "LF")
			else:
				outputFile.Get("Exp_0").Draw("AL")
			for iGraph in xrange(len(outputGraphs[expectedContour]) ):
				outputFile.Get("Exp_%d"%iGraph).Draw("L")
			for iGraph in xrange(len(outputGraphs[observedContour]) ):
				outputFile.Get("Obs_%d"%iGraph).Draw("L")
			ROOT.gPad.RedrawAxis()
			canvas.Write()
		except:
			print (">>> WARNING: Had some problems making a canvas for you. Probably some curves are missing for some reason")

		if args.debug:
			canvas.SaveAs("DebugFinalCurves.pdf")

	return


def harvestToDict( harvestInputFileName = "" , tmpListOfContours = listOfContours ):
	"""This parses the input file into a dictionary object for simpler handling"""

	print (">>> Entering harvestToDict()")

	modelDict = {}

	harvestInput = open(harvestInputFileName,"r")

	constraintsDict = {}
	if args.fixedParamsFile:
		with open(args.fixedParamsFile) as inputFixedParamsFile:
			inputFixedParamsJSON = json.load(inputFixedParamsFile)
			constraintsDict = inputFixedParamsJSON

	if ".json" in harvestInputFileName:
		print (">>> ... Interpreting json file %s"%harvestInputFileName)

		with open(harvestInputFileName) as inputJSONFile:
			inputJSON = json.load(inputJSONFile)

			for sample in inputJSON:

				## Allowing filtering of entries via a constraints file
				if args.fixedParamsFile:
					failConstraintCutList = [not sample[str(constrainedVar)]==constrainedVal for (constrainedVar, constrainedVal) in constraintsDict.iteritems()]
					if any(failConstraintCutList):
						continue

				try:
					sampleParams = (float(sample[args.xVariable]),float(sample[args.yVariable]) )
				except:
					print (">>> ... Error: %s or %s doesn't exist as an entry in the input file"%(args.xVariable,args.yVariable))
					print (">>> ... Use cmd line options -x and -y to point to variables that exist in the input")
					print (">>> Available variables are listed below:")
					print (">>> ")
					print (">>> "+"\n>>> ".join(sample.keys()))
					sys.exit(1)

				sampleParamsList = list(sampleParams)
				if args.logX:
					sampleParamsList[0] = math.log10(sampleParamsList[0])
				if args.logY:
					sampleParamsList[1] = math.log10(sampleParamsList[1])
				sampleParams = tuple(sampleParamsList)

				if not math.isinf(float(sample[expectedContour])) :
					tmpList = [float(sample["%s"%x]) if (args.noSig or x in ["upperLimit","expectedUpperLimit"]) else ROOT.RooStats.PValueToSignificance( float(sample["%s"%x]) ) for x in tmpListOfContours]
					modelDict[sampleParams] = dict(zip(tmpListOfContours,  tmpList ) )
					if "fID" in sample:
						modelDict[sampleParams]["fID"] = sample["fID"]
					else:
						modelDict[sampleParams]["fID"] = ""


				else:
					if not sampleParams in modelDict:
						modelDict[sampleParams] = dict(zip(tmpListOfContours,  [args.sigmax for x in tmpListOfContours] ) )
						modelDict[sampleParams]["fID"] = ""
				if(args.debug):
					print (sampleParams, float(sample[observedContour]), float(sample[expectedContour]) if args.noSig else ROOT.RooStats.PValueToSignificance( float(sample[observedContour])     ))


	else:
		print (">>> ... Interpreting text file -- (This feature hasn't been fully tested)")
		print (">>> ... Also why aren't you just using JSON you fool")
		print (">>> ... Seriously -- HF now spits out a JSON, and if you're converting that back to a text file you deserve to have things not work...")

		try:
			from summary_harvest_tree_description import treedescription
			# from summary_harvest_tree_description_MEffRJRCombine import treedescription
			dummy,fieldNames = treedescription()
			fieldNames = fieldNames.split(':')
		except:
			print (">>> Crash and burn -- I need a harvest tree description file!")
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

			tmpList = [float(values["%s/F"%x]) if (args.noSig or x in ["upperLimit","expectedUpperLimit"]) else ROOT.RooStats.PValueToSignificance( float(values["%s/F"%x]) ) for x in tmpListOfContours]

			modelDict[sampleParams] = dict(zip(tmpListOfContours,  tmpList ) )


	return modelDict


def addValuesToDict(inputDict, function, numberOfPoints = 100, value = 0):
	"""This takes in a TF1 and dots zero points along that function, and adds to the dict"""

	tmpListOfXValues = [entry[0] for entry in inputDict.keys()]
	lowerLimit = min(tmpListOfXValues)
	upperLimit = max(tmpListOfXValues)

	forbiddenFunction = ROOT.TF1("forbiddenFunction${}".format(value),args.forbiddenFunction,lowerLimit,upperLimit)
	forbiddenFunction.Write("forbiddenFunction${}".format(value))


	if value == "mirror":
		from scipy.spatial.distance import cdist
		def closest_point(pt, others):
		    distances = cdist(pt, others)
		    return others[distances.argmin()]

		def rotate(origin, point, angle=math.pi):
		    ox, oy = origin
		    px, py = point

		    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
		    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
		    return qx, qy

		inputDictCopy = copy.deepcopy(inputDict)

		forbiddenLineArray = []
		for xValue in [lowerLimit + x*(upperLimit-lowerLimit)/float(numberOfPoints*100) for x in range(numberOfPoints*100)]:
			forbiddenLineArray.append( ( xValue,forbiddenFunction.Eval(xValue) ) )

		# now to loop over entries in the inputDict. rotate them about this closest point on the forbidden line
		for signalPoint in inputDict:
			closestPointOnLine = list(closest_point(np.array([signalPoint]),np.array(forbiddenLineArray) ) )
			inputDictCopy[tuple(closestPointOnLine)] = dict(zip(listOfContours,  [1 for x in listOfContours] ) )
			fakeMirroredSignalPoint = rotate(closestPointOnLine, signalPoint)
			tmpDict = copy.deepcopy(inputDictCopy[signalPoint])
			for key in tmpDict:
				if isinstance(tmpDict[key], (int, long, float)):
					tmpDict[key] *= -1*np.sign(tmpDict[key])
			inputDictCopy[fakeMirroredSignalPoint] = tmpDict

		inputDict = copy.deepcopy(inputDictCopy)

	else:
		for xValue in [lowerLimit + x*(upperLimit-lowerLimit)/float(numberOfPoints) for x in range(numberOfPoints)]:
			inputDict[(xValue,forbiddenFunction.Eval(xValue))] = dict(zip(listOfContours,  [value for x in listOfContours] ) )

	return inputDict

def interpolateSurface(modelDict = {}, interpolationFunction = "linear", useROOT=False, outputSurface=False, outputSurfaceTGraph=False, tmpListOfContours=listOfContours):
	"""The actual interpolation"""

	modelPoints = modelDict.keys()
	modelPointsValues = modelDict.values()
	x0 =   list( zip( *modelPoints )[0] )
	y0 =   list( zip( *modelPoints )[1] )

	zValues = {} # entry x points
	x={} # entry x points
	y={} # entry x points

	graphs = {}

	for whichContour in tmpListOfContours:
		zValues[whichContour] = [ tmpEntry[whichContour] for tmpEntry in modelPointsValues]
		x[whichContour]       = [ a for a in x0 ];
		y[whichContour]       = [ a for a in y0 ];

	# remove inf point in each entry
	for whichContour in tmpListOfContours:

		while any([math.isinf(tmp) or math.isnan(tmp) for tmp in zValues[whichContour]  ]):#  np.isinf( zValues[whichContour]  ).any():
			myindex = [math.isinf(tmp) or math.isnan(tmp) for tmp in zValues[whichContour] ].index(True)
			if (args.debug):
				print (">>> ... Remove Inf or NaN at i=%d x=%d y=%d" % (myindex,x[whichContour][myindex],y[whichContour][myindex]))
			x[whichContour].pop(myindex)
			y[whichContour].pop(myindex)
			zValues[whichContour].pop(myindex)
			pass;

		if any([math.isinf(tmp) or math.isnan(tmp) for tmp in zValues[whichContour]  ]):
			print (">>> ... Still infs or nans in %s!! This is a problem... Exiting." % whichContour)
			sys.exit(0)

	if useROOT:
		print (">>> ... Using ROOT's internal interpolation scheme (triangular).")
		print (">>> ... If you like your plot to look like a dinosaur's back or an escalator, then you're entitled to that..")


		canvas = ROOT.TCanvas("c1","c1",800,600);
		h2D    = ROOT.TH2D("h","h",200,min(x0),max(x0),200,min(y0),max(y0) );

		for whichContour in tmpListOfContours:
			graphs[whichContour] = createGraphsFromArrays(x[whichContour],y[whichContour],zValues[whichContour],whichContour)

		return graphs

	else:
		print (">>> ... Using scipy interpolate scheme (RBF).")

		xi = {}
		yi = {}
		zi = {}
		for whichContour in tmpListOfContours:
			print (">>> ... Interpolating %s"%whichContour)

			# Convert everything to numpy arrays
			xArray = np.array(x[whichContour])
			yArray = np.array(y[whichContour])
			zArray = np.array( zValues[whichContour] )

			# this scaling here equalizes the axes such that using a radial basis function makes sense!
			yScaling = np.max(xArray)/np.max(yArray) if np.max(yArray) else 1
			yArray = yArray*yScaling

			# Creating some linspaces for interpolation
			xlinspace = np.linspace(xArray.min() if args.xMin == None else args.xMin,
									xArray.max() if args.xMax == None else args.xMax,
									args.xResolution)
			ylinspace = np.linspace(yArray.min() if args.yMin == None else args.yMin,
									yArray.max() if args.yMax == None else args.yMax,
									args.yResolution)

			# Creating meshgrid for interpolation
			xymeshgrid = np.meshgrid(xlinspace,ylinspace)


			# Optional smoothing given by -s option
			smoothingFactor = 0
			if args.smoothing:
				smoothingFactor = float(args.smoothing)

			try:
				# Actual interpolation done by RBF
				if args.interpolationEpsilon:
					rbf = scipy.interpolate.Rbf(xArray, yArray, zArray, function=interpolationFunction, smooth=smoothingFactor , epsilon=args.interpolationEpsilon)
				else:
					rbf = scipy.interpolate.Rbf(xArray, yArray, zArray, function=interpolationFunction, smooth=smoothingFactor )
			except:
				print (">>> Interpolation failing!!! Check to make sure there are no NANs or double defined points in your input JSON!")
				print (">>> Printing points we're trying to interpolate (x,y,z) triplets:")

				print (sorted( zip(xArray,yArray,zArray), key = lambda x: x[0]*x[1] ))
				sys.exit(1)


			ZI = rbf(xymeshgrid[0], xymeshgrid[1])

			# Undo the scaling from above to get back to original units
			xymeshgrid[1] = xymeshgrid[1] / yScaling

			# Spit out some diagnostic plots
			if args.debug and whichContour==expectedContour and outputSurface:
				fig, ax = plt.subplots()
				plt.pcolor(xymeshgrid[0], xymeshgrid[1], ZI)
				plt.scatter(xArray, yArray, 10,zArray)
				plt.contour(xymeshgrid[0], xymeshgrid[1], ZI)

				plt.colorbar()
				fig.savefig("scipy_debug_surface.pdf")

			if whichContour==expectedContour and outputSurface:
				print (">>> Writing out expected surface to pickle file")
				with open(args.outputFile+'.expectedSurface.pkl', 'w') as outfile:
					pickle.dump({"x": xymeshgrid[0], "y": xymeshgrid[1],"z": ZI} ,outfile, pickle.HIGHEST_PROTOCOL)
			elif whichContour==observedContour and outputSurface:
				print (">>> Writing out observed surface to pickle file")
				with open(args.outputFile+'.observedSurface.pkl', 'w') as outfile:
					pickle.dump({"x": xymeshgrid[0], "y": xymeshgrid[1],"z": ZI} ,outfile, pickle.HIGHEST_PROTOCOL)

			if outputSurfaceTGraph:
				return createTGraph2DFromMeshGrid(xymeshgrid[0],xymeshgrid[1],ZI)

			# Turn this surface into contours!
			contourList = getContourPoints(xymeshgrid[0],xymeshgrid[1],ZI, args.level)

			graphs[whichContour] = []
			for contour in contourList:
				graph = ROOT.TGraph(len(contour[0]), contour[0].flatten('C'), contour[1].flatten('C') )
				if graph.Integral() > args.areaThreshold:
					graphs[whichContour].append(graph)

			# Let's sort output graphs by area so that the band construction later is more likely to get the right pairs
			graphs[whichContour] = sorted(graphs[whichContour], key=lambda g: g.Integral() , reverse=True)

		return graphs

def createTGraph2DFromArrays(x,y,z):
	"""Helper function to quickly create a TGraph2D from three python iterables"""
	from array import array
	return ROOT.TGraph2D(len(x),
		array('f',x),
		array('f',y),
		array('f',z) )

def createTGraph2DFromMeshGrid(x,y,z):

	xList = x.flatten().tolist()
	yList = y.flatten().tolist()
	zList = z.flatten().tolist()

	zList = [1e-3 if z<1e-3 else z for z in zList]

	return createTGraph2DFromArrays( xList, yList, zList )

def createTGraphFromDict(modelDict,myName,listOfFIDs=None):
	"""Given the results dictionary, can make a TGraph2D of values. Has support for fID as strings."""

	modelPoints = modelDict.keys()
	modelPointsValues = modelDict.values()

	outputGraph = ROOT.TGraph2D(len(modelPoints))
	outputGraph.SetName(myName)
	for imodel,model in enumerate(modelPoints):
		if listOfFIDs!=None:
			try:
				outputGraph.SetPoint(imodel, model[0], model[1], listOfFIDs.index( modelDict[model][myName] ) )
			except:
				print (">>> WARNING: Model point has a SR not in the list for some reason! Skipping, but check for problems in input JSON!")
				continue
		else:
			value = modelDict[model][myName] if (args.noSig or myName in ["upperLimit","expectedUpperLimit"]) else ROOT.RooStats.SignificanceToPValue(modelDict[model][myName])
			outputGraph.SetPoint(imodel, model[0], model[1], value )

	return outputGraph

def createListOfFIDs(modelDict, file=None):
	"""Given a results dictionary, construct a list of possible signal regions (fIDs) and write it to the output file"""

	modelPoints = modelDict.keys()
	modelPointsValues = modelDict.values()
	listOfFIDs = []
	for imodel,model in enumerate(modelPoints):
		if not modelDict[model]["fID"] in listOfFIDs:
			listOfFIDs.append( modelDict[model]["fID"] )
	listOfFIDs.sort()

	if file!=None:
		file.cd()
		listOfFIDsForROOT = ROOT.TObjArray()
		for fID in listOfFIDs:
			listOfFIDsForROOT.Add(ROOT.TObjString(str(fID) ) )
		listOfFIDsForROOT.Write("fIDList",ROOT.TObject.kSingleKey)
		if args.debug:
			listOfFIDsForROOT.Print("all")

	return listOfFIDs

def truncateSignificances(modelDict,sigmax=5):
	"""Truncates significance to sigmax option"""

	for model in modelDict:
		for thing in listOfContours:
			if modelDict[model][thing] > sigmax:
				modelDict[model][thing] = sigmax

	return

def createGraphsFromArrays(x,y,z,label):

	if args.debug:
		print (">>> ... In createGraphsFromArrays for %s"%label)

	gr = createTGraph2DFromArrays(x,y,z)

	hist = gr.GetHistogram().Clone(label)
	if args.smoothing:
		hist.Smooth(1, args.smoothing)

	if label in [expectedContour,observedContour]:
		hist.Write("%s_hist"%label)

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
		if contour.Integral() > args.areaThreshold:
			allGraphs.append(l)
	if biggestGraph and args.debug:
		biggestGraph.Draw("ALP")

	if args.debug:
		print (">>> ... ... Number of graphs %d"%len(allGraphs))

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

def createBandFromContours(contour1,contour2=None):

	if not contour2:
		outputGraph = contour1
	else:
		outputSize = contour1.GetN()+contour2.GetN()+1

		pointOffset = 0
		if args.closedBands:
			outputSize += 2
			pointOffset = 1

		outputGraph = ROOT.TGraph(outputSize)
		tmpx, tmpy = ROOT.Double(), ROOT.Double()
		for iPoint in xrange(contour2.GetN()):
			contour2.GetPoint(iPoint,tmpx,tmpy)
			outputGraph.SetPoint(iPoint,tmpx,tmpy)

		if args.closedBands:
			contour2.GetPoint(0,tmpx,tmpy)
			outputGraph.SetPoint(contour2.GetN()+1, tmpx,tmpy)

		for iPoint in xrange(contour1.GetN()):
			contour1.GetPoint(contour1.GetN()-1-iPoint,tmpx,tmpy)
			outputGraph.SetPoint(contour2.GetN()+pointOffset+iPoint,tmpx,tmpy)

		if args.closedBands:
			contour1.GetPoint(contour1.GetN()-1,tmpx,tmpy)
			outputGraph.SetPoint(contour1.GetN()+contour2.GetN(), tmpx,tmpy)

		contour2.GetPoint(0,tmpx,tmpy)
		outputGraph.SetPoint(contour1.GetN()+contour2.GetN()+pointOffset,tmpx,tmpy)

	outputGraph.SetFillStyle(1001);
	outputGraph.SetLineWidth(1)

	return outputGraph

if __name__ == "__main__":
	main()
