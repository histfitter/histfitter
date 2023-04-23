import ROOT
import os
import math

# snippet to dump test info from cache
"""
import ROOT
f = ROOT.TFile("data/hf_test/histCache.root")


for k in f.GetListOfKeys():
    val = f.Get(k.GetName()).Integral()
    print(f"{k.GetName()}: {val},")
"""

bkg_only_test_values = {
    'hbkg1Nom_CR_obs_m': 3.2219999999999756, 
    'hbkg1Nom_SR_obs_m': 5.777999999999959, 
    'hbkg1user_histoSysHigh_CR_obs_m': 3.3830999999999745, 
    'hbkg1user_histoSysHigh_SR_obs_m': 6.066899999999957, 
    'hbkg1user_histoSysLow_CR_obs_m': 3.0608999999999766, 
    'hbkg1user_histoSysLow_SR_obs_m': 5.489099999999961, 
    'hbkg1user_overallSysHigh_CR_obs_m': 3.3830999999999745, 
    'hbkg1user_overallSysHigh_SR_obs_m': 6.066899999999957, 
    'hbkg1user_overallSysLow_CR_obs_m': 3.0608999999999766, 
    'hbkg1user_overallSysLow_SR_obs_m': 5.489099999999961, 
    'hbkg1weight_histoSysEnvelopeSymHigh_CR_obs_m': 3.2846586611647037, 
    'hbkg1weight_histoSysEnvelopeSymHigh_SR_obs_m': 6.070510527144715, 
    'hbkg1weight_histoSysEnvelopeSymLow_CR_obs_m': 3.1593413388352474, 
    'hbkg1weight_histoSysEnvelopeSymLow_SR_obs_m': 5.485489472855202, 
    'hbkg1weight_histoSysHigh_CR_obs_m': 3.3440255509705903, 
    'hbkg1weight_histoSysHigh_SR_obs_m': 6.146948772620593, 
    'hbkg1weight_histoSysLow_CR_obs_m': 3.1044935654749426, 
    'hbkg1weight_histoSysLow_SR_obs_m': 5.43164435395858, 
    'hbkg1weight_histoSysOneSideHigh_CR_obs_m': 3.301659330582352, 
    'hbkg1weight_histoSysOneSideHigh_SR_obs_m': 6.010925263572357, 
    'hbkg1weight_histoSysOneSideLow_CR_obs_m': 3.301659330582352, 
    'hbkg1weight_histoSysOneSideLow_SR_obs_m': 6.010925263572357, 
    'hbkg1weight_histoSysOneSideSymHigh_CR_obs_m': 3.3389524407764695, 
    'hbkg1weight_histoSysOneSideSymHigh_SR_obs_m': 6.107827018096476, 
    'hbkg1weight_histoSysOneSideSymLow_CR_obs_m': 3.1050475592234816, 
    'hbkg1weight_histoSysOneSideSymLow_SR_obs_m': 5.448172981903442, 
    'hbkg1weight_overallHistoSysHigh_CR_obs_m': 3.264366220388233, 
    'hbkg1weight_overallHistoSysHigh_CR_obs_mNorm': 3.221999999999975, 
    'hbkg1weight_overallHistoSysHigh_SR_obs_m': 5.914023509048238, 
    'hbkg1weight_overallHistoSysHigh_SR_obs_mNorm': 5.77799999999996, 
    'hbkg1weight_overallHistoSysLow_CR_obs_m': 3.1801950365209026, 
    'hbkg1weight_overallHistoSysLow_CR_obs_mNorm': 3.221999999999975, 
    'hbkg1weight_overallHistoSysLow_SR_obs_m': 5.645185558107728, 
    'hbkg1weight_overallHistoSysLow_SR_obs_mNorm': 5.777999999999958, 
    'hbkg1weight_overallSysHigh_CR_obs_m': 3.2915131101941175, 
    'hbkg1weight_overallSysHigh_SR_obs_m': 5.9326817545241175, 
    'hbkg1weight_overallSysLow_CR_obs_m': 3.1539577128203415, 
    'hbkg1weight_overallSysLow_SR_obs_m': 5.627371169475674, 
    'hbkg2Nom_CRNorm': 90.99999999999979, 
    'hbkg2Nom_CR_obs_m': 90.99999999999979, 
    'hbkg2Nom_SR_obs_m': 12.000000000000002, 
    'hbkg2tree_normHistoSysOneSideSymHigh_CRNorm': 90.99999999999979, 
    'hbkg2tree_normHistoSysOneSideSymHigh_CR_obs_m': 90.99999999999979, 
    'hbkg2tree_normHistoSysOneSideSymHigh_CR_obs_mNorm': 90.99999999999979, 
    'hbkg2tree_normHistoSysOneSideSymHigh_SR_obs_m': 12.000000000000002, 
    'hbkg2tree_normHistoSysOneSideSymHigh_SR_obs_mNorm': 12.000000000000002, 
    'hbkg2tree_normHistoSysOneSideSymLow_CRNorm': 90.99999999999979, 
    'hbkg2tree_normHistoSysOneSideSymLow_CR_obs_m': 90.99999999999979, 
    'hbkg2tree_normHistoSysOneSideSymLow_CR_obs_mNorm': 90.99999999999979, 
    'hbkg2tree_normHistoSysOneSideSymLow_SR_obs_m': 12.000000000000002, 
    'hbkg2tree_normHistoSysOneSideSymLow_SR_obs_mNorm': 12.000000000000002, 
    'hbkg2user_normHistoSysHigh_CRNorm': 95.54999999999978, 
    'hbkg2user_normHistoSysHigh_CR_obs_m': 95.54999999999978, 
    'hbkg2user_normHistoSysHigh_CR_obs_mNorm': 90.99999999999979, 
    'hbkg2user_normHistoSysHigh_SR_obs_m': 12.600000000000003, 
    'hbkg2user_normHistoSysHigh_SR_obs_mNorm': 12.000000000000002, 
    'hbkg2user_normHistoSysLow_CRNorm': 86.44999999999979, 
    'hbkg2user_normHistoSysLow_CR_obs_m': 86.44999999999979, 
    'hbkg2user_normHistoSysLow_CR_obs_mNorm': 90.99999999999977, 
    'hbkg2user_normHistoSysLow_SR_obs_m': 11.4, 
    'hbkg2user_normHistoSysLow_SR_obs_mNorm': 12.0, 
    'hbkg2weight_normHistoSysEnvelopeSymHigh_CRNorm': 92.82000000000059, 
    'hbkg2weight_normHistoSysEnvelopeSymHigh_CR_obs_m': 92.82000000000059, 
    'hbkg2weight_normHistoSysEnvelopeSymHigh_CR_obs_mNorm': 90.99999999999979, 
    'hbkg2weight_normHistoSysEnvelopeSymHigh_SR_obs_m': 12.239999999999997, 
    'hbkg2weight_normHistoSysEnvelopeSymHigh_SR_obs_mNorm': 11.999999999999892, 
    'hbkg2weight_normHistoSysEnvelopeSymLow_CRNorm': 89.2156862745101, 
    'hbkg2weight_normHistoSysEnvelopeSymLow_CR_obs_m': 89.17999999999898, 
    'hbkg2weight_normHistoSysEnvelopeSymLow_CR_obs_mNorm': 90.96359999999845, 
    'hbkg2weight_normHistoSysEnvelopeSymLow_SR_obs_m': 11.760000000000007, 
    'hbkg2weight_normHistoSysEnvelopeSymLow_SR_obs_mNorm': 11.995199999999938, 
    'hbkg2weight_normHistoSysHigh_CRNorm': 92.82000000000059, 
    'hbkg2weight_normHistoSysHigh_CR_obs_m': 92.82000000000059, 
    'hbkg2weight_normHistoSysHigh_CR_obs_mNorm': 90.99999999999979, 
    'hbkg2weight_normHistoSysHigh_SR_obs_m': 12.239999999999997, 
    'hbkg2weight_normHistoSysHigh_SR_obs_mNorm': 11.999999999999892, 
    'hbkg2weight_normHistoSysLow_CRNorm': 89.2156862745101, 
    'hbkg2weight_normHistoSysLow_CR_obs_m': 89.2156862745101, 
    'hbkg2weight_normHistoSysLow_CR_obs_mNorm': 90.99999999999979, 
    'hbkg2weight_normHistoSysLow_SR_obs_m': 11.764705882352942, 
    'hbkg2weight_normHistoSysLow_SR_obs_mNorm': 11.999999999999932, 
    'hbkg2weight_normHistoSysOneSideHigh_CRNorm': 91.91000000000042, 
    'hbkg2weight_normHistoSysOneSideHigh_CR_obs_m': 91.91000000000042, 
    'hbkg2weight_normHistoSysOneSideHigh_CR_obs_mNorm': 90.99999999999977, 
    'hbkg2weight_normHistoSysOneSideHigh_SR_obs_m': 12.119999999999997, 
    'hbkg2weight_normHistoSysOneSideHigh_SR_obs_mNorm': 11.999999999999913, 
    'hbkg2weight_normHistoSysOneSideLow_CRNorm': 91.91000000000042, 
    'hbkg2weight_normHistoSysOneSideLow_CR_obs_m': 91.91000000000042, 
    'hbkg2weight_normHistoSysOneSideLow_CR_obs_mNorm': 90.99999999999977, 
    'hbkg2weight_normHistoSysOneSideLow_SR_obs_m': 12.119999999999997, 
    'hbkg2weight_normHistoSysOneSideLow_SR_obs_mNorm': 11.999999999999913, 
    'hbkg2weight_overallNormHistoSysEnvelopeSymHigh_CRNorm': 93.73000000000009, 
    'hbkg2weight_overallNormHistoSysEnvelopeSymHigh_CR_obs_m': 93.73000000000009, 
    'hbkg2weight_overallNormHistoSysEnvelopeSymHigh_CR_obs_mNorm': 90.99999999999979, 
    'hbkg2weight_overallNormHistoSysEnvelopeSymHigh_SR_obs_m': 12.360000000000007, 
    'hbkg2weight_overallNormHistoSysEnvelopeSymHigh_SR_obs_mNorm': 12.000000000000004, 
    'hbkg2weight_overallNormHistoSysEnvelopeSymLow_CRNorm': 88.34951456310662, 
    'hbkg2weight_overallNormHistoSysEnvelopeSymLow_CR_obs_m': 88.26999999999948, 
    'hbkg2weight_overallNormHistoSysEnvelopeSymLow_CR_obs_mNorm': 90.99999999999979, 
    'hbkg2weight_overallNormHistoSysEnvelopeSymLow_SR_obs_m': 11.639999999999997, 
    'hbkg2weight_overallNormHistoSysEnvelopeSymLow_SR_obs_mNorm': 12.0, 
    'hbkg2weight_overallNormSysHigh_CRNorm': 93.73000000000009, 
    'hbkg2weight_overallNormSysHigh_CR_obs_m': 93.73000000000009, 
    'hbkg2weight_overallNormSysHigh_CR_obs_mNorm': 90.99999999999979, 
    'hbkg2weight_overallNormSysHigh_SR_obs_m': 12.360000000000007, 
    'hbkg2weight_overallNormSysHigh_SR_obs_mNorm': 12.000000000000004, 
    'hbkg2weight_overallNormSysLow_CRNorm': 88.34951456310662, 
    'hbkg2weight_overallNormSysLow_CR_obs_m': 88.34951456310662, 
    'hbkg2weight_overallNormSysLow_CR_obs_mNorm': 90.99999999999979, 
    'hbkg2weight_overallNormSysLow_SR_obs_m': 11.650485436893199, 
    'hbkg2weight_overallNormSysLow_SR_obs_mNorm': 12.0, 
    'hdata_CR_obs_m': 105.0, 
    'hdata_SR_obs_m': 21.0
}


