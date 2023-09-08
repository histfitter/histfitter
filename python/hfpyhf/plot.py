import pyhf
import numpy as np
import matplotlib.pyplot as plt
from pyhf.contrib.viz import brazil

def brazil_plot(data, model, test_stat:str="qtilde"):
    print("Making a brazil plot")
    #Find parameter of interest
    poi_index = model.config.poi_index
    poi_name = model.config.par_order[poi_index]
    poi_multiplicity = model.config.param_set(poi_name).n_parameters

    #Find limits
    poi_min, poi_max = model.config.suggested_bounds()[poi_index]
    print(f"Suggested bounds: { poi_min, poi_max }")

    poi_vals = np.linspace(poi_min, poi_max, 100)
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
    return fig, ax
    