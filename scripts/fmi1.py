# -----------------------------------------------------------------
# Copyright (c) 2017-2019, AIT Austrian Institute of Technology GmbH.
# All rights reserved. See file MATLAB_FMU_LICENSE.txt for details.
# -----------------------------------------------------------------

#
# Collection of helper functions for creating FMU CS according to FMI 1.0
#


# Get templates for the XML model description depending on the FMI version.
def fmi1GetModelDescriptionTemplates( verbose, modules ):
    # Template string for XML model description header.
    header = '<?xml version="1.0" encoding="UTF-8"?>\n<fmiModelDescription fmiVersion="1.0" modelName="__MODEL_NAME__" modelIdentifier="__MODEL_IDENTIFIER__" description="MATLAB/MEX FMI CS export" generationTool="FMI++ MATLAB/MEX Export Utility" generationDateAndTime="__DATE_AND_TIME__" variableNamingConvention="flat" numberOfContinuousStates="0" numberOfEventIndicators="0" author="__USER__" guid="{__GUID__}">\n\t<VendorAnnotations>\n\t\t<Tool name="matlab">\n\t\t\t<Executable arguments="__STARTUP_FLAGS__ -logfile __MODEL_IDENTIFIER__.log -r &quot;try; fmippPath=getenv(\'MATLAB_FMIPP_ROOT\'); addpath(genpath(fullfile(fmippPath,\'packages\'))); obj = __MODEL_NAME__(); obj.initBackEnd(); obj.run(); catch err; disp(err); end; quit;&quot;" executableURI="__MATLAB_EXE_URI__"/>\n\t\t</Tool>\n\t</VendorAnnotations>\n\t<ModelVariables>\n'

    # Template string for XML model description of scalar variables.
    scalar_variable_node = '\t\t<ScalarVariable name="__VAR_NAME__" valueReference="__VAL_REF__" variability="continuous" causality="__CAUSALITY__">\n\t\t\t<__VAR_TYPE____START_VALUE__/>\n\t\t</ScalarVariable>\n'

    # Template string for XML model description footer.
    footer = '\t</ModelVariables>\n\t<Implementation>\n\t\t<CoSimulation_Tool>\n\t\t\t<Capabilities canHandleVariableCommunicationStepSize="__VARIABLE_COM_STEP__" canHandleEvents="__VARIABLE_COM_STEP__" canRejectSteps="false" canInterpolateInputs="false" maxOutputDerivativeOrder="0" canRunAsynchronuously="false" canSignalEvents="false" canBeInstantiatedOnlyOncePerProcess="false" canNotUseMemoryManagementFunctions="true"/>\n\t\t\t<Model entryPoint="fmu://resources/__CLASS_FILE_NAME__" manualStart="false" type="application/x-matlab">__ADDITIONAL_FILES__\n\t\t\t</Model>\n\t\t</CoSimulation_Tool>\n\t</Implementation>\n</fmiModelDescription>'

    return ( header, scalar_variable_node, footer )


# Add optional files to XML model description.
def fmi1AddOptionalFilesToModelDescription( optional_files, header, footer, verbose, modules ):
    if ( 0 == len( optional_files ) ):
        footer = footer.replace( '__ADDITIONAL_FILES__', '' )
    else:
        additional_files_description = ''
        indent = '\n\t\t\t'

        for file_name in optional_files:
            additional_files_description += indent + '\t<File file=\"fmu://resources/' + modules.os.path.basename( file_name ) + '\"/>'
            if ( True == verbose ): modules.log( '[DEBUG] Added additional file to model description: ', modules.os.path.basename( file_name ) )

        footer = footer.replace( '__ADDITIONAL_FILES__', additional_files_description )

    return ( header, footer )


# Create DLL for FMU.
def fmi1CreateSharedLibrary( fmi_model_identifier, matlab_fmu_root_dir, verbose, modules ):
    # Define name of shared library.
    fmu_shared_library_name = fmi_model_identifier + '.dll'

    # Check if batch file for build process exists.
    build_process_batch_file = modules.os.path.join( matlab_fmu_root_dir, 'scripts', 'fmi1_build.bat' )
    if ( False == modules.os.path.isfile( build_process_batch_file ) ):
        modules.log( '\n[ERROR] Could not find file: ', build_process_batch_file )
        raise Exception( 8 )
    # Remove possible leftovers from previous builds.
    for file_name in modules.glob.glob( fmi_model_identifier + '.*' ):
        if not ( ( ".dck" in file_name ) or ( ".tpf" in file_name ) ): modules.os.remove( file_name ) # Do not accidentaly remove the deck file!
    if ( True == modules.os.path.isfile( 'fmiFunctions.obj' ) ): modules.os.remove( 'fmiFunctions.obj' )
    # Compile FMU shared library.
    build_process = modules.subprocess.Popen( [build_process_batch_file, fmi_model_identifier] )
    stdout, stderr = build_process.communicate()

    if ( False == modules.os.path.isfile( fmu_shared_library_name ) ):
        modules.log( '\n[ERROR] Not able to create shared library: ', fmu_shared_library_name )
        raise Exception( 17 )

    return fmu_shared_library_name
