import subprocess
import os

os.chdir(os.path.dirname(__file__))

# run all tests in this directory
subprocess.call([
    "python3", "-m", "unittest", "discover", "-s",
    ".", "-t", "."
])
