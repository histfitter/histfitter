def test_tutorial_MyUserAnalysis_pyhf(script_runner):
    command = "HistFitter.py -w --pyhf -j -z -F disc ${HISTFITTER_WORKDIR}/analysis/tutorial/MyUserAnalysis.py"
    (ret,outRaw,errRaw) = script_runner(command)
    assert ret.returncode == 0
    stdout = outRaw.decode("utf-8")
    assert "* * * Welcome to HistFitter * * *" in stdout
    assert "import pyhf successful" in stdout
    assert "pyhf command line tool installed" in stdout
    assert "HistFitter: Leaving HistFitter... Bye!" in stdout
    
