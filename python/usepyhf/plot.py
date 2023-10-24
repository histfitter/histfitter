import pyhf
import numpy as np
import matplotlib.pyplot as plt
from pyhf.contrib.viz import brazil
from usepyhf import util

def brazil_plot(workspace:pyhf.Workspace, n_points:int=20, bounds=None, test_stat:str="qtilde", size=[7, 5]):
    """
    Make a brazil band plot to show the upper limit CI and +/- [1, 2] sigma CL.
    """
    #Extract model and data
    model = workspace.model()
    data = workspace.data(model)

    #Find parameter of interest
    poi_index = model.config.poi_index
    poi_name = model.config.par_order[poi_index]

    #Find bounds
    if type(bounds)==tuple and len(bounds)==2:
        poi_min, poi_max = bounds
    else:
        poi_min, poi_max = model.config.suggested_bounds()[poi_index]
    
    #Values to scan over
    poi_vals = np.linspace(poi_min, poi_max, n_points)
    
    #Fix the parameter "SigXsec" if it exists
    fix_pars = util.fix_sigxsec(model)

    #Calculate p-value for each POI value
    results = [
        pyhf.infer.hypotest(
            test_poi, data, model, test_stat=test_stat, fixed_params=fix_pars, return_expected_set=True
        )
        for test_poi in poi_vals
    ]
    
    #Plot
    fig, ax = plt.subplots()
    fig.set_size_inches(size[0], size[1])
    brazil.plot_results(poi_vals, results, ax=ax)
    ax.set_xlabel(poi_name)
    ax.set_ylabel("p-value")
    ax.set_xlim(left=0)
    return fig, ax
