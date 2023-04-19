def test_tutorial_MyUserAnalysis(script_runner):
    command = "HistFitter.py -w -f ${HISTFITTER}/analysis/tutorial/MyUserAnalysis.py"
    (ret,outRaw,errRaw) = script_runner(command)

    stderr = errRaw.decode("utf-8")
    assert "results/MyUserAnalysis/fit_parameters.root has been created" in stderr

    stdout = outRaw.decode("utf-8")
    assert "Status : MINIMIZE=0 HESSE=0" in stdout
    assert "HistFitter: Leaving HistFitter... Bye!" in stdout
    assert "* * * Welcome to HistFitter * * *" in stdout