def test_treeToHist(script_runner):

    # Make input TTree if needed
    if not os.path.isfile("test_tree.root"): 
        command = "root -l -b -q ${HISTFITTER}/test/scripts/genTree.C+"
        (ret,outRaw,errRaw) = script_runner(command)
        assert ret.returncode == 0 # ROOT file with TTrees generated

    command = "HistFitter.py -t ${HISTFITTER}/test/scripts/config_for_pytest.py"
    (ret,outRaw,errRaw) = script_runner(command)
    assert ret.returncode == 0

    assert os.path.isfile("data/hf_test/histCache.root") # histcache generated

    # values from snippet above
    hc = ROOT.TFile("data/hf_test/histCache.root")
    for k in hc.GetListOfKeys():
        name = k.GetName()
        val = hc.Get(name).Integral()

        assert math.isclose(bkg_only_test_values[name], val) # histogram integral matches test values


def test_backupCache(script_runner):
    command = 'mv ${HISTFITTER}/test/data/hf_test/histCache.root ${HISTFITTER}/test/test_backup_cache.root'
    (ret, outRaw, errRaw) = script_runner(command)

    hc = ROOT.TFile.Open('test_backup_cache.root', 'UPDATE')
    for k in hc.GetListOfKeys():
        name = k.GetName()
        if name.endswith('mNorm'):
            hc.Delete(f'{name};*')
    hc.Close()

    command = "HistFitter.py -w -u='--manualBackupCache ${HISTFITTER}/test/test_backup_cache.root' ${HISTFITTER}/test/scripts/config_for_pytest.py"
    (ret,outRaw,errRaw) = script_runner(command)
    assert ret.returncode == 0

    assert os.path.isfile("data/hf_test/histCache.root") # histcache generated

    # values from snippet above
    hc = ROOT.TFile("data/hf_test/histCache.root")
    for k in hc.GetListOfKeys():
        name = k.GetName()
        val = hc.Get(name).Integral()

        assert math.isclose(bkg_only_test_values[name], val) # histogram integral matches test values

