# contourPlotter Example
L. Lee (Feb 2018)

### Creation of JSON

Run the tutorial (for `MySimpleChannelConfig.py`). Once you run the fits (`-p` option), you'll be handed a trio of root files.

```
MySimpleChannelAnalysis_fixSigXSecNominal_hypotest.root
MySimpleChannelAnalysis_fixSigXSecUp_hypotest.root
MySimpleChannelAnalysis_fixSigXSecDown_hypotest.root
```

where the last two are theory cross section variation files. We need to get these into a readable format, so we'll convert them to JSON using the following (assuming these files are in a directory `inputHypoTestResults/`):

```
GenerateJSONOutput.py -i inputHypoTestResults/MySimpleChannelAnalysis_fixSigXSecNominal_hypotest.root -f "hypo_SU_%f_%f_0_10" -p "m0:m12"
```

(See `GenerateJSONOutput.py -h` for help!) This will automatically pick up the theory variation files.

This produces some output JSON:

```
MySimpleChannelAnalysis_fixSigXSecNominal_hypotest__1_harvest_list.json
MySimpleChannelAnalysis_fixSigXSecUp_hypotest__1_harvest_list.json
MySimpleChannelAnalysis_fixSigXSecDown_hypotest__1_harvest_list.json
```

For convenience, you can find these in this example directory under `inputJSON/`. These JSON contain all of the fit results. 

### Multiplexing JSON (e.g. Single file with "best" SR from best expected CLs value)

If you have multiple JSON (for multiple SRs) you can combine them using the `multiplexJSON.py` functionality given in the HF `scripts` directory (and in your path if your environment is setup via `source setup.sh`).

### Contour Production

Once you're ready to get some contours out, you can hand JSON to the `harvestToContours.py` command (again, see `harvestToContours.py -h` for help!):

```
harvestToContours.py -i inputJSON/MySimpleChannelAnalysis_fixSigXSecNominal_hypotest__1_harvest_list.json -s 100 -x m0 -y m12 -d --areaThreshold 100 --interpolation linear
```

This command will automatically pick up the theory variation files. This will perform a linear interpolation using `scipy` -- additional options are available. ROOT interpolation can be acheived using the `-r` flag. `-x` and `-y` define which JSON fields should be used for the x and y axes. Here, contours under `--areaThreshold`(=100) are not considered to remove interpolation artifacts. A smoothing of `100` is used here. There are all fully analysis-specific.

This will give you a ROOT file full of information. (Configurable via `-o` option.)

### Contour Plotting

To help with final plotting, a python class is defined (again in the `scripts/` directory, but in your python path already) called `contourPlotter`.

Checkout the script `contourPlotterExample.py` for an exampel of how to use this plotting helper class. This will give you a fully formatted plot for ~20 lines of simple python. You can run it with a simple:

```
python contourPlotterExample.py
```




