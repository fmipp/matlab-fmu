# -----------------------------------------------------------------
# Copyright (c) 2015, AIT Austrian Institute of Technology GmbH.
# All rights reserved. See file MEX_FMU_LICENSE.txt for details.
# -----------------------------------------------------------------

import sys, os, shutil, time, getpass, uuid, urlparse, urllib, getopt, pickle, subprocess, glob


def generateMexFMU(
                fmi_model_identifier,
                script_file_name,
                matlab_install_dir,
                fmi_input_vars,
                fmi_output_vars,
                start_values,
                optional_files,
                mex_fmu_root_dir ):
        """Generate an FMU from MATLAB using binary MEX files.

    Keyword arguments:
        fmi_model_identifier -- FMI model identfier for FMU (string)
        script_file_name -- name of MATLAB script (string)
        matlab_install_dir -- MATLAB installation directory (string)
        fmi_input_vars -- definition of input variable names (list of strings)
        fmi_output_vars -- definition of output variable names (list of strings)
        start_values -- definition of start values (map of strings to strings)
        optional_files -- definition of additional files (list of strings)
        mex_fmu_root_dir -- path root dir of MEX FMU Export Utility (string)
        """
        
        # Template string for XML model description header.
        model_description_header = '<?xml version="1.0" encoding="UTF-8"?>\n<fmiModelDescription fmiVersion="1.0" modelName="__MODEL_NAME__" modelIdentifier="__MODEL_IDENTIFIER__" description="MATLAB/MEX FMI CS export" generationTool="FMI++ MATLAB/MEX Export Utility" generationDateAndTime="__DATE_AND_TIME__" variableNamingConvention="flat" numberOfContinuousStates="0" numberOfEventIndicators="0" author="__USER__" guid="{__GUID__}">\n\t<ModelVariables>\n'

        # Template string for XML model description of scalar variables.
        scalar_variable_node = '\t\t<ScalarVariable name="__VAR_NAME__" valueReference="__VAL_REF__" variability="continuous" causality="__CAUSALITY__">\n\t\t\t<Real__START_VALUE__/>\n\t\t</ScalarVariable>\n'

        # Template string for XML model description footer.
        model_description_footer = '\t</ModelVariables>\n\t<Implementation>\n\t\t<CoSimulation_Tool>\n\t\t\t<Capabilities canHandleVariableCommunicationStepSize="true" canHandleEvents="true" canRejectSteps="false" canInterpolateInputs="false" maxOutputDerivativeOrder="0" canRunAsynchronuously="false" canSignalEvents="false" canBeInstantiatedOnlyOncePerProcess="false" canNotUseMemoryManagementFunctions="true"/>\n\t\t\t<Model entryPoint="fmu://__SCRIPT_FILE_NAME__" manualStart="false" type="application/x-matlab">__ADDITIONAL_FILES__</Model>\n\t\t</CoSimulation_Tool>\n\t</Implementation>\n\t<VendorAnnotations>\n\t\t<matlab arguments="-nosplash -nojvm -logfile __MODEL_IDENTIFIER__.log -r &quot;try; run(\'__SCRIPT_FILE_NAME__\'); catch err; disp(err); end; quit;&quot;" executableURI="__MATLAB_EXE_URI__"/>\n\t</VendorAnnotations>\n</fmiModelDescription>'

        # Create new XML model description file.
        model_description_name = 'modelDescription.xml'
        model_description = open( model_description_name, 'w' )

        #
        # Replace template arguments in header.
        #

        # FMI model identifier.
        model_description_header = model_description_header.replace( '__MODEL_IDENTIFIER__', fmi_model_identifier )
        model_description_footer = model_description_footer.replace( '__MODEL_IDENTIFIER__', fmi_model_identifier )

        # Model name.
        fmi_model_name = os.path.basename( script_file_name ).split( '.' )[0] # Script file name with extension.
        model_description_header = model_description_header.replace( '__MODEL_NAME__', fmi_model_name )

        # Creation date and time.
        model_description_header = model_description_header.replace( '__DATE_AND_TIME__', time.strftime( "%Y-%m-%dT%H:%M:%S" ) )

        # Author name.
        model_description_header = model_description_header.replace( '__USER__', getpass.getuser() )

        # GUID.
        model_description_header = model_description_header.replace( '__GUID__', str( uuid.uuid1() ) )

        # Write header to file.
        model_description.write( model_description_header );

        #
        # Add scalar variable description.
        #
        input_val_ref = 1 # Value references for inputs start with 1.
        for var in fmi_input_vars:
                scalar_variable_description = scalar_variable_node
                scalar_variable_description = scalar_variable_description.replace( '__VAR_NAME__', var )
                scalar_variable_description = scalar_variable_description.replace( '__CAUSALITY__', "input" )
                scalar_variable_description = scalar_variable_description.replace( '__VAL_REF__', str( input_val_ref ) )
                if var in start_values:
                        start_value_description = ' start=\"' + start_values[var] + '\"'
                        scalar_variable_description = scalar_variable_description.replace( '__START_VALUE__', start_value_description )
                        if ( True == verbose ): print '[DEBUG] Added start value to model description: ', var, '=', start_values[var]
                else:
                        scalar_variable_description = scalar_variable_description.replace( '__START_VALUE__', '' )
                input_val_ref += 1
                # Write scalar variable description to file.
                model_description.write( scalar_variable_description );

        # Value references for outputs start with 1001 (except there are already input value references with corresponding values).
        output_val_ref = 1001 if ( input_val_ref < 1001 ) else input_val_ref
        for var in fmi_output_vars:
                scalar_variable_description = scalar_variable_node
                scalar_variable_description = scalar_variable_description.replace( '__VAR_NAME__', var )
                scalar_variable_description = scalar_variable_description.replace( '__CAUSALITY__', "output" )
                scalar_variable_description = scalar_variable_description.replace( '__VAL_REF__', str( output_val_ref ) )
                if var in start_values:
                        start_value_description = ' start=\"' + start_values[var] + '\"'
                        scalar_variable_description = scalar_variable_description.replace( '__START_VALUE__', start_value_description )
                        if ( True == verbose ): print '[DEBUG] Added start value to model description: ', var, '=', start_values[var]
                else:
                        scalar_variable_description = scalar_variable_description.replace( '__START_VALUE__', '' )
                output_val_ref += 1
                # Write scalar variable description to file.
                model_description.write( scalar_variable_description );

        #
        # Replace template arguments in footer.
        #

        # URI of MATLAB main executable (matlab.exe).
        matlab_exe_uri = urlparse.urljoin( 'file:', urllib.pathname2url( matlab_install_dir ) ) + '/bin/win32/matlab.exe'
        model_description_footer = model_description_footer.replace( '__MATLAB_EXE_URI__', matlab_exe_uri )

        # Input script file.
        model_description_footer = model_description_footer.replace( '__SCRIPT_FILE_NAME__', os.path.basename( script_file_name ) )

        # Additional input files.
        if ( 0 == len( optional_files ) ):
                model_description_footer = model_description_footer.replace( '__ADDITIONAL_FILES__', '' )
        else:
                additional_files_description = ''
                for file_name in optional_files:
                        additional_files_description += '\n\t\t\t\t<File file=\"fmu://' + os.path.basename( file_name ) + '\"/>'
                        if ( True == verbose ): print '[DEBUG] Added additional file to model description: ', os.path.basename( file_name )
                additional_files_description += '\n\t\t\t'
                model_description_footer = model_description_footer.replace( '__ADDITIONAL_FILES__', additional_files_description )


        # Write footer to file.
        model_description.write( model_description_footer );

        # Close file.
        model_description.close()

        # Check if model description is XML compliant.
        #import xml.etree.ElementTree as ET
        #tree = ET.parse( 'model_description.xml' )

        # FMU shared library name.
        fmu_shared_library_name = fmi_model_identifier + '.dll'

        # Check if batch file for build process exists.
        build_process_batch_file = mex_fmu_root_dir + '\\build.bat'
        if ( False == os.path.isfile( build_process_batch_file ) ):
                print '\n[ERROR] Could not find file', build_process_batch_file
                raise Exception( 8 )

        # Compile FMU shared library.
        for file_name in glob.glob( fmi_model_identifier + '.*' ):
                if not ( ".m" in file_name ): os.remove( file_name ) # Do not accidentaly remove the script file!
        if ( True == os.path.isfile( 'fmiFunctions.obj' ) ): os.remove( 'fmiFunctions.obj' )
        build_process = subprocess.Popen( [build_process_batch_file, fmi_model_identifier] )
        stdout, stderr = build_process.communicate()

        # Check if batch script has executed successfully.
        if ( False == os.path.isfile( fmu_shared_library_name ) ):
		print '\n[ERROR] Not able to create shared library (%s).' % fmu_shared_library_name
		raise Exception( 16 )

        # Check if working directory for FMU creation already exists.
        if ( True == os.path.isdir( fmi_model_identifier ) ):
                shutil.rmtree( fmi_model_identifier, False )

        # Working directory path for the FMU DLL.
        binaries_dir = os.path.join( fmi_model_identifier, 'binaries', 'win32' )

        # Create working directory (incl. sub-directories) for FMU creation.
        os.makedirs( binaries_dir )

        # Copy all files to working directory.
        shutil.copy( model_description_name, fmi_model_identifier ) # XML model description.
        shutil.copy( script_file_name, fmi_model_identifier ) # MATLAB script.
        for file_name in optional_files: # Additional files.
                shutil.copy( file_name, fmi_model_identifier )
        shutil.copy( fmu_shared_library_name, binaries_dir ) # FMU DLL.


        # Create ZIP archive.
        if ( True == os.path.isfile( fmi_model_identifier + '.zip' ) ):
                os.remove( fmi_model_identifier + '.zip' )
        shutil.make_archive( fmi_model_identifier, 'zip', fmi_model_identifier )

        # Finally, create the FMU!!!
        if ( True == os.path.isfile( fmi_model_identifier + '.fmu' ) ):
                os.remove( fmi_model_identifier + '.fmu' )
        os.rename( fmi_model_identifier + '.zip', fmi_model_identifier + '.fmu' )

        # Clean up.
        if ( False == litter ):
                os.remove( model_description_name )
                os.remove( 'build.log' )
                os.remove( 'fmiFunctions.obj' )
                shutil.rmtree( fmi_model_identifier, False )
                for file_name in glob.glob( fmi_model_identifier + '.*' ):
                        if not ( ( ".fmu" in file_name ) or ( ".dck" in file_name ) or ( ".tpf" in file_name ) ): os.remove( file_name )


