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

	return intersection(x1,y1,x2,y2)



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









import numpy as np
import matplotlib.pyplot as plt
"""
Sukhbinder
5 April 2017

from https://github.com/sukhbinder/intersection
Based on:
"""

def _rect_inter_inner(x1,x2):
    n1=x1.shape[0]-1
    n2=x2.shape[0]-1
    X1=np.c_[x1[:-1],x1[1:]]
    X2=np.c_[x2[:-1],x2[1:]]
    S1=np.tile(X1.min(axis=1),(n2,1)).T
    S2=np.tile(X2.max(axis=1),(n1,1))
    S3=np.tile(X1.max(axis=1),(n2,1)).T
    S4=np.tile(X2.min(axis=1),(n1,1))
    return S1,S2,S3,S4

def _rectangle_intersection_(x1,y1,x2,y2):
    S1,S2,S3,S4=_rect_inter_inner(x1,x2)
    S5,S6,S7,S8=_rect_inter_inner(y1,y2)

    C1=np.less_equal(S1,S2)
    C2=np.greater_equal(S3,S4)
    C3=np.less_equal(S5,S6)
    C4=np.greater_equal(S7,S8)

    ii,jj=np.nonzero(C1 & C2 & C3 & C4)
    return ii,jj

def intersection(x1,y1,x2,y2):
    """
INTERSECTIONS Intersections of curves.
   Computes the (x,y) locations where two curves intersect.  The curves
   can be broken with NaNs or have vertical segments.
usage:
x,y=intersection(x1,y1,x2,y2)
    Example:
    a, b = 1, 2
    phi = np.linspace(3, 10, 100)
    x1 = a*phi - b*np.sin(phi)
    y1 = a - b*np.cos(phi)
    x2=phi
    y2=np.sin(phi)+2
    x,y=intersection(x1,y1,x2,y2)
    plt.plot(x1,y1,c='r')
    plt.plot(x2,y2,c='g')
    plt.plot(x,y,'*k')
    plt.show()
    """
    ii,jj=_rectangle_intersection_(x1,y1,x2,y2)
    n=len(ii)

    dxy1=np.diff(np.c_[x1,y1],axis=0)
    dxy2=np.diff(np.c_[x2,y2],axis=0)

    T=np.zeros((4,n))
    AA=np.zeros((4,4,n))
    AA[0:2,2,:]=-1
    AA[2:4,3,:]=-1
    AA[0::2,0,:]=dxy1[ii,:].T
    AA[1::2,1,:]=dxy2[jj,:].T

    BB=np.zeros((4,n))
    BB[0,:]=-x1[ii].ravel()
    BB[1,:]=-x2[jj].ravel()
    BB[2,:]=-y1[ii].ravel()
    BB[3,:]=-y2[jj].ravel()

    for i in range(n):
        try:
            T[:,i]=np.linalg.solve(AA[:,:,i],BB[:,i])
        except:
            T[:,i]=np.NaN


    in_range= (T[0,:] >=0) & (T[1,:] >=0) & (T[0,:] <=1) & (T[1,:] <=1)

    xy0=T[2:,in_range]
    xy0=xy0.T
    return xy0[:,0],xy0[:,1]





if __name__ == "__main__":
	main()




