import os
import subprocess
#Histfitter imports

def create_json(prefix:str, ana_name:str):
    if not os.path.isdir(f"./json/{ana_name}"):
        os.mkdir(f"./json/{ana_name}")
    fileName = f"{ana_name}_{prefix}.json"
    filePath = f"./json/{ana_name}/{fileName}"
    xmlPath = f"./config/{ana_name}/{prefix}.xml"
    create_file = subprocess.run(["pyhf", "xml2json", f"{xmlPath}", "--basedir", ".", 
                                "--output-file", f"{filePath}"])