classdef SimpleController < fmipputils.FMIAdapter

	properties
	
		Thigh_ = 90;
		Tlow_ = 80;
		Pheat_ = 0;

	end % properties


	methods
	
		% Full constructor.
        function obj = SimpleController()
            obj@fmipputils.FMIAdapter();
        end
		
		function init( obj, currentCommunicationPoint )
		
			% Define inputs (of type real).
			inputVariableNames = { 'T' };
			defineRealInputs( obj, inputVariableNames );

			% Define outputs (of type real).
			outputVariableNames = { 'Pheat' };
			defineRealOutputs( obj, outputVariableNames );

			disp( 'FMI++ backend for co-simulation: INIT DONE.' );

		end % function init


		function doStep( obj, currentCommunicationPoint, communicationStepSize )
			
			syncTime = currentCommunicationPoint + communicationStepSize;

			% Read current input values.
			realInputValues = getRealInputValues( obj );
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
			setRealOutputValues( obj, obj.Pheat_ );

		end % function doStep

	end % methods

end % classdef