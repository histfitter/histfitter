#!/usr/bin/env python

# harvestToContours.py #################
#
# An attempt to unify contour production so we don't have a million attempts to reinvent a broken wheel...
#
# Reads in a harvest list from the HF output in either text file or json formats (but c'mon.. use json.. what are you doing?)
# Then the CLs values are interpreted as p-values and converted to significances and then interpolated
# Interpolation of significance surface can be configured to e.g. linear, cubic (options from scipy.interpolate)
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
parser.add_argument("--interpolation",   type=str, help="type of interpolation for scipy. e.g. linear, cubic, etc", default = "linear") # linear, multiquadric
parser.add_argument("--level",           type=float, help="contour level output. Default to 95% CL", default = ROOT.RooStats.PValueToSignificance( 0.05 ))
parser.add_argument("--useROOT","-r", help="use the root interpolation engine instead of mpl", action="store_true", default=False)

parser.add_argument("--sigmax",          type=float, help="maximum significance in sigmas", default = 5.0)

parser.add_argument("--xVariable","-x",  type=str, default = "mg" )
parser.add_argument("--yVariable","-y",  type=str, default = "mlsp" )

parser.add_argument("--fixedParamsFile","-f", type=str, help="give a json file with key=variable and value=value. e.g. use for pinning down third parameter in harvest list", default="constraints.json")

args = parser.parse_args()

if not args.useROOT:

	import matplotlib as mpl
	mpl.use('pdf')

	import matplotlib.pyplot as plt
	import numpy as np
	import scipy.interpolate

	from matplotlib.mlab import griddata



def main():
	"""Main function for driving the whole thing..."""

	# Step 1 - Read in harvest list in either text or json format and dump it into a dictionary
	tmpdict = harvestToDict( args.inputFile )

	# addZerosToDict(tmpdict,maxyvalue = 0)

	# Step 2 - Interpolate the fit results
	print ">>> Interpolating mass plane"
	outputGraphs = interpolateMassPlane( tmpdict , args.interpolation , args.x, args.y)

	f = ROOT.TFile(args.outputFile,"recreate")

	print ">>> Writing contours out"
	# Step 3 - get TGraph contours
	for whichEntry in ["CLs","CLsexp","clsu1s","clsu2s","clsd1s","clsd2s"]:
		try:
			outputGraphs[whichEntry].Write("%s_Contour"%(whichEntry))
		except:
			print "well that one's no good... - %s"%whichEntry


	canvas = ROOT.TCanvas("FinalCurves","FinalCurves")
	outputGraphs["CLs"].Draw("AL")
	for whichEntry in ["CLsexp","clsu1s","clsd1s"]:
		outputGraphs[whichEntry].SetLineStyle(7)
		outputGraphs[whichEntry].Draw("L")
	outputGraphs["CLs"].SetMinimum(0)
	outputGraphs["CLs"].SetMaximum(400)

	canvas.SaveAs("FinalCurves.pdf")
	print ">>> Closing file"

	f.Write()
	f.Close()


