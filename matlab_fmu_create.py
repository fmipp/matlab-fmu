# -----------------------------------------------------------------
# Copyright (c) 2015, AIT Austrian Institute of Technology GmbH.
# All rights reserved. See file MEX_FMU_LICENSE.txt for details.
# -----------------------------------------------------------------

### Setup for Python 2.
try:
    import sys, os, shutil, time, getpass, uuid, urlparse, urllib, getopt, pickle, subprocess, glob
except:
    pass

### Setup for Python 3.
try:
    import sys, os, shutil, time, getpass, uuid, urllib.parse as urlparse, urllib.request as urllib, getopt, pickle, subprocess, glob
except:
    pass

def log( *arg ):
    print( ' '.join( map( str, arg ) ) )
    sys.stdout.flush()

def generateMexFMU(
                fmi_model_identifier,
                class_file_name,
                matlab_install_dir,
                fmi_input_vars,
                fmi_output_vars,
                start_values,
                optional_files,
                matlab_fmu_root_dir,
                use_jvm,
                fixed_step ):
        """Generate an FMU from MATLAB using binary MEX files.

    Keyword arguments:
        fmi_model_identifier -- FMI model identfier for FMU (string)
        class_file_name -- name of MATLAB script (string)
        matlab_install_dir -- MATLAB installation directory (string)
        fmi_input_vars -- definition of input variable names (list of strings)
        fmi_output_vars -- definition of output variable names (list of strings)
        start_values -- definition of start values (map of strings to strings)
        optional_files -- definition of additional files (list of strings)
        matlab_fmu_root_dir -- path root dir of FMI++ MATLAB FMU Export Utility (string)
        use_jvm -- start JVM together with MATLAB (boolean)
        fixed_step -- enforce fixed step simulation (boolean)
        """

        fmi_model_name = os.path.basename( class_file_name ).split( '.' )[0] # Class definition file name with extension.

        startup_flags = '-nosplash -nojvm' if ( use_jvm == False ) else '-nosplash'

        # Template string for XML model description header.
        model_description_header = '<?xml version="1.0" encoding="UTF-8"?>\n<fmiModelDescription fmiVersion="1.0" modelName="__MODEL_NAME__" modelIdentifier="__MODEL_IDENTIFIER__" description="MATLAB/MEX FMI CS export" generationTool="FMI++ MATLAB/MEX Export Utility" generationDateAndTime="__DATE_AND_TIME__" variableNamingConvention="flat" numberOfContinuousStates="0" numberOfEventIndicators="0" author="__USER__" guid="{__GUID__}">\n\t<ModelVariables>\n'

        # Template string for XML model description of scalar variables.
        scalar_variable_node = '\t\t<ScalarVariable name="__VAR_NAME__" valueReference="__VAL_REF__" variability="continuous" causality="__CAUSALITY__">\n\t\t\t<__VAR_TYPE____START_VALUE__/>\n\t\t</ScalarVariable>\n'

        # Template string for XML model description footer.
        model_description_footer = '\t</ModelVariables>\n\t<Implementation>\n\t\t<CoSimulation_Tool>\n\t\t\t<Capabilities canHandleVariableCommunicationStepSize="__VARIABLE_COM_STEP__" canHandleEvents="true" canRejectSteps="false" canInterpolateInputs="false" maxOutputDerivativeOrder="0" canRunAsynchronuously="false" canSignalEvents="false" canBeInstantiatedOnlyOncePerProcess="false" canNotUseMemoryManagementFunctions="true"/>\n\t\t\t<Model entryPoint="fmu://__CLASS_FILE_NAME__" manualStart="false" type="application/x-matlab">__ADDITIONAL_FILES__</Model>\n\t\t</CoSimulation_Tool>\n\t</Implementation>\n\t<VendorAnnotations>\n\t\t<matlab arguments="__STARTUP_FLAGS__ -logfile __MODEL_IDENTIFIER__.log -r &quot;try; fmippPath=getenv(\'MATLAB_FMIPP_ROOT\'); addpath(genpath(fullfile(fmippPath,\'packages\'))); obj = __MODEL_NAME__(); obj.initBackEnd(); obj.run(); catch err; disp(err); end; quit;&quot;" executableURI="__MATLAB_EXE_URI__"/>\n\t</VendorAnnotations>\n</fmiModelDescription>'

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
        model_description_header = model_description_header.replace( '__MODEL_NAME__', fmi_model_name )
        model_description_footer = model_description_footer.replace( '__MODEL_NAME__', fmi_model_name )

        # Creation date and time.
        model_description_header = model_description_header.replace( '__DATE_AND_TIME__', time.strftime( "%Y-%m-%dT%H:%M:%S" ) )

        # Author name.
        model_description_header = model_description_header.replace( '__USER__', getpass.getuser() )

        # GUID.
        model_description_header = model_description_header.replace( '__GUID__', str( uuid.uuid1() ) )

        # MATLAB startup flags.
        model_description_footer = model_description_footer.replace( '__STARTUP_FLAGS__', startup_flags )

        # Enforce fixed simulation step size.
        if fixed_step == True:
                model_description_footer = model_description_footer.replace( '__VARIABLE_COM_STEP__', 'false' )
        else:
                model_description_footer = model_description_footer.replace( '__VARIABLE_COM_STEP__', 'true' )

        # Write header to file.
        model_description.write( model_description_header );

        #
        # Add scalar variable description.
        #
        input_val_ref = 1 # Value references for inputs start with 1.
        for var in fmi_input_vars:
                var_type = var[0]
                var_name = var[1]
                scalar_variable_description = scalar_variable_node
                scalar_variable_description = scalar_variable_description.replace( '__VAR_NAME__', var_name )
                scalar_variable_description = scalar_variable_description.replace( '__VAR_TYPE__', var_type )
                scalar_variable_description = scalar_variable_description.replace( '__CAUSALITY__', "input" )
                scalar_variable_description = scalar_variable_description.replace( '__VAL_REF__', str( input_val_ref ) )
                if var_name in start_values:
                        start_value_description = ' start=\"' + start_values[var_name] + '\"'
                        scalar_variable_description = scalar_variable_description.replace( '__START_VALUE__', start_value_description )
                        if ( True == verbose ): log( '[DEBUG] Added start value to model description: ', var_name, '=', start_values[var_name] )
                else:
                        scalar_variable_description = scalar_variable_description.replace( '__START_VALUE__', '' )
                input_val_ref += 1
                # Write scalar variable description to file.
                model_description.write( scalar_variable_description );

        # Value references for outputs start with 1001 (except there are already input value references with corresponding values).
        output_val_ref = 1001 if ( input_val_ref < 1001 ) else input_val_ref
        for var in fmi_output_vars:
                var_type = var[0]
                var_name = var[1]
                scalar_variable_description = scalar_variable_node
                scalar_variable_description = scalar_variable_description.replace( '__VAR_NAME__', var_name )
                scalar_variable_description = scalar_variable_description.replace( '__VAR_TYPE__', var_type )
                scalar_variable_description = scalar_variable_description.replace( '__CAUSALITY__', "output" )
                scalar_variable_description = scalar_variable_description.replace( '__VAL_REF__', str( output_val_ref ) )
                if var_name in start_values:
                        start_value_description = ' start=\"' + start_values[var_name] + '\"'
                        scalar_variable_description = scalar_variable_description.replace( '__START_VALUE__', start_value_description )
                        if ( True == verbose ): log( '[DEBUG] Added start value to model description: ', var_name, '=', start_values[var_name] )
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
        model_description_footer = model_description_footer.replace( '__CLASS_FILE_NAME__', os.path.basename( class_file_name ) )

        # Additional input files.
        if ( 0 == len( optional_files ) ):
                model_description_footer = model_description_footer.replace( '__ADDITIONAL_FILES__', '' )
        else:
                additional_files_description = ''
                for file_name in optional_files:
                        additional_files_description += '\n\t\t\t\t<File file=\"fmu://' + os.path.basename( file_name ) + '\"/>'
                        if ( True == verbose ): log( '[DEBUG] Added additional file to model description: ', os.path.basename( file_name ) )
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
        build_process_batch_file = matlab_fmu_root_dir + '\\build.bat'
        if ( False == os.path.isfile( build_process_batch_file ) ):
                log( '\n[ERROR] Could not find file', build_process_batch_file )
                raise Exception( 8 )

        # Compile FMU shared library.
        for file_name in glob.glob( fmi_model_identifier + '.*' ):
                if not ( ".m" in file_name ): os.remove( file_name ) # Do not accidentaly remove the script file!
        if ( True == os.path.isfile( 'fmiFunctions.obj' ) ): os.remove( 'fmiFunctions.obj' )
        build_process = subprocess.Popen( [build_process_batch_file, fmi_model_identifier] )
        stdout, stderr = build_process.communicate()

        # Check if batch script has executed successfully.
        if ( False == os.path.isfile( fmu_shared_library_name ) ):
                log( '\n[ERROR] Not able to create shared library:', fmu_shared_library_name )
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
        shutil.copy( class_file_name, fmi_model_identifier ) # MATLAB script.
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
                        if not ( ( ".fmu" in file_name ) or ( ".m" in file_name ) ): os.remove( file_name )


