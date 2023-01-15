#!/usr/bin/env python

# contourPlotter.py
#
# Tools for making final contour plots. See contourPlotterExample.py
#
# By: Larry Lee - Dec 2017

import ROOT

ROOT.gROOT.SetBatch()

from array import array
import csv

class contourPlotter:
    def __init__(self, plotName="test", xSize=800, ySize=600):
        self.plotName = plotName
        self.xSize = xSize
        self.ySize = ySize
        self.canvas = ROOT.TCanvas(self.plotName, self.plotName, xSize, ySize)

        self.canvas.SetLeftMargin(0.15)
        self.canvas.SetRightMargin(0.07)
        self.canvas.SetTopMargin(0.07)
        self.canvas.SetBottomMargin(0.15)

        self.xAxisLabel = "x label"
        self.yAxisLabel = "y label"

        self.processLabel = "Process Title -- Describe The Grid!"
        self.lumiLabel = "#sqrt{s}=XX TeV, YY fb^{-1}, All limits at 95% CL"
        self.figLabel = "#it{Example Label}"

        self.bottomObject = 0
        self.legendObjects = []

        return

    def setXAxisLabel(self, label="",titlesize=0.05,labelsize=0.045):
        self.xAxisLabel = label
        if self.bottomObject:
            self.bottomObject.GetXaxis().SetTitle(self.xAxisLabel)
            self.bottomObject.GetXaxis().SetTitleSize(titlesize)
            self.bottomObject.GetXaxis().SetLabelSize(labelsize)

        return

    def setYAxisLabel(self, label="",titlesize=0.05,labelsize=0.045):
        self.yAxisLabel = label
        if self.bottomObject:
            self.bottomObject.GetYaxis().SetTitle(self.yAxisLabel)
            self.bottomObject.GetYaxis().SetTitleSize(titlesize)
            self.bottomObject.GetYaxis().SetLabelSize(labelsize)

        return

    def setYAxisLog(self, b=1):
        if self.canvas:
            self.canvas.SetLogy(b)
        return

    def drawAxes(self, axisRange=[0, 0, 2000, 2000]):
        self.canvas.cd()
        self.bottomObject = self.canvas.DrawFrame(*axisRange)
        self.bottomObject.SetTitle(f";{self.xAxisLabel};{self.yAxisLabel}")
        self.bottomObject.GetYaxis().SetTitleOffset(1.3)
        self.bottomObject.GetXaxis().SetTitleOffset(1.3)
        self.canvas.Update()
        return

    def drawOneSigmaBand(
        self, band, color=ROOT.TColor.GetColor("#ffd700"), alpha=0.5, legendOrder=0
    ):
        self.canvas.cd()
        band.SetFillColorAlpha(color, alpha)
        band.SetFillStyle(1001)
        band.SetLineStyle(1)
        band.SetLineWidth(1)
        band.SetLineColorAlpha(ROOT.kGray, 0.5)
        band.Draw("F")
        band.Draw("L")
        self.canvas.Update()
        tmpLegendObject = band.Clone("1SigmaBand")
        tmpLegendObject.SetLineColor(ROOT.kBlack)
        tmpLegendObject.SetLineStyle(7)
        tmpLegendObject.SetLineWidth(1)
        if type(legendOrder) == int:
            self.legendObjects.append(
                (
                    legendOrder,
                    tmpLegendObject,
                    "Expected Limit (#pm1 #sigma_{exp})",
                    "lf",
                )
            )
        return

    def drawExpected(
        self,
        curve,
        color=ROOT.kBlack,
        alpha=0.9,
        legendOrder=None,
        title="Expected Limit",
        drawOption="L",
    ):
        self.canvas.cd()
        curve.SetLineColorAlpha(color, alpha)
        curve.SetLineStyle(7)
        curve.SetLineWidth(1)
        curve.Draw(drawOption)
        self.canvas.Update()
        if type(legendOrder) == int:
            self.legendObjects.append((legendOrder, curve, title, "l"))
        return

    def drawObserved(
        self,
        curve,
        title="Observed Limit (#pm1 #sigma_{theory}^{SUSY})",
        color=ROOT.TColor.GetColor("#800000"),
        alpha=0.7,
        legendOrder=1,
        drawOption="L",
    ):
        self.canvas.cd()
        curve.SetLineColorAlpha(color, alpha)
        curve.SetLineStyle(1)
        curve.SetLineWidth(3)
        curve.Draw(drawOption)
        self.canvas.Update()
        if type(legendOrder) == int:
            self.legendObjects.append(
                (legendOrder, curve.Clone("Observed"), title, "L")
            )
        return

    def drawTheoryUncertaintyCurve(
        self, curve, color=ROOT.TColor.GetColor("#800000"), alpha=0.7, style=3
    ):
        self.canvas.cd()
        curve.SetLineColorAlpha(color, alpha)
        curve.SetLineStyle(style)
        curve.SetLineWidth(1)
        curve.Draw("L")
        self.canvas.Update()
        return

    def drawTextFromTGraph2D(
        self,
        graph,
        title="Grey numbers represent blah",
        color=ROOT.TColor.GetColor("#000000"),
        alpha=0.6,
        angle=30,
        size=0.015,
        format="%.1g",
        titlesize=0.03,
    ):
        self.canvas.cd()
        tmpText = ROOT.TLatex()
        tmpText.SetTextSize(size)
        tmpText.SetTextColorAlpha(color, alpha)
        tmpText.SetTextAngle(angle)
        x, y, z, n = graph.GetX(), graph.GetY(), graph.GetZ(), graph.GetN()
        for i in range(n):
            tmpText.DrawLatex(x[i], y[i], format % z[i])

        tmpText.SetTextSize(titlesize)
        tmpText.SetTextAngle(-90)
        tmpText.DrawLatexNDC(0.94, 0.9, title)
        self.canvas.Update()
        return

    def drawShadedRegion(
        self, curve, color=ROOT.kGray, alpha=0.5, title="title", legendOrder=2
    ):
        self.canvas.cd()
        curve.SetFillStyle(1001)
        curve.SetFillColorAlpha(color, alpha)
        curve.SetLineStyle(1)
        curve.SetLineWidth(1)
        curve.SetLineColorAlpha(color,alpha)
        curve.Draw("F")
        curve.Draw("L")
        self.canvas.Update()
        if type(legendOrder) == int:
            self.legendObjects.append(
                (legendOrder, curve.Clone("ShadedRegion_" + title), title, "F")
            )
        return

    def drawLine(
        self, coordinates, label="", color=ROOT.kGray, style=7, labelLocation=0, angle=0
    ):
        self.canvas.cd()
        tmpLine = ROOT.TLine()
        tmpLine.SetLineColorAlpha(color, 1.0)
        tmpLine.SetLineStyle(style)
        tmpLine.DrawLine(*coordinates)
        xmin, ymin, xmax, ymax = coordinates

        tmpLineLabel = ROOT.TLatex()
        tmpLineLabel.SetTextSize(0.028)
        tmpLineLabel.SetTextColor(color)
        tmpLineLabel.SetTextAngle(angle)
        if labelLocation:
            tmpLineLabel.DrawLatex(labelLocation[0], labelLocation[1], label)
        else:
            tmpLineLabel.DrawLatex(
                coordinates[0] + 0.1 * (coordinates[2] - coordinates[0]),
                coordinates[1] + 0.18 * (coordinates[3] - coordinates[1]),
                label,
            )

        self.canvas.Update()
        return

    def decorateCanvas(self):
        self.canvas.cd()
        latexObject = ROOT.TLatex()
        latexObject.SetTextSize(0.028)
        latexObject.DrawLatexNDC(0.15, 0.95, self.processLabel)

        latexObject.SetTextSize(0.037)
        latexObject.DrawLatexNDC(0.18, 0.8, self.lumiLabel)

        latexObject.SetTextSize(0.05)
        latexObject.DrawLatexNDC(0.18, 0.85, self.figLabel)

        ROOT.gPad.RedrawAxis()
        self.canvas.Update()
        return

    def createLegend(self, shape=(0.22, 0.55, 0.65, 0.75)):
        self.canvas.cd()
        legend = ROOT.TLegend(*shape)
        ROOT.SetOwnership(legend, 0)
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextFont(42)

        self.legendObjects.sort(key=lambda x: x[0], reverse=False)
        for iItem, (legendOrder, item, title, style) in enumerate(self.legendObjects):
            legend.AddEntry(item, title, style)

        return legend

    def drawTheoryLegendLines(
        self,
        xyCoord,
        length=0.05,
        ySeparation=0.026,
        color=ROOT.TColor.GetColor("#800000"),
        alpha=0.7,
        style=3,
    ):
        self.canvas.cd()
        tmpLine = ROOT.TLine()
        tmpLine.SetLineWidth(2)
        tmpLine.SetLineColorAlpha(color, alpha)
        tmpLine.SetLineStyle(style)
        tmpLine.DrawLineNDC(xyCoord[0], xyCoord[1], xyCoord[0] + length, xyCoord[1])
        tmpLine.DrawLineNDC(
            xyCoord[0],
            xyCoord[1] + ySeparation,
            xyCoord[0] + length,
            xyCoord[1] + ySeparation,
        )

    def writePlot(self, format="pdf"):
        self.canvas.SaveAs(f"{self.plotName:s}.{format:s}")
        return

    # Pass a lambda function, e.g. y_new = lambda x,y : x - y
    def rotateTGraph(self, tg, x_new, y_new):
        n = tg.GetN()
        x = array("d")
        y = array("d")
        for i in range(n):
            x_temp = tg.GetPointX(i)
            y_temp = tg.GetPointY(i)

            x.append(x_new(x_temp, y_temp))
            y.append(y_new(x_temp, y_temp))

        tg_new = ROOT.TGraph(n, x, y)

        return tg_new

    def rotateTGraph2D(self, tg, x_new, y_new):

        n = tg.GetN()
        x = array("d")
        y = array("d")
        z = array("d")


        x_temp = tg.GetX()
        y_temp = tg.GetY()
        z_temp = tg.GetZ()

        for i in range(n):
            x.append(x_new(x_temp[i], y_temp[i]))
            y.append(y_new(x_temp[i], y_temp[i]))
            z.append(z_temp[i])

        tg_new = ROOT.TGraph2D(n, x, y, z)

        return tg_new


    """
    Reads in csv file with factors to apply, with the following format
    x,y,factor # header
    600,,0.1E+02 # first point
    800,,0.12E+01 # second point etc.
    """
    def applyFactorToTGraph2D(self, tg, csvFile):
        n = tg.GetN()

        x_tg = tg.GetX()
        y_tg = tg.GetY()
        z_tg = tg.GetZ()

        x_out = array( 'd' )
        y_out = array( 'd' )
        z_out = array( 'd' )

        # open csv file with factors to multiply in
        with open(csvFile) as cf:
            # Loop over TGraph points
            for i in range(n):
                x_temp = x_tg[i]
                y_temp = y_tg[i]
                z_temp = z_tg[i]

                appended = False

                # Look for factor to apply
                cf.seek(0)
                c_reader = csv.DictReader(cf)
                for row in c_reader:
            
                    x_fac = row['x']
                    y_fac = row['y']
                    f = float(row['factor'])

                    if x_fac == '' or float(x_fac) == x_temp:
                        if y_fac == '' or float(y_fac) == y_temp:
                        
                            x_out.append(x_temp)
                            y_out.append(y_temp)
                            z_out.append(z_temp * f)
                            appended = True

                if not appended:
                    x_out.append(x_temp)
                    y_out.append(y_temp)
                    z_out.append(z_temp)


        tg_new = ROOT.TGraph2D(n, x_out, y_out, z_out)
            
        return tg_new
