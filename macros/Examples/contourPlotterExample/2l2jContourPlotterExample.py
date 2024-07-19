#!/usr/bin/env python

# 2l2jContourPlotterExample.py #################
#
# Example from Strong SUSY 2L2J analysis meant to
# illustrate how various features can be used, e.g.
# to add CLs values, rotate, and overlay contours etc.
#
# By: Jonathan Long - Feb 2022

import ROOT
import sys
import contourPlotter

# Signal grids
key="SS_N2_ZN1" # GG_N2_ZN1 GG_N2_SLN1 SS_N2_ZN1                                                         
#region="SR_deltam"                                                                                      
region="comb"

# Take in command line argument for faster key/region setting
for a in sys.argv[1:]:
    if "SR" in a or 'comb' in a: region = a
    else: key = a

# Various options for the drawing
drawTheorySysts = True
doUpperLimit = True
doCLs = False
doDeltam = False
rotate = False
    
plot = contourPlotter.contourPlotter("contourOverlay_"+key+region+ ("_deltam" if doDeltam else "")+("_UL" if doUpperLimit else "")+("_CLs" if doCLs else ""),800,600)

# Rotate into mass vs delta-m
if rotate:
    x_new = lambda x,y : x
    y_new = lambda x,y : x - y

# Set labels based on process
if "GG_N2_ZN1" in key:
    plot.processLabel = "#tilde{g}-#tilde{g}; #tilde{g} #rightarrow q#bar{q} #tilde{#chi}^{0}_{2}; #tilde{#chi}^{0}_{2} #rightarrow Z^{(*)} #tilde{#chi}^{0}_{1}; m(#tilde{#chi}^{0}_{2})=[m(#tilde{g}) + m(#tilde{#chi}^{0}_{1})]/2"
elif "SS_N2_ZN1" in key:
    plot.processLabel = "#tilde{q}-#tilde{q}; #tilde{q} #rightarrow q #tilde{#chi}^{0}_{2}; #tilde{#chi}^{0}_{2} #rightarrow Z^{(*)} #tilde{#chi}^{0}_{1}; m(#tilde{#chi}^{0}_{2})=[m(#tilde{q}) + m(#tilde{#chi}^{0}_{1})]/2"
else:
    plot.processLabel = "#tilde{g}-#tilde{g}; #tilde{g} #rightarrow q#bar{q} #tilde{#chi}^{0}_{2}; #tilde{#chi}^{0}_{2} #rightarrow #tilde{l}^{#pm} l^{#mp}; #tilde{l}^{#pm} #rightarrow l^{#pm} #tilde{#chi}^{0}_{1}; m(#tilde{#chi}^{0}_{2})=[m(#tilde{g}) + m(#tilde{#chi}^{0}_{1})]/2; m(#tilde{l})=[m(#tilde{#chi}^{0}_{2})) + m(#tilde{#chi}^{0}_{1})]/2"

# Add labels as desired
#plot.lumiLabel = "#sqrt{s}=13 TeV, 139 fb^{-1}, All limits at 95% CL"

## Just open up a root file with TGraphs in it so you can hand them to the functions below!
f_reg = ROOT.TFile("outputGraphs_"+key+"_" + region + ("_deltam" if doDeltam else "") + ".root")


## Axes
if doDeltam:
    plot.drawAxes( [601,0,2500,500] )

    if "SS" in key:
        plot.setYAxisLabel( "m_{#tilde{q}} - m_{#tilde{#chi}^{0}_{1}} [GeV]"  )
    else:
        plot.setYAxisLabel( "m_{#tilde{g}} - m_{#tilde{#chi}^{0}_{1}} [GeV]"  )
else:
    if "SS" in key:
        if doUpperLimit:
            plot.drawAxes( [601,100,2500,2400] )
        else:
            plot.drawAxes( [601,100,1700,1600] )
        plot.drawLine(  coordinates = [601,601,1000,1000], label = "m_{#tilde{q}} < m_{#tilde{#chi}^{0}_{1}}", style = 7, angle = 33, color = ROOT.TColor.GetColor("#777777") )
    elif "SLN" in key:
        if doUpperLimit:
            plot.drawAxes( [601,100,2500,2500] )
        else:
            plot.drawAxes( [601,100,2500,2500] )
        plot.drawLine(  coordinates = [601,601,1400,1400], label = "m_{#tilde{g}} < m_{#tilde{#chi}^{0}_{1}}", style = 7, angle = 33, color = ROOT.TColor.GetColor("#777777") )
    else:
        if doUpperLimit:
            plot.drawAxes( [601,100,2500,2400] )
        else:
            plot.drawAxes( [601,100,2100,2200] )
        plot.drawLine(  coordinates = [601,601,1200,1200], label = "m_{#tilde{g}} < m_{#tilde{#chi}^{0}_{1}}", style = 7, angle = 33, color = ROOT.TColor.GetColor("#777777")  )
    plot.setYAxisLabel( "m_{#tilde{#chi}^{0}_{1}} [GeV]"  )

