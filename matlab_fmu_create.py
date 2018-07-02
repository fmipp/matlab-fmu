# -----------------------------------------------------------------
# Copyright (c) 2017-2019, AIT Austrian Institute of Technology GmbH.
# All rights reserved. See file MATLAB_FMU_LICENSE.txt for details.
# -----------------------------------------------------------------

#
# This file is used to create FMUs for CoSimulation from MATLAB scripts.
#

### Setup for Python 2.
try:
    import sys, os, shutil, time, getpass, uuid, getopt, pickle, subprocess, glob, argparse, urlparse, urllib, collections
except:
    pass

### Setup for Python 3.
try:
    import sys, os, shutil, time, getpass, uuid, getopt, pickle, subprocess, glob, argparse, urllib.parse as urlparse, urllib.request as urllib, collections
except:
    pass

def log( *arg ):
    print( ' '.join( map( str, arg ) ) )
    sys.stdout.flush()


from scripts.utils import *
from scripts.generate_fmu import *


def main( matlab_fmu_root_dir = os.path.dirname( __file__ ), parser = None ):

    # Create container for all used Python modules, which will be passed to all called functions.
    # This makes it easier to run this script with different Python version (2.x and 3.x).
    Modules = collections.namedtuple( 'Modules', [ 'sys', 'os', 'shutil', 'time', 'getpass', 'uuid', 'urlparse', 'urllib', 'getopt', 'pickle', 'subprocess', 'glob', 'argparse', 'log' ] )
    modules = Modules( sys, os, shutil, time, getpass, uuid, urlparse, urllib, getopt, pickle, subprocess, glob, argparse, log )

    # Retrieve parsed command line arguments.
    cmd_line_args = parseCommandLineArguments( modules ) if ( parser == None ) else parser()

    # FMI model identifier.
    fmi_model_identifier = cmd_line_args.model_id

    # MATLAB script.
    class_file_name = cmd_line_args.script

    # File containing FMI input variable names.
    input_var_file_name = cmd_line_args.input_var_file

    # File containing FMI output variable names.
    output_var_file_name = cmd_line_args.output_var_file

    # Set MATLAB install dir.
    matlab_install_dir = cmd_line_args.matlab_install_dir

    # Verbose flag.
    verbose = cmd_line_args.verbose

    # Litter flag.
    litter = cmd_line_args.litter

    # Flag for starting MATLAB with/without JVM.
    use_jvm = cmd_line_args.use_jvm

    # Flag for starting MATLAB with/without JVM.
    fixed_step = cmd_line_args.fixed_step

    # FMI version
    fmi_version = cmd_line_args.fmi_version
    if ( True == verbose ): modules.log( '[DEBUG] Using FMI version', fmi_version )

    # Check if specified MATLAB script exists.
    if ( False == os.path.isfile( class_file_name ) ):
        modules.log( '\n[ERROR] Specified MATLAB script not found: ', class_file_name )
        sys.exit(4)

    # Retrieve start values and additional files from command line arguments.
    ( optional_files, start_values ) = parseAdditionalInputs( cmd_line_args.extra_arguments, verbose, modules  )

    # Lists containing the FMI input and output variable names.
    fmi_input_vars = []
    fmi_output_vars = []

    # Parse file to retrieve FMI input variable names.
    if ( None != input_var_file_name ):
        retrieveLabelsFromFile( input_var_file_name, fmi_input_vars );

    # Parse file to retrieve FMI output variable names.
    if ( None != output_var_file_name ):
        retrieveLabelsFromFile( output_var_file_name, fmi_output_vars );

    # Check if specified MATLAB install directory exists.
    if ( False == modules.os.path.isdir( matlab_install_dir ) ):
        modules.log( '\n[WARNING] Provided MATLAB installation directory does not exist: ', matlab_install_dir )

    if ( True == verbose ):
        modules.log( '[DEBUG] FMI model identifier: ', fmi_model_identifier )
        modules.log( '[DEBUG] MATLAB class definition: ', class_file_name )
        modules.log( '[DEBUG] MATLAB install directory: ', matlab_install_dir )
        if True == use_jvm: log( '[DEBUG] Using JVM.' )
        if True == fixed_step: log( '[DEBUG] Enforce fixed step size.' )

        if 0 != len( optional_files ): log( '[DEBUG] Additional files:' )
        for file_name in optional_files: modules.log( '\t', file_name )

        modules.log( '[DEBUG] FMI input variables/parameters:' )
        for var in fmi_input_vars: modules.log( '\t', var[0], ':', var[1] )

        modules.log( '[DEBUG] FMI output variables:' )
        for var in fmi_output_vars: modules.log( '\t', var[0], ':', var[1] )

    #try:
    fmu_name = generateMatlabFMU(
        fmi_version,
        fmi_model_identifier,
        class_file_name,
        matlab_install_dir,
        fmi_input_vars,
        fmi_output_vars,
        start_values,
        optional_files,
        matlab_fmu_root_dir,
        use_jvm,
        fixed_step,
        verbose,
        litter,
        modules )

    if ( True == verbose ): modules.log( "[DEBUG] FMU created successfully:", fmu_name )

    # except Exception as e:
        # modules.log( e )
        # modules.sys.exit( e.args[0] )

# Main function
if __name__ == "__main__":
    main()
