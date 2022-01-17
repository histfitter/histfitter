def test_tutorial_MyUserAnalysis(script_runner):
    command = "HistFitter.py -w -f analysis/tutorial/MyUserAnalysis.py"
    ret = script_runner(command)

    stderr = ret.stderr.read().decode("utf-8")

    # n.b this Hesse is valid line doesn't  show up in ROOT 6.24, but does with 6.22
    assert (
        "Info in Minuit2Minimizer::Hesse : Hesse is valid - matrix is accurate"
        in stderr
    )
    assert "results/MyUserAnalysis/fit_parameters.root has been created" in stderr

    stdout = ret.stdout.read().decode("utf-8")
    assert "Status : MINIMIZE=0 HESSE=0" in stdout
    assert "HistFitter: Leaving HistFitter... Bye!" in stdout
    assert "* * * Welcome to HistFitter * * *" in stdout
