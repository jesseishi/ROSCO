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

FULL_TEST = False


def sweep_tcipc_control_mode(start_group, **control_sweep_opts):
    """
    Sweep TCIPC_ControlMode parameter to compare baseline (0) vs enabled (1)
    
    Args:
        start_group: Starting group number for parameter sweep
        **control_sweep_opts: Additional control sweep options
    
    Returns:
        case_inputs_control: Dictionary with TCIPC_ControlMode sweep values
    """
    case_inputs_control = {}
    
    # Define the TCIPC_ControlMode values to sweep
    tcipc_modes = [0, 1]  # 0: baseline (off), 1: enabled (on)
    
    # Set up the parameter sweep
    case_inputs_control[('DISCON_in','TCIPC_ControlMode')] = {
        'vals': tcipc_modes, 
        'group': start_group
    }
    
    return case_inputs_control


def main():
    # Input yaml and output directory
    parameter_filename = os.path.join(this_dir, "Tune_Cases/IEA15MW.yaml")

    # Set DISCON input dynamically through yaml/dict
    controller_params = {}
    controller_params["DISCON"] = {}
    controller_params["DISCON"]["Echo"] = 1
    controller_params["LoggingLevel"] = 3

    # Set the options for the tower clearance IPC controller
    controller_params["DISCON"]["TCIPC_MaxTipDeflection"] = 10

    # simulation set up
    r = run_FAST_ROSCO()
    r.tuning_yaml = parameter_filename
    r.case_inputs = {}

    # Set up the TCIPC_ControlMode parameter sweep
    r.control_sweep_fcn = sweep_tcipc_control_mode

    # Disable floating DOFs for clarity
    r.case_inputs[("ElastoDyn", "PtfmSgDOF")] = {"vals": ["False"], "group": 0}
    r.case_inputs[("ElastoDyn", "PtfmSwDOF")] = {"vals": ["False"], "group": 0}
    r.case_inputs[("ElastoDyn", "PtfmHvDOF")] = {"vals": ["False"], "group": 0}
    r.case_inputs[("ElastoDyn", "PtfmRDOF")] = {"vals": ["False"], "group": 0}
    r.case_inputs[("ElastoDyn", "PtfmPDOF")] = {"vals": ["False"], "group": 0}
    r.case_inputs[("ElastoDyn", "PtfmYDOF")] = {"vals": ["False"], "group": 0}

    # IPC has to be enabled in the bladed interface.
    r.case_inputs[("ServoDyn", "Ptch_Cntrl")] = {"vals": ["1"], "group": 0}

    run_dir = os.path.join(example_out_dir, "33_tip_clearance/compare_tcipc_modes")

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
    # The sweep will generate multiple output files: IEA15MW_0.outb (TCIPC_ControlMode=0) and IEA15MW_1.outb (TCIPC_ControlMode=1)
    outfile0 = [os.path.join(run_dir, "IEA15MW_0.outb")]  # Baseline (TCIPC_ControlMode = 0)
    outfile1 = [os.path.join(run_dir, "IEA15MW_1.outb")]  # Enabled (TCIPC_ControlMode = 1)
    
    cases = {}
    cases["Baseline"] = ["Wind1VelX", "BldPitch1", "GenTq", "RotSpeed", "GenPwr", "TipDxc1"]
    cases["TCIPC"] = ["Wind1VelX", "BldPitch1", "GenTq", "RotSpeed", "GenPwr", "TipDxc1"]
    
    fast_out = output_processing.output_processing()
    
    # Load and plot baseline case (TCIPC_ControlMode = 0)
    fast_out.load_fast_out(outfile0)
    fast_out.plot_fast_out(cases=cases, showplot=False)

    # Load and plot enabled case (TCIPC_ControlMode = 1)
    fast_out.load_fast_out(outfile1)
    fast_out.plot_fast_out(cases=cases, showplot=False)

    plt.savefig(os.path.join(example_out_dir, "33_tip_clearance_comparison.png"))


if __name__ == "__main__":
    main()
