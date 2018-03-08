#!/usr/bin/env python

# multiplexContours.py #################
#
# A "multiplexer" to combine many contours (like for different SRs) using the expected CLs as the figure of merit
#
# By: Larry Lee - Mar 2018

import pickle
import ROOT
import math,sys,os,argparse
import itertools

ROOT.gROOT.SetBatch()


parser = argparse.ArgumentParser()
parser.add_argument('--inputFiles','-i', type=str, nargs='+', help='input json files', required=True)
parser.add_argument("--outputFile","-o", type = str, help="output ROOT file", default = "multiplexedContours.root")
parser.add_argument("--debug","-d",      help = "print extra debugging info", action="store_true", default=False)
parser.add_argument("--distanceThreshold", type=float, default = 1)

args = parser.parse_args()


## If I need to use scipy, please let me have scipy. I'll even help you out!
try:
	import matplotlib.pyplot as plt
	import numpy as np
	import scipy.interpolate
except:
	print ">>> You need scipy/matplotlib to run this. And you had to have run harvestToContours in scipy mode [default]"
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
			import matplotlib.pyplot as plt
			import numpy as np
			import scipy.interpolate
		except:
			print ">>> ... Setup didn't work for some reason!"
	else:
		print ">>> Quitting -- You don't have matplotlib/numpy setup and you requested mpl-based interpolation"
		sys.exit(1)

import intersection

def main():

	dict_TFiles = {}
	dict_Surfaces = {}
	dict_Exp = {}
	dict_Obs = {}

	dict_Exp_u1s = {}
	dict_Exp_d1s = {}

	dict_Obs_u1s = {}
	dict_Obs_d1s = {}


	isoExpectedContours = {}

	listOfInputFiles = [tmp.translate(None,", ") for tmp in args.inputFiles]

	for inputFileName in listOfInputFiles:
		dict_TFiles[inputFileName] = ROOT.TFile(inputFileName)
		dict_Surfaces[inputFileName] = pickle.load( open( inputFileName+".expectedSurface.pkl", "rb" ) )

		dict_Exp[inputFileName] = dict_TFiles[inputFileName].Get("Exp_0").Clone(inputFileName+"_Exp_0")
		dict_Obs[inputFileName] = dict_TFiles[inputFileName].Get("Obs_0").Clone(inputFileName+"_Obs_0")

		dict_Exp_u1s[inputFileName] = dict_TFiles[inputFileName].Get("SubGraphs/clsu1s_Contour_0").Clone(inputFileName+"_Exp_u1s")
		dict_Exp_d1s[inputFileName] = dict_TFiles[inputFileName].Get("SubGraphs/clsd1s_Contour_0").Clone(inputFileName+"_Exp_d1s")

		dict_Obs_u1s[inputFileName] = dict_TFiles[inputFileName].Get("Obs_0_Up").Clone(inputFileName+"_Obs_u1s")
		dict_Obs_d1s[inputFileName] = dict_TFiles[inputFileName].Get("Obs_0_Down").Clone(inputFileName+"_Obs_d1s")


	fig, ax = plt.subplots()

	for (region1, region2) in itertools.combinations(listOfInputFiles, 2):
		print region1, region2

		x,y = dict_Surfaces[region1]["x"], dict_Surfaces[region1]["y"]
		z1,z2 = dict_Surfaces[region1]["z"], dict_Surfaces[region2]["z"]
		cs = ax.contour(x,y,z1-z2, levels=[0] )

		isoExpectedContours[(region1,region2)] = cs.allsegs[0]


	outputFile = ROOT.TFile(args.outputFile,"RECREATE")
	outputFile.cd()


	allIsoExpectedContours = []
	for thing in isoExpectedContours:
		for otherThing in isoExpectedContours[thing]:
			allIsoExpectedContours.append( otherThing )

	for i,thing in enumerate(allIsoExpectedContours):
		convertArraysToTGraph(thing[0],thing[1]).Write("isoExpectedContour_%d"%i)

	# given a tgraph and the isoexpectedcontours
	# return a list of subcontours


	for tmpname,mygraph in dict_Exp.iteritems():
		listOfSubContours = breakUpTGraph(mygraph, allIsoExpectedContours)
		for i,thing in enumerate(listOfSubContours):
			ax.plot(thing[0],thing[1],"--")
			convertArraysToTGraph(thing[0],thing[1]).Write("Exp_%s_%d"%(tmpname,i))


	for tmpname,mygraph in dict_Obs.iteritems():
		listOfSubContours = breakUpTGraph(mygraph, allIsoExpectedContours)
		for i,thing in enumerate(listOfSubContours):
			ax.plot(thing[0],thing[1])
			convertArraysToTGraph(thing[0],thing[1]).Write("Obs_%s_%d"%(tmpname,i))


	for tmpname,mygraph in dict_Exp_d1s.iteritems():
		listOfSubContours = breakUpTGraph(mygraph, allIsoExpectedContours)
		for i,thing in enumerate(listOfSubContours):
			ax.plot(thing[0],thing[1],alpha=0.5)
			convertArraysToTGraph(thing[0],thing[1]).Write("Exp_d1s_%s_%d"%(tmpname,i))

	for tmpname,mygraph in dict_Exp_u1s.iteritems():
		listOfSubContours = breakUpTGraph(mygraph, allIsoExpectedContours)
		for i,thing in enumerate(listOfSubContours):
			ax.plot(thing[0],thing[1],alpha=0.5)
			convertArraysToTGraph(thing[0],thing[1]).Write("Exp_u1s_%s_%d"%(tmpname,i))


	for tmpname,mygraph in dict_Obs_d1s.iteritems():
		listOfSubContours = breakUpTGraph(mygraph, allIsoExpectedContours)
		for i,thing in enumerate(listOfSubContours):
			ax.plot(thing[0],thing[1],":",alpha=0.5)
			convertArraysToTGraph(thing[0],thing[1]).Write("Obs_d1s_%s_%d"%(tmpname,i))

	for tmpname,mygraph in dict_Obs_u1s.iteritems():
		listOfSubContours = breakUpTGraph(mygraph, allIsoExpectedContours)
		for i,thing in enumerate(listOfSubContours):
			ax.plot(thing[0],thing[1],":",alpha=0.5)
			convertArraysToTGraph(thing[0],thing[1]).Write("Obs_u1s_%s_%d"%(tmpname,i))



	fig.savefig("test_%s_%s.pdf"%(region1,region2))

	outputFile.Write()
	outputFile.Close()

	return