def harvestToDict( harvestInputFileName = "" ):
	"""This parses the input file into a dictionary object for simpler handling"""
	print ">>> entering harvestToDict()"

	massPlaneDict = {}

	harvestInput = open(harvestInputFileName,"r")

	constraintsDict = {}
	if args.fixedParamsFile:
		with open(args.fixedParamsFile) as inputFixedParamsFile:
			inputFixedParamsJSON = json.load(inputFixedParamsFile)
			# print inputFixedParamsJSON
			constraintsDict = inputFixedParamsJSON

	if ".json" in harvestInputFileName:
		print ">>> >>> Interpreting json file %s"%harvestInputFileName

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
					massPlaneDict[sampleParams] = {
						"CLs":        ( ROOT.RooStats.PValueToSignificance( float(sample["CLs"])     )  ),
						"CLsexp":     ( ROOT.RooStats.PValueToSignificance( float(sample["CLsexp"])  )  ),
						"clsu1s":     ( ROOT.RooStats.PValueToSignificance( float(sample["clsu1s"])  )  ),
						"clsu2s":     ( ROOT.RooStats.PValueToSignificance( float(sample["clsu2s"])  )  ),
						"clsd1s":     ( ROOT.RooStats.PValueToSignificance( float(sample["clsd1s"])  )  ),
						"clsd2s":     ( ROOT.RooStats.PValueToSignificance( float(sample["clsd2s"])  )  ),
					}

				else:
					if not sampleParams in massPlaneDict:
						massPlaneDict[sampleParams] = {
							"CLs":        args.sigmax,
							"CLsexp":     args.sigmax,
							"clsu1s":     args.sigmax,
							"clsu2s":     args.sigmax,
							"clsd1s":     args.sigmax,
							"clsd2s":     args.sigmax,
						}
				print sampleParams, float(sample["CLs"]), ROOT.RooStats.PValueToSignificance( float(sample["CLs"])     )


	else:
		print ">>> Interpreting text file"


		try:
			from summary_harvest_tree_description import treedescription
			# from summary_harvest_tree_description_MEffRJRCombine import treedescription
			dummy,fieldNames = treedescription()
			fieldNames = fieldNames.split(':')
		except:
			print "Crash and burn -- I need a harvest tree description file!"
			sys.exit(0)

		for massLine in harvestInput.readlines():
			values = massLine.split()
			values = dict(zip(fieldNames, values))

			# print values["fID/F"]

			if "m12/F" in values:
				massPoint = (  float(values["m0/F"])  , float(values["m12/F"])   )
			elif "mgluino/F" in values:
				massPoint = (  float(values["mgluino/F"])  , float(values["mlsp/F"])   )
			elif "msquark/F" in values:
				massPoint = (  float(values["msquark/F"])  , float(values["mlsp/F"])   )


			massPlaneDict[massPoint] = {
				"CLs":        ROOT.RooStats.PValueToSignificance( float(values["CLs/F"])     ) ,
				"CLsexp":     ROOT.RooStats.PValueToSignificance( float(values["CLsexp/F"])  ) ,
				"clsu1s":     ROOT.RooStats.PValueToSignificance( float(values["clsu1s/F"])  ) ,
				"clsu2s":     ROOT.RooStats.PValueToSignificance( float(values["clsu2s/F"])  ) ,
				"clsd1s":     ROOT.RooStats.PValueToSignificance( float(values["clsd1s/F"])  ) ,
				"clsd2s":     ROOT.RooStats.PValueToSignificance( float(values["clsd2s/F"])  ) ,
			}

			print massPoint, ROOT.RooStats.PValueToSignificance( float(values["CLs/F"])     )

	return massPlaneDict


def addZerosToDict(mydict, maxyvalue = 0):
	# for tau in np.linspace( -0.5,-0.4, 2 ):
	#   for mg in np.linspace(0,2000,100):
	#     mydict[(mg,100,tau)] = {
	#         "CLs":    ROOT.RooStats.PValueToSignificance( 0.005 ),
	#         "CLsexp": ROOT.RooStats.PValueToSignificance( 0.005 ),
	#         "clsu1s": ROOT.RooStats.PValueToSignificance( 0.005 ),
	#         "clsu2s": ROOT.RooStats.PValueToSignificance( 0.005 ),
	#         "clsd1s": ROOT.RooStats.PValueToSignificance( 0.005 ),
	#         "clsd2s": ROOT.RooStats.PValueToSignificance( 0.005 ),
	#       }

	# for x in np.linspace( -2,2, 50 ):
	#   for mg in xrange(100,1800,100):
	#     mydict[(mg,100,x)] = {
	#         "CLs":    0.0001,
	#         "CLsexp": 0.0001,
	#         "clsu1s": 0.0001,
	#         "clsu2s": 0.0001,
	#         "clsd1s": 0.0001,
	#         "clsd2s": 0.0001,
	#       }


	# if maxyvalue:
	#   for x in np.linspace( 0, 2000, 100 ):
	#     mydict[(x,maxyvalue)] = {
	#         "CLs":    0,
	#         "CLsexp": 0,
	#         "clsu1s": 0,
	#         "clsu2s": 0,
	#         "clsd1s": 0,
	#         "clsd2s": 0,
	#       }

	pass
	# return mydict


