# -----------------------------------------------------------------
# Copyright (c) 2017-2019, AIT Austrian Institute of Technology GmbH.
# All rights reserved. See file MATLAB_FMU_LICENSE.txt for details.
# -----------------------------------------------------------------

#
# Collection of helper functions for creating FMU CS according to FMI 2.0
#


# Get templates for the XML model description depending on the FMI version.
def fmi2GetModelDescriptionTemplates( verbose, modules ):
    # Template string for XML model description header.
    header = '<?xml version="1.0" encoding="UTF-8"?>\n<fmiModelDescription\n\txmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n\tfmiVersion="2.0"\n\tmodelName="__MODEL_NAME__"\n\tguid="{__GUID__}"\n\tgenerationTool="FMI++ MATLAB/MEX Export Utility"\n\tauthor="__USER__"\n\tgenerationDateAndTime="__DATE_AND_TIME__"\n\tvariableNamingConvention="flat"\n\tnumberOfEventIndicators="0">\n\t<CoSimulation\n\t\tmodelIdentifier="__MODEL_IDENTIFIER__"\n\t\tneedsExecutionTool="true"\n\t\tcanHandleVariableCommunicationStepSize="__VARIABLE_COM_STEP__"\n\t\tcanNotUseMemoryManagementFunctions="true"\n\t\tcanInterpolateInputs="false"\n\t\tmaxOutputDerivativeOrder="0"\n\t\tcanGetAndSetFMUstate="false"\n\t\tprovidesDirectionalDerivative="false"/>\n\t<VendorAnnotations>\n\t\t<Tool name="FMI++Export">\n\t\t\t<Executable\n\t\t\t\targuments="__STARTUP_FLAGS__ -logfile __MODEL_IDENTIFIER__.log -r &quot;try; fmippPath=getenv(\'MATLAB_FMIPP_ROOT\'); addpath(genpath(fullfile(fmippPath,\'packages\'))); obj = __MODEL_NAME__(); obj.initBackEnd(); obj.run(); catch err; disp(err); end; quit;&quot;"\n\t\t\t\texecutableURI="__MATLAB_EXE_URI__"\n\t\t\t\tentryPointURI="fmu://resources/__CLASS_FILE_NAME__"/>__ADDITIONAL_FILES__\n\t\t</Tool>\n\t</VendorAnnotations>\n\t<ModelVariables>\n'

    # Template string for XML model description of scalar variables.
    scalar_variable_node = '\t\t<ScalarVariable name="__VAR_NAME__" valueReference="__VAL_REF__" variability="continuous" causality="__CAUSALITY__" __INITIAL__>\n\t\t\t<__VAR_TYPE____START_VALUE__/>\n\t\t</ScalarVariable>\n'

    # Template string for XML model description footer.
    footer = '\t</ModelVariables>\n\t<ModelStructure/>\n</fmiModelDescription>'

    return ( header, scalar_variable_node, footer )


# Add optional files to XML model description.
def fmi2AddOptionalFilesToModelDescription( optional_files, header, footer, verbose, modules ):
    if ( 0 == len( optional_files ) ):
        header = header.replace( '__ADDITIONAL_FILES__', '' )
    else:
        additional_files_description = ''
        indent = '\n\t\t'

        for file_name in optional_files:
            additional_files_description += indent + '\t<File file=\"fmu://resources/' + modules.os.path.basename( file_name ) + '\"/>'
            if ( True == verbose ): modules.log( '[DEBUG] Added additional file to model description: ', modules.os.path.basename( file_name ) )

        header = header.replace( '__ADDITIONAL_FILES__', additional_files_description )

    return ( header, footer )


# Create DLL for FMU.
def fmi2CreateSharedLibrary( fmi_model_identifier, matlab_fmu_root_dir, verbose, modules ):
    # Define name of shared library.
    fmu_shared_library_name = fmi_model_identifier + '.dll'

    fmi2_dll_path = modules.os.path.join( matlab_fmu_root_dir, 'binaries', 'fmi2.dll' )
    if ( False == modules.os.path.isfile( fmi2_dll_path ) ):
        modules.log( '\n[ERROR] DLL not found: ', fmi2_dll_path )
        raise Exception( 16 )
    modules.shutil.copy( fmi2_dll_path, fmu_shared_library_name )

    if ( False == modules.os.path.isfile( fmu_shared_library_name ) ):
        modules.log( '\n[ERROR] Not able to create shared library: ', fmu_shared_library_name )
        raise Exception( 17 )

    return fmu_shared_library_name
