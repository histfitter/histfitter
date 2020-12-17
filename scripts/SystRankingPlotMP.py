#!/usr/bin/env python

import sys
import os
import pickle
from collections import namedtuple
from copy import deepcopy

from ROOT import *

AFTER_FIT = 'RooExpandedFitResult_afterFit'
AFTER_FIT_SNAPSHOT = 'snapshot_paramsVals_' + AFTER_FIT

PerParamResult = namedtuple("PerParamResult", "name val err_hi err_lo init_p1s init_m1s final_p1s final_m1s")

from multiprocessing import Pool, cpu_count

# map to rename the NPs
renameAlpha = {
  "MET_SoftTrk_ResoPara":"E^{miss}_{T} para. resolution",
  "MET_SoftTrk_ResoPerp":"E^{miss}_{T} perp. resolution",
  "MET_SoftTrk_Scale":"E^{miss}_{T} scale",
  "JET_GroupedNP_1":"Jet energy scale NP 1",
  "JET_GroupedNP_2":"Jet energy scale NP 2",
  "JET_GroupedNP_3":"Jet energy scale NP 3",
  "FT_EFF_B_systematics":"Flavor tagging b-jet",
  "FT_EFF_C_systematics":"Flavor tagging c-jet",
  "FT_EFF_Light_systematics":"Flavor tagging light-jet",
  "TheoryTTbar_QCDScale":"t#bar{t} QCD scale",
  "TheorySherpa_QCDScale":"Sherpa QCD scale",
  "TheorySherpa_PDFVariation":"Sherpa PDF variation",
  "EL_EFF_ID_TOTAL_1NPCOR_PLUS_UNCOR":"El. ID efficiency",
  "EL_EFF_Reco_TOTAL_1NPCOR_PLUS_UNCOR":"El. reco. efficiency",
  "EL_EFF_Iso_TOTAL_1NPCOR_PLUS_UNCOR":"El. iso. efficiency",
  "EL_EFF_Trig_TOTAL_1NPCOR_PLUS_UNCOR":"El. trig. efficiency",
  "FakeFactorsMuon":"Muon fake factor",
  "FakeFactorsElectron":"Electron fake factor",
  "MUON_EFF_RECO_SYS":"Muon reco. efficiency",
  "MUON_EFF_ISO_SYS":"Muon iso. efficiency",
  "MUON_EFF_TTVA_SYS":"Muon TTVA",
  "MUON_EFF_TrigSystUncertainty":"Muon trig. efficiency",
  "JET_JER_SINGLE_NP":"Jet energy resolution",
  "PileUp":"Pileup modeling",
}

ready_list = []
def dummy_func(index):
    global ready_list
    ready_list.append(index)

def get_syst_ranking(opts):
    global ready_list
    w = Util.GetWorkspaceFromFile(opts.workspace, 'w')
    if not w:
        print("Error: Failed to open workspace")
        sys.exit(1)

    result = w.obj(AFTER_FIT)

    float_pars_initial = result.floatParsInit()
    float_pars_final = result.floatParsFinal()

    ranking = []

    if opts.maxCores < 0:
      pool = Pool(processes=cpu_count())
    else:
      pool = Pool(processes=opts.maxCores)
    results = {}

    for i in range(float_pars_final.getSize()):
        par_name = float_pars_final[i].GetName()
        fileNamePar = os.path.join(opts.output, opts.name + "_%s.data" % par_name)

        if not opts.noFit and not os.path.isfile(fileNamePar):
          print("submitting job for %s ..." % par_name)
          results[i] = pool.apply_async(refit_parameter, args=(opts, i), callback=dummy_func)
          for ready in ready_list:
            results[ready].wait()
            del results[ready]
          ready_list = []

    # wait for all jobs to complete
    pool.close()
    pool.join()

    for i in range(float_pars_final.getSize()):
        par_name = float_pars_final[i].GetName()
        fileNamePar = os.path.join(opts.output, opts.name + "_%s.data" % par_name)
        if os.path.isfile(fileNamePar):
          print(f"reading {par_name} from file {fileNamePar}")
          Param = pickle.load( open(fileNamePar))
          ranking.append( Param )

    return ranking


