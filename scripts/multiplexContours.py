#!/usr/bin/env python

# multiplexContours.py #################
#
# A "multiplexer" to combine many contours (like for different SRs) using the expected CLs as the figure of merit
#
# By: Larry Lee - Mar 2018
# Updated in June 2020 by Jonathan Long

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pickle
import ROOT
import math,sys,os,argparse
import itertools
import copy

ROOT.gROOT.SetBatch()


parser = argparse.ArgumentParser()
parser.add_argument('--inputFiles','-i', type=str, nargs='+', help='input json files', required=True)
parser.add_argument("--outputFile","-o", type = str, help="output ROOT file", default = "multiplexedContours.root")
parser.add_argument("--debug","-d",      help = "print extra debugging info", action="store_true", default=False)
parser.add_argument("--skipTheory", action="store_true", help="Skip theory variations")
parser.add_argument("--plotUsedContours", "-p", action="store_true", help="Generate a plot of the used contours.")
parser.add_argument("--ignoreInteriorLines", action="store_true", help="Ignore subRegions that are contained in the total expected. ")
parser.add_argument("--noSubRegionMerge", action="store_false", help="Do not merge split subregions.")
parser.add_argument("--showPastLimit", action="store_true", help="Show the best expected region past the limit when using --plotUsedContours.")
parser.add_argument("--minArea", type=float, default=-1, help="Remove subregions below this area.  Helps to remove very small subRegions by setting this to 1.")


args = parser.parse_args()

## If I need to use scipy, please let me have scipy. I'll even help you out!
try:
    import matplotlib as mpl
    mpl.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.lines import Line2D
    import numpy as np
    import scipy.interpolate

    from shapely.ops import cascaded_union, polygonize, split, unary_union
    from shapely.geometry import Polygon,MultiPolygon
    from shapely.geometry import LineString, Point
    from shapely.geometry.collection import GeometryCollection
    from shapely import affinity
    from shapely.geometry.base import BaseMultipartGeometry

except:
    print (">>> You need scipy/matplotlib and shapely to run this. And you had to have run harvestToContours in scipy mode [default]")
    print (">>> In an ATLAS environment, you can...")
    print ('>>> > lsetup "views LCG_94 x86_64-centos7-gcc62-opt" # or replace with a newer LCG release or more appropriate arch')
    print (">>> ")
    print (">>> Try that and then run this again!")
    sys.exit(1)