def convertTGraphToArrays(mygraph):
	size = mygraph.GetN()
	x1buffer = mygraph.GetX()
	y1buffer = mygraph.GetY()

	x1 = np.array([ x1buffer[i]  for i in range(size) ])
	y1 = np.array([ y1buffer[i]  for i in range(size) ])

	return (x1,y1)

def convertArraysToTGraph(x,y):
	mygraph = ROOT.TGraph(len(x))
	for iPoint,(x,y) in enumerate(zip(x,y)):
		mygraph.SetPoint(iPoint,x,y)
	return mygraph

def findIntersectionTGraphArray(mygraph, myarray):

	x1,y1 = convertTGraphToArrays(mygraph)

	x2 = myarray[:,0]
	y2 = myarray[:,1]

	return intersection.intersection(x1,y1,x2,y2)



def splitUpContour(x,y,listOfBreakPoints):
	listOfSplitContours = []
	tmpx = []
	tmpy = []

	points = zip(x,y)
	for iPoint in xrange(len(points)-1 ):
		p1 = points[iPoint]
		p2 = points[iPoint+1]

		tmpx.append(p1[0])
		tmpy.append(p1[1])

		shouldBreakHere = False
		newPoint = (0,0)
		for breakingPoint in listOfBreakPoints:
			pbreak = (breakingPoint[0],breakingPoint[1])
			print breakingPoint
			tmpDistance = dist(p1[0],p1[1],p2[0],p2[1], breakingPoint[0],breakingPoint[1])
			if args.debug:
				print "Distance to intersection: %f"%tmpDistance
			if tmpDistance<args.distanceThreshold:
				print "breaking up contour at %f,%f"%(breakingPoint[0],breakingPoint[1])
				shouldBreakHere = True
				newPoint = (breakingPoint[0],breakingPoint[1])

		if shouldBreakHere:
			tmpx.append(newPoint[0])
			tmpy.append(newPoint[1])
			listOfSplitContours.append( (tmpx,tmpy) )

			tmpx = [newPoint[0]]
			tmpy = [newPoint[1]]

	listOfSplitContours.append( (tmpx,tmpy) )

	return listOfSplitContours

def dist(x1,y1, x2,y2, x3,y3): # x3,y3 is the point
    px = x2-x1
    py = y2-y1

    something = px*px + py*py

    u =  ((x3 - x1) * px + (y3 - y1) * py) / float(something)

    if u > 1:
        u = 1
    elif u < 0:
        u = 0

    x = x1 + u * px
    y = y1 + u * py

    dx = x - x3
    dy = y - y3

    dist = math.sqrt(dx*dx + dy*dy)

    return dist


def breakUpTGraph(graph, isoExpectedContours):
		intersectionPoints = []

		for thisIsoExpectedCurve in isoExpectedContours:
			thisIntersection = findIntersectionTGraphArray( graph , thisIsoExpectedCurve )
			for myItem in zip(thisIntersection[0],thisIntersection[1]):
				intersectionPoints.append(myItem)

		if len(intersectionPoints)==0:
			return []
		x,y = convertTGraphToArrays(graph)
		listOfSubContours = splitUpContour(x,y,intersectionPoints)

		return listOfSubContours



if __name__ == "__main__":
	main()