def test_bkgFit(script_runner):

    # Make input TTree if needed
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

    # list of files that should have been created
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
        assert os.path.isfile(f"results/hf_test/{f}") # post fit files exist

    out = outRaw.decode('utf-8')
    assert "mu_bkg    1.0000e+00    1.1" in out # postfit bkg norm value

def test_sigExclusionAll(script_runner):

    # Make input TTree if needed
    if not os.path.isfile("test_tree.root"): 
        command = "root -l -b -q ${HISTFITTER}/test/scripts/genTree.C+"
        (ret,outRaw,errRaw) = script_runner(command)
        assert ret.returncode == 0 # ROOT file with TTrees generated

    command = 'HistFitter.py -t -w -F excl -f -D"before,after,corrMatrix" ${HISTFITTER}/test/scripts/config_for_pytest.py'
    (ret,outRaw,errRaw) = script_runner(command)
    assert ret.returncode == 0

    # YieldTable
    command = "YieldsTable.py -c SR,CR -w results/hf_test/Sig_excl_combined_BasicMeasurement_model_afterFit.root -s bkg1,bkg2,signal -b -o yieldTable.tex"
    (ret,outRaw,errRaw) = script_runner(command)
    assert ret.returncode == 0
    assert os.path.isfile(f"yieldTable.tex")

    out = outRaw.decode('utf-8')
    assert "YieldsTable: nobs: [21.0, 105.0]" in out  # data yields
    assert "TOTAL_FITTED_bkg_events: [21.3" in out  # bkg yield
    assert "TOTAL_FITTED_bkg_events_err: [3.2" in out  # bkg err


    # SysTable
    command = "SysTable.py -c SR -w results/hf_test/Sig_excl_combined_BasicMeasurement_model_afterFit.root -s bkg1,bkg2,signal -o sysTable.tex -%"
    (ret,outRaw,errRaw) = script_runner(command)
    assert ret.returncode == 0
    assert os.path.isfile(f"sysTable.tex")

    with open('sysTable.tex') as f:
        contents = f.read()
        assert "Total background expectation             &  $5.7" in contents # bkg 1 yield
        assert "Total background systematic               & $\\pm 0.9" in contents # bkg 1 sys
        

    # Exclusion Asymptotics
    command = "HistFitter.py -F excl -l ${HISTFITTER}/test/scripts/config_for_pytest.py"
    (ret,outRaw,errRaw) = script_runner(command)
    assert ret.returncode == 0
    
    out = outRaw.decode('utf-8')
    assert "HypoTestTool: The computed upper limit is: 1.06" in out  # computed upper limit asymptotics
    assert "HypoTestTool:  expected limit (median) 0.80" in out  # expected upper limit asymptotics


    # Exclusion Toys
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