def main():

    print (">>> Launching multiplexContours.py! ")


    dict_TFiles = {}
    dict_Surfaces = {}
    dict_rbf_Surf = {}
    dict_Exp = {}
    dict_Obs = {}

    dict_Exp_u1s = {}
    dict_Exp_d1s = {}

    dict_Obs_u1s = {}
    dict_Obs_d1s = {}


    isoExpectedContours = {}

    listOfInputFiles = [tmp.translate(None,", ") for tmp in args.inputFiles]

    print (">>> Grabbing input information from input files:")
    print (">>> >>> " + " ".join(listOfInputFiles))
    print (">>> ")
    print (">>> FYI, I'm also going to grab the *.expectedSurface.pkl files that should be in the same location")


    for inputFileName in listOfInputFiles:
        dict_TFiles[inputFileName] = ROOT.TFile(inputFileName)
        try:
            dict_Surfaces[inputFileName] = pickle.load( open( inputFileName+".expectedSurface.pkl", "rb" ) )            
        except FileNotFoundError:
            print (">>> I need those *.expectedSurface.pkl files that are produced from harvestToContours! Exiting...")
            sys.exit(1)

        dict_Exp[inputFileName] = dict_TFiles[inputFileName].Get("Exp_0").Clone(inputFileName+"_Exp_0")
        dict_Obs[inputFileName] = dict_TFiles[inputFileName].Get("Obs_0").Clone(inputFileName+"_Obs_0")

        dict_Exp_u1s[inputFileName] = dict_TFiles[inputFileName].Get("SubGraphs/clsu1s_Contour_0").Clone(inputFileName+"_Exp_u1s")
        dict_Exp_d1s[inputFileName] = dict_TFiles[inputFileName].Get("SubGraphs/clsd1s_Contour_0").Clone(inputFileName+"_Exp_d1s")

        if not args.skipTheory:
            dict_Obs_u1s[inputFileName] = dict_TFiles[inputFileName].Get("Obs_0_Up").Clone(inputFileName+"_Obs_u1s")
            dict_Obs_d1s[inputFileName] = dict_TFiles[inputFileName].Get("Obs_0_Down").Clone(inputFileName+"_Obs_d1s")

    print (">>> Creating output ROOT file: %s"%args.outputFile)

    outputFile = ROOT.TFile(args.outputFile,"RECREATE")

    fig, ax = plt.subplots()

    print (">>> Creating iso expected contours for all pairwise combinations of SRs")

    # Loop over combinations of input files and grab coordinates from surfances in pkl files
    # Thanks to Luigi Longo for the more comprehensive input checks
    for (region1, region2) in itertools.combinations(listOfInputFiles, 2):
        #x,y = dict_Surfaces[region1]["x"], dict_Surfaces[region1]["y"]
        #z1,z2 = dict_Surfaces[region1]["z"], dict_Surfaces[region2]["z"]
        #cs = ax.contour(x,y,z1-z2, ":", levels=[0] ) # this creates contours where the two surfaces have the same Z value
        #          
        #isoExpectedContours[(region1,region2)] = cs.allsegs[0] # grab list of arrays of coords of intersection contour

        x,y = dict_Surfaces[region1]["x"], dict_Surfaces[region1]["y"]
        
        # Used to check that regions have same grid
        x_ref = dict_Surfaces[region2]['x']
        y_ref = dict_Surfaces[region2]['y']
        
        # Input checks
        if len(x) == len(x_ref) and len(y) == len(y_ref):
            if len(x)>0 and len(y)>0:
                if len(x[0]) == len(x_ref[0]) and len(y[0]) == len(y_ref[0]):
                    if ( np.isclose(x_ref,x).all() and np.isclose(y_ref,y).all() ):
                        z1,z2 = dict_Surfaces[region1]["z"], dict_Surfaces[region2]["z"]
                        cs = ax.contour(x,y,z1-z2, ":", levels=[0] ) # this creates contours where the two surfaces have the same Z value
                  
                        isoExpectedContours[(region1,region2)] = cs.allsegs[0] # grab list of arrays of coords of intersection contour
                    else:
                        if not np.isclose(x_ref,x).all():
                            print ("X for %s from: %f to %f" % (region1, x[0][0],y[-1][0]))
                            print ("X for %s from: %f to %f" % (region2, x_ref[0][0],x_ref[-1][0]))
                        if not np.isclose(y_ref,y).all():
                            print ("Y for %s from: %f to %f" % (region1, y[0][0],y[-1][0]))
                            print ("Y for %s from: %f to %f" % (region2, y_ref[0][0],y_ref[-1][0]))
                  
                        print(">>> Error, inputs are not close.  %s is different"%(region1))
                        sys.exit(1)
                
                else:
                    print(">>> Error, inputs must use same x and y limits and resolution in harvest contours.  %s is different"%(region1))
                    sys.exit(1)

    ax.cla()

    uncutRegions = {} # dictionary of all contours for each region

    bestRegions = {}
    
    # Retrieve and convert tgraphs of various contours into polygons
    for inputFileName in listOfInputFiles:
        region = {}

        region["Exp"]     = tGraphToPolygon(dict_Exp[inputFileName])
        region["Exp_u1s"] = tGraphToPolygon(dict_Exp_u1s[inputFileName])
        region["Exp_d1s"] = tGraphToPolygon(dict_Exp_d1s[inputFileName])
        region["Obs"]     = tGraphToPolygon(dict_Obs[inputFileName])
        if not args.skipTheory:
            region["Obs_u1s"] = tGraphToPolygon(dict_Obs_u1s[inputFileName])
            region["Obs_d1s"] = tGraphToPolygon(dict_Obs_d1s[inputFileName])

        uncutRegions[inputFileName] = region

        bestRegions[inputFileName] = list()

    sumOfExpecteds = cascaded_union([polygons["Exp"] for regionName,polygons in uncutRegions.iteritems()]) # geometric union of all expected contours
    
    sumOfContours = copy.deepcopy(sumOfExpecteds)
    for key in ["Exp_u1s", "Exp_d1s", "Obs"] + (["Obs_u1s","Obs_d1s"] if not args.skipTheory else []):
        
        sumOfContours = cascaded_union([polygons[key] for regionName,polygons in uncutRegions.iteritems()] + [sumOfContours]) # geometric union of all expected contours


    sumOfExpectedsArea = sumOfExpecteds.area

    if args.debug:
        print (">>> Number of regions being added to the best expected contour: %d"%len(uncutRegions) )
        print (">>> Integral of the best expected contour: %d"%sumOfExpecteds.area)

        x,y = sumOfExpecteds.exterior.coords.xy
        convertArraysToTGraph(x,y).Write("debug_sumOfExpecteds")
        ax.cla()
        ax.plot(x,y,alpha=0.5)
        fig.savefig("debug_sumOfExpecteds.pdf")

        for i,singleExpectedCurve in enumerate([v["Exp"] for k,v in uncutRegions.iteritems()]):
            x,y = singleExpectedCurve.exterior.coords.xy
            ax.cla()
            ax.plot(x,y,alpha=0.5)
            fig.savefig("debug_singleExpected_%d.pdf"%i)


    allIsoExpectedContours = []
    allIsoExpectedContoursLineStrings = []
    allIsoExpectedContours_regionName = []
    for two_region_tuple in isoExpectedContours:

        for intersectionContour in isoExpectedContours[two_region_tuple]:
            # JDL: couldn't this be a list of arrays?

            ## Better handling of bad geometries like splitting overlapping lines.  Not sure it's always needed, but did fix a crash on a complicated test
            if False:
                try:
                    if Polygon(intersectionContour).is_valid:                
                        tmpLineString = LineString(intersectionContour)
                        if args.ignoreInteriorLines:                            
                            if tmpLineString.within(sumOfExpecteds): # check if intersection contour is completely within sum of expecteds
                                continue
                
                        allIsoExpectedContours.append( intersectionContour )
                        allIsoExpectedContoursLineStrings.append( tmpLineString )
                
                    else:
                
                        ls_temp = LineString(intersectionContour)
                        lr = LineString(ls_temp.coords[:]+ls_temp.coords[0:1])
                
                        mls = unary_union(lr)
                
                        for ls in mls:
                            allIsoExpectedContours.append(intersectionContour)
                            allIsoExpectedContoursLineStrings.append(ls)
                
                except ValueError:
                    print(">>> Failed to handle an intersection contour")
                    continue
                
            else:
                tmpLineString = LineString(intersectionContour)
                if args.ignoreInteriorLines:
                    if tmpLineString.within(sumOfExpecteds): # check if intersection contour is completely within sum of expecteds
                        continue
                allIsoExpectedContours.append( intersectionContour )
                allIsoExpectedContoursLineStrings.append( tmpLineString )

    # Add cut lines of the input expectected contours.  This helps with irregularities in the final expectected contour seen in a test with EWK comb contours
    for regionName,polygons in uncutRegions.iteritems():
        allIsoExpectedContoursLineStrings.append( LineString(polygons["Exp"].exterior.coords) )


    if args.debug:
        ax.cla()
        x,y = sumOfExpecteds.exterior.xy
        ax.plot(x,y,linewidth=1,color='k') 
        for ls in allIsoExpectedContoursLineStrings:
            x,y = ls.coords.xy
            ax.plot(x,y,linewidth=2,color=np.random.rand(3,),linestyle=":")
        fig.savefig("debug_allEICs.pdf")

    
    print (">>> Total number of isoExpectedContours: %d"%len(allIsoExpectedContoursLineStrings))

    listOfBestCurves = {}

    for tmpKey in uncutRegions[inputFileName]:
        listOfBestCurves[tmpKey] = []

    print (">>> Cutting space up into regions based on iso expected contours")

    # Cut up the union of contours into individual parts
    allIsoExpectedContoursLineStrings = sorted(allIsoExpectedContoursLineStrings, key=lambda x: x.length, reverse=True)

    # Cut up a the sum of all contours
    subRegions = [sumOfContours]
        
    for cutLine in allIsoExpectedContoursLineStrings: # loop over all cuts, i.e. iso contours
        tmpSubRegions = []
        for subRegion in subRegions: # apply cut to each subRegion

            # special case of interior circle that doesn't split properly.  Only really needed for looking at usedContour figure
            if subRegion.contains(cutLine) and not cutLine.is_ring and len(cutLine.coords) > 2:
                x_start, y_start = cutLine.coords[0:1][0][0], cutLine.coords[0:1][0][1]
                x_end, y_end = cutLine.coords[-2:-1][0][0], cutLine.coords[-2:-1][0][1]
                x_end2, y_end2 = cutLine.coords[-3:-2][0][0], cutLine.coords[-3:-2][0][1]
                
                dist_close = math.sqrt((x_start-x_end)**2 + (y_start- y_end)**2 )
                dist_neighbor = math.sqrt((x_end2-x_end)**2 + (y_end2- y_end)**2 )

                # if closing the line requires a jump not greater than 1.5x the distance in the 2nd to last point, try it
                if abs(dist_close-dist_neighbor)/dist_neighbor < 1.5:
                    cutLine = LineString(cutLine.coords[:]+cutLine.coords[0:1])

            tmpGeoms = split(subRegion, cutLine)
            tmpSubRegions.extend(tmpGeoms)
        subRegions = tmpSubRegions


    if args.debug:
        print (">>> Number of regions in this plane: %d"%len(subRegions))

    if args.debug: # JDL
        ax.cla()
        for i,poly in enumerate(subRegions):
            x,y = poly.exterior.xy
            ax.plot(x,y,linewidth=2,color=np.random.rand(3,),linestyle=":")
        x,y = sumOfExpecteds.exterior.xy
        ax.plot(x,y,linewidth=1,color='k')
        fig.savefig("debug_CutUpExpected.pdf")



    # Gather points to do interpretation only once
    ZI_reg_dict = {}
    interiorPoints = []
    for subRegion in subRegions:
        x_cent,y_cent = subRegion.representative_point().xy
        interiorPoints.append(([x_cent[0], y_cent[0]]))
    
    for regionName,region in uncutRegions.iteritems():
        x,y = dict_Surfaces[regionName]["x"], dict_Surfaces[regionName]["y"]
        z = dict_Surfaces[regionName]["z"]
        ZI_reg_dict[regionName] = scipy.interpolate.griddata( (x.flatten(), y.flatten()), z.flatten(), interiorPoints, method="linear" )


    # Fill list of best SR per subRegion
    subRegion_SR_dict = {}
    for iSubRegion,subRegion in enumerate(subRegions):
        bestSR = ""
        bestZvalue = -100 
    

        # See if the test point is inside of an expected curve
        interiorPoint = Point(interiorPoints[iSubRegion])
        isInExpecteds = sumOfExpecteds.contains(interiorPoint)

        if isInExpecteds: # only consider SRs where point is in expected
            for regionName,region in uncutRegions.iteritems():
                if region["Exp"].contains(interiorPoint):
                    ZI = ZI_reg_dict[regionName][iSubRegion]        
                    
                    if ZI > bestZvalue:
                        bestZvalue = ZI
                        bestSR = regionName            
        else: # just go through and find the best point
            for regionName,region in uncutRegions.iteritems():
                ZI = ZI_reg_dict[regionName][iSubRegion]        
            
                if ZI > bestZvalue:
                    bestZvalue = ZI
                    bestSR = regionName

        subRegion_SR_dict[subRegion.area]=bestSR

    nSubRegionsPre = len(subRegions)

    # Merge subregions, speeds up later steps
    if args.noSubRegionMerge:
        i = 0
        while i < len(subRegions):
            subRegion = subRegions[i]
        
            match = False
            for j,sR in enumerate(subRegions):
                if i==j: continue
                if  (doPolygonsTouch(subRegion,sR) or subRegion.contains(sR) or sR.contains(subRegion)) and subRegion_SR_dict[subRegion.area] == subRegion_SR_dict[sR.area]: # do Polygons touch or does one contain the other and have the same assigned SR
                    newPoly = cascaded_union([subRegion, sR])
                    
                    if type(newPoly) == MultiPolygon: continue # Even though they shouldn't, don't merge things that don't form a single polygon

                    subRegions.remove(subRegion)
                    subRegions.remove(sR)
                    subRegions.append(newPoly)

                    subRegion_SR_dict[newPoly.area] = subRegion_SR_dict[subRegion.area]
                    match=True
                    break
            if not match:
                i+=1
        print(">>> Number of subRegions reduced from %d to %d"%(nSubRegionsPre,len(subRegions)))
    else:
        print(">>> Number of subRegions %d"%(len(subRegions)))


    if args.minArea>0:
        areaRemoved = 0.
        for sR in subRegions:
            if sR.area < args.minArea:
                areaRemoved += sR.area
                subRegions.remove(sR)
        print (">>>Area removed over total %f / %f"%(areaRemoved,sumOfContours.area))
        print(">>> New number of subRegions %d"%(len(subRegions)))

    if args.debug: # JDL
        ax.cla()
        for i,poly in enumerate(subRegions):
            x,y = poly.exterior.xy
            ax.plot(x,y,linewidth=2,color=np.random.rand(3,),linestyle=":")
        x,y = sumOfExpecteds.exterior.xy
        ax.plot(x,y,linewidth=1,color='k')
        fig.savefig("debug_CutUpExpected_Merged.pdf")


    # Now go through subcurves and dice them up
    for iSubRegion,subRegion in enumerate(subRegions): # subRegions are the cut up space associated with the best SR in each region
        if args.debug:
            print (">>> >>> Loop through sub regions: %d"%iSubRegion)

        # this subRegion -- Figure out which SR it corresponds to

        # Pick Best SR
        bestSR = subRegion_SR_dict[subRegion.area]

        if bestSR=="":
            allIsoExpectedContours_regionName.append("none")
            print(">>> Skipping a subRegion because I couldn't find it's SR")
            continue
        else:
            allIsoExpectedContours_regionName.append(bestSR)

        # now I know that this subRegion should go with bestSR
        # so now I need to loop over all other types of curves associated with best SR
        # and cut them up with all the IECs (e.g. obs, exp+1sig, etc)

        if args.debug:
            print (">>> >>> Identified the best SR in this region as %s"%bestSR)


        if args.showPastLimit:
            bestRegions[bestSR].append(subRegion) 

        # Now loop through types of curves and cookie cut out shapes based on subRegions
        for typeOfCurve, srCurve in uncutRegions[bestSR].iteritems(): #typeOfCurve is 'Exp', 'Obs' etc, srCurve is then that curves polygon, i.e. a single SR
            
            if subRegion.intersects( srCurve):
                cookieCut = subRegion.intersection(srCurve)
                if type(cookieCut) == Polygon:
                    listOfBestCurves[typeOfCurve].append(cookieCut)
                    if not args.showPastLimit and typeOfCurve == 'Exp': bestRegions[bestSR].append(cookieCut) # keep best exp curves for each SR                    
                elif type(cookieCut) == MultiPolygon:
                    for poly in cookieCut:
                        listOfBestCurves[typeOfCurve].append(poly)
                        if not args.showPastLimit and typeOfCurve == 'Exp': bestRegions[bestSR].append(poly) # keep best exp curves for each SR                            
                elif type(cookieCut) == GeometryCollection:
                    for poly in cookieCut:
                        if type(poly) == Polygon:
                            listOfBestCurves[typeOfCurve].append(poly)
                            if not args.showPastLimit and typeOfCurve == 'Exp': bestRegions[bestSR].append(poly) # keep best exp curves for each SR
                        else:
                            if args.debug:
                                print(">>> geom obj type: %s"%(type(poly)))
                            
                else:
                    if args.debug:
                        print(">>> cookieCut type: %s"%(type(cookieCut))) 

    if args.debug:
        for typeOfCurve in listOfBestCurves:
            print("nCurves to Sum for %s = %d"%(typeOfCurve,len(listOfBestCurves[typeOfCurve])))
            ax.cla()
            for poly in listOfBestCurves[typeOfCurve]:
                x,y = poly.exterior.xy
                ax.plot(x,y,linewidth=2,color=np.random.rand(3,),linestyle=":")
            x,y = sumOfExpecteds.exterior.xy
            ax.plot(x,y,linewidth=1,color='k')
            fig.savefig("debug_polyToSum_%s.pdf"%(typeOfCurve))


    ax.cla()

    for iIEC,IEC in enumerate(allIsoExpectedContours):
        convertArraysToTGraph(IEC[:,0],IEC[:,1]).Write("isoExpectedContour_%d"%iIEC)
        ax.plot(IEC[:,0],IEC[:,1],alpha=0.5,linewidth=0.1)


    print (">>> Creating summed curves and writing to output file")
    summedCurves = {}

    expCurve = ()
    for typeOfCurve in listOfBestCurves:
        print (">>> Adding together: %s"%typeOfCurve)

        summedCurves[typeOfCurve]   = cascaded_union( listOfBestCurves[typeOfCurve] )

        # Try various things to get one good polygon
        if type(summedCurves[typeOfCurve])==MultiPolygon: 
            # Try to join multipoly by expanding everything a tinybit
            summedCurves[typeOfCurve]   = cascaded_union([c.buffer(1e-1) for c in listOfBestCurves[typeOfCurve]])

            # For some reason polygons inside another don't always behave well
            #if type(summedCurves[typeOfCurve])==MultiPolygon:
            #
            #    for poly in listOfBestCurves[typeOfCurve]:
            #        # if poly is contained in another, remove it
            #        for polyTest in listOfBestCurves[typeOfCurve]:
            #            if poly==polyTest: continue
            #            if polyTest.contains(poly):
            #                print("removed poly")
            #                listOfBestCurves[typeOfCurve].remove(poly)
            #
            #    summedCurves[typeOfCurve]   = cascaded_union( listOfBestCurves[typeOfCurve] )
                
            # Last resort, convex hull
            if type(summedCurves[typeOfCurve])==MultiPolygon and not ("Exp_u1s" == typeOfCurve or "Exp_d1s" == typeOfCurve):
                print(">>> Warning, I've made a convex_hull of %s.  It won't have all of the expected inward wiggles."%(typeOfCurve))
                summedCurves[typeOfCurve] = summedCurves[typeOfCurve].convex_hull

        if "Exp_u1s" == typeOfCurve or "Exp_d1s" == typeOfCurve:
            continue

            
        x,y =  summedCurves[typeOfCurve].exterior.coords.xy
        ax.plot(x,y,alpha=0.5)

        if "Exp" == typeOfCurve:
            expCurve = (x,y)

        convertArraysToTGraph(x,y).Write("%s"%typeOfCurve)

    print (">>> Creating Exp +/-1 sigma band and writing to output file")

    if "Exp_u1s" in summedCurves and "Exp_d1s" in summedCurves:
        
        summedCurves["Exp_u1s"] = summedCurves["Exp_u1s"].buffer(1e-1) # this fixed some bad behavior where the band was the whole area
        band = summedCurves["Exp_d1s"].difference(summedCurves["Exp_u1s"])
        
        
        if type(band)==MultiPolygon:
            band = sorted(band, key=lambda x: x.area, reverse=True)
            for i,thing in enumerate(band):
                x,y = thing.exterior.coords.xy
                ax.plot(x,y,alpha=0.9)
                convertArraysToTGraph(x,y).Write("ExpectedBand_%d"%i)
        else:
            x,y = band.exterior.coords.xy
            ax.plot(x,y,alpha=0.9)

            convertArraysToTGraph(x,y).Write("ExpectedBand")

    if args.debug:
        print (">>> Saving debugging plot: debug.pdf")
        fig.savefig("debug.pdf")

    outputFile.Write()
    outputFile.Close()


    for name in listOfInputFiles:
        if name not in allIsoExpectedContours_regionName:
            print("Warning! Region " + name + " was not used.  For best results, remove it from the input files and run again.")

    return (bestRegions, expCurve)

