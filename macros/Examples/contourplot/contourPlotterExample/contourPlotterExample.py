#!/usr/bin/env python

# contourPlotterExample.py #################
#
# Example for using contourPlotter.py (assuming you've used harvestToContours)
#
# The file that's used here just needs to contain TGraphs for this setup to work.
# Easy way to make those TGraphs:
#     python harvestToContours.py --interpolation linear -o stopToStauExample.root -i stopToStauExample.json -x m0 -y m12
#
# By: Larry Lee - Dec 2017

import ROOT

import contourPlotter
import externalGraphs

ROOT.gROOT.LoadMacro("AtlasStyle.C")
ROOT.gROOT.LoadMacro("AtlasLabels.C")
ROOT.SetAtlasStyle()

drawTheorySysts = True

plot = contourPlotter.contourPlotter("stopToStau",800,600)

plot.processLabel = "Example Process Line Defining Grid. #tilde{g}#rightarrowwhatever"

## Just open up a root file with TGraphs in it so you can hand them to the functions below!

f = ROOT.TFile("stopToStauExample.root")

## Axes

plot.drawAxes( [0,0,1500,2000] )

## Other limits to draw

plot.drawShadedRegion( Run1.curve, title="ATLAS 8 TeV, 20.3 fb^{-1} (observed)" )
plot.drawShadedRegion( Run1.lep  , title="LEP Limits" , color = ROOT.kBlue      )

## Main Result

plot.drawOneSigmaBand(  f.Get("Band_1s_0")   )
plot.drawExpected(      f.Get("Exp_0")       )
plot.drawObserved(      f.Get("Obs_0"), title="Observed Limit (#pm1 #sigma_{theory}^{SUSY})" if drawTheorySysts else "Observed Limit")

## Draw Lines

plot.drawLine(  coordinates = [0,0,1500,1500], label = "Kinematically Forbidden or blah", style = 7, angle = 30 )

## Axis Labels

plot.setXAxisLabel( "boom [GeV]" )
plot.setYAxisLabel( "bap [GeV]"  )

plot.drawLegend()

if drawTheorySysts:
	# coordinate in NDC
	plot.drawTheoryLegendLines( xyCoord=(0.236,0.6625), length=0.075 )

ROOT.ATLASLabel(0.24,0.85," Internal")

plot.decorateCanvas( )
plot.writePlot()




