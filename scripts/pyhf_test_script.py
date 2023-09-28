#!/usr/bin/env python

import json
import pyhf
import argparse
import numpy as np

#HistFitter imports
from usepyhf import hypotest
from usepyhf import plot
from usepyhf import inference

#Arguments
parser = argparse.ArgumentParser(description="pyhf script options:")
parser.add_argument("-a", "--ana-name", help="The name of the analysis folder", default="")
parser.add_argument("-n", "--config-name", help="The name of the config file", default="")
parser.add_argument("-t", "--test-stat", help="The test statistics. Default 'qtilde'", default="qtilde")
parser.add_argument("-v", "--poi-value", help="The value of the parameter of interest", type=float, default=None)
args = parser.parse_args()

#Backend
pyhf.set_backend(pyhf.tensorlib, pyhf.optimize.minuit_optimizer(tolerance=1e-3))

#Set variable names
poi_value = args.poi_value
test_stat = args.test_stat
config_name = args.config_name
ana_name = args.ana_name
json_file_path = f"./json/{ana_name}/{ana_name}_{config_name}.json"

with open(json_file_path) as serialized:
    json_file = json.load(serialized)

workspace = pyhf.Workspace(json_file)
model = workspace.model()
data = workspace.data(model)

#Print information
print(f"  channels: {model.config.channels}")
print(f"     nbins: {model.config.channel_nbins}")
print(f"   samples: {model.config.samples}")
print(f" modifiers: {model.config.modifiers}")
print(f"parameters: {model.config.parameters}")
print(f"  nauxdata: {model.config.nauxdata}")
print(f"   auxdata: {model.config.auxdata}")
print(f"samples (workspace): {workspace.samples}")
print(f"samples (  model  ): {model.config.samples}")
print("---------------------------------")

#Make a plot
fig, ax = plot.brazil_plot(workspace)
fig.savefig(f"./results/{ana_name}/{config_name}.png")

#p values
print("Exclusion")
hypotest.p_values_excl(workspace, test_stat)

print("---------------------------------")

#p values
print("BkgOnly")
hypotest.p_values_disc(workspace, test_stat)
print("---------------------------------")

#Upper limit
print(pyhf.infer.intervals.upper_limits.upper_limit(data, model, scan=np.linspace(0,5,50)))

#Maximum likelihood fit
bestfit_pars = inference.mle_fit(workspace)
