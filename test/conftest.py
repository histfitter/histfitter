import pytest
import shlex
import subprocess

@pytest.fixture
def script_runner():
    def run(cmd):
        print(shlex.split(cmd))
        proc =  subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=True)
        proc.wait()
        return proc
    yield run