def get_parameter(param_list, par_name):
    for i in range(param_list.getSize()):
        if param_list[i].GetName() == par_name:
            return param_list[i]

    print("Error: Failed to find parameter '" + par_name + "' in parameter list")
    return None

def get_fit_regions(opts, w):
    region_cat = w.obj("channelCat")

    all_regions = []
    for reg in opts.regions:
        full_name = Util.GetFullRegionName(region_cat, reg)
        all_regions.append(full_name.Data())
    fit_regions = ",".join(all_regions)
    return fit_regions

def refit_fixed(fit_name, par_name, value, w, fit_regions, data_set):
    w.loadSnapshot(AFTER_FIT_SNAPSHOT)
    par = w.var(par_name)
    par.setVal(value)
    par.setConstant(True)

    fit_result = Util.FitPdf(w, fit_regions, True, data_set, fit_name, True, "all")

    par.setConstant(False)

    return fit_result

def refit_parameter(opts, index):

    w = Util.GetWorkspaceFromFile(opts.workspace, 'w')
    if not w:
        print("Error: Failed to open workspace")
        sys.exit(1)

    result = w.obj(AFTER_FIT)

    float_pars_initial = result.floatParsInit()
    float_pars_final = result.floatParsFinal()

    poi_best_fit = get_parameter(float_pars_final, opts.parameter)
    if not poi_best_fit:
        print("POI:", opts.parameter, "is not found in workspace")
        sys.exit(1)
    print(f"Best fit value for {opts.parameter}: {poi_best_fit.getVal():f}")

    w.loadSnapshot(AFTER_FIT_SNAPSHOT)

    data_set = w.data(opts.dataSet)
    fit_regions = get_fit_regions(opts, w)
    par_name = float_pars_final[index].GetName()
    fileNamePar = os.path.join(opts.output, opts.name + "_%s.data" % par_name)

    if par_name.startswith(opts.parameter):
        return None
    if opts.sysOnly and par_name.startswith("gamma"):
        return None
    if opts.statOnly and par_name.startswith("alpha"):
        return None
    if not par_name.startswith("alpha") and not par_name.startswith("gamma") and not par_name.startswith("mu"):
        return None

    par_init = get_parameter(float_pars_initial, par_name)
    par_final = get_parameter(float_pars_final, par_name)

    print("Parameter:", par_name)
    print(f"Initial value: {par_init.getVal():.2f} + {par_init.getErrorHi():.2f} - {par_init.getErrorLo():.2f}")
    print(f"Final value:   {par_final.getVal():.2f} + {par_final.getErrorHi():.2f} - {par_final.getErrorLo():.2f}")

    fix_list = [
            (par_name + "_init_p1s", par_init.getErrorHi()),
            (par_name + "_init_m1s", par_init.getErrorLo()),
            (par_name + "_final_p1s", par_final.getErrorHi()),
            (par_name + "_final_m1s", par_final.getErrorLo()),
    ]

    poi_shifts = []

    for name, value in fix_list:
        if "init" in name:
            value+=par_init.getVal()
        elif "final" in name:
            value+=par_final.getVal()
        else:
            print("FATAL in get parameter nominal value")
            sys.exit()

        if par_name.startswith("gamma") and opts.minGamma != None and value < opts.minGamma:
          print(f"Truncating parameter {par_name} at {opts.minGamma}")
          value = opts.minGamma

        fit_result = refit_fixed(name + "_fixed", par_name, value, w, fit_regions, data_set)

        exp_result = RooExpandedFitResult(fit_result, float_pars_final)
        float_pars = exp_result.floatParsFinal()

        poi = get_parameter(float_pars, opts.parameter)

        poi_shifts.append(poi_best_fit.getVal() - poi.getVal())

    Param = PerParamResult(
                      par_name,
                      par_final.getVal(), par_final.getErrorHi(), par_final.getErrorLo(),
                      *poi_shifts
                    )
    pickle.dump(Param, open(fileNamePar, "w") )

