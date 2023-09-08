#!/usr/bin/env python

import json
import pyhf
import numpy as np
import argparse

def p_values(json_file_path:str, poi_value:float=None, test_stat:str="qtilde"):
    #Extract workspace, model and data
    with open(json_file_path) as serialized:
        json_file = json.load(serialized)

    workspace = pyhf.Workspace(json_file)
    model = workspace.model()
    data = workspace.data(model)

    #Find parameter of interest
    poi_index = model.config.poi_index
    poi_name = model.config.par_order[poi_index]
    print(f"Parameter of interest: {poi_name}")
    poi_multiplicity = model.config.param_set(poi_name).n_parameters

    #Set initial value if specified
    if poi_value is None:
        poi_init_value = model.config.suggested_init()[poi_index]
    else: poi_init_value = poi_value

    #Calculate and print p-values
    print(f"P values for {poi_name} = {poi_init_value}")
    results = pyhf.infer.hypotest(
            poi_init_value, data, model, test_stat=test_stat, return_tail_probs=True
        )
    print(f"CLs: {results[0]}")
    print(f"CLb: {results[1][1]}")
    print(f"CLs+b: {results[1][0]}")