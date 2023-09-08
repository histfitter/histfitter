#!/usr/bin/env python

import json
import pyhf
import numpy as np
import matplotlib.pyplot as plt
from pyhf.contrib.viz import brazil
import argparse


#arguments
parser = argparse.ArgumentParser(description="pyhf script options:")
parser.add_argument("-n", "--config-name", help="The name of the config file", default="")
parser.add_argument("-a", "--ana-name", help="The name of the analysis folder", default="")
args = parser.parse_args()

config_name = args.config_name
ana_name = args.ana_name
json_file_path = f"./json/{ana_name}/{ana_name}_{config_name}.json"

with open(json_file_path) as serialized:
    json_file = json.load(serialized)

workspace = pyhf.Workspace(json_file)
model = workspace.model()
data = workspace.data(model)
print(f"  channels: {model.config.channels}")
print(f"     nbins: {model.config.channel_nbins}")
print(f"   samples: {model.config.samples}")
print(f" modifiers: {model.config.modifiers}")
print(f"parameters: {model.config.parameters}")
print(f"  nauxdata: {model.config.nauxdata}")
print(f"   auxdata: {model.config.auxdata}")

print(f"samples (workspace): {workspace.samples}")
print(f"samples (  model  ): {model.config.samples}")
print(model.config.par_order)
print(model.config.suggested_init())
print(model.config.suggested_bounds())
print(model.config.poi_index)

CLs_obs, CLs_exp = pyhf.infer.hypotest(
    0,  # null hypothesis
    data,
    model,
    test_stat="qtilde",
    return_expected_set=True,
)
print(f"      Observed CLs: {CLs_obs:.4f}")
for expected_value, n_sigma in zip(CLs_exp, np.arange(-2, 3)):
    print(f"Expected CLs({n_sigma:2d} σ): {expected_value:.4f}")

poi_vals = np.linspace(0, 5, 41)
pyhf.set_backend("numpy")
results = [
    pyhf.infer.hypotest(
        test_poi, data, model, test_stat="qtilde", return_expected_set=True
    )
    for test_poi in poi_vals
]
fig, ax = plt.subplots()
fig.set_size_inches(7, 5)
brazil.plot_results(poi_vals, results, ax=ax)
fig.savefig(f"./results/{ana_name}/{config_name}.png")

print("P values for  mu_SIG =  1")
results_1 = pyhf.infer.hypotest(
        1, data, model, test_stat="qtilde", return_tail_probs=True
    )
print(f"CLs: {results_1[0]}")
print(f"CLb: {results_1[1][1]}")
print(f"CLs+b: {results_1[1][0]}")