def nice_param_name(par_name):
    if par_name.startswith("gamma"):
        nice_name = par_name.replace("gamma_stat_", "")
        nice_name = nice_name.replace("_"," ")
        return "#gamma(%s)" % (nice_name)

    elif par_name.startswith("alpha"):
        if par_name[6:] in list(renameAlpha.keys()):
          return renameAlpha[par_name[6:]]
        else:
          print("Not renamed: ",par_name[6:])
          return par_name[6:]
    elif par_name.startswith("mu"):
        return "#mu_{"+par_name[3:]+"}"

def get_dmu_graph(n_bins_y, ranking, final=True):
  gshift = TGraphAsymmErrors()
  gpulls = TGraphAsymmErrors()
  gpulls_mu = TGraphAsymmErrors()
  largest_shift = 0

  height = 1.

  for i, param in enumerate(ranking):
    ypos = n_bins_y-(i+0.5)
    
    if final:
      p1s = param.final_p1s
      m1s = param.final_m1s
      print(param.name," ",param.final_p1s," ",param.final_m1s)
    else:
      p1s = param.init_p1s
      m1s = param.init_m1s    
      print(param.name," ",param.init_p1s," ",param.init_m1s)

    up_norm = max(p1s, m1s)
    dn_norm = min(p1s, m1s)

    up = max(p1s,m1s)
    dn = min(p1s,m1s)
    center = (up+dn)/2.

    # mu_sig shift
    if not (param.name.startswith("mu") and not final):
      gshift.SetPoint(i, center, ypos)
      gshift.SetPointEXlow(i, abs(center-dn))
      gshift.SetPointEXhigh(i, abs(center-up))
      gshift.SetPointEYlow(i, 0.35*height)
      gshift.SetPointEYhigh(i, 0.35*height)
      gshift.GetXaxis().SetNdivisions(0)
    # pulls
    if param.name.startswith("mu"):
      gpulls_mu.SetPoint(gpulls_mu.GetN(), param.val, ypos)
      gpulls_mu.SetPointEXlow(gpulls_mu.GetN()-1, -param.err_lo)
      gpulls_mu.SetPointEXhigh(gpulls_mu.GetN()-1, param.err_hi)
      gpulls_mu.SetPointEYlow(gpulls_mu.GetN()-1, 0.)
      gpulls_mu.SetPointEYhigh(gpulls_mu.GetN()-1, 0.)
    else:
      gpulls.SetPoint(gpulls.GetN(), param.val, ypos)
      if param.name.startswith("gamma"):
        gpulls.SetPointEXlow(gpulls.GetN()-1,  -param.err_lo if (param.val+param.err_lo > 0) else param.val)
        gpulls.SetPointEXhigh(gpulls.GetN()-1, param.err_hi)
      else:
        gpulls.SetPointEXlow(gpulls.GetN()-1,  -param.err_lo)
        gpulls.SetPointEXhigh(gpulls.GetN()-1, param.err_hi)
      gpulls.SetPointEYlow(gpulls.GetN()-1, 0.)
      gpulls.SetPointEYhigh(gpulls.GetN()-1, 0.)

    largest_shift = max(largest_shift, abs(dn), abs(up))

  return gshift, largest_shift, gpulls, gpulls_mu

gROOT.SetBatch(True)

