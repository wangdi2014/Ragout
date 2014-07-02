#!/usr/bin/env python

from __future__ import print_function
import os
import subprocess
import shutil

TESTS = {"ecoli" : {"recipe" : "examples/E.Coli/ecoli.rcp",
                    "coords" : "examples/E.Coli/mg1655.coords",
                    "max_errros" : 0,
                    "min_contigs" : 79,
                    "max_scaffolds" : 1,
                    "outdir" : "ecoli-test"},
         "helicobacter" : {"recipe" : "examples/H.Pylori/helicobacter.rcp",
                           "coords" : "examples/H.Pylori/SJM180.coords",
                           "max_errros" : 0,
                           "min_contigs" : 45,
                           "max_scaffolds" : 1,
                           "outdir" : "helicobacter-test"},
         "cholerae" : {"recipe" : "examples/V.Cholerae/cholerae.rcp",
                       "coords" : "examples/V.Cholerae/h1.coords",
                       "max_errros" : 0,
                       "min_contigs" : 170,
                       "max_scaffolds" : 2,
                       "outdir" : "cholerae-test"},
         "aureus" : {"recipe" : "examples/S.Aureus/aureus.rcp",
                     "coords" : "examples/S.Aureus/usa300.coords",
                     "max_errros" : 1,
                     "min_contigs" : 100,
                     "max_scaffolds" : 1,
                     "outdir" : "aureus-test"}}

TEST_DIR = "test-dir"
RAGOUT_EXEC = "ragout.py"
VERIFY_EXEC = os.path.join("scripts", "verify-order.py")


def test_environment():
    if not os.path.isfile(RAGOUT_EXEC):
        raise RuntimeError("File \"{0}\" was not found".format(RAGOUT_EXEC))

    if not os.path.isfile(VERIFY_EXEC):
        raise RuntimeError("File \"{0}\" was not found".format(VERIFY_EXEC))


def run_test(parameters):
    outdir = os.path.join(TEST_DIR, parameters["outdir"])
    cmd = ["python2.7", "ragout.py", parameters["recipe"],
           "--outdir", outdir, "--refine"]
    print("Running:", " ".join(cmd), "\n")
    subprocess.check_call(cmd)

    ord_simple = os.path.join(outdir, "scaffolds.ord")
    ord_simple_out = os.path.join(outdir, "scaffolds.ord_verify")
    ord_refined = os.path.join(outdir, "scaffolds_refined.ord")
    ord_refined_out = os.path.join(outdir, "scaffolds_refined.ord_verify")

    cmd = ["python2.7", VERIFY_EXEC, parameters["coords"], ord_simple]
    print("Running:", " ".join(cmd), "\n")
    subprocess.check_call(cmd, stdout=open(ord_simple_out, "w"))

    with open(ord_simple_out, "r") as f:
        for line in f:
            #print(line, end="")
            if line.startswith("Total miss-ordered: "):
                value = int(line.strip()[20:])
                print("Errors:", value)
                if value > parameters["max_errros"]:
                    raise RuntimeError("Too much miss-ordered contigs")

            if line.startswith("Total contigs: "):
                value = int(line.strip()[15:])
                print("Contigs:", value)
                if value < parameters["min_contigs"]:
                    raise RuntimeError("Too few contigs")

            if line.startswith("Total scaffolds: "):
                value = int(line.strip()[17:])
                print("Scaffolds:", value)
                if value > parameters["max_scaffolds"]:
                    raise RuntimeError("Too much scaffolds")

    cmd = ["python2.7", VERIFY_EXEC, parameters["coords"], ord_refined]
    print("Running:", " ".join(cmd), "\n")
    subprocess.check_call(cmd, stdout=open(ord_refined_out, "w"))


def main():
    test_environment()
    if os.path.isdir(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.mkdir(TEST_DIR)

    for name, params in TESTS.items():
        print("\n********Running test:", name, "********\n")
        run_test(params)

    print("\n********All tests were succesfully completed********")
    shutil.rmtree(TEST_DIR)


if __name__ == "__main__":
    main()