def tGraphToPolygon(myGraph, pinPoint=None):
    x,y = convertTGraphToArrays(myGraph)
    if pinPoint==None:
        x = np.append(x,[min(x)])
        y = np.append(y,[min(y)])
    if not Polygon(zip(x,y)).is_valid:
        x,y = x[:-1],y[:-1]
    
    return Polygon(zip(x,y))

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


def doPolygonsTouch(poly1, poly2):

    return len(set(poly1.exterior.coords) & set(poly2.exterior.coords) ) > 2



def plotBestRegion(bestRegions, expCurve):

    fig, ax = plt.subplots()

    colors = ['b','g','r','c','m','y','k']
    for i in range(10):
        colors.append(np.random.rand(3,))

    # Plot pieces
    for reg in bestRegions.keys():
        for curve in bestRegions[reg]:

            try:
                x,y = curve.exterior.xy
                c = colors[ (bestRegions.keys()).index(reg) ]
                ax.fill(x,y,alpha=0.3,linewidth=0.2,color=c)
            except:
                print(">>> Skipped a subRegion.")
                pass

    # Plot combined expected
    ax.plot(expCurve[0],expCurve[1],linewidth=1,color='k')
                
    # Make legend
    patches=[]
    for i,reg in enumerate(bestRegions.keys()):
        patches.append(mpatches.Patch(color=colors[i], label=reg))

    patches.append(Line2D([0], [0], color='k', lw=1, label="Combined Expected"))

    x1,x2,y1,y2 = plt.axis()
    plt.axis((x1,x2,y1,1.7*y2))

    ax.legend(handles=patches, loc=1)

    print (">>> Saving used expected contours: usedExpectedContours.pdf")
    fig.savefig("usedExpectedContours.pdf")


if __name__ == "__main__":

    bestRegions, expCurve = main()

    if args.plotUsedContours: 
        plotBestRegion(bestRegions, expCurve)



