# -----------------------------------------------------------------
# Copyright (c) 2017-2019, AIT Austrian Institute of Technology GmbH.
# All rights reserved. See file MATLAB_FMU_LICENSE.txt for details.
# -----------------------------------------------------------------

#
# Collection of helper functions for creating FMU CS for MATLAB.
#

### Import helper functions for specific FMI versions.
from .fmi1 import *
from .fmi2 import *


def generateMatlabFMU(
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
    modules ):
    """Generate an FMU for MATLAB.

    Keyword arguments:
        fmi_version -- FMI version (string)
        fmi_model_identifier -- FMI model identfier for FMU (string)
        class_file_name -- name of MATLAB script (string)
        matlab_install_dir -- MATLAB installation directory (string)
        fmi_input_vars -- definition of input variable names (list of strings)
        fmi_output_vars -- definition of output variable names (list of strings)
        start_values -- definition of start values (map of strings to strings)
        optional_files -- definition of additional files (list of strings)
        matlab_fmu_root_dir -- path root dir of MATLAB FMU Export Utility (string)
        use_jvm -- specify whether to start JVM together with MATLAB (boolean)
        fixed_step -- enforce fixed simulation step size (boolean)
        verbose -- verbosity flag (boolean)
        litter -- do not clean-up intermediate files (boolean)
        modules -- named tuple containing all imported modules
    """

    # Create FMU model description.
    model_description_name = createModelDescription(
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
        modules )

    # Create FMU shared library.
    fmu_shared_library_name = createSharedLibrary( fmi_model_identifier, matlab_fmu_root_dir, fmi_version, verbose, modules )

    # Check if working directory for FMU creation already exists.
    if ( True == modules.os.path.isdir( fmi_model_identifier ) ):
        modules.shutil.rmtree( fmi_model_identifier, False )

    # Working directory path for the FMU DLL.
    binaries_dir = modules.os.path.join( fmi_model_identifier, 'binaries', 'win64' )

    # Create working directory (incl. sub-directories) for FMU creation.
    modules.os.makedirs( binaries_dir )

    # Resources directory path.
    resources_dir = modules.os.path.join( fmi_model_identifier, 'resources' )

    # Create resources directory for FMU creation.
    modules.os.makedirs( resources_dir )

    # Copy all files to working directory.
    modules.shutil.copy( model_description_name, fmi_model_identifier ) # XML model description.
    modules.shutil.copy( class_file_name, resources_dir ) # MATLAB script.
    for file_name in optional_files: # Additional files.
        modules.shutil.copy( file_name, resources_dir )
    modules.shutil.copy( fmu_shared_library_name, binaries_dir ) # FMU DLL.

    # Create ZIP archive.
    if ( True == modules.os.path.isfile( fmi_model_identifier + '.zip' ) ):
        modules.os.remove( fmi_model_identifier + '.zip' )
    modules.shutil.make_archive( fmi_model_identifier, 'zip', fmi_model_identifier )

    # Finally, create the FMU!!!
    fmu_file_name = fmi_model_identifier + '.fmu'
    if ( True == modules.os.path.isfile( fmu_file_name ) ):
        modules.os.remove( fmu_file_name )
    modules.os.rename( fmi_model_identifier + '.zip', fmu_file_name )

    # Clean up.
    if ( False == litter ):
        for fn in [ model_description_name, 'build.log', 'fmiFunctions.obj' ]:
            modules.os.remove( fn ) if modules.os.path.isfile( fn ) else None
        modules.shutil.rmtree( fmi_model_identifier, False )
        for file_name in modules.glob.glob( fmi_model_identifier + '.*' ):
            if not ( ( ".fmu" in file_name ) or ( ".m" in file_name ) ): modules.os.remove( file_name )

    # Return name of created FMU.
    return fmu_file_name


