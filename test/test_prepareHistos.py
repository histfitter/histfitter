import ROOT
ROOT.gROOT.SetBatch(True)

import pytest

from array import array

# the thing we test
import prepareHistos

# get the object
prepareHistosObj = prepareHistos.PrepareHistos()

# set these two to None to not confuse the __del__ method
prepareHistosObj.cacheFile = None
prepareHistosObj.cache2File = None

# make a proxy channel
prepareHistosObj.configMgr.analysisName = "ana"
fit = prepareHistosObj.configMgr.addFitConfig("fit")
channel = fit.addChannel("var",["reg"],4,10,80)

# set the proxy channel
prepareHistosObj.channel = channel

def test_rebin():
  # define some bin edges
  edges = [10, 20, 40, 80]

  # simulate already filled bin edges
  prepareHistosObj.regBins["R1"] = edges

  # make histogram with same edges
  array_edges = array('d', edges)
  h = ROOT.TH1D("R1h","R1h", len(array_edges)-1, array_edges)
  prepareHistosObj.configMgr.hists["R1h"] = h

  # do the mapping
  prepareHistosObj.mapIntoEquidistant("R1h")

  # check that the new histograms has equidistant bins [0, 1, ..., N]
  bins = []
  h = prepareHistosObj.configMgr.hists["R1h"].Clone()
  for i in range(1, h.GetNbinsX()+1):
    bins += [h.GetBinLowEdge(i)]
  bins += [h.GetBinLowEdge(h.GetNbinsX()) + h.GetBinWidth(h.GetNbinsX())]
  assert bins == list(range(len(bins)))

def test_rebin_exception():
  # define some bin edges
  edges1 = [10, 20, 40, 80]
  edges2 = [10, 20, 41, 80]

  # simulate already filled bin edges
  prepareHistosObj.regBins["R2"] = edges1

  # make histogram with same edges
  array_edges = array('d', edges2)
  h = ROOT.TH1D("R2h","R2h", len(array_edges)-1, array_edges)
  prepareHistosObj.configMgr.hists["R2h"] = h

  # do the mapping and require it to fail
  with pytest.raises(Exception) as e_info:
    prepareHistosObj.mapIntoEquidistant("R2h")
