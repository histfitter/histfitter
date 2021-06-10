# **********************************************************************************
# * Project: HistFitter - A ROOT-based package for statistical data analysis       *
# * Package: HistFitter                                                            *
# * Created: 11 July 2016                                                          *
# *                                                                                *
# * Description: functionality to plot impact of errors                            *
# *                                                                                *
# * Authors:                                                                       *
# *      HistFitter group, CERN, Geneva                                            *
# *                                                                                *
# * Redistribution and use in source and binary forms, with or without             *
# * modification, are permitted according to the terms listed in the file          *
# * LICENSE.                                                                       *
# **********************************************************************************/

import ROOT
ROOT.gROOT.SetBatch(True)

import itertools
import os
import sys

class SystematicsPlotter:
    def __init__(self, filename, samples=[], regions=[], systematics=[], variable="cuts"):
        self.filename = filename
        self.samples = samples
        self.regions = regions
        self.systematics = systematics
        self.variable = variable
        self.outputDir = os.getcwd()

        if isinstance(self.samples, str):
            self.samples = [self.samples]
        if isinstance(self.regions, str):
            self.regions = [self.regions]
        if isinstance(self.systematics, str):
            self.systematics = [self.systematics]

    def writePlots(self):
        for c in itertools.product(self.samples, self.regions, self.systematics):
            p = SystematicsPlot(filename=self.filename, sample=c[0], region=c[1], systematic=c[2], variable=self.variable)
            p.outputDir = self.outputDir
            p.write()

class SystematicsPlot:
    def __init__(self, filename, sample="", region="", systematic="", variable="cuts"):
        self.filename = filename

        self.sample = sample
        self.region = region
        self.systematic = systematic
        self.variable = variable

        self.nominalName = self.buildHistogramName("Nominal") 
        self.upName = self.buildHistogramName("Up")
        self.downName = self.buildHistogramName("Down")

        self.nominalHistogram = None
        self.upHistogram = None
        self.downHistogram = None

        self.outputDir = os.getcwd()

        pass

    def buildHistogramName(self, type="Nominal"):
        if self.sample == "" or self.region == "" or self.systematic == "" or self.variable == "":
            return ""
        
        types = {"Nominal" : "Nom", "Up" : "High", "Down": "Low"}

        if type == "Nominal":
            t = types[type]
        else:
            t = f"{self.systematic}{types[type]}"

        s = f"h{self.sample}{t}_{self.region}_obs_{self.variable}"
        return s

    def getHistograms(self):
        if not os.path.exists(self.filename) or not os.path.isfile(self.filename):
            print(f"Error: file {self.filename} does not exist or is not a file")
            return False

        f = ROOT.TFile.Open(self.filename)
        self.nominalHistogram = f.Get(self.nominalName)
        self.upHistogram = f.Get(self.upName)
        self.downHistogram = f.Get(self.downName)

        retval = True
        try:
            self.nominalHistogram.SetDirectory(0)
        except:
            print(f"WARNING: Cannot find nominal histogram {self.nominalName} in {self.filename} (plotting for {self.systematic})")
            retval = False
        
        try:
            self.upHistogram.SetDirectory(0)
        except:
            print(f"WARNING: Cannot find up histogram {self.upName} in {self.filename} (plotting for {self.systematic})")
            retval = False
        
        try:
            self.downHistogram.SetDirectory(0)
        except:
            print(f"WARNING: Cannot find down histogram {self.downName} in {self.filename} (plotting for {self.systematic})")
            retval = False

        f.Close()

        return retval

    def write(self):
        if not self.getHistograms(): 
            print("WARNING: one or more of the histograms doesn't exist; not plotting")
            return 

        ROOT.gStyle.SetOptStat(0)

        # Name of canvas and output file
        canvasName = f"c_{self.upName}_{self.systematic}_{self.variable}"

        c = ROOT.TCanvas(canvasName, canvasName, 600, 400)

        if self.variable != "cuts":
            self.nominalHistogram.SetTitle(f"Impact on {self.sample} in {self.region} (binned: {self.variable}) of {self.systematic}")
        else:
            self.nominalHistogram.SetTitle(f"Impact on {self.sample} in {self.region} of {self.systematic}")
        self.nominalHistogram.SetMarkerColor(ROOT.kBlack)
        self.nominalHistogram.SetMarkerStyle(20)
        self.nominalHistogram.SetLineWidth(2)
        self.nominalHistogram.Draw("e")

        self.upHistogram.SetLineColor(ROOT.kCyan-3)
        self.upHistogram.SetLineStyle(ROOT.kDashed)
        self.upHistogram.SetMarkerColor(ROOT.kCyan-3)
        self.upHistogram.SetMarkerStyle(25)
        self.upHistogram.SetLineWidth(2)
        self.upHistogram.Draw("esame")
        
        self.downHistogram.SetLineColor(ROOT.kMagenta-3)
        self.downHistogram.SetLineStyle(ROOT.kDotted)
        self.downHistogram.SetMarkerColor(ROOT.kMagenta-3)
        self.downHistogram.SetMarkerStyle(26)
        self.downHistogram.SetLineWidth(2)
        self.downHistogram.Draw("esame")
  
        upRange = self.nominalHistogram.GetBinContent(self.nominalHistogram.GetMaximumBin()) * 1.5 
        downRange = self.nominalHistogram.GetBinContent(self.nominalHistogram.GetMinimumBin()) / 2.0
        if downRange == 0.0: downRange = -0.5
 
        print(f"Y axis range: {downRange} - {upRange}")
        self.nominalHistogram.GetYaxis().SetRangeUser(downRange, upRange)
        legend = ROOT.TLegend(0.7, 0.75, 0.9, 0.9, "")
        legend.SetFillStyle(0)
        legend.SetFillColor(0)
        legend.SetBorderSize(0)
        legend.AddEntry(self.nominalHistogram, "nominal", "lp")
        legend.AddEntry(self.upHistogram, f"{self.systematic} up", "lp")
        legend.AddEntry(self.downHistogram, f"{self.systematic} down", "lp")
        legend.Draw()
       
        c.SaveAs(os.path.join(self.outputDir, f"{canvasName}.pdf"))
        c.SaveAs(os.path.join(self.outputDir, f"{canvasName}.eps"))
        c.SaveAs(os.path.join(self.outputDir, f"{canvasName}.png"))

        print(f"Region: {self.region}, sample: {self.sample}, systematic: {self.systematic}, variable: {self.variable}")

        for i in range(1, self.nominalHistogram.GetNbinsX()+1):
            if abs(self.nominalHistogram.GetBinContent(i) - 0.0001) < 0.0: continue
            print(f"Bin: {i} MC stat error: +/- {self.nominalHistogram.GetBinContent(i)}    bin-value {self.nominalHistogram.GetBinError(i)}")
            if self.nominalHistogram.GetBinContent(i) > 0.0:
                print(f"         MC stat error %: {self.nominalHistogram.GetBinError(i) / self.nominalHistogram.GetBinContent(i) * 100.0}")

        return