# Create model description.
def createModelDescription(
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
    modules ):

    # Retrieve templates for different parts of XML model description according to FMI version.
    ( model_description_header, scalar_variable_node, model_description_footer ) = getModelDescriptionTemplates( fmi_version, verbose, modules )

    # Creation date and time.
    model_description_header = model_description_header.replace( '__DATE_AND_TIME__', modules.time.strftime( "%Y-%m-%dT%H:%M:%S" ) )

    # Author name.
    model_description_header = model_description_header.replace( '__USER__', modules.getpass.getuser() )

    # GUID.
    model_description_header = model_description_header.replace( '__GUID__', str( modules.uuid.uuid1() ) )

    # FMI model identifier.
    model_description_header = model_description_header.replace( '__MODEL_IDENTIFIER__', fmi_model_identifier )
    model_description_footer = model_description_footer.replace( '__MODEL_IDENTIFIER__', fmi_model_identifier )

    # Model name.
    fmi_model_name = modules.os.path.basename( class_file_name ).split( '.' )[0]
    model_description_header = model_description_header.replace( '__MODEL_NAME__', fmi_model_name )
    model_description_footer = model_description_footer.replace( '__MODEL_NAME__', fmi_model_name )

    # MATLAB startup flags.
    startup_flags = '-nosplash -nojvm' if ( use_jvm == False ) else '-nosplash'
    model_description_header = model_description_header.replace( '__STARTUP_FLAGS__', startup_flags )
    model_description_footer = model_description_footer.replace( '__STARTUP_FLAGS__', startup_flags )

    # Enforce fixed simulation step size.
    variable_com_flag = 'false' if ( fixed_step == True ) else 'true'
    model_description_header = model_description_header.replace( '__VARIABLE_COM_STEP__', variable_com_flag )
    model_description_footer = model_description_footer.replace( '__VARIABLE_COM_STEP__', variable_com_flag )

    # URI of MATLAB main executable (matlab.exe).
    matlab_exe_uri = modules.urlparse.urljoin( 'file:', modules.urllib.pathname2url( matlab_install_dir ) ) + '/bin/win64/matlab.exe'
    model_description_header = model_description_header.replace( '__MATLAB_EXE_URI__', matlab_exe_uri )
    model_description_footer = model_description_footer.replace( '__MATLAB_EXE_URI__', matlab_exe_uri )

    # Input script file.
    model_description_header = model_description_header.replace( '__CLASS_FILE_NAME__', modules.os.path.basename( class_file_name ) )
    model_description_footer = model_description_footer.replace( '__CLASS_FILE_NAME__', modules.os.path.basename( class_file_name ) )

    # Define a string to collect all scalar variable definitions.
    model_description_scalars = ''

    # Add scalar input variables description. Value references for inputs start with 1.
    input_val_ref = 1
    for var in fmi_input_vars:
        var_type = var[0]
        var_name = var[1]
        scalar_variable_description = scalar_variable_node
        scalar_variable_description = scalar_variable_description.replace( '__VAR_NAME__', var_name )
        scalar_variable_description = scalar_variable_description.replace( '__VAR_TYPE__', var_type )
        scalar_variable_description = scalar_variable_description.replace( '__CAUSALITY__', 'input' )
        scalar_variable_description = scalar_variable_description.replace( '__VAL_REF__', str( input_val_ref ) )
        scalar_variable_description = scalar_variable_description.replace( '__INITIAL__', '' )
        if var_name in start_values:
            start_value_description = ' start=\"' + start_values[var_name] + '\"'
            scalar_variable_description = scalar_variable_description.replace( '__START_VALUE__', start_value_description )
            if ( True == verbose ): modules.log( '[DEBUG] Added start value to model description: ', var_name, '=', start_values[var_name] )
        else:
            scalar_variable_description = scalar_variable_description.replace( '__START_VALUE__', '' )
        input_val_ref += 1
        # Write scalar variable description to file.
        model_description_scalars += scalar_variable_description;

    # Add scalar input variables description. Value references for outputs start with 1001 (except there are already input value references with corresponding values).
    output_val_ref = 1001 if ( input_val_ref < 1001 ) else input_val_ref
    for var in fmi_output_vars:
        var_type = var[0]
        var_name = var[1]
        scalar_variable_description = scalar_variable_node
        scalar_variable_description = scalar_variable_description.replace( '__VAR_NAME__', var_name )
        scalar_variable_description = scalar_variable_description.replace( '__VAR_TYPE__', var_type )
        scalar_variable_description = scalar_variable_description.replace( '__CAUSALITY__', 'output' )
        scalar_variable_description = scalar_variable_description.replace( '__VAL_REF__', str( output_val_ref ) )
        if var_name in start_values:
            start_value_description = ' start=\"' + start_values[var_name] + '\"'
            scalar_variable_description = scalar_variable_description.replace( '__START_VALUE__', start_value_description )
            scalar_variable_description = scalar_variable_description.replace( '__INITIAL__', 'initial="exact"' )
            if ( True == verbose ): modules.log( '[DEBUG] Added start value to model description: ', var_name, '=', start_values[var_name] )
        else:
            scalar_variable_description = scalar_variable_description.replace( '__START_VALUE__', '' )
            scalar_variable_description = scalar_variable_description.replace( '__INITIAL__', '' )
        output_val_ref += 1
        # Write scalar variable description to file.
        model_description_scalars += scalar_variable_description;

    # Optional files.
    ( model_description_header, model_description_footer ) = \
        addOptionalFilesToModelDescription( model_description_header, model_description_footer, optional_files, fmi_version, verbose, modules)

    # Create new XML model description file.
    model_description_name = 'modelDescription.xml'
    model_description = open( model_description_name, 'w' )
    model_description.write( model_description_header );
    model_description.write( model_description_scalars );
    model_description.write( model_description_footer );
    model_description.close()

    return model_description_name


# Get templates for the XML model description depending on the FMI version.
def getModelDescriptionTemplates( fmi_version, verbose, modules ):
    if ( '1' == fmi_version ): # FMI 1.0
       return fmi1GetModelDescriptionTemplates( verbose, modules )
    elif ( '2' == fmi_version ): # FMI 2.0
        return fmi2GetModelDescriptionTemplates( verbose, modules )


# Add optional files to XML model description.
def addOptionalFilesToModelDescription( header, footer, optional_files, fmi_version, verbose, modules ):
    if ( '1' == fmi_version ):
        return fmi1AddOptionalFilesToModelDescription( optional_files, header, footer, verbose, modules )
    if ( '2' == fmi_version ):
        return fmi2AddOptionalFilesToModelDescription( optional_files, header, footer, verbose, modules )


# Create DLL for FMU.
def createSharedLibrary( fmi_model_identifier, matlab_fmu_root_dir, fmi_version, verbose, modules ):
    if ( '1' == fmi_version ):
        return fmi1CreateSharedLibrary( fmi_model_identifier, matlab_fmu_root_dir, verbose, modules )
    if ( '2' == fmi_version ):
        return fmi2CreateSharedLibrary( fmi_model_identifier, matlab_fmu_root_dir, verbose, modules )