# Helper function. Retrieve labels from file. The file is expected to
# have one entry per line, comment lines start with a semicolon (;).
def retrieveLabelsFromFile( file_name, labels ):
        input_file = open( file_name, 'r' ) # Open the file.
        while True:
                line = input_file.readline() # Read next line.
                if not line: break # End of file.

                line = line.strip(' "\'\t\n') # Strip all leasing and trailing whitespaces etc.

                semicolon_position = line.find( ';' ) # Check for comments.
                if ( 0 == semicolon_position ):
                        continue # Comment line.
                elif ( -1 != semicolon_position ):
                        line = line[0:semicolon_position].strip(' "\'\t\n') # Remove comment from line

                if 0 != len( line ):
                        [ var_type, var_name ] = line.split( ':' );
                        var_type = var_type.strip(' "\'\t\n')
                        var_name = var_name.strip(' "\'\t\n')
                        if var_type not in [ 'Real', 'Integer', 'Boolean', 'String' ]:
                                log( '\n[ERROR] The type of variable', var_name, 'is not recognized:', var_type )
                                sys.exit(8)
                        labels.append( [ var_type, var_name ] ) # Append to list of labels.


# Helper function
def usage():
        """Print the usage of this script when used as main program."""
        log( '\nABOUT:' )
        log( 'This script generates FMUs for Co-Simulation (tool coupling) from MATLAB scripts with the help of ' )
        log( '\nUSAGE:' )
        log( 'python mex_fmu_create.py [-h] [-v] [-I matlab_install_dir] -m model_id -s class_file_name [-i input_var_file] [-o output_var_file] [additional_file_1 ... additional_file_N] [var1=start_val1 ... varN=start_valN]' )
        log( '\nREQUIRED ARGUMENTS:' )
        log( '-m, --model-id=\t\tspecify FMU model identifier' )
        log( '-s, --script=\tpath to MATLAB script' )
        log( '\nOPTIONAL ARGUMENTS:' )
        log( '-i, --input-var-file=\tspecify file containing list of input variable names' )
        log( '-o, --output-var-file=\tspecify file containing list of output variable names' )
        log( '-h, --help\t\tdisplay this information' )
        log( '-v, --verbose\t\tturn on log messages' )
        log( '-l, --litter\t\tdo not clean-up intermediate files' )
        log( '-J, --useJVM\t\tstart JVM together with MATLAB' )
        log( '-F, --fixedStep\t\tenforce fixed simulation step size' )
        log( '-I, --matlab-install-dir=\tpath to MATLAB installation directory (e.g., C:\\MATLAB)' )
        log( '\nAdditional files may be specified (e.g., additional scripts or data files) that will be automatically copied to the FMU.' )
        log( '\nStart values for variables may be defined. For instance, to set variable with name \"var1\" to value 12.34, specifiy \"var1=12.34\" in the command line as optional argument.' )


