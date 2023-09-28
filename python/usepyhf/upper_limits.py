import pyhf
import numpy as np

def upper_limit(workspace:pyhf.Workspace):
    #Extract model and data
    model = workspace.model()
    data = workspace.data(model)
    #Find limits
    poi_index = model.config.poi_index
    poi_min, poi_max = model.config.suggested_bounds()[poi_index]
    poi_name = model.config.par_order[poi_index]
    print(f"Parameter of interest: {poi_name}")
    print(f"Suggested bounds: { poi_min, poi_max }")

    poi_values = np.linspace(poi_min, poi_max, 50)
    obs_limit, exp_limits = pyhf.infer.intervals.upper_limits.upper_limit(
        data, model, poi_values, level=0.05
    )

    print(f"The computed upper limit is: {obs_limit}")
    print(r"expected limit -2 sigma", exp_limits[0])
    print(r"expected limit -1 sigma", exp_limits[1])
    print(r"expected limit median", exp_limits[2])
    print(r"expected limit +1 sigma", exp_limits[3])
    print(r"expected limit +2 sigma", exp_limits[4])
    
