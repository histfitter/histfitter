#!/usr/bin/env python

# contourPlotterExample.py #################
#
# Example for using contourPlotter.py
#
# See README for details
#
# By: Larry Lee - Dec 2017

import ROOT

import contourPlotter

drawTheorySysts = False

plot = contourPlotter.contourPlotter("contourPlotterExample",800,600)

plot.processLabel = "Example Process Line Defining Grid. e.g. #tilde{g}#rightarrowwhatever"
plot.lumiLabel = "#sqrt{s}=14 TeV, 1000 fb^{-1}, All limits at 95% CL"

## Just open up a root file with TGraphs in it so you can hand them to the functions below!

f = ROOT.TFile("outputGraphs.root")

f.ls()

## Axes

plot.drawAxes( [0,100,1200,600] )

## Other limits to draw

# plot.drawShadedRegion( externalGraphs.curve, title="ATLAS 8 TeV, 20.3 fb^{-1} (observed)" )

## Main Result

plot.drawTextFromTGraph2D( f.Get("CLs_gr")  , angle=30 , title = "Grey Numbers Represent Observed CLs Value")

plot.drawOneSigmaBand(  f.Get("Band_1s_0")   )
plot.drawExpected(      f.Get("Exp_0")       )
plot.drawObserved(      f.Get("Obs_0"), title="Observed Limit (#pm1 #sigma_{theory}^{SUSY})" if drawTheorySysts else "Observed Limit")

## Draw Lines

# plot.drawLine(  coordinates = [0,0,800,800], label = "Kinematically Forbidden or blah", style = 7, angle = 30 )

## Axis Labels

plot.setXAxisLabel( "m_{0} [GeV]" )
plot.setYAxisLabel( "m_{1/2} [GeV]"  )

plot.createLegend(shape=(0.22,0.58,0.55,0.77) ).Draw()

if drawTheorySysts:
	plot.drawTheoryUncertaintyCurve( f.Get("Obs_0_Up") )
	plot.drawTheoryUncertaintyCurve( f.Get("Obs_0_Down") )
	# coordinate in NDC
	plot.drawTheoryLegendLines( xyCoord=(0.234,0.6625), length=0.057 )

plot.decorateCanvas( )
plot.writePlot( )




