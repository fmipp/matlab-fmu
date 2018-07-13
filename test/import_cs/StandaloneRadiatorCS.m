% Load FMI++ interface.
fmippPath = getenv( 'MATLAB_FMIPP_ROOT' );
addpath( genpath( fullfile( fmippPath, 'packages' ) ) );

% Specify the FMU's model name.
model_name = 'StandaloneRadiatorCS';

% Specify the path to the extracted (unzipped) FMU.
uri_to_extracted_fmu = 'file:///C:/Development/matlab-fmipp/test/import_cs/StandaloneRadiatorCS';

% Specify the FMU's configuration parameters.
logging_on = fmippim.fmiTrue(); % Turn verbosity on/off.
time_diff_resolution = 1e-9;    % resolution for comparing the (external) master time with the (intrenal) slave time.

% Load the FMU.
fmu = fmippim.FMUCoSimulationV2( uri_to_extracted_fmu, model_name, logging_on, time_diff_resolution )

% Instantiate the FMU.
time_out = 0;
visible = fmippim.fmiFalse();
interactive = fmippim.fmiFalse();

status = fmu.instantiate( 'standalone_radiator1', time_out, visible, interactive );
if status ~= fmippim.fmiOK(); error( 'instantiation not successful' ); end

% Set value of parameter Tlow.
Tlow = 82.0;
status = fmu.setRealValue( 'Tlow', Tlow );
if status ~= fmippim.fmiOK(); error( 'setRealValue not successful' ); end

% Set value of parameter Thigh.
Thigh = 90.0;
status = fmu.setRealValue( 'Thigh', Thigh );
if status ~= fmippim.fmiOK(); error( 'setRealValue not successful' ); end

% Initialize the FMU.
start_time = 0;
stop_time_defined = fmippim.fmiTrue();
stop_time = 4 * 60 * 60;

status = fmu.initialize( start_time, stop_time_defined, stop_time );
if status ~= fmippim.fmiOK(); error( 'initialzation not successful' ); end

% Specify default step size of one synchronization step.
step_size = 300;
t = start_time;

result = [];

% Simulation loop.
while t < stop_time
    % Let the FMU make a simulation step.
	new_step = fmippim.fmiTrue;
    status = fmu.doStep( t, step_size, new_step )
	if status ~= fmippim.fmiOK(); error( 'simulation step not successful' ); end

    T = fmu.getRealValue( 'T' );  % retrieve value for output variable 'T'
    
    if ( T > Thigh )
        fmu.setRealValue( 'Pheat', 0.0 );  % turn off heating
    elseif ( T < Tlow )
        fmu.setRealValue( 'Pheat', 1e3 );  % turn on heating
    end

	result = vertcat( result, [ t/3600 T ] );
	
	t = t + step_size;
end

% Plot the results.
scatter( result(:,1), result(:,2) );