%% Creating an FMU
% Function |createFMU| in the |fmipputils| package generates an FMU from a
% class implementing base class |FMIAdapter|.

% Init MATLAB FMI++ Export package. 
run( 'C:\Development\matlab-fmipp\setup.m' );

% Define FMI model identifier.
model_identifier = 'TestController';

% Specify the MATLAB file with the class definition.
class_definition_file = 'SimpleController.m';

% Specify additional files (none in this case).
additional_files = '';

% Generate the FMU.
fmipputils.createFMU( model_identifier, class_definition_file, additional_files, false );