# this style is initialized below
Style = TStyle("ATLAS","Modified ATLAS style")
def _init_style():
    global Style
    Style.SetOptStat(0)
    _icol=0
    Style.SetFrameBorderMode(_icol)
    Style.SetCanvasBorderMode(_icol)
    Style.SetPadBorderMode(_icol)
    Style.SetPadColor(_icol)
    Style.SetCanvasColor(_icol)
    Style.SetStatColor(_icol)
    Style.SetPaperSize(20,26)
    Style.SetPadTopMargin(0.06)
    Style.SetPadRightMargin(0.05)
    Style.SetPadBottomMargin(0.16)
    Style.SetPadLeftMargin(0.16)
    Style.SetFrameFillColor(_icol)

    _font=42
    _tsize=0.06
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
    Style.SetPadTickX(0)
    Style.SetPadTickY(0)
    Style.SetTitleXOffset(1.2)
    Style.SetTitleYOffset(1.3)
    Style.SetPalette(51)
    TGaxis.SetMaxDigits(4)
    gROOT.SetStyle("ATLAS")
    gROOT.ForceStyle()

_init_style()

def legend(leg, font_size=0.05):
    leg.SetFillStyle(0)
    leg.SetFillColor(0)
    leg.SetLineColor(0)
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    leg.SetTextSize(font_size)

OBJECTS = [] # store some objects so they don't get GC'd
def atlas(text, x=0.18, y=0.89, text_offset=0.13, rel=.8):
    atl_str = TLatex(x, y, "ATLAS")
    atl_str.SetNDC()
    atl_str.SetName("atlas_str")
    atl_str.SetTextFont(72)
    atl_str.SetTextSize(rel * atl_str.GetTextSize())

    atl_str.Draw("same")
    global OBJECTS
    OBJECTS.append(atl_str)

    if text:
        add_str = TLatex(x+text_offset, y, text)
        add_str.SetNDC()
        add_str.SetName("atlas_add_str")
        add_str.SetTextSize(rel * add_str.GetTextSize())
        OBJECTS.append(add_str)
        add_str.Draw("same")

def _get_nice_lumi_unit(lumi_fb):
    if lumi_fb > 0.5:
        return lumi_fb, "fb"

    lumi_pb = lumi_fb * 1e3
    if lumi_pb > 0.5:
        return lumi_pb, "pb"

    lumi_nb = lumi_pb * 1e3
    return lumi_nb, "nb"


def sqrts_lumi(sqrts, lumi_fb, x=0.36, y=0.84, rel=.8):
    lumi_val, lumi_unit = _get_nice_lumi_unit(lumi_fb)

    sl_str = TLatex(x, y, "#sqrt{s} = %d TeV, %.1f %s^{-1}" % (sqrts, lumi_val, lumi_unit))
    sl_str.SetNDC()
    sl_str.SetName("sl_str")
    sl_str.SetTextSize(rel * sl_str.GetTextSize())

    sl_str.Draw("same")
    global OBJECTS
    OBJECTS.append(sl_str)

def text(text, x=0.36, y=0.84, rel=.8, color = kBlack):

    sl_str = TLatex(x, y, text)
    sl_str.SetNDC()
    sl_str.SetName("sl_str")
    sl_str.SetTextSize(rel * sl_str.GetTextSize())
    sl_str.SetTextColor(color)

    sl_str.Draw("same")
    global OBJECTS
    OBJECTS.append(sl_str)

def set_shift_style(gr, fill_clr, line_clr, fill_style = 1001):
    gr.SetFillStyle(fill_style)
    gr.SetLineColor(line_clr)
    gr.SetFillColor(fill_clr)
    gr.SetLineWidth(2)

def save_canv(canv, base_path, name=None):
    if not name:
        name = canv.GetName()
    canv.SaveAs(os.path.join(base_path, name + ".root"))
    canv.SaveAs(os.path.join(base_path, name + ".pdf"))
    canv.SaveAs(os.path.join(base_path, name + ".eps"))

