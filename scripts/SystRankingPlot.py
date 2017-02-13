#!/usr/bin/env python

import sys
import os
import pickle
from collections import namedtuple

from ROOT import *

AFTER_FIT = 'RooExpandedFitResult_afterFit'
AFTER_FIT_SNAPSHOT = 'snapshot_paramsVals_' + AFTER_FIT

PerParamResult = namedtuple("PerParamResult", "name val err_hi err_lo init_p1s init_m1s final_p1s final_m1s")

def get_parameter(param_list, par_name):
	for i in xrange(param_list.getSize()):
		if param_list[i].GetName() == par_name:
			return param_list[i]

	print "Error: Failed to find parameter '" + par_name + "' in parameter list"
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

	fit_result = Util.FitPdf(w, fit_regions, True, data_set, fit_name, False, "all")

	par.setConstant(False)

	return fit_result

def get_syst_ranking(opts):
	w = Util.GetWorkspaceFromFile(opts.workspace, 'w')
	if not w:
		print "Error: Failed to open workspace"
		sys.exit(1)

	result = w.obj(AFTER_FIT)

	float_pars_initial = result.floatParsInit()
	float_pars_final = result.floatParsFinal()

	poi_best_fit = get_parameter(float_pars_final, opts.parameter)
	if not poi_best_fit:
	 print "POI:", opts.parameter, "is not found in workspace"
         sys.exit(1)
	print "Best fit value for %s: %.2f" % (opts.parameter, poi_best_fit.getVal())

	w.loadSnapshot(AFTER_FIT_SNAPSHOT)

	data_set = w.data('obsData')
	fit_regions = get_fit_regions(opts, w)

	ranking = []

	for i in xrange(float_pars_final.getSize()):
		par_name = float_pars_final[i].GetName()

		if not par_name.startswith("alpha") and not par_name.startswith("gamma"):
			continue

		par_init = get_parameter(float_pars_initial, par_name)
		par_final = get_parameter(float_pars_final, par_name)

		print "Parameter:", par_name
		print "Initial value: %.2f + %.2f - %.2f" % (par_init.getVal(), par_init.getErrorHi(), par_init.getErrorLo())
		print "Final value:   %.2f + %.2f - %.2f" % (par_final.getVal(), par_final.getErrorHi(), par_final.getErrorLo())

		fix_list = [
			(par_name + "_init_p1s", par_init.getErrorHi()),
			(par_name + "_init_m1s", par_init.getErrorLo()),
			(par_name + "_final_p1s", par_final.getErrorHi()),
			(par_name + "_final_p1s", par_final.getErrorLo()),
		]

		poi_shifts = []

		for name, value in fix_list:
			fit_result = refit_fixed(name + "_fixed", par_name, value, w, fit_regions, data_set)

			exp_result = RooExpandedFitResult(fit_result, float_pars_final)
			float_pars = exp_result.floatParsFinal()

			poi = get_parameter(float_pars, opts.parameter)

			poi_shifts.append(poi_best_fit.getVal() - poi.getVal())

		ranking.append(
			PerParamResult(
				par_name,
				par_final.getVal(), par_final.getErrorHi(), par_final.getErrorLo(),
				*poi_shifts
			)
		)

	# now do the stat. only fit
	w.loadSnapshot(AFTER_FIT_SNAPSHOT)
	fit_name = "STAT_ONLY"

	for i in xrange(float_pars_final.getSize()):
		if not par_name.startswith("alpha") and not par_name.startswith("gamma"):
			continue
		par_name = float_pars_final[i].GetName()
		par = w.var(par_name)
		par.setConstant(True)

	fit_result = Util.FitPdf(w, fit_regions, True, data_set, fit_name, False, "all")
	exp_result = RooExpandedFitResult(fit_result, float_pars_final)
	float_pars = exp_result.floatParsFinal()
	poi = get_parameter(float_pars, opts.parameter)

	for i in xrange(float_pars_final.getSize()):
		if not par_name.startswith("alpha") and not par_name.startswith("gamma"):
				continue
		par_name = float_pars_final[i].GetName()
		par = w.var(par_name)
		par.setConstant(False)

	stat_only = (poi.getErrorLo(), poi.getErrorHi())

	# sort by largest shift
	ranking.sort(key=lambda r: max(*[abs(getattr(r, i)) for i in ("init_p1s", "init_m1s", "final_p1s", "final_m1s")]), reverse=True)

	return ranking, stat_only

