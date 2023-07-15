import math
import subprocess


def evaluation(pyres_addr, hsres_addr):
    python_res = subprocess.check_output("cat %s" % pyres_addr, shell=True).decode()
    haskell_res = subprocess.check_output("cat %s" % hsres_addr, shell=True).decode()
    error_msgs = ""

    error_msgs += evaluate(python_res, haskell_res, "OrderRs")
    error_msgs += evaluate(python_res, haskell_res, "Trades")
    error_msgs += evaluate(python_res, haskell_res, "Trade")
    error_msgs += evaluate(python_res, haskell_res, "Orders")
    error_msgs += evaluate(python_res, haskell_res, "Order")
    error_msgs += evaluate(python_res, haskell_res, "Ownerships")
    error_msgs += evaluate(python_res, haskell_res, "Ownership")
    error_msgs += evaluate(python_res, haskell_res, "Credits")
    error_msgs += evaluate(python_res, haskell_res, "Credit")

    assert error_msgs == "", "\nerror_messages:\n" + error_msgs


def evaluate(python_res, haskell_res, template):
    def error_template(expected, output):
        return "\nError matching [%s]! %s = %s\n" \
               "expected:   %s\n" \
               "output:     %s\n" % (
                template, "" if template in ["Order", "Trade"] else "order_id",
                math.ceil((index + 1) / div), expected, output)

    div = 7 if template in ["Ownership", "Credit"] else 1
    hs = find(haskell_res, template)
    py = find(python_res, template)
    for index, rs in enumerate(hs):
        if index < len(py):
            if rs != py[index]:
                return error_template(rs, py[index])
        else:
            return error_template(rs, "Nothing")
    return ""


def find(testcase_output, template):
    return [elem.split("\n", 1)[0].strip() for elem in testcase_output.split("%s\t" % template)[1:]]


def indexed_output(output):
    return [(i + 1, x) for i, x in enumerate(output)]