def plot_ranking(opts, ranking):
  from pprint import pprint
  pprint(ranking)

  # sort by largest shift
  rankingTemp = []
  if opts.statOnly:
    for elem in ranking:
      if not (elem.name.startswith("mu") or elem.name.startswith("alpha")):
        rankingTemp.append(elem)
    ranking = rankingTemp
  if opts.sysOnly:
    for elem in ranking:
      print(elem)
      if not elem.name.startswith("gamma"):
        rankingTemp.append(elem)
    ranking = rankingTemp

  ranking.sort(key=lambda r: max(*(abs(getattr(r, i)) for i in ("final_p1s", "final_m1s"))), reverse=True)
  if opts.max_np > 0 and len(ranking) > opts.max_np:
    ranking = ranking[:opts.max_np]
  # get workspace
  w = Util.GetWorkspaceFromFile(opts.workspace, 'w')
  if not w:
    print("Error: Failed to open workspace")
    sys.exit(1)

  result = w.obj(AFTER_FIT)
  float_pars_final = result.floatParsFinal()
  poi_best_fit = get_parameter(float_pars_final, opts.parameter)
  print(f"Best fit value for {opts.parameter}: {poi_best_fit.getVal():f}")

  num_params = len(ranking)
  total_width = 800
  total_height = 120 + 40 * opts.max_np
  leftMargin = 0.3
  topMargin = 0.05
  n_bins_y = num_params+5

  if opts.statOnly:
    fpull = TH2F("fpull", "", 1, 0., 2., n_bins_y, 0, n_bins_y)
  else:
    fpull = TH2F("fpull", "", 1, -1.5, 1.5, n_bins_y, 0, n_bins_y)

  if not opts.post_fit:
    gshift_init, imax, gpulls, gpulls_mu = get_dmu_graph(n_bins_y-5, ranking, final=False)
    set_shift_style(gshift_init, kYellow-9, kYellow-9)
  gshift_final, fmax, gpulls, gpulls_mu = get_dmu_graph(n_bins_y-5, ranking, final=True)
  set_shift_style(gshift_final, kBlue+2, kBlue+2, 3004)
  shift_max = max(imax if not opts.post_fit else 0, fmax) * 1.3

  # canvas
  canv = TCanvas("rankingCanvas", "", total_width, total_height)
  canv.SetLeftMargin(leftMargin)
  canv.SetTopMargin(topMargin)
  canv.SetBottomMargin(0.1)

  # axis for mu_sig shifts
  axis = TH2F("axis", "", 1, -shift_max, shift_max, n_bins_y, 0, n_bins_y)
  for i, param in enumerate(ranking):
    axis.GetYaxis().SetBinLabel(num_params - i, nice_param_name(param.name))
  axis.GetYaxis().SetLabelSize(0.030)
  axis.GetYaxis().SetTickLength(0)
  axis.GetXaxis().SetLabelSize(0.0)
  axis.GetXaxis().SetTitleSize(0.0)
  axis.GetXaxis().SetNdivisions(0)
  axis.Draw()

  # legend
  temp_red = TGraph()
  temp_red.SetLineColor(kRed)
  temp_red.SetMarkerColor(kRed)
  temp_red.SetMarkerStyle(24)

  leg_height = 0.13
  leg_lines = 4
  if opts.post_fit:
    leg_lines -= 1
  if opts.statOnly:
    leg_lines -= 1
  if opts.no_pulls:
    leg_lines -= 2

  leg = TLegend(0.31, 0.92, 0.5, 0.92 - leg_height*(leg_lines/4.))
  legend(leg, font_size=0.030)
  if not opts.post_fit:
    leg.AddEntry(gshift_init, "#font[42]{Pre-fit  impact on %s}" % opts.param_title, "F")
  leg.AddEntry(gshift_final, "#font[42]{Post-fit impact on %s}" % opts.param_title, "F")
  if not opts.no_pulls:
    if opts.statOnly:
      leg.AddEntry(gpulls, "#font[42]{After fit NP #pm stat. unc.}", "LP")
    else:
      leg.AddEntry(gpulls, "#font[42]{Nuis. param. pull}", "LP")
      leg.AddEntry(temp_red, "#font[42]{Fitted yield}", "LP")

  ## plot boxes
  color = TColor(9999, 246/255., 230/255., 247/255.);
  boxes = []
  for i in range(2,num_params+1,2):
    height = axis.GetYaxis().GetBinWidth(i)
    center = axis.GetYaxis().GetBinCenter(i)
    canv.Update()
    xmin = gPad.GetUxmin()
    xmax = gPad.GetUxmax()
    box = deepcopy(TBox(xmin,center - height/2.,xmax, center + height/2.))
    box.SetFillColor(9999)
    box.Draw()
    boxes += [box]

  #Plot a second x-axis
  ypos = canv.GetFrame().GetY2()
  ymin = canv.GetFrame().GetY1()
  canvSet = axis.GetXaxis()
  xmin_def = canvSet.GetXmin()
  xmax_def = canvSet.GetXmax()

  x_axis2 = TGaxis(xmin_def,ypos,xmax_def,ypos,xmin_def,xmax_def,2,"-")
  x_axis2.SetLabelFont(42)
  x_axis2.SetNdivisions(4)
  x_axis2.SetLabelSize(0.040)
  x_axis2.SetLineColor(kBlue+2)
  x_axis2.SetTextColor(kBlue+2)
  x_axis2.SetLabelColor(kBlue+2)
  x_axis2.SetNdivisions(505)
  if not opts.no_pulls:
    x_axis2.Draw("axis")

  x_axis3 = TGaxis(xmin_def,num_params,xmax_def,num_params,xmin_def,xmax_def,2,"-")
  x_axis3.SetNdivisions(4)
  x_axis3.SetLabelSize(0)
  x_axis3.SetLineColor(kBlue+2)
  x_axis3.SetTextColor(kBlue+2)
  x_axis3.SetNdivisions(505)
  x_axis3.Draw("axis")

  # start drawing everything
  if not opts.post_fit:
    gshift_init.Draw("5")
  gshift_final.Draw("5")
  leg.Draw()

  overlay =  TPad("pad2","",0,0,1,1);
  overlay.SetLeftMargin(leftMargin)
  overlay.SetTopMargin(topMargin)
  overlay.SetBottomMargin(0.1)
  overlay.SetFillStyle(4000);
  overlay.SetFrameFillStyle(0);
  overlay.Draw()
  overlay.cd()

  if opts.no_pulls:
    # override the pull axis with the ranking axis
    fpull = TH2F("fpull", "", 1, -shift_max, shift_max, n_bins_y, 0, n_bins_y)
  fpull.GetYaxis().SetLabelSize(0)  
  fpull.GetYaxis().SetNdivisions(0)
  if not opts.no_pulls:
    fpull.GetXaxis().SetNdivisions(10)
  if opts.no_pulls:
    fpull.GetXaxis().SetTitle("#Delta#mu_{S}")
  elif opts.statOnly:
    fpull.GetXaxis().SetTitle("After fit NP  (N_{i} = #gamma_{i} (s+b)_{i})")
  elif opts.sysOnly:
    fpull.GetXaxis().SetTitle("After fit NP  (#theta - #theta_{0})/#Delta#theta")
  else:
    fpull.GetXaxis().SetTitle("After fit NP  (#theta - #theta_{0})/#Delta#theta or (N_{i} = #gamma_{i} (s+b)_{i})")
  fpull.GetXaxis().SetLabelFont(42)
  fpull.GetXaxis().SetLabelSize(0.040)
  fpull.GetXaxis().SetTitleSize(0.040)
  fpull.GetXaxis().SetTitleOffset(1)
  fpull.Draw()
  gpulls.SetLineWidth(2)
  gpulls_mu.SetLineWidth(2)
  gpulls_mu.SetMarkerStyle(24)
  gpulls_mu.SetLineColor(kRed)
  gpulls_mu.SetMarkerColor(kRed)
  if not opts.no_pulls:
    gpulls_mu.Draw("e p Same")
    gpulls.Draw("e p Same")

  dotted_line = TLine()
  dotted_line.SetLineColor(kBlack)
  dotted_line.SetLineStyle(kDotted)
  dotted_line.SetLineWidth(2)

  if  opts.no_pulls:
    dotted_line.DrawLine (shift_max/2, 0,  shift_max/2, num_params)
    dotted_line.DrawLine(-shift_max/2, 0, -shift_max/2, num_params)
    dotted_line.DrawLine(0, 0, 0, num_params)
  elif opts.statOnly:
    dotted_line.DrawLine(1.5, 0, 1.5, num_params)
    dotted_line.DrawLine(0.5, 0, 0.5, num_params)
    dotted_line.DrawLine(1, 0, 1, num_params)
    fpull.GetXaxis().SetNdivisions(5)
  else:
    dotted_line.DrawLine(0, 0, 0, num_params)
    dotted_line.DrawLine(-1, 0, -1, num_params)
    dotted_line.DrawLine(1, 0, 1, num_params)

  atlas(opts.atlas, x=.65, rel=0.55, y=0.89)
  sqrts_lumi(opts.sqrts, opts.lumi, x=.65, y=0.86, rel=0.55)
  text(opts.text1, x=.65, y=0.83, rel=0.55)
  text(opts.text2, x=.65, y=0.80, rel=0.55)
  if not opts.no_pulls:
    text("#Delta#mu_{S}", x=.2, y=0.95, rel=0.55, color=kBlue+2)
  leg.Draw()

  save_canv(canv, opts.output, opts.name)

