def test_tutorial_MyUserAnalysis(script_runner):
    command = "HistFitter.py -w -f analysis/tutorial/MyUserAnalysis.py"
    ret = script_runner(command)

    stderr = ret.stderr.read().decode("utf-8")
    assert "data/MyUserAnalysis.root does not exist" in stderr
    assert (
        "Info in Minuit2Minimizer::Hesse : Hesse is valid - matrix is accurate"
        in stderr
    )
    assert "results/MyUserAnalysis/fit_parameters.root has been created" in stderr

    stdout = ret.stdout.read().decode("utf-8")
    assert "HistFitter: Leaving HistFitter... Bye!" in stdout
    assert "* * * Welcome to HistFitter * * *" in stdout
