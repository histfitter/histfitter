#!/usr/bin/env python

import json
import pyhf
import argparse
import numpy as np

#HistFitter imports
from hfpyhf import hypotest
from hfpyhf import plot

#Arguments
parser = argparse.ArgumentParser(description="pyhf script options:")
parser.add_argument("-a", "--ana-name", help="The name of the analysis folder", default="")
parser.add_argument("-j", "--json-file", help="The path to the json file for the analysis", default="")
parser.add_argument("-n", "--config-name", help="The name of the config file", default="")
parser.add_argument("-t", "--test-stat", help="The test statistics. Default 'qtilde'", default="qtilde")
parser.add_argument("-v", "--poi-value", help="The value of the parameter of interest", type=float, default=None)
args = parser.parse_args()

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

#Make a plot
fig, ax = plot.brazil_plot(data, model)
fig.savefig(f"./results/{ana_name}/{config_name}.png")

#p values
print("Test p-value script")
hypotest.p_values(json_file_path, poi_value, test_stat)