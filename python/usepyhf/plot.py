import pyhf
import numpy as np
import matplotlib.pyplot as plt
from pyhf.contrib.viz import brazil
from usepyhf import hypotest

def brazil_plot(workspace:pyhf.Workspace, poi_value:float=None, test_stat:str="qtilde"):
    """
    ...
    """
    #Extract model and data
    model = workspace.model()
    data = workspace.data(model)

    #Find parameter of interest
    poi_index = model.config.poi_index
    poi_name = model.config.par_order[poi_index]
    print(f"Parameter of interest: {poi_name}")

    #Find bounds
    poi_min, poi_max = model.config.suggested_bounds()[poi_index]
    poi_vals = np.linspace(poi_min, poi_max, 100)
    print(f"Suggested bounds for POI: {poi_min}, {poi_max}")
    
    #Match parameter name and indices
    #Fix SigXSec
    par_order = model.config.par_order
    if "SigXsec" in par_order:
        sigXsec_idx = [i for i in range(len(par_order)) if par_order[i] == "SigXsec"][0]
        fix_pars = [False]*len(par_order)
        fix_pars[sigXsec_idx]=True
    else:
        fix_pars = [False]*len(par_order)

    results = [
        pyhf.infer.hypotest(
            test_poi, data, model, test_stat=test_stat, fixed_params=fix_pars, return_expected_set=True
        )
        for test_poi in poi_vals
    ]
    fig, ax = plt.subplots()
    fig.set_size_inches(7, 5)
    brazil.plot_results(poi_vals, results, ax=ax)
    return fig, ax
