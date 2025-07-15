"""
33_tip_clearance
----------------

Demonstrate how to get tip displacement from OpenFAST


"""

import os
import numpy as np
import matplotlib.pyplot as plt
from rosco.toolbox.ofTools.case_gen.run_FAST import run_FAST_ROSCO
from rosco.toolbox.ofTools.case_gen import CaseLibrary as cl
from rosco.toolbox.ofTools.fast_io import output_processing

rpm2RadSec = 2.0 * (np.pi) / 60.0
deg2rad = np.pi / 180.0

# directories
this_dir = os.path.dirname(os.path.abspath(__file__))
example_out_dir = os.path.join(this_dir, "examples_out")
os.makedirs(example_out_dir, exist_ok=True)

FULL_TEST = True


def main():
    # Input yaml and output directory
    parameter_filename = os.path.join(this_dir, "Tune_Cases/IEA15MW.yaml")

    # Set DISCON input dynamically through yaml/dict
    controller_params = {}
    controller_params["DISCON"] = {}
    controller_params["DISCON"]["Echo"] = 1
    controller_params["LoggingLevel"] = 3


    # simulation set up
    r = run_FAST_ROSCO()
    r.tuning_yaml = parameter_filename
    r.case_inputs = {}

    # Disable floating DOFs for clarity
    r.case_inputs[("ElastoDyn", "PtfmSgDOF")] = {"vals": ["False"], "group": 0}
    r.case_inputs[("ElastoDyn", "PtfmSwDOF")] = {"vals": ["False"], "group": 0}
    r.case_inputs[("ElastoDyn", "PtfmHvDOF")] = {"vals": ["False"], "group": 0}
    r.case_inputs[("ElastoDyn", "PtfmRDOF")] = {"vals": ["False"], "group": 0}
    r.case_inputs[("ElastoDyn", "PtfmPDOF")] = {"vals": ["False"], "group": 0}
    r.case_inputs[("ElastoDyn", "PtfmYDOF")] = {"vals": ["False"], "group": 0}

    # IPC has to be enabled in the bladed interface.
    r.case_inputs[("ServoDyn", "Ptch_Cntrl")] = {"vals": ["1"], "group": 0}

    run_dir = os.path.join(example_out_dir, "33_tip_clearance/0_setup_sim")

    # Wind case (steady)
    r.wind_case_fcn = cl.power_curve  # type: ignore
    r.wind_case_opts = {
        "U": [12],
        "TMax": 300,
    }
    if not FULL_TEST:
        r.wind_case_opts["TMax"] = 2


    # Run simulation
    os.makedirs(run_dir, exist_ok=True)
    r.controller_params = controller_params
    r.save_dir = run_dir
    # r.openfast_exe = '/Users/dzalkind/Tools/openfast-mc/build/glue-codes/openfast/openfast'   # path do compiled OpenFAST executable
    r.openfast_exe = os.path.join(this_dir, "../..", "OpenFAST/install/bin/openfast")
    r.run_FAST()

    # Plot output
    outfile0 = [os.path.join(run_dir, "IEA15MW_0.outb")]
    # outfile1 = [os.path.join(run_dir, "IEA15MW_1.outb")]
    cases = {}
    cases["Baseline"] = ["Wind1VelX", "BldPitch1", "GenTq", "RotSpeed", "GenPwr"]
    fast_out = output_processing.output_processing()
    
    fast_out.load_fast_out(outfile0)
    fast_out.plot_fast_out(cases=cases, showplot=False)

    # fast_out.load_fast_out(outfile1)
    # fast_out.plot_fast_out(cases=cases, showplot=False)

    plt.savefig(os.path.join(example_out_dir, "32_startup.png"))


if __name__ == "__main__":
    main()