def parse_opts():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--workspace", required=True, help="Workspace")
    parser.add_argument("-f", "--fit-regions", required=True, help="All fit regions to use, comma separated")
    parser.add_argument("-p", "--parameter", default="mu_signal", help="Parameter of interest")
    parser.add_argument("-o", "--output", default="plots/", help="Output directory")
    parser.add_argument("-n", "--name", default="ranking", help="Output name")
    parser.add_argument("--maxCores", type=int, default=1, help="Number of used cores. One core is default. Use -1 for all cores.")
    parser.add_argument("--noFit", action="store_true", help="Don't do any fits, just take the existing results.")

    parser.add_argument("--dataSet", default="obsData", help="obsData or asimovData")

    parser.add_argument("--post-fit", action="store_true", help="Only show post-fit impact on the POI")
    parser.add_argument("--no-pulls", action="store_true", help="Do not overlay the NP pulls")
    parser.add_argument("--sysOnly", action="store_true", help="Use only alpha and mu NPs, not gammas")
    parser.add_argument("--statOnly", action="store_true", help="Use only gamma NPs")
    parser.add_argument("--minGamma", type=float, default=None, help="Truncate gamma parameters below this value. Do nothing if default value.")

    parser.add_argument("--atlas", default="Internal", help="ATLAS label")
    parser.add_argument("--sqrts", type=float, default=13, help="sqrt(s)")
    parser.add_argument("--lumi", type=float, default=36.5, help="Luminosity in /fb")
    parser.add_argument("--text1", default="", help="some space for additional text")
    parser.add_argument("--text2", default="", help="some space for additional text")
    parser.add_argument("--param-title", default="#mu_{S}", help="Nice title for the POI")
    parser.add_argument("--max-np", type=int, default=20, help="Max number of NPs to show")

    opts = parser.parse_args()

    opts.regions = opts.fit_regions.split(",")

    return opts

def main():
    opts = parse_opts()

    gSystem.Load("libSusyFitter.so")
    # this is strange but in oder to access some HF
    # objects from the library we need to somehow touch
    # (ROOT.)LimitResult
    _ = LimitResult

    ranking = get_syst_ranking(opts)

    plot_ranking(opts, ranking)


if __name__ == '__main__':
    main()