def test_discoveryAll(script_runner):
    # Make input TTree if needed
    if not os.path.isfile("test_tree.root"): 
        command = "root -l -b -q ${HISTFITTER}/test/scripts/genTree.C+"
        (ret,outRaw,errRaw) = script_runner(command)
        assert ret.returncode == 0 # ROOT file with TTrees generated

    # Make discovery workspace and fit
    #command = 'HistFitter.py -t -w -F disc -f -D"before,after,corrMatrix" ${HISTFITTER}/test/scripts/config_for_pytest.py' 
    # plotting crashes, something to fix!
    command = 'HistFitter.py -t -w -F disc -f ${HISTFITTER}/test/scripts/config_for_pytest.py'
    (ret,outRaw,errRaw) = script_runner(command)
    assert ret.returncode == 0

    # Upper limit table
    command = 'UpperLimitTable.py -c SR_disc -w results/hf_test/Discovery_combined_BasicMeasurement_model.root -l 10 -p mu_Discovery -o ulTable.tex -a -R 10'
    (ret,outRaw,errRaw) = script_runner(command)
    assert ret.returncode == 0

    with open('ulTable.tex') as f:
        contents = f.read()
        assert 'SR\\_disc    & $0.75$ &  $7.5$ & $ { 5.6 }^{ +3.0 }_{ -1.8 }$ & $0.75$ & $ 0.21$~$(0.81)$' in contents # UL table