# Helper function. Retrieve labels from file. The file is expected to
# have one entry per line, comment lines start with a semicolon (;).
def retrieveLabelsFromFile( file_name, labels ):
        input_file = open( file_name, 'r' ) # Open the file.
        while True:
                line = input_file.readline() # Read next line.
                if not line: break # End of file.

                line = line.strip(' "\'\n') # Strip all leasing and trailing whitespaces etc.

                semicolon_position = line.find( ';' ) # Check for comments.
                if ( 0 == semicolon_position ):
                        continue # Comment line.
                elif ( -1 != semicolon_position ):
                        line = line[0:semicolon_position].strip(' "\'\n') # Remove comment from line

                if 0 != len( line ):
                        labels.append( line ) # Append line to list of labels.
                        

# Helper function
def usage():
        """Print the usage of this script when used as main program."""
        print '\nABOUT:'
        print 'This script generates FMUs for Co-Simulation (tool coupling) from MATLAB scripts with the help of '
        print '\nUSAGE:'
        print 'python mex_fmu_create.py [-h] [-v] [-I matlab_install_dir] -m model_id -s script_file_name [-i input_var_file] [-o output_var_file] [additional_file_1 ... additional_file_N] [var1=start_val1 ... varN=start_valN]'
        print '\nREQUIRED ARGUMENTS:'
        print '-m, --model-id=\t\tspecify FMU model identifier'
        print '-s, --script=\tpath to MATLAB script'
        print '\nOPTIONAL ARGUMENTS:'
        print '-i, --input-var-file=\tspecify file containing list of input variable names'
        print '-o, --output-var-file=\tspecify file containing list of output variable names'
        print '-h, --help\t\tdisplay this information'
        print '-v, --verbose\t\tturn on log messages'
        print '-l, --litter\t\tdo not clean-up intermediate files'
        print '-I, --matlab-install-dir=\tpath to MATLAB installation directory (e.g., C:\\MATLAB)'
        print '\nAdditional files may be specified (e.g., additional scripts or data files) that will be automatically copied to the FMU.'
        print '\nStart values for variables may be defined. For instance, to set variable with name \"var1\" to value 12.34, specifiy \"var1=12.34\" in the command line as optional argument.'


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
                        labels.append( line ) # Append line to list of labels.


