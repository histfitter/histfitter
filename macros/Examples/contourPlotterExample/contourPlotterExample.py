#!/usr/bin/env python

# contourPlotterExample.py #################
#
# Example for using contourPlotter.py (assuming you've used harvestToContours)
#
# The file that's used here just needs to contain TGraphs for this setup to work.
# Easy way to make those TGraphs:
#     harvestToContours.py --interpolation linear -o stopToStauExample.root -i stopToStauExample.json -x m0 -y m12 -l "x"
#
# If you don't have a JSON file, you can also use the command GenerateJSONOutput.py to take your
# ROOT file output from the HF fit and create a JSON that can be used with harvestToContours.py
#    GenerateJSONOutput.py \
#        -i [hypotest result root file] \
#        -f [format of result object name e.g. "hypo_SU_%f_%f_0_10"] \
#        -p [interpretation of the variables in the name above. e.g. "m0:m12"]
# By: Larry Lee - Dec 2017

import ROOT

import contourPlotter
import externalGraphs

ROOT.gROOT.LoadMacro("AtlasStyle.C")
ROOT.gROOT.LoadMacro("AtlasLabels.C")
ROOT.SetAtlasStyle()

drawTheorySysts = False

plot = contourPlotter.contourPlotter("stopStau",800,600)

plot.processLabel = "Example Process Line Defining Grid. #tilde{g}#rightarrowwhatever"

## Just open up a root file with TGraphs in it so you can hand them to the functions below!

f = ROOT.TFile("stopToStauExample.root")

## Axes

plot.drawAxes( [0,0,1400,2000] )

## Other limits to draw

plot.drawShadedRegion( externalGraphs.curve, title="ATLAS 8 TeV, 20.3 fb^{-1} (observed)" )
plot.drawShadedRegion( externalGraphs.lep  , title="Fake LEP Limits" , color = ROOT.kBlue      )

## Main Result

plot.drawTextFromTGraph2D( f.Get("CLs_gr")  , angle=30 )

plot.drawOneSigmaBand(  f.Get("Band_1s_0")   )
plot.drawExpected(      f.Get("Exp_0")       )
plot.drawObserved(      f.Get("Obs_0"), title="Observed Limit (#pm1 #sigma_{theory}^{SUSY})" if drawTheorySysts else "Observed Limit")

## Draw Lines

plot.drawLine(  coordinates = [0,0,800,800], label = "Kinematically Forbidden or blah", style = 7, angle = 30 )

## Axis Labels

plot.setXAxisLabel( "boom [GeV]" )
plot.setYAxisLabel( "bap [GeV]"  )

plot.createLegend(shape=(0.22,0.58,0.55,0.77) ).Draw()

if drawTheorySysts:
	plot.drawTheoryUncertaintyCurve( f.Get("Obs_0_Up") )
	plot.drawTheoryUncertaintyCurve( f.Get("Obs_0_Down") )
	# coordinate in NDC
	plot.drawTheoryLegendLines( xyCoord=(0.234,0.6625), length=0.057 )

ROOT.ATLASLabel(0.24,0.85," Internal")

plot.decorateCanvas( )
plot.writePlot()




