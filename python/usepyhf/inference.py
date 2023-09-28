import json
import pyhf
import numpy as np

def mle_fit(workspace:pyhf.Workspace, return_uncertainties=True):
    #Extract model and data
    model = workspace.model()
    data = workspace.data(model)

    #Match parameter name and indices
    pars = model.config.parameters
    par_order = model.config.par_order
    par_order_idx = [0]*len(par_order)
    fix_pars = [False]*len(par_order)
    for i, par in enumerate(pars):
        for j, item in enumerate(par_order):
            if par == item:
                par_order_idx[i] = int(j)
                if par == "SigXSec":
                    fix_pars[j] = True

    #Perform fit
    print("Running maximum likelihood fit")
    bestfit_pars = pyhf.infer.mle.fit(
            data, model, return_uncertainties=True, fixed_params=fix_pars
    )
    for i in range(len(pars)):
        print(f"{pars[i]} = {bestfit_pars[par_order_idx[i]][0]} +/- {bestfit_pars[par_order_idx[i]][1]}")
    print("---------------------------------")

    return (bestfit_pars)