def interpolateMassPlane(massPlaneDict = {}, interpolationFunction = "linear", xindex = 0, yindex = 1):
	"""The actual interpolation"""

	massPoints = massPlaneDict.keys()
	massPointsValues = massPlaneDict.values()

	# print xindex, yindex
	# print massPoints

	x0 =   list( zip( *massPoints )[xindex] )
	y0 =   list( zip( *massPoints )[yindex] )


	canvas = ROOT.TCanvas("c1","c1",800,600);
	h2D    = ROOT.TH2D("h","h",200,min(x0),max(x0),200,min(y0),max(y0) );

	#print  massPoints;
	#print  massPointsValues;

	zValues = {} # entry x points
	x={} # entry x points
	y={} # entry x points

	graphs = {}

	for whichEntry in ["CLs","CLsexp","clsu1s","clsu2s","clsd1s","clsd2s"]:
		zValues[whichEntry] = [ tmpEntry[whichEntry] for tmpEntry in massPointsValues]
		x[whichEntry]       = [ a for a in x0 ];
		y[whichEntry]       = [ a for a in y0 ];
		graphs[whichEntry] = turnAJunkIntoAGraph(x[whichEntry],y[whichEntry],zValues[whichEntry],whichEntry)
		pass;

	# print zValues["CLsexp"]



	return graphs



	# # remove inf point in each entry
	# for whichEntry in ["CLs","CLsexp","clsu1s","clsu2s","clsd1s","clsd2s"]:

	#   if np.isinf( zValues[whichEntry]  ).any():
	#     print "infs in %s!" % whichEntry;
	#     pass;

	#   while np.isinf( zValues[whichEntry]  ).any():
	#     myindex = np.isinf( zValues[whichEntry]  ).tolist().index(True)
	#     print "remove i=%d x=%d x=%d" % (myindex,x[whichEntry][myindex],y[whichEntry][myindex])
	#     x[whichEntry].pop(myindex)
	#     y[whichEntry].pop(myindex)
	#     zValues[whichEntry].pop(myindex)
	#     pass;

	#   if np.isinf( zValues[whichEntry]  ).any():
	#     print "still infs in %s!" % whichEntry
	#     pass;

	#   pass;
 
	# # for i in xrange(len(zValues["CLs"]) ):
	# #   if i-1 > len(zValues["CLs"]):
	# #     break
	# #   if np.isinf(zValues["CLs"][i]):
	# #     x.pop(i)
	# #     y.pop(i)
	# #     for k,v in zValues.iteritems():
	# #       zValues[k].pop(i)
	# #     i = i-1


	# # """
	# # to check value in zValues
	# for whichEntry in ["CLs","CLsexp","clsu1s","clsu2s","clsd1s","clsd2s"]:
	#   for i in range(len(x[whichEntry])):
	#     mass1 = x[whichEntry][i];
	#     mass2 = y[whichEntry][i];
	#     z = zValues[whichEntry][i];
	#     print "(%.2f,%.2f)" % (mass1,mass2) , z;
	#     h2D.SetBinContent(h2D.GetXaxis().FindBin(mass1),h2D.GetYaxis().FindBin(mass2),z);
	#     pass;
	#   h2D.Draw("colz");
	#   # h2D.Draw("c same");
	#   # ROOT.gPad.SetLogx()
	#   canvas.SaveAs("input_harvest_"+whichEntry+".pdf");
	#   pass;
	# # """

	# xi = {}
	# yi = {}
	# zi = {}
	# for whichEntry in ["CLs","CLsexp","clsu1s","clsu2s","clsd1s","clsd2s"]:
	#   print ">>>> Interpolating %s"%whichEntry;
	#   xArray = np.array(x[whichEntry]);
	#   yArray = np.array(y[whichEntry]);
	#   zValuesArray = np.array( zValues[whichEntry] );

	#   n = []
	#   for i in xrange(len(x[whichEntry]) ):
	#     n.append( (xArray[i], yArray[i],zValuesArray[i]) )

	#   n = np.array(n)
	#   # print n



	#   # get xi, yi
	#   xi[whichEntry], yi[whichEntry] = np.linspace(xArray.min(), xArray.max(), 100), np.linspace(yArray.min(), yArray.max(), 100);
	#   xi[whichEntry], yi[whichEntry] = np.meshgrid(xi[whichEntry], yi[whichEntry]);

	#   # print xi[whichEntry]
	#   # print scipy.interpolate.griddata(n[:,0:2], n[:,2], [(1,1500), (1.2, 1500)], method='linear')
	#   zi[whichEntry] = griddata(xArray, yArray, zValuesArray, xi[whichEntry], yi[whichEntry], interp='linear')


	#   # interpolate and get zi
	#   # print "size of (x,y,z) = (%d,%d,%d)" % (len(x[whichEntry]), len(y[whichEntry]), len(zValues[whichEntry]));
	#   # rbf = LSQ_Rbf(x[whichEntry], y[whichEntry], zValues[whichEntry], function=interpolationFunction, smooth=0.1);
	#   # print "setting zi";
	#   # zi[whichEntry] = rbf(xi[whichEntry], yi[whichEntry]);
	#   # print zi[whichEntry]
	#   pass;

	# return (xi,yi,zi);
	# # return (x,y,zValues)