def nice_param_name(par_name):
	if par_name.startswith("gamma"):
		nice_name = par_name.replace("gamma_stat_", "")
		if nice_name.endswith("_cuts_bin_0"):
			nice_name = nice_name.replace("_cuts_bin_0", "")

		return "#gamma(%s)" % (nice_name)

	elif par_name.startswith("alpha"):
		return par_name[6:]

def get_pull_graph(yaxis, ranking):
	gpull = TGraphAsymmErrors()

	for i, param in enumerate(ranking):
		ypos = yaxis.GetBinCenter(len(ranking)-i)

		gpull.SetPoint(i, param.val, ypos)
		gpull.SetPointEXlow(i, -param.err_lo)
		gpull.SetPointEXhigh(i, param.err_hi)

	return gpull

def get_dmu_graph(yaxis, ranking, final=True):
	gshift = TGraphAsymmErrors()

	largest_shift = 0

	height = yaxis.GetBinWidth(1)

	for i, param in enumerate(ranking):
		ypos = yaxis.GetBinCenter(len(ranking)-i)


		if final:
			p1s = param.final_p1s
			m1s = param.final_m1s
		else:
			p1s = param.init_p1s
			m1s = param.init_m1s		

		up = max(p1s, m1s)
		dn = min(p1s, m1s)

		gshift.SetPoint(i, 0, ypos)
		gshift.SetPointEXlow(i, abs(dn))
		gshift.SetPointEXhigh(i, abs(up))
		gshift.SetPointEYlow(i, 0.35*height)
		gshift.SetPointEYhigh(i, 0.35*height)

		largest_shift = max(largest_shift, abs(dn), abs(up))

	return gshift, largest_shift

### plotting utilities

gROOT.SetBatch(True)

# this style is initialized below
Style = TStyle("ATLAS","Modified ATLAS style")
def _init_style():
	global Style
	# use plain black on white colors
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
	Style.SetPadTickX(1)
	Style.SetPadTickY(1)

	Style.SetTitleXOffset(1.2)
	Style.SetTitleYOffset(1.3)

	Style.SetPalette(51)

	TGaxis.SetMaxDigits(4)

	gROOT.SetStyle("ATLAS")
	gROOT.ForceStyle()

_init_style()

def legend(leg, font_size=0.05):
	leg.SetFillStyle(0)
	leg.SetFillColorAlpha(0, 0.01)
	leg.SetLineColorAlpha(0, 0.01)
	leg.SetBorderSize(1)
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

def set_shift_style(gr, fill_clr, line_clr):
	gr.SetLineColor(line_clr)
	gr.SetFillColor(fill_clr)
	gr.SetLineWidth(2)

def save_canv(canv, base_path, name=None):
	if not name:
		name = canv.GetName()
	canv.SaveAs(os.path.join(base_path, name + ".root"))
	canv.SaveAs(os.path.join(base_path, name + ".pdf"))
###