## Limits from old results on HEPdata
if key == "GG_N2_SLN1":
    f_prev = ROOT.TFile("../GG_N2_SLN1_36ifb.root")
    plot.drawShadedRegion( f_prev.Get('hepdata_graph'), title="ATLAS 13 TeV, 36.1 fb^{-1} (observed)" )
elif key == "GG_N2_ZN1":
    f_prev = ROOT.TFile("../GG_N2_ZN1_36ifb.root")
    plot.drawShadedRegion( f_prev.Get('hepdata_graph'), title="ATLAS 13 TeV, 36.1 fb^{-1} (observed)" )


## Main Result
if doUpperLimit: 
    ul = f_reg.Get("upperLimit_gr")
    if 'SS' in key:
        ul = plot.applyFactorToTGraph2D(ul, "../ss_xs.csv")
    elif 'GG' in key:
        ul = plot.applyFactorToTGraph2D(ul, "../gg_xs.csv")
    plot.drawTextFromTGraph2D( ul  , angle=30 , title = "Grey Numbers Represent Cross Section Upper Limit [pb]", format="%.2g")

    x,y,z,n = ul.GetX(), ul.GetY(), ul.GetZ(), ul.GetN()
    ul_vals = sorted(zip(x,y,z))
    #for u in ul_vals:
    #    print("{} & {} & {:.3g} \\\\".format(u[0], u[1], u[2]))
        

if doCLs:
    cls = f_reg.Get("CLs_gr")
    plot.drawTextFromTGraph2D( cls  , angle=30 , title = "Grey Numbers Represent Observed CLs Values", format="%.2g")

    x,y,z,n = cls.GetX(), cls.GetY(), cls.GetZ(), cls.GetN()
    cls_vals = sorted(zip(x,y,z))
    #for u in cls_vals:
    #    print("{} & {} & {:.3e} \\\\".format(u[0], u[1], u[2]))

# Plot band, sometimes it gets broken up into multiple graphs
firstBand = True
for k in f_reg.GetListOfKeys():
    if "ExpectedBand" in k.GetName():
        band = plot.rotateTGraph(f_reg.Get(k.GetName()), x_new, y_new) if rotate else f_reg.Get(k.GetName())        
        if firstBand:
            plot.drawOneSigmaBand( band )
            firstBand = False
        else:        
            plot.drawOneSigmaBand( band , legendOrder = "none")

exp = plot.rotateTGraph(f_reg.Get("Exp"), x_new, y_new) if rotate else f_reg.Get("Exp")
plot.drawExpected( exp,color=ROOT.kBlack) # ,title=region ,legendOrder=1     )

obs = plot.rotateTGraph(f_reg.Get("Obs"),x_new, y_new) if rotate else f_reg.Get("Obs")
plot.drawObserved( obs, title="Observed Limit (#pm1 #sigma_{theory}^{SUSY})" if drawTheorySysts else "Observed Limit")



if "SS" in key:
    plot.createLegend(shape=(0.18,0.645,0.61,0.77) ).Draw()
    plot.setXAxisLabel( "m_{#tilde{q}} [GeV]" )
else:   
   plot.createLegend(shape=(0.18,0.58,0.61,0.77) ).Draw()
   plot.setXAxisLabel( "m_{#tilde{g}} [GeV]" )



if drawTheorySysts:
    plot.drawTheoryUncertaintyCurve( f_reg.Get("Obs_u1s") )
    plot.drawTheoryUncertaintyCurve( f_reg.Get("Obs_d1s") )
    # coordinate in NDC
    #plot.drawTheoryLegendLines( xyCoord=(0.195,0.6625), length=0.057 )
        # Annoying, but tweak the extra lines in the legend
        plot.drawTheoryLegendLines( xyCoord=(0.195,0.6625), length=0.08 )

plot.decorateCanvas( )
plot.writePlot( )
plot.writePlot( 'eps')
 