# Main function
if __name__ == "__main__":

        if ( None == os.getenv( 'MATLAB_FMIPP_ROOT' ) ):
		        warning = '\n[WARNING] Environment variable "MATLAB_FMIPP_ROOT" is not defined!\n'
		        log( warning )

        # FMI model identifier.
        fmi_model_identifier = None

        # MATLAB script.
        class_file_name = None

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
        matlab_fmu_root_dir = os.path.dirname( sys.argv[0] ) if len( os.path.dirname( sys.argv[0] ) ) else '.'

        # Verbose flag.
        verbose = False

        # Litter flag.
        litter = False

        # Flag for starting MATLAB with/without JVM.
        use_jvm = False

        # Flag for starting MATLAB with/without JVM.
        fixed_step = False

        # Parse command line arguments.
        try:
                options_definition_short = "vhlJFm:c:I:i:o:"
                options_definition_long = [ "verbose", "help", "litter", "useJVM", "fixedStep", "model-id=", 'class=', 'matlab-install-dir=', 'input-var-file=', 'output-var-file=' ]
                options, extra = getopt.getopt( sys.argv[1:], options_definition_short, options_definition_long )
        except getopt.GetoptError as err:
                log( str( err ) )
                usage()
                sys.exit(1)

        # Parse options.
        for opt, arg in options:
                if opt in ( '-h', '--help' ):
                        usage()
                        sys.exit()
                elif opt in ( '-m', '--model-id' ):
                        fmi_model_identifier = arg
                elif opt in ( '-c', '--class' ):
                        class_file_name = arg
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
                elif opt in ( '-J', '--useJVM' ):
                        use_jvm = True
                elif opt in ( '-F', '--fixedStep' ):
                        fixed_step = True

        # Check if FMI model identifier has been specified.
        if ( None == fmi_model_identifier ):
                log( '\n[ERROR] No FMU model identifier specified!' )
                usage()
                sys.exit(2)

        # Check if MATLAB class definition file has been specified.
        if ( None == class_file_name ):
                log( '\n[ERROR] No MATLAB class definition file specified!' )
                usage()
                sys.exit(3)
        elif ( False == os.path.isfile( class_file_name ) ): # Check if specified class definition file exists.
                log( '\n[ERROR] Invalid MATLAB class definition file:', class_file_name )
                usage()
                sys.exit(4)

        # No MATLAB install directory provided.
        if ( None == matlab_install_dir ):
                log( '\n[ERROR] Invalid MATLAB install dir:', matlab_install_dir )
                usage()
                sys.exit(5)

        # Check if specified MATLAB install directory exists.
        if ( False == os.path.isdir( matlab_install_dir ) ):
                log( '\n[WARNING] MATLAB install directory does not exist:', matlab_install_dir )

        # Retrieve additional files from command line arguments.
        for item in extra:
                if "=" in item:
                        start_value_pair = item.split( '=' )
                        varname = start_value_pair[0].strip(' "\n')
                        value = start_value_pair[1].strip(' "\n')
                        if ( True == verbose ): log( '[DEBUG] Found start value:', varname, '=', value )
                        start_values[varname] = value;
                elif ( True == os.path.isfile( item ) ): # Check if this is an additional input file.
                        optional_files.append( item )
                        if ( True == verbose ): log( '[DEBUG] Found additional file:', item )
                else:
                        log( '\n[ERROR] Invalid input argument:', item )
                        usage()
                        sys.exit(7)

        if ( True == verbose ):
                log( '[DEBUG] FMI model identifier:', fmi_model_identifier )
                log( '[DEBUG] MATLAB class definition:', class_file_name )
                log( '[DEBUG] MATLAB install directory:', matlab_install_dir )
                if True == use_jvm: log( '[DEBUG] Using JVM.' )
                if True == fixed_step: log( '[DEBUG] Enforce fixed step size.' )
                if 0 != len( optional_files ): log( '[DEBUG] Additional files:' )
                for file_name in optional_files:
                        log( '\t', file_name )

        # Lists containing the FMI input and output variable names.
        fmi_input_vars = []
        fmi_output_vars = []

        # Parse file to retrieve FMI input variable names.
        if ( None != input_var_file_name ):
                retrieveLabelsFromFile( input_var_file_name, fmi_input_vars );
        if ( True == verbose ):
                log( '[DEBUG] FMI input variables/parameters:' )
                for var in fmi_input_vars:
                        log( '\t', var[0], ':', var[1] )

        # Parse file to retrieve FMI output variable names.
        if ( None != output_var_file_name ):
                retrieveLabelsFromFile( output_var_file_name, fmi_output_vars );
        if ( True == verbose ):
                log( '[DEBUG] FMI output variables:' )
                for var in fmi_output_vars:
                        log( '\t', var[0], ':', var[1] )

        try:
                generateMexFMU(
                        fmi_model_identifier,
                        class_file_name,
                        matlab_install_dir,
                        fmi_input_vars,
                        fmi_output_vars,
                        start_values,
                        optional_files,
                        matlab_fmu_root_dir,
                        use_jvm,
                        fixed_step )
        except Exception as e:
                sys.exit( e.args[0] )

        if ( True == verbose ): log( "[DEBUG] FMU created successfully!" )