# Main function
if __name__ == "__main__":

        if ( None == os.getenv( 'MATLAB_FMIPP_ROOT' ) ):
		        warning = '\n[WARNING] Environment variable "MATLAB_FMIPP_ROOT" is not defined!\n'
		        print warning

        # FMI model identifier.
        fmi_model_identifier = None

        # MATLAB script.
        script_file_name = None

        # File containing FMI input variable names.
        input_var_file_name = None

        # File containing FMI output variable names.
        output_var_file_name = None

        # Set MATLAB install dir.
        matlab_install_dir = None

        # List of optional files (e.g., weather file)
        optional_files = []

        # Dictionary of start values.
        start_values = {}

        # Relative or absolute path to MATLAB/MEX FMU Export Utility.
        mex_fmu_root_dir = os.path.dirname( sys.argv[0] ) if len( os.path.dirname( sys.argv[0] ) ) else '.'

        # Verbose flag.
        verbose = False

        # Litter flag.
        litter = False

        # Parse command line arguments.
        try:
                options_definition_short = "vhlm:s:I:i:o:"
                options_definition_long = [ "verbose", "help", "litter", "model-id=", 'script=', 'matlab-install-dir=', 'input-var-file=', 'output-var-file=' ]
                options, extra = getopt.getopt( sys.argv[1:], options_definition_short, options_definition_long )
        except getopt.GetoptError as err:
                print str( err )
                usage()
                sys.exit(1)

        # Parse options.
        for opt, arg in options:
                if opt in ( '-h', '--help' ):
                        usage()
                        sys.exit()
                elif opt in ( '-m', '--model-id' ):
                        fmi_model_identifier = arg
                elif opt in ( '-s', '--script' ):
                        script_file_name = arg
                elif opt in ( '-i', '--input-var-file' ):
                        input_var_file_name = arg
                elif opt in ( '-o', '--output-var-file' ):
                        output_var_file_name = arg
                elif opt in ( '-I', '--matlab-install-dir' ):
                        matlab_install_dir = arg
                elif opt in ( '-v', '--verbose' ):
                        verbose = True
                elif opt in ( '-l', '--litter' ):
                        litter = True

        # Check if FMI model identifier has been specified.
        if ( None == fmi_model_identifier ):
                print '\n[ERROR] No FMU model identifier specified!'
                usage()
                sys.exit(2)

        # Check if MATLAB script has been specified.
        if ( None == script_file_name ):
                print '\n[ERROR] No MATLAB script specified!'
                usage()
                sys.exit(3)
        elif ( False == os.path.isfile( script_file_name ) ): # Check if specified script exists.
                print '\n[ERROR] Invalid MATLAB script:', script_file_name
                usage()
                sys.exit(4)
        
        # No MATLAB install directory provided -> read from file (created by script 'mex_fmu_install.py').
        if ( None == matlab_install_dir ):
                pkl_file_name = mex_fmu_root_dir + '\\mex_fmu_install.pkl'
                if ( True == os.path.isfile( pkl_file_name ) ):
                        pkl_file = open( pkl_file_name, 'rb' )
                        matlab_install_dir = pickle.load( pkl_file )
                        pkl_file.close()
                else:
                        print '\n[ERROR] Please re-run script \'mex_fmu_install.py\' or provide MATLAB install directory via command line option -i (--matlab-install-dir)!'
                        usage()
                        sys.exit(5)

        # Check if specified MATLAB install directory exists.
        if ( False == os.path.isdir( matlab_install_dir ) ):
                print '\n[WARNING] MATLAB install directory does not exist:', matlab_install_dir
        
        # Retrieve additional files from command line arguments.
        for item in extra:
                if "=" in item:
                        start_value_pair = item.split( '=' )
                        varname = start_value_pair[0].strip(' "\n')
                        value = start_value_pair[1].strip(' "\n')
                        if ( True == verbose ): print '[DEBUG] Found start value:', varname, '=', value
                        start_values[varname] = value;
                elif ( True == os.path.isfile( item ) ): # Check if this is an additional input file.
                        optional_files.append( item )
                        if ( True == verbose ): print '[DEBUG] Found additional file:', item
                else:
                        print '\n[ERROR] Invalid input argument:', item
                        usage()
                        sys.exit(7)

        if ( True == verbose ):
                print '[DEBUG] FMI model identifier:', fmi_model_identifier
                print '[DEBUG] MATLAB script:', script_file_name 
                print '[DEBUG] MATLAB install directory:', matlab_install_dir
                print '[DEBUG] Aditional files:'
                for file_name in optional_files:
                        print '\t', file_name

        # Lists containing the FMI input and output variable names.
        fmi_input_vars = []
        fmi_output_vars = []

        # Parse file to retrieve FMI input variable names.
        if ( None != input_var_file_name ):
                retrieveLabelsFromFile( input_var_file_name, fmi_input_vars );
        if ( True == verbose ):
                print '[DEBUG] FMI input parameters:'
                for var in fmi_input_vars:
                        print '\t', var

        # Parse file to retrieve FMI output variable names.
        if ( None != output_var_file_name ):
                retrieveLabelsFromFile( output_var_file_name, fmi_output_vars );
        if ( True == verbose ):
                print '[DEBUG] FMI output parameters:'
                for var in fmi_output_vars:
                        print '\t', var

        try:
                generateMexFMU(
                        fmi_model_identifier,
                        script_file_name,
                        matlab_install_dir,
                        fmi_input_vars,
                        fmi_output_vars,
                        start_values,
                        optional_files,
                        mex_fmu_root_dir )
        except Exception as e:
                sys.exit( e.args[0] )
        
        if ( True == verbose ): print "[DEBUG] FMU created successfully!"                       