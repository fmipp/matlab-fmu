% Load FMI++ interface.
fmippPath = getenv( 'MATLAB_FMIPP_ROOT' );
addpath( genpath( fullfile( fmippPath, 'packages' ) ) );

% Specify the FMU's model name.
model_name = 'StandaloneRadiatorME';

% Specify the path to the extracted (unzipped) FMU.
uri_to_extracted_fmu = 'file:///C:/Development/matlab-fmipp/test/import_me/StandaloneRadiatorME';

% Specify the FMU's configuration parameters.
logging_on = fmippim.fmi2True();        % Turn verbosity on/off.
stop_before_event = true;               % Stop integration directly before an event occurs.
event_search_precision = 1e-2;          % Set precision for searching for events.
integrator_type = fmippim.bdf();        % Specify Sundials CVODE solver (Backward Differentiation Formula).
%integrator_type = fmippim.rk();        % Alternatively, specify Runge-Kutta integrator.

% Load the FMU (FMI 2.0).
fmu = fmippim.FMUModelExchangeV2( uri_to_extracted_fmu, model_name, logging_on, stop_before_event, event_search_precision, integrator_type )


% Instantiate the FMU.
status = fmu.instantiate( 'standalone_radiator1' )
if status ~= fmippim.fmiOK(); error( 'instantiation not successful' ); end

% Set value of parameter Tlow.
Tlow = 82.0;
status = fmu.setRealValue( 'Tlow', Tlow )
if status ~= fmippim.fmiOK(); error( 'setRealValue not successful' ); end

% Set value of parameter Thigh.
Thigh = 90.0
status = fmu.setRealValue( 'Thigh', Thigh )
if status ~= fmippim.fmiOK(); error( 'setRealValue not successful' ); end

% Initialize the FMU.
status = fmu.initialize()
if status ~= fmippim.fmiOK(); error( 'initialzation not successful' ); end

% Specify default step size of one integration step and the internal intergrator step size.
stepsize = 300;
integrator_stepsize = stepsize/10;

t = 0;
tstop = 4 * 60 * 60;

result = [];

% Simulation loop.
while t < tstop
    % Integrate the FMU: try to make a full step, but stop in case an event is detected.
    t = fmu.integrate( t + stepsize, integrator_stepsize ); % integrate model

    T = fmu.getRealValue( 'T' );        % retrieve value for output variable 'T'
    derT = fmu.getRealValue( 'derT' );  % retrieve value for output variable 'derT'

    if ( ( abs( T - Thigh ) < 1e-2 ) && ( derT > 0 ) )
        fmu.setRealValue( 'Pheat', 0.0 );  % turn off heating
    elseif ( ( abs( T - Tlow ) < 1e-2 ) && ( derT < 0 ) )
        fmu.setRealValue( 'Pheat', 1e3 );  % turn on heating
    end

	result = vertcat( result, [ t/3600 T ] );
end

% Plot the results.
scatter( result(:,1), result(:,2) );