def turnAJunkIntoAGraph(x,y,z,label):

	from array import array

	gr = ROOT.TGraph2D(len(x),
		array('f',x),
		array('f',y),
		array('f',z) )

	hist = gr.GetHistogram().Clone()

	canvas = ROOT.TCanvas("turnAJunkDiagnostic","turnAJunkDiagnostic")
	hist.Draw("colz")
	# gr.Draw("P0 TRI1")
	for i in xrange(5):
		hist.Smooth(1,"k5b")
	canvas.SaveAs("underlyingHist_%s.pdf"%label)

	hist.SetContour(1)
	# hist.SetContourLevel(0,9.)
	hist.SetContourLevel(0,ROOT.RooStats.PValueToSignificance( 0.05 ))
	# print ROOT.RooStats.PValueToSignificance( 0.05 )
	ROOT.SetOwnership(hist,0)
	hist.Draw("CONT LIST")
	ROOT.gPad.Update()
	outputContours = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
	# print len(outputContours.At(0))
	maxIntegral = 0
	biggestGraph = 0
	for contour in outputContours.At(0):
		# print contour
		l = contour.Clone()
		ROOT.SetOwnership(l,0)
		# print l
		# print outputContours
		# print biggestGraph.GetN()
		l.Draw("ALP")
		# print contour.Integral()
		if contour.Integral() > maxIntegral:
			maxIntegral = contour.Integral()
			biggestGraph = contour.Clone()
	if biggestGraph:
		biggestGraph.Draw("ALP")
	# print maxIntegral
	# ROOT.gPad.SetLogx()
	canvas.SaveAs("gr_%s.pdf"%label)
	return biggestGraph
	# pass


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



class LSQ_Rbf(scipy.interpolate.Rbf):

		def __init__(self, *args, **kwargs):
				self.xi = np.asarray([np.asarray(a, dtype=float).flatten()
													 for a in args[:-1]])
				self.N = self.xi.shape[-1]
				self.di = np.asarray(args[-1]).flatten()

				if not all([x.size == self.di.size for x in self.xi]):
						raise ValueError("All arrays must be equal length.")

				self.norm = kwargs.pop('norm', self._euclidean_norm)
				r = self._call_norm(self.xi, self.xi)
				self.epsilon = kwargs.pop('epsilon', None)
				if self.epsilon is None:
						self.epsilon = r.mean()
				self.smooth = kwargs.pop('smooth', 0.0)

				self.function = kwargs.pop('function', 'multiquadric')

				# attach anything left in kwargs to self
				#  for use by any user-callable function or
				#  to save on the object returned.
				for item, value in kwargs.items():
						setattr(self, item, value)

				print "init_function - eye*smooth"
				self.A = self._init_function(r) - np.eye(self.N)*self.smooth
				# use linalg.lstsq rather than linalg.solve to deal with
				# overdetermined cases
				print "linalg.lstsq"
				self.nodes = np.linalg.lstsq(self.A, self.di)[0]
				print "End of LSQ_Rbf initialization"


if __name__ == "__main__":
	main()
