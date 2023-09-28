import pyhf
import numpy as np

def p_values(workspace:pyhf.Workspace, poi_value:float=None, test_stat:str="qtilde"):
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
    print(f"Suggested bounds for POI: { model.config.suggested_bounds()[poi_index] }")
    
    #Match parameter name and indices
    #Fix SigXSec
    par_order = model.config.par_order
    if "SigXsec" in par_order:
        sigXsec_idx = [i for i in range(len(par_order)) if par_order[i] == "SigXsec"][0]
        fix_pars = [False]*len(par_order)
        fix_pars[sigXsec_idx]=True
    else:
        fix_pars = [False]*len(par_order)

    #Set initial value if specified
    if poi_value is None:
        poi_init_value = model.config.suggested_init()[poi_index]
    else: poi_init_value = poi_value

    #Calculate and print p-values
    print(f"P values for {poi_name} = {poi_init_value}")
    results = pyhf.infer.hypotest(
            poi_init_value, data, model, test_stat=test_stat, return_tail_probs=True,
            fixed_params=fix_pars
        )
    print(f"CLs: {results[0]}")
    print(f"CLb: {results[1][1]}")
    print(f"CLs+b: {results[1][0]}")


def p_values_disc(workspace:pyhf.Workspace, test_stat:str="qtilde"):
    """
    ...
    """
    p_values(workspace, poi_value=0, test_stat=test_stat)

def p_values_excl(workspace:pyhf.Workspace, test_stat:str="qtilde"):
    """
    ...
    """
    #If the model has the SigXsec parameter, run hypotest at SigXsec = [0, 1, -1]

    #Extract model and data
    model = workspace.model()
    data = workspace.data(model)

    #Find parameter of interest
    poi_index = model.config.poi_index
    poi_name = model.config.par_order[poi_index]
    print(f"Parameter of interest: {poi_name}")
    print(f"Suggested bounds for POI: { model.config.suggested_bounds()[poi_index] }")

    #Find SigXSec
    par_order = model.config.par_order
    init_pars = model.config.suggested_init()
    if "SigXsec" in par_order:
        sigXsec_idx = [i for i in range(len(par_order)) if par_order[i] == "SigXsec"][0]
        fix_pars = [False]*len(par_order)
        fix_pars[sigXsec_idx]=True
        sigXSec_values = [init_pars[sigXsec_idx], 1, -1]
        for value in sigXSec_values:
            temp_inits = init_pars.copy()
            temp_inits[sigXsec_idx] = value
            temp_inits[poi_index] = 1
            #Calculate and print p-values
            print(f"P values for {poi_name} = 1 and sigXSec = {value}")
            results = pyhf.infer.hypotest(
                    1, data, model, test_stat=test_stat, return_tail_probs=True,
                    init_pars = temp_inits, fixed_params=fix_pars
                )
            print(f"CLs: {results[0]}")
            print(f"CLb: {results[1][1]}")
            print(f"CLs+b: {results[1][0]}")

    else:
        p_values(workspace, 1, test_stat)
    
    

