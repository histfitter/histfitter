def test_tutorial_MyUserAnalysis(script_runner):
    command = "HistFitter.py -w --pyhf -j -z -F disc ${HISTFITTER_WORKDIR}/analysis/tutorial/MyUserAnalysis.py"
    (ret,outRaw,errRaw) = script_runner(command)

    stderr = errRaw.decode("utf-8")
    assert "results/MyUserAnalysis/fit_parameters.root has been created" in stderr

    stdout = outRaw.decode("utf-8")
    assert "import pyhf successful" in stdout
    assert "pyhf command line tool installed" in stdout
    assert "HistFitter: Leaving HistFitter... Bye!" in stdout
    assert "* * * Welcome to HistFitter * * *" in stdout
