import pytest
import shlex
import subprocess


@pytest.fixture
def script_runner():
    def run(cmd):
        print(shlex.split(cmd))
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        try:
            out,err = proc.communicate(timeout=240)
            return (proc,out,err)
        except TimeoutExpired:
            print("script_runner timedout")
            proc.kill()
            return proc

    yield run
