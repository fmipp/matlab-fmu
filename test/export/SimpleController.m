% Load FMI++ interface.
fmippPath = getenv( 'MATLAB_FMIPP_ROOT' );
addpath( genpath( fullfile( fmippPath, 'packages' ) ) );

% Create a new FMI backend.
backend = fmippex.FMIComponentBackEnd();

% Initialize the backend.
backend.startInitialization();

% Define inputs (of type real).
inputVariableNames = { 'T' };
[realInputs, realInputSize] = fmipputils.defineRealInputs( backend, inputVariableNames );

% Define outputs (of type real).
outputVariableNames = { 'Pheat' };
[realOutputs, realOutputSize] = fmipputils.defineRealOutputs( backend, outputVariableNames );

% End initialization.
backend.endInitialization();

% Define controller parameters.
Thigh = 90;
Tlow = 80;
Pheat = 0;

% Pseudo simulation loop.
while true
    % Wait for simulation master to hand over control.
    backend.waitForMaster();

    % Get current model time.
    syncTime = backend.getCurrentCommunicationPoint() + backend.getCommunicationStepSize();

    % Read current input values.
    inputValues = fmipputils.getRealInputValues( backend, realInputs, realInputSize );

    % Calculate output values.
    T = inputValues(1);

    if ( T >= Thigh )
        Pheat = 0.;   % turn off heating
    elseif ( T <= Tlow )
        Pheat = 1e3;  % turn on heating
    end

    % Write current output values.
    fmipputils.setRealOutputValues( backend, realOutputs, realOutputSize, Pheat );

    % Give back control to simulation master.
    backend.signalToMaster();
end
