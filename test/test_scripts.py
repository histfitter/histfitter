import time

def test_help(script_runner):
    command = 'HistFitter.py -h'
    start = time.time()
    ret = script_runner(command)
    end = time.time()
    elapsed = end - start
    # output stream
    stdout = ret.stdout.read()
    stderr = ret.stderr.read()
    # check output
    assert stderr == ""
    assert " * * * Welcome to HistFitter * * *" in stdout

def test_backupCacheExampleAnalysis(script_runner):
    # create input ROOT file with a python script
    command1 = 'python test/scripts/backupCache_input.py data/backupCache_example.root'
    ret = script_runner(command1)
    assert ret.stderr.read() == ""
    # run HistFitter
    command2 = 'HistFitter.py -R -w -f -F bkg -D before,after test/scripts/backupCache_config.py'
    ret = script_runner(command2)
    stdout = ret.stdout.read()
    assert "Leaving HistFitter... Bye!" in stdout
    # parse output
    from scripts.backupCache_parse import backupCacheParser
    parser = backupCacheParser(log = stdout, ref = 'test/scripts/backupCache_log.ref', precision = 1e-4)
    parser.parse()
