import os
import subprocess
from src.tc_runner import TCRunner
from tester import evaluate_outputs


def get_python_testcase_output():
    TCRunner("TCs/RT/tc.txt", "TCs/RT/tc-pyres.txt")


def get_haskell_testcase_output():
    haskell_result = subprocess.check_output(
        "./oracle/GetTCTraces --trades TCs/RT/tc.txt", shell=True).decode().replace("\"", "")
    haskell_result_file = open("TCs/RT/tc-hsres.txt", "w")
    haskell_result_file.write(haskell_result)
    haskell_result_file.close()
    # os.system("echo \"%s\" > TCs/RT/tc-hsres.txt" % haskell_result)


get_haskell_testcase_output()
get_python_testcase_output()
evaluate_outputs.evaluation("TCs/RT/tc-pyres.txt", "TCs/RT/tc-hsres.txt")
