%% Creating an FMU
% Function |createFMU| in the |fmipputils| package generates an FMU from a
% class implementing base class |FMIAdapter|.

% Init MATLAB FMI++ Export package. 
fmippPath = getenv( 'MATLAB_FMIPP_ROOT' );
addpath( genpath( fullfile( fmippPath, 'packages' ) ) );

% Define FMI model identifier.
model_identifier = 'TestController';

% Specify the MATLAB file with the class definition.
class_definition_file = 'SimpleController.m';

% Specify the FMI version.
fmi_version = '2';

% Specify additional files (none in this case).
additional_files = '';

% Generate the FMU.
fmipputils.createFMU( model_identifier, class_definition_file, fmi_version, additional_files, false );