% Init MATLAB FMI++ Export package. 
run( 'C:\Development\matlab-fmipp\setup.m' );

% Create FMU.
model_identifier = 'TestController';
class_definition_file = 'SimpleController.m';
additional_files = '';
fmipputils.createFMU( model_identifier, class_definition_file, additional_files, false );