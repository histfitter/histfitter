import pyhf
import pandas as pd
import numpy as np
from usepyhf import util
from pValue import pValueToSignificance

def p_values_disc(workspace:pyhf.Workspace):
    """
    Hypothesis test for the discovery of a positive signal.
    Null hypothesis: Background only
    Alternative hypothesis: Signal+background model.
    Discovery can be claimed if the null hypothesis can be rejected
    at 5 sigma confidence level.
    Uses the q0 test statistics and sets POI to 0.
    """

    #Extract model and data
    model = workspace.model()
    data = workspace.data(model)

    #Find parameter of interest
    poi_index = model.config.poi_index
    poi_name = model.config.par_order[poi_index]

    #Fix the parameter "SigXsec" if it exists
    fix_pars = util.fix_sigxsec(model)

    #Print information
    print("<INFO> pyhf: Running a discovery hypothesis test:")
    print(f"Suggested bounds for POI: { model.config.suggested_bounds()[poi_index] }")
    print(f"Calculating p-values for POI {poi_name} = 0:\n")

    #Calculate and print p-values
    results = pyhf.infer.hypotest(
            0, data, model, test_stat="q0", return_tail_probs=True,
            fixed_params=fix_pars
        )
    print(f"CLb: {results[0]:.6f}")
    print(f"CLs+b: {results[1][0]:.6f}")
    print(f"CLs: {(results[1][0]/results[0]):.6f}\n")
    print(f"Null hypothesis p-value: {results[0]:.6f}")
    print(f"Significance level: {pValueToSignificance(results[0], True):.6f}\n")


def p_values_excl(workspace:pyhf.Workspace):
    """
    Hypothesis test for the exclusion of a signal model.
    Null hypothesis: Signal + background model
    If the null hypothesis can be rejected at 1.65 significance
    (CLs < 0.05) then the signal model can be excluded.
    Uses the qtilde test statistics and sets POI to 1.
    If the model has the SigXsec parameter, run test at SigXsec = [0, 1, -1]
    """

    #Extract model and data
    model = workspace.model()
    data = workspace.data(model)

    #Find parameter of interest
    poi_index = model.config.poi_index
    poi_name = model.config.par_order[poi_index]

    #Find SigXSec
    par_order = model.config.par_order
    init_pars = model.config.suggested_init()

    #Print info
    print("<INFO> pyhf: Running an exclusion hypothesis test:")

    if "SigXsec" in par_order:
        #Fix the parameter "SigXsec" if it exists
        fix_pars = util.fix_sigxsec(model)
        sigXsec_idx = [i for i, x in enumerate(fix_pars) if x][0] #sigXsec is only True in list
        sigXSec_values = [0, 1, -1]
        CLs=[]
        CLb=[]
        CLsplusb=[]
        #Iterate over sigXSec=[0, 1, -1]
        print(f"Suggested bounds for POI: { model.config.suggested_bounds()[poi_index] }")
        print(f"Calculating p-values for POI {poi_name} = 1 and sigXSec = {sigXSec_values}:\n")
        for value in sigXSec_values:
            temp_inits = init_pars.copy()
            temp_inits[sigXsec_idx] = value
            #Calculate and print p-values
            results = pyhf.infer.hypotest(
                    1, data, model, test_stat="qtilde", return_tail_probs=True,
                    init_pars = temp_inits, fixed_params=fix_pars
                )
            CLs.append(results[0])
            CLb.append(results[1][1])
            CLsplusb.append(results[1][0])
        
        print(f"CLs: [{CLs[0]:.6f}, {CLs[1]:.6f}, {CLs[2]:.6f}]")
        print(f"CLb: [{CLb[0]:.6f}, {CLb[1]:.6f}, {CLb[2]:.6f}]")
        print(f"CLs+b: [{CLsplusb[0]:.6f}, {CLsplusb[1]:.6f}, {CLsplusb[2]:.6f}]\n")

    else:
        #Print information
        print(f"Suggested bounds for POI: { model.config.suggested_bounds()[poi_index] }")
        print(f"Calculating p-values for POI {poi_name} = 1:\n")

        #Calculate and print p-values
        results = pyhf.infer.hypotest(
                    1, data, model, test_stat="qtilde", return_tail_probs=True
                )
        print(f"CLs: {results[0]:.6f}")
        print(f"CLb: {results[1][1]:.6f}")
        print(f"CLs+b: {results[1][0]:.6f}\n")
    

def mle_fit(workspace:pyhf.Workspace):
    """
    Perform a maximum likelihood fit.
    It is important that the backend is set properly, for instance: 
    pyhf.set_backend(pyhf.tensorlib, pyhf.optimize.minuit_optimizer(tolerance=1e-3))
    """
    #Extract model and data
    model = workspace.model()
    data = workspace.data(model)

    #Match parameter name and indices
    par_order = model.config.par_order

    #Fix the parameter "SigXsec" if it exists
    fix_pars = util.fix_sigxsec(model)
    
    #Perform fit
    print("<INFO> pyhf: Running maximum likelihood fit:")
    print("*--------------------------------------------------------*")
    bestfit_pars = pyhf.infer.mle.fit(
            data, model, return_uncertainties=True, fixed_params=fix_pars
    )

    #Make dataframe for nice printing
    value = [bestfit_pars[i][0] for i in range(len(bestfit_pars))]
    error = [bestfit_pars[i][1] for i in range(len(bestfit_pars))]
    results = pd.DataFrame({
        "Parameter": par_order,
        "Final value": value,
        "Error": error
    })
    print(results.to_string(index=False))
    print("*--------------------------------------------------------*")

    return (bestfit_pars)