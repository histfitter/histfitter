import ROOT
import os
import math

# dump test info
"""
import ROOT
f = ROOT.TFile("data/hf_test/histCache.root")


for k in f.GetListOfKeys():
    val = f.Get(k.GetName()).Integral()
    print(f"{k.GetName()}: {val},")
"""

def test_treeToHist(script_runner):

    # Make input ttree if needed
    if not os.path.isfile("test_tree.root"): 
        command = "root -l -b -q ${HISTFITTER}/test/scripts/genTree.C+"
        (ret,outRaw,errRaw) = script_runner(command)
        assert ret.returncode == 0 # ROOT file with TTrees generated

    command = "HistFitter.py -t ${HISTFITTER}/test/scripts/config_for_pytest.py"
    (ret,outRaw,errRaw) = script_runner(command)
    assert ret.returncode == 0

    assert os.path.isfile("data/hf_test/histCache.root") # histcache generated

    # values from snippet above
    test_values = {
        "hbkg1Nom_CR_obs_m": 3.2219999999999756,
        "hbkg1Nom_SR_obs_m": 5.777999999999959,
        "hbkg1user_overallSysHigh_CR_obs_m": 3.3830999999999745,
        "hbkg1user_overallSysHigh_SR_obs_m": 6.066899999999957,
        "hbkg1user_overallSysLow_CR_obs_m": 3.0608999999999766,
        "hbkg1user_overallSysLow_SR_obs_m": 5.489099999999961,
        "hbkg1weight_sysHigh_CR_obs_m": 3.3440255509705903,
        "hbkg1weight_sysHigh_SR_obs_m": 6.146948772620593,
        "hbkg1weight_sysLow_CR_obs_m": 3.1044935654749426,
        "hbkg1weight_sysLow_SR_obs_m": 5.43164435395858,
        "hbkg2Nom_CR_obs_m": 90.99999999999979,
        "hbkg2Nom_SR_obs_m": 12.000000000000002,
        "hbkg2tree_sysHigh_CR_obs_m": 90.99999999999979,
        "hbkg2tree_sysHigh_SR_obs_m": 12.000000000000002,
        "hbkg2tree_sysLow_CR_obs_m": 90.99999999999979,
        "hbkg2tree_sysLow_SR_obs_m": 12.000000000000002,
        "hdata_CR_obs_m": 105.0,
        "hdata_SR_obs_m": 21.0
    }

    hc = ROOT.TFile("data/hf_test/histCache.root")
    for k in hc.GetListOfKeys():
        name = k.GetName()
        val = hc.Get(name).Integral()

        assert math.isclose(test_values[name], val) # histogram integral matches test values



def test_bkgFit(script_runner):

    # Make input ttree if needed
    if not os.path.isfile("test_tree.root"): 
        command = "root -l -b -q ${HISTFITTER}/test/scripts/genTree.C+"
        (ret,outRaw,errRaw) = script_runner(command)
        assert ret.returncode == 0 # ROOT file with TTrees generated

    command = 'HistFitter.py -t -w ${HISTFITTER}/test/scripts/config_for_pytest.py'
    (ret,outRaw,errRaw) = script_runner(command)
    assert ret.returncode == 0

    assert os.path.isfile("results/hf_test/BkgOnly_combined_BasicMeasurement_model.root") # workspace was created

    command = 'HistFitter.py -f -D"before,after,corrMatrix" ${HISTFITTER}/test/scripts/config_for_pytest.py'
    (ret,outRaw,errRaw) = script_runner(command)
    assert ret.returncode == 0

    out_files = [
        "SR_m_beforeFit.pdf",
        "SR_m_beforeFit.eps",
        "SR_m_beforeFit.root",
        "CR_m_beforeFit.pdf",
        "CR_m_beforeFit.eps",
        "CR_m_beforeFit.root",
        "SR_m_afterFit.pdf",
        "SR_m_afterFit.eps",
        "SR_m_afterFit.root",
        "CR_m_afterFit.pdf",
        "CR_m_afterFit.eps",
        "CR_m_afterFit.root",
        "c_corrMatrix_RooExpandedFitResult_afterFit.pdf",
        "c_corrMatrix_RooExpandedFitResult_afterFit.eps",
        "BkgOnly_combined_BasicMeasurement_model_afterFit.root",
        "fit_parameters.root",
    ]

    for f in out_files:
        assert os.path.isfile(f"results/hf_test/{f}") # post fit files

    out = outRaw.decode('utf-8')
    assert "mu_bkg    1.0000e+00    1.1" in out # postfit bkg norm value

