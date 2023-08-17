import time
import os

def test_help(script_runner):
    command = "HistFitter.py -h"
    start = time.time()
    (ret,outRaw,errRaw) = script_runner(command)
    end = time.time()
    elapsed = end - start

    out = outRaw.decode('utf-8')
    err = errRaw.decode('utf-8')
    assert err == ""
    assert " * * * Welcome to HistFitter * * *" in out


def test_backupCacheExampleAnalysis(script_runner):
    # create input ROOT file with a python script

        #make directory
    if not os.path.isdir("data/BackupCacheExample"):
        os.mkdir("data/BackupCacheExample")
    
    command1 = "python test/scripts/backupCache_input.py data/BackupCacheExample/backupCache_example.root"
    (ret,outRaw,errRaw) = script_runner(command1)
    err = errRaw.decode('utf-8')
    assert err == ""
    # run HistFitter
    command2 = "HistFitter.py -R -w -f -F bkg -D before,after test/scripts/backupCache_config.py"
    (ret,outRaw,errRaw) = script_runner(command2)
    stdout = outRaw.decode('utf-8')
    assert "Leaving HistFitter... Bye!" in stdout
    # parse output
    from scripts.backupCache_parse import backupCacheParser

    parser = backupCacheParser(
        log=stdout, ref="test/scripts/backupCache_log.ref", precision=1e-4
    )
    parser.parse()
