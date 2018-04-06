classdef SimpleController < fmipputils.FMIAdapter

	properties
	
		Thigh_ = 90;
		Tlow_ = 80;
		Pheat_ = 0;

	end % properties


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