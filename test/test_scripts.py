import time

def test_help(script_runner):
    command = 'HistFitter.py -h'
    start = time.time()
    ret = script_runner(command)
    end = time.time()
    elapsed = end - start
    # output stream
    stdout = ret.stdout.read().decode("utf-8")
    stderr = ret.stderr.read().decode("utf-8")
    # check output
    assert stderr == ""
    assert " * * * Welcome to HistFitter * * *" in stdout

def test_backupCacheExampleAnalysis(script_runner):
    # create input ROOT file with a python script
    command1 = 'python test/scripts/backupCache_input.py data/backupCache_example.root'
    ret = script_runner(command1)
    # FIXME: FAIL
    # test/scripts/backupCache_input.py:131: FutureWarning: ROOT.Double is deprecated and will disappear in a future version of ROOT. Instead, use ctypes.c_double for pass-by-ref of doubles
    # hNorm.SetBinContent(1,h.IntegralAndError(0,h.GetNbinsX(),NormErr,""))
    assert ret.stderr.read().decode("utf-8") == ""
    # run HistFitter
    command2 = 'HistFitter.py -R -w -f -F bkg -D before,after test/scripts/backupCache_config.py'
    ret = script_runner(command2)
    stdout = ret.stdout.read().decode("utf-8")
    # c.f. configManager FIXME
    assert "Leaving HistFitter... Bye!" in stdout
    # parse output
    from scripts.backupCache_parse import backupCacheParser
    parser = backupCacheParser(log = stdout, ref = 'test/scripts/backupCache_log.ref', precision = 1e-4)
    parser.parse()
