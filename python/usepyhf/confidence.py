import pyhf
import numpy as np
from usepyhf import util

def upper_limit(workspace:pyhf.Workspace, n_points:int=20, bounds=None):
    """
    Calculates the observed upper limit of the POI at the 95% CL.
    This function also prints the expected limit median and +/- [1, 2] sigma.
    """
    #Extract model and data
    model = workspace.model()
    data = workspace.data(model)
    poi_index = model.config.poi_index
    poi_name = model.config.par_order[poi_index]
    
    #Find bounds
    if type(bounds)==tuple and len(bounds)==2:
        poi_min, poi_max = bounds
    else:
        poi_min, poi_max = model.config.suggested_bounds()[poi_index]
        
    #Print info
    print("<INFO> pyhf: Finding upper limits:")
    print(f"Parameter of interest: {poi_name}")
    print(f"Bounds: { poi_min, poi_max }")

    #Fix the parameter "SigXsec" if it exists
    fix_pars = util.fix_sigxsec(model)

    #Calculate upper limits
    poi_values = np.linspace(poi_min, poi_max, n_points)
    obs_limit, exp_limits = pyhf.infer.intervals.upper_limits.upper_limit(
        data, model, poi_values, level=0.05, fixed_params=fix_pars
    )

    print(f"The observed upper limit is: {obs_limit:.6f} at 95% CL")
    print(f"expected limit -2 sigma: {exp_limits[0]:.6f}")
    print(f"expected limit -1 sigma: {exp_limits[1]:.6f}")
    print(f"expected limit median: {exp_limits[2]:.6f}")
    print(f"expected limit +1 sigma: {exp_limits[3]:.6f}")
    print(f"expected limit +2 sigma: {exp_limits[4]:.6f}")
    
