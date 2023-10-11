import os
import subprocess

def create_json(ana_name:str, prefix:str):
    """
    Creates a JSON file in the /json folder with the name {ana_name}_{prefix}.json.
    https://pyhf.readthedocs.io/en/v0.7.2/babel.html
    """
    if not os.path.isdir(f"./json/{ana_name}"):
        os.makedirs(f"./json/{ana_name}")
    fileName = f"{ana_name}_{prefix}.json"
    filePath = f"./json/{ana_name}/{fileName}"
    xmlPath = f"./config/{ana_name}/{prefix}.xml"
    create_file = subprocess.run(["pyhf", "xml2json", f"{xmlPath}", "--basedir", ".", 
                                "--output-file", f"{filePath}"])
    
def fix_sigxsec(model):
    """
    The parameter SigXsec should be fixed.
    """
    par_order = model.config.par_order
    if "SigXsec" in par_order:
        sigXsec_idx = [i for i in range(len(par_order)) if par_order[i] == "SigXsec"][0]
        fix_pars = [False]*len(par_order)
        fix_pars[sigXsec_idx]=True
    else:
        fix_pars = [False]*len(par_order)
    return fix_pars