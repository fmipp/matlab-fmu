% Init MATLAB FMI++ Export package. 
fmippPath = getenv( 'MATLAB_FMIPP_ROOT' );
addpath( genpath( fullfile( fmippPath, 'packages' ) ) );

% Create FMU.
model_identifier = 'TestController';
class_definition_file = 'SimpleController.m';
fmi_version = '2';
additional_files = '';
fmipputils.createFMU( model_identifier, class_definition_file, fmi_version, additional_files, false );