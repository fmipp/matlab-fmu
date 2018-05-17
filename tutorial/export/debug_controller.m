%% Debugging MATLAB code before FMU export
% Implemented MATLAB code can be tested and debugged before exporting it as
% an FMU for Co-Simulation. This can be done using the dedicated methods
% |debugSetRealInputValues|, |debugGetRealOutputValues|, etc. of class
% |fmipputils.FMIAdapter| to set/get the inputs/outputs/parameters.

%%
% When in debug mode, the interface used by external master algorithms is
% not activated. This will cause warnings like _"Warning: FMI++ export
% interface is not active."_. The following command mutes these warnings.
warning( 'off', 'all' );

%%
% Import the class implementing the controller.
import SimpleController

%%
% Instantiate the controller.
test = SimpleController();

%%
% This will initialize an input variable called _Pheat_ and an output
% variable called _T_.
test.init( 0. );

%%
% Set the input variable _Pheat_ to 95.
test.debugSetRealInputValues( [ 95 ] );

%%
% Iterate the controller once. Given the previous input, the controller
% should set _Pheat_ to 0.
test.doStep( 0., 0. );

%%
% Retrieve the output and check that the value is correct.
output = test.debugGetRealOutputValues();
assert( 0 == output(1) );

%%
% Set the input variable _Pheat_ to 75.
test.debugSetRealInputValues( [ 75 ] );

%%
% Iterate the controller once. Given the previous input, the controller
% should set _Pheat_ to 1000.
test.doStep( 0., 0. );

%%
% Retrieve the output and check that the value is correct.
output = test.debugGetRealOutputValues();
assert( 1e3 == output(1) );
