def test_tutorial_MyUserAnalysis(script_runner):
    command = f"HistFitter.py -w -f {os.getenv('HISTFITTER')}/analysis/tutorial/MyUserAnalysis.py"
    ret = script_runner(command)

    stderr = ret.stderr.read().decode("utf-8")
    assert f"{os.getenv('HISTFITTER')}/results/MyUserAnalysis/fit_parameters.root has been created" in stderr

    stdout = outRaw.decode("utf-8")
    assert "Status : MINIMIZE=0 HESSE=0" in stdout
    assert "HistFitter: Leaving HistFitter... Bye!" in stdout
    assert "* * * Welcome to HistFitter * * *" in stdout
