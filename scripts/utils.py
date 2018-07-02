# -----------------------------------------------------------------
# Copyright (c) 2017-2019, AIT Austrian Institute of Technology GmbH.
# All rights reserved. See file MATLAB_FMU_LICENSE.txt for details.
# -----------------------------------------------------------------

#
# Collection of helper functions for creating FMU CS for MATLAB.
#

# Parse command line arguments.
def parseCommandLineArguments( modules ):
    # Create new parser.
    parser = modules.argparse.ArgumentParser( description = 'This script generates FMUs for Co-Simulation (tool coupling) from MATLAB scripts.', prog = 'matlab_fmu_create' )

    # Define optional arguments.
    parser.add_argument( '-v', '--verbose', action = 'store_true', help = 'turn on log messages' )
    parser.add_argument( '-l', '--litter', action = 'store_true', help = 'do not clean-up intermediate files' )
    parser.add_argument( '-i', '--input-var-file', default = None, help = 'specify file containing list of input variable names', metavar = 'INPUT-VAR-FILE' )
    parser.add_argument( '-o', '--output-var-file', default = None, help = 'specify file containing list of output variable names', metavar = 'OUTPUT-VAR-FILE' )
    parser.add_argument( '-f', '--fmi-version', choices = [ '1', '2' ], default = '2', help = 'specify FMI version (default: 2)' )
    parser.add_argument( '-J', '--use-jvm', action = 'store_true', help = 'start JVM together with MATLAB' )
    parser.add_argument( '-F', '--fixed-step', action = 'store_true', help = 'enforce fixed simulation step size' )

    # Define mandatory arguments.
    required_args = parser.add_argument_group( 'required arguments' )
    required_args.add_argument( '-m', '--model-id', required = True, help = 'specify FMU model identifier', metavar = 'MODEL-ID' )
    required_args.add_argument( '-s', '--script', required = True, help = 'path to MATLAB script', metavar = 'SCRIPT' )
    required_args.add_argument( '-I', '--matlab-install-dir', required = True, help = 'path to MATLAB installation directory', metavar = 'MATLAB-INSTALL-DIR' )

    # Parse remaining optional arguments (start values, additional files).
    #parser.add_argument( 'extra_arguments', nargs = modules.argparse.REMAINDER, help = 'extra files and/or start values', metavar = 'additional arguments' )
    parser.add_argument( 'extra_arguments', nargs = '*', default = None, help = 'extra files and/or start values', metavar = 'additional arguments' )

    # Add help for additional files.
    parser.add_argument_group( 'additional files', 'Additional files (e.g., for weather data) may be specified as extra arguments. These files will be automatically copied to the resources directory of the FMU.' )

    # Add help for start values.
    parser.add_argument_group( 'start values', 'Specify start values for FMU input variables and parameters.' )

    return parser.parse_args()


# Parse additional command line inputs (start values, additional files).
def parseAdditionalInputs( extra_arguments, verbose, modules ):
    # List of optional files (e.g., weather file)
    optional_files = []

    # Dictionary of start values.
    start_values = {}

    # Retrieve additional files from command line arguments.
    if extra_arguments != None:
        for item in extra_arguments:
            if '=' in item:
                start_value_pair = item.split( '=' )
                varname = start_value_pair[0].strip(' "\n\t')
                value = start_value_pair[1].strip(' "\n\t')
                if ( True == verbose ): modules.log( '[DEBUG] Found start value: ', varname, '=', value )
                start_values[varname] = value;
            elif ( True == modules.os.path.isfile( item ) ): # Check if this is an additional input file.
                optional_files.append( item )
                if ( True == verbose ): modules.log( '[DEBUG] Found additional file: ', item )
            else:
                modules.log( '\n[ERROR] Invalid input argument: ', item )
                modules.sys.exit(7)

    return ( optional_files, start_values )


# Helper function. Retrieve labels from file. The file is expected to
# have one entry per line, comment lines start with a semicolon (;).
def retrieveLabelsFromFile( file_name, labels ):
    input_file = open( file_name, 'r' ) # Open the file.
    while True:
        line = input_file.readline() # Read next line.
        if not line: break # End of file.

        line = line.strip(' "\'\n\t') # Strip all leading and trailing whitespaces etc.

        semicolon_position = line.find( ';' ) # Check for comments.
        if ( 0 == semicolon_position ):
            continue # Comment line.
        elif ( -1 != semicolon_position ):
            line = line[0:semicolon_position].strip(' "\'\n\t') # Remove comment from line

        if 0 != len( line ):
            [ var_type, var_name ] = line.split( ':' );
            var_type = var_type.strip( ' "\'\t\n' )
            var_name = var_name.strip( ' "\'\t\n' )
            if var_type not in [ 'Real', 'Integer', 'Boolean', 'String' ]:
                log( '\n[ERROR] The type of variable', var_name, 'is not recognized:', var_type )
                sys.exit(8)
            labels.append( [ var_type, var_name ] ) # Append to list of labels.
