%% Exporting MATLAB code as FMU for Co-Simulation
% This class shows a simple example of how to export MATLAB as an FMU for
% Co-Simulation (FMI version 1.0).
%
% This requires to inherit a new class from base class
% |fmipputils.FMIAdapter| and define the following abstract methods:
%
% * |init( obj, currentCommunicationPoint )|: This method is used to define
% the input/output variables and parameters of the FMU that can be accessed
% by an external master algorithm.
% * |doStep( obj, currentCommunicationPoint, communicationStepSize )|: This
% method is called every time the FMU's |doStep| method is called by the
% external master algorithm.

%% Inherit from class |fmipputils.FMIAdapter|
% Class |FMIAdapter| is defined as part of the |fmipputils| package.
classdef SimpleController < fmipputils.FMIAdapter

%% Define private member variables
% Private member variables will not be automatically accessible by the
% external master algorithm.
	properties
	
		Thigh_ = 90;
		Tlow_ = 80;
		Pheat_ = 0;

	end % properties

%% Implement abstract methods
	methods
	
		function init( obj, currentCommunicationPoint )
		
			% Define inputs (of type real).
			inputVariableNames = { 'T' };
			obj.defineRealInputs( inputVariableNames );

			% Define outputs (of type real).
			outputVariableNames = { 'Pheat' };
			obj.defineRealOutputs( outputVariableNames );
			
			obj.enforceTimeStep( 300 );

			disp( 'FMI++ backend for co-simulation: INIT DONE.' );

		end % function init


		function doStep( obj, currentCommunicationPoint, communicationStepSize )
			
			syncTime = currentCommunicationPoint + communicationStepSize;

			% Read current input values.
			realInputValues = obj.getRealInputValues();
			T = realInputValues(1);
			
			% Calculate output values.
			if ( T >= obj.Thigh_ )
				obj.Pheat_ = 0.;   % turn off heating
				disp( [ 'turn heating OFF at t = ', num2str( syncTime ) ] );
			elseif ( T <= obj.Tlow_ )
				obj.Pheat_ = 1e3;  % turn on heating
				disp( [ 'turn heating ON at t = ', num2str( syncTime ) ] );
			end

			% Write current output values.
			obj.setRealOutputValues( obj.Pheat_ );

		end % function doStep

	end % methods

end % classdef