def test_sigExclusionAll(script_runner):

    # Make input ttree if needed
    if not os.path.isfile("test_tree.root"): 
        command = "root -l -b -q ${HISTFITTER}/test/scripts/genTree.C+"
        (ret,outRaw,errRaw) = script_runner(command)
        assert ret.returncode == 0 # ROOT file with TTrees generated

    command = 'HistFitter.py -t -w -F excl -f -D"before,after,corrMatrix" ${HISTFITTER}/test/scripts/config_for_pytest.py'
    (ret,outRaw,errRaw) = script_runner(command)
    assert ret.returncode == 0

    # YieldTable
    print("YieldTable")

    command = "YieldsTable.py -c SR,CR -w results/hf_test/Sig_excl_combined_BasicMeasurement_model_afterFit.root -s bkg1,bkg2,signal -b -o yieldTable.tex"
    (ret,outRaw,errRaw) = script_runner(command)
    assert ret.returncode == 0
    assert os.path.isfile(f"yieldTable.tex")

    out = outRaw.decode('utf-8')
    assert "YieldsTable: nobs: [21.0, 105.0]" in out  # data yields
    assert "TOTAL_FITTED_bkg_events: [21.3" in out  # bkg yield
    assert "TOTAL_FITTED_bkg_events_err: [3.2" in out  # bkg err


    # SysTable
    print("SysTable")

    command = "SysTable.py -c SR -w results/hf_test/Sig_excl_combined_BasicMeasurement_model_afterFit.root -s bkg1,bkg2,signal -o sysTable.tex -%"
    (ret,outRaw,errRaw) = script_runner(command)
    assert ret.returncode == 0
    assert os.path.isfile(f"sysTable.tex")

    with open('sysTable.tex') as f:
        contents = f.read()
        assert "Total background expectation             &  $5.7" in contents # bkg 1 yield
        assert "Total background systematic               & $\\pm 0.7" in contents # bkg 1 sys
        

    # Exclusion Asymptotics
    print("Asymptotics")

    command = "HistFitter.py -F excl -l ${HISTFITTER}/test/scripts/config_for_pytest.py"
    (ret,outRaw,errRaw) = script_runner(command)
    assert ret.returncode == 0
    
    out = outRaw.decode('utf-8')
    assert "HypoTestTool: The computed upper limit is: 1.06" in out  # computed upper limit asymptotics
    assert "HypoTestTool:  expected limit (median) 0.80" in out  # expected upper limit asymptotics


    # Exclusion Toys
    print("Toys")

    command = 'HistFitter.py -F excl -l -u"--useToys" ${HISTFITTER}/test/scripts/config_for_pytest.py'
    (ret,outRaw,errRaw) = script_runner(command)
    assert ret.returncode == 0
    
    out = outRaw.decode('utf-8')
    ul = 0.
    exp_ul = 0.

    # Grab last value in output
    for line in out.splitlines():
        if "The computed upper limit is" in line:
            ul = float(line.split(":")[2].split("+")[0])
        if "expected limit (median) " in line:
            exp_ul = float(line.split(")")[1])

    assert math.isclose(ul, 1.05, abs_tol = 0.1)
    assert math.isclose(exp_ul, 0.8, abs_tol = 0.1)


