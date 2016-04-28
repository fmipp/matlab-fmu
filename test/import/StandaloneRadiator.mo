within ;
model StandaloneRadiator 
  
  output Real T(start = Tstart); // radiator temperature [degC]
  output Real derT; // derivative of temperature
  Real Q(start = M*C*Tstart); // energy stored in radiator [J]
  
  input Real Pheat(start = 0); // heating power [W]
  Real Pdemand;  // heating demand [W]
  
  output Boolean ToperateOK(start = false); // indicator to show if operating temperature is within the limits
  
  input Real Tlow(start = 80); // minimum operating temperature [degC]
  input Real Thigh(start = 90); // maximum operating temperature [degC]
  parameter Real Tstart = 85; // radiator temperature at simulation start [degC]
  
  parameter Real C = 4185.5; // thermal capacity of radiator (water at 15degC, 101.325 kPa) [J/(kg⋅degC)]
  parameter Real M = 50; // mass of stored water [kg]
  
algorithm 
  Pdemand := 5e2 + 2e2 * Modelica.Math.sin(1e-3*time); // heating demand changes over time
  
equation 
  if (T < Tlow) or (T > Thigh) then
    ToperateOK = true; 
  else
    ToperateOK = false;
  end if;
  
  Q = M * C * T; // thermal energy in storage
  der(Q) = Pheat - Pdemand; // heat flow balance
  
  derT = der(T);
  
  annotation (uses(Modelica(version="2.2.2")));
end StandaloneRadiator;