def plot_ranking(opts, ranking, stat_only):
	from pprint import pprint
	pprint(ranking)
	pprint(stat_only)

	num_params = len(ranking)

	total_width = 800
	total_height = 40 + 40 * num_params

	n_bins_y = num_params+3
	axis = TH2F("axis", "", 1, -2, 2, n_bins_y, 0, 1)

	gpull = get_pull_graph(axis.GetYaxis(), ranking)

	gshift_init, imax = get_dmu_graph(axis.GetYaxis(), ranking, final=False)
	gshift_final, fmax = get_dmu_graph(axis.GetYaxis(), ranking, final=True)

	set_shift_style(gshift_init, kWhite, kBlack)
	set_shift_style(gshift_final, kGray+1, kGray+1)

	stat_only_max = 0
	if opts.stat:
		stat_only_graph = TGraphAsymmErrors()
		stat_only_graph.SetPoint(0, 0, axis.GetYaxis().GetBinCenter(num_params+1))
		stat_only_graph.SetPointEXlow(0, abs(stat_only[0]))
		stat_only_graph.SetPointEXhigh(0, abs(stat_only[1]))
		stat_only_graph.SetLineWidth(2)

		stat_only_max = max(abs(stat_only[0]), abs(stat_only[1]))

	shift_max = max(imax, fmax, stat_only_max) * 1.3

	axis.GetXaxis().SetRangeUser(-shift_max, shift_max)
	print -shift_max, shift_max

	axis = TH2F("axis", "", 1, -shift_max, shift_max, n_bins_y, 0, 1)

	axis.GetXaxis().SetTitle("#Delta{poi}".format(poi=opts.param_title))
	axis.GetXaxis().CenterTitle()

	for i, param in enumerate(ranking):
		axis.GetYaxis().SetBinLabel(num_params - i, nice_param_name(param.name))
	if opts.stat:
		axis.GetYaxis().SetBinLabel(num_params +1, "Data stat.")

	axis.GetYaxis().SetLabelSize(0.04)
	axis.GetYaxis().SetTickLength(0)

	axis.GetXaxis().SetLabelSize(0.035)
	axis.GetXaxis().SetTitleSize(0.040)
	axis.GetXaxis().SetNdivisions(506)

	dotted_line = TLine()
	dotted_line.SetLineColor(kBlack)
	dotted_line.SetLineStyle(kDotted)

	leg_height = 0.07 if not opts.post_fit else 0.035
	leg = TLegend(0.03, 0.97, .38, 0.97 - leg_height)
	legend(leg, font_size=0.025)
	if not opts.post_fit:
		leg.AddEntry(gshift_init, "Pre-fit impact on %s" % opts.param_title, "F")
	leg.AddEntry(gshift_final, "Post-fit impact on %s" % opts.param_title, "F")

	canv = TCanvas("cranking", "", total_width, total_height)
	canv.SetLeftMargin(0.4)
	canv.SetBottomMargin(0.12)
	axis.Draw("axis")

	if opts.stat:
		gStyle.SetEndErrorSize(5)
		stat_only_graph.Draw("e5")
		stat_only_graph.Draw("||")
		dotted_line.DrawLine(stat_only[0], 0, stat_only[0], 1)
		dotted_line.DrawLine(stat_only[1], 0, stat_only[1], 1)

	if not opts.post_fit:
		gshift_init.Draw("5")
	gshift_final.Draw("5")

	dotted_line.DrawLine(0, 0, 0, 1)

	atlas(opts.atlas, x=.42, rel=.6)
	sqrts_lumi(opts.sqrts, opts.lumi, y=0.89, x=.67, rel=.5)
	leg.Draw()

	save_canv(canv, opts.output, opts.name)

def parse_opts():
	import argparse

	parser = argparse.ArgumentParser()
	parser.add_argument("-w", "--workspace", required=True, help="Workspace")
	parser.add_argument("-f", "--fit-regions", required=True, help="All fit regions to use, comma separated")
	parser.add_argument("-p", "--parameter", default="mu_signal", help="Parameter of interest")
	parser.add_argument("--param-title", default="#mu_{signal}", help="Nice title for the POI")

	parser.add_argument("-o", "--output", default="plots/", help="Output directory")
	parser.add_argument("-n", "--name", default="ranking", help="Output name")

	parser.add_argument("--max-np", type=int, default=20, help="Max number of NPs to show")
	parser.add_argument("--stat", action="store_true", help="Show stat. only uncertainty")
	parser.add_argument("-i", "--input", help="Use stored fit results from last run, do not do the re-fitting again. Useful if you only want to change the layout")

	parser.add_argument("--post-fit", action="store_true", help="Only show post-fit impact on the POI")

	parser.add_argument("--atlas", default="Internal", help="ATLAS label")
	parser.add_argument("--sqrts", type=float, default=13, help="sqrt(s)")
	parser.add_argument("--lumi", type=float, default=36.5, help="Luminosity in /fb")


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

	if not opts.input:
		ranking, stat_only = get_syst_ranking(opts)

		pfile = open(os.path.join(opts.output, opts.name + ".data"), "w")
		pickle.dump((ranking, stat_only), pfile)
		pfile.close()
	else:
		pfile = open(os.path.join(opts.output, opts.name + ".data"), "r")
		ranking, stat_only = pickle.load(pfile)
		pfile.close()

	if opts.max_np > 0 and len(ranking) > opts.max_np:
		ranking = ranking[:opts.max_np]

	plot_ranking(opts, ranking, stat_only)


if __name__ == '__main__':
	main()
