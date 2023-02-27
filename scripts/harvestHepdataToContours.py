#!/usr/bin/env python

############### harvestHepdataToContours.py #################
# Example usage:
# harvestHepdata.py --inputFile GG_N2_SLN1_36ifb.csv --outputFile GG_N2_SLN1_36ifb.root
#
# Script to facilitate converting hepdata contour (CSV) to a TGraph for the 
# previous exclusion grey shaded areas
#
# Reads in a csv file downloaded from HepData.
# Option to insert points help close the contour:
# --closeContour "0,0 100,0"
# 
# By: Jonathan Long - April 2021



import ROOT, csv, argparse, math

ROOT.gROOT.SetBatch()


parser = argparse.ArgumentParser()
parser.add_argument("--inputFile","-i",  type = str, help="input hepdata csv file", default = "test.csv")
parser.add_argument("--outputFile","-o", type = str, help="output ROOT file", default = "outputGraphs.root")
parser.add_argument("--closeContour","-c", type = str, help="Insert these points into the TGraph to help close the contour.  The syntax is a space separated set of points \"0,0 600,0 0,600\"", default = "")

args = parser.parse_args()


""" Main function"""
def main():
    # Open the csv file
    with open(args.inputFile) as f:
        fc = csv.reader(f)
   
        x = []
        y = []
   
        # skip comment lines and those which are text, i.e. don't convert to a float
        for row in fc:
            if '#' in row: continue
   
            try:
                x.append(float(row[0]))
                y.append(float(row[1]))
            except:
                # Some hepdata text we don't want
                continue
   
        # Add extra points to close contour
        if args.closeContour !="":
            x,y = closeContour(x,y, args.closeContour)
           
        # Convert arrays to ROOT TGraph
        outfile = ROOT.TFile(args.outputFile, "recreate")
   
        from array import array
        graph =  ROOT.TGraph(len(x), array('f',x), array('f',y))
   
        graph.Write("hepdata_graph")    
        outfile.Close()
    
    return


def closeContour(x,y, argument):
    # Insert a point into the TGraph next to the closest existing point.

    points = []
    text_points = argument.split()

    # Parse input into points
    for tp in text_points:
        points.append( (float( tp.split(",")[0] ), 
                       float( tp.split(",")[1] ) ) )


    # Add each point
    for x_close, y_close in points:
        dist_save = 1e12
        i_save = -1

        #print(f"Appending point {x_close}, {y_close}")
        print(f"Appending point {x_close}, {y_close}" )
        
        # Compute distance to closest existing point
        for i, (x_test, y_test) in enumerate(zip(x,y)):
            test_dist = math.sqrt( (x_test-x_close)**2 +(y_test-y_close)**2 )
            
            if test_dist < dist_save:
                dist_save = test_dist
                i_save = i
    
        if (dist_save == 1e12):
            print("Error, the closest point to the contour was larger than 1e12")
            exit(1)

        #print(f"Closest point was {x[i_save]}, {y[i_save]}, with distance of {dist_save} at position {i_save}")

        # Figure out position to insert, either before or after the existing point
        # This is unfortunately needed because the csv might wrap in the middle...
        prev = (len(x)-1 if i_save == 0 else i_save - 1)
        post = (0 if i_save == len(x)-1 else i_save + 1)

        dist_prev = math.sqrt( (x[prev]-x_close)**2 +(y[prev]-y_close)**2 )
        dist_post = math.sqrt( (x[post]-x_close)**2 +(y[post]-y_close)**2 ) 
        
        if (dist_prev < dist_post):
            x.insert(post, x_close)
            y.insert(post, y_close)
        else:
            x.insert(i_save, x_close)
            y.insert(i_save, y_close)
    
    return (x,y)






if __name__ == "__main__":
    main()
