# HistFitter 

[![stable-release-python3](https://img.shields.io/badge/StablePython3-v1.3.1-green)](https://github.com/histfitter/histfitter/releases/tag/v1.3.1)
[![stable-release-python2](https://img.shields.io/badge/StablePython2-v0.66.0-green)](https://gitlab.cern.ch/HistFitter/HistFitter/-/releases/v0.66.0)
[![Documentation](https://img.shields.io/badge/Documentation-blue)](https://twiki.cern.ch/twiki/bin/viewauth/AtlasProtected/SusyFitter)
[![Tutorial](https://img.shields.io/badge/Tutorial-orange)](https://twiki.cern.ch/twiki/bin/viewauth/AtlasProtected/HistFitterTutorial)

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/histfitter/histfitter/master.svg)](https://results.pre-commit.ci/latest/github/histfitter/histfitter/master)

## Contact

The HistFitter Group mailing-list, for **any** of your questions: <atlas-phys-susy-histfitter@cern.ch>

## Acquire

### StatAnalysis

HistFitter is available in the ATLAS StatAnalysis release, which can be loaded with:

```
setupATLAS
asetup StatAnalysis, 0.3.0
```
If you use this option you can skip the next step and go straight to Setup.

### Building from source
HistFitter has 2 stable versions, one compliant with Python2 (v0.66.0) and one with Python3 (v1.x.y).
If you're going to be using HistFitter directly as a standalone application, clone the latest stable release. The Python2 version is no longer being updated.

```
git clone https://github.com/histfitter/histfitter
git checkout vX.XX.X -b vX.XX.X
```
This creates a directory named histfitter with the source code.

If you're using HistFitter as a submodule in a project, specify the latest stable release while adding the submodule

```
# Relative path gives nicer clones in CI if the parent project on CERN's GitLab
git submodule add ../../HistFitter/HistFitter.git
cd HistFitter && git checkout vX.XX.X -b vX.XX.X && cd ..
git add HistFitter && git commit -m "Add HistFitter submodule"
```

### Recommended Root version

The recommended Root version is `6.30/02`. This version of HistFitter is not compatible with ROOT versions < 6.28.  The minimum cmake version is `3.21`.

An LCG release with the correct ROOT, Python, and cmake versions can be loaded on lxplus via the ATLAS software setup:

```
lsetup "views LCG_105 x86_64-el9-gcc12-opt"
```

## Build and install

Make your build directory and specify an install directory. You have to point cmake to where the cloned source directory is located.
```
mkdir build
cd build
cmake -DCMAKE_INSTALL_PREFIX=/path/to/install/ /path/to/histfitter/
make install
```
Depending on your cmake version, you may need to add '-B.' in order to get cmake to put the build files into the current directory.

HistFitter was originally built and used in the same directory as the source code. If you prefer this option, simply go to the source directory and make the build directory there. This will treat the source code directory `histfitter` as the install location, creating the `install` directory directly there.
```
cd histfitter
mkdir build
cd build
cmake  ..
make install
```
This will create an install directory with the installed libraries as well as other files needed at runtime.


## Setup

The environment must be set by activating the setup script (`install/bin/setup_histfitter.sh`) in the directory where you want to work. This will create three new directories in your work directory: `config`, `data`, and `results`. It also copies the `HistFactorySchema.dtd` file into the config directory. Most importantly, the setup script sets the environment variable paths that are required for the scripts to work. Use the `-e` flag to obtain a copy of the `analysis` and `macros` folders containing the examples, which are a good starting point for creating your own analysis. If you want to import additional python files, make sure that they are located in a folder which is added to the `PYTHONPATH` environment variable (like `analysis`).

```
mkdir HistFitterProject
cd HistFitterProject
source /path/to/install/bin/setup_histfitter.sh
```
You can also run the setup script from any directory if you use the -p flag and the path to the work directory.

```
source /path/to/install/bin/setup_histfitter.sh -p /path/to/HistFitterProject
```

If you are using HistFitter through StatAnalysis, the setup script location is already in the PATH environment variable:

```
mkdir HistFitterProject
cd HistFitterProject
source setup_histfitter.sh
```

## Workflow

See the ATLAS tutorial.

## pyhf

pyhf is now enabled as a backend for running maximum likelihood fits, calculating upper limits and hypothesis testing. Use the --pyhf flag to use pyhf. For pyhf to work, JSON files must be created from the existing XML files. You can do this by using the -j flag. If you make any changes to the fit configuration, the XML and JSON files must be recreated (-j does both). pyhf must be installed on the command line and as a python library. This can be done through pip:

```
pip install pyhf[xmlio, minuit]
```
If you want other backends you can install them in a similar manner. See the pyhf [documentation](https://pyhf.readthedocs.io/en/v0.7.4/installation.html) for more information.

You can change the backend by setting it using the --pyhf-backend flag. The options are ['numpy', 'tensorflow', 'pytorch', 'jax']. The corresponding pyhf extension library must be installed. The default backend is numpy.

```
pip install pyhf['jax']
```

## Directory structure
### source code

- `analysis`: Contains example configuration files in `tutorial/`.
- `config`: Contains HistFactory schema
- `doc`: This is a placeholder directory for Doxygen's output.
- `macros`: Macros for making plots, testing the fit, ongoing work, etc
- `python`: Python base classes
- `scripts`: Scripts for making workspaces based on root files in `data/`. Scripts for submitting batch jobs.
- `src`: Source code to make workspaces, do toys.
- `test`: pytest tests

### working directory

- `analysis`: Contains all files related to an analysis. E.g. `ZeroLepton/`.
- `config`: Contains HistFactory schema and XML files
- `results`: Where root files with workspaces generated by HistFactory get stored
- `data`: Contains data root files, provided externally, used to create workspaces for analysis

## Tests and troubleshooting
To check that everything is working properly, you can run the tests. This requires you to have the pytest python module installed. Run the setup script with the `-t` flag.
```
source /path/to/install/bin/setup_histfitter.sh -t
```
This copies the `/test` directory into the work directory. Now run the tests.
```
pytest test/
```
If you get errors of the type 'no module named ...' the `PYTHONPATH` and/or `LD_LIBRARY_PATH` are not set correctly which means HistFitter is not built/installed properly. If some tests pass and others fail it could be related to results from toys, which are non-deterministic, or changes in ROOT. 

## Contributing

To contribute to development please first fork HistFitter and do all of your development on a feature branch that is **not** `master`.
If you are planning on making feature changes please first [open up an Issue](https://github.com/histfitter/histfitter/issues) and outline your plans so that development can be discussed with the maintainer team, streamlining the process as your PR is written.

When you make a PR, include a summary in the body of the PR of your changes that can be easily found and incorporated into Changelog for the next release.
