# this style is initialized below
from ROOT import gROOT, gPad, TGaxis, TLatex, TStyle
Style = TStyle("ATLAS","Modified ATLAS style")
def ATLASStyle():
    global Style
    Style.SetOptStat(0)
    _icol=0
    Style.SetFrameBorderMode(_icol)
    Style.SetFrameFillColor(_icol)
    Style.SetCanvasBorderMode(_icol)
    Style.SetPadBorderMode(_icol)
    Style.SetPadColor(_icol)
    Style.SetCanvasColor(_icol)
    Style.SetStatColor(_icol)

    Style.SetPaperSize(20,26)

    Style.SetPadTopMargin(0.05)
    Style.SetPadRightMargin(0.05)
    Style.SetPadBottomMargin(0.16)
    Style.SetPadLeftMargin(0.16)

    Style.SetTitleXOffset(1.4)
    Style.SetTitleYOffset(1.4)

    _font=42
    _tsize=0.05

    Style.SetTextFont(_font)
    Style.SetTextSize(_tsize)

    Style.SetLabelFont(_font, "x")
    Style.SetTitleFont(_font, "x")
    Style.SetLabelFont(_font, "y")
    Style.SetTitleFont(_font, "y")
    Style.SetLabelFont(_font, "z")
    Style.SetTitleFont(_font, "z")

    Style.SetLabelSize(_tsize, "x")
    Style.SetTitleSize(_tsize, "x")
    Style.SetLabelSize(_tsize, "y")
    Style.SetTitleSize(_tsize, "y")
    Style.SetLabelSize(_tsize, "z")
    Style.SetTitleSize(_tsize, "z")

    Style.SetMarkerStyle(20)
    Style.SetMarkerSize(1.2)
    Style.SetHistLineWidth(2)
    Style.SetLineStyleString(2, "[12 12]")

    Style.SetEndErrorSize(0.)
    Style.SetOptTitle(0)
    Style.SetOptFit(0)
    Style.SetPadTickX(1)
    Style.SetPadTickY(1)

    Style.SetPalette(51)

    TGaxis.SetMaxDigits(4)

    gROOT.SetStyle("ATLAS")
    gROOT.ForceStyle()


def ATLASLabel(x, y, text, color=1):
    l = TLatex()
    l.SetNDC()
    l.SetTextFont(72)
    l.SetTextColor(color)
    l.DrawLatex(x, y, "ATLAS")

    if text:
        delx = 0.115*696*gPad.GetWh()/(472*gPad.GetWw())
        p = TLatex() 
        p.SetNDC()
        p.SetTextFont(42)
        p.SetTextColor(color)
        p.DrawLatex(x+delx, y, text)

        return l, p
    return l
