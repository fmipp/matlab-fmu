within ;
model ControlledRadiator

  SimpleController_fmu simpleController_fmu(fmi_loggingOn=true,fmi_CommunicationStepSize=300);

  Real T(start = Tstart); // radiator temperature [degC]
  Real Q(start = M*C*Tstart); // energy stored in radiator [J]
  Real Pheat; // heating power [W]

  parameter Real Tstart = 85; // radiator temperature at simulation start [degC]
  parameter Real Pdemand = 5e2; // heating demand [W]
  parameter Real C = 4185.5; // thermal capacity of radiator (water at 15degC, 101.325 kPa) [J/(kg*‹…degC)]
  parameter Real M = 50; // mass of stored water [kg]

algorithm
  simpleController_fmu.T := T;
  Pheat := simpleController_fmu.Pheat;

equation

  Q = M * C * T; // thermal energy in storage
  der(Q) = Pheat - Pdemand; // heat flow balance

  annotation (uses(Modelica(version="3.2.1")),
    experiment(StopTime=36000),
    __Dymola_experimentSetupOutput);
end ControlledRadiator;
