within ;
model ControlledRadiator
  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor
                                        heatCapacitor(C=500000, T(start=358.15,
        fixed=true))
    annotation (Placement(transformation(extent={{-10,-26},{10,-46}},
          rotation=0)));
  Modelica.Thermal.HeatTransfer.Celsius.TemperatureSensor
                                         temperatureSensor  annotation (Placement(
        transformation(
        origin={0,-4},
        extent={{-10,10},{10,-10}},
        rotation=90)));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow prescribedHeatFlow
    annotation (Placement(transformation(extent={{-38,-30},{-18,-10}})));
  Modelica.Thermal.HeatTransfer.Sources.FixedHeatFlow fixedHeatFlow(Q_flow=-400)
    annotation (Placement(transformation(extent={{38,-30},{18,-10}})));
  Modelica.Blocks.Interfaces.RealInput Pheat
    annotation (Placement(transformation(extent={{-88,-40},{-48,0}})));
  Modelica.Blocks.Interfaces.RealOutput T
    annotation (Placement(transformation(extent={{36,10},{56,30}})));
equation
  connect(prescribedHeatFlow.port, temperatureSensor.port) annotation (Line(
        points={{-18,-20},{0,-20},{0,-14}},             color={191,0,0}));
  connect(fixedHeatFlow.port, temperatureSensor.port)
    annotation (Line(points={{18,-20},{0,-20},{0,-14}},   color={191,0,0}));
  connect(heatCapacitor.port, temperatureSensor.port)
    annotation (Line(points={{0,-26},{0,-14}},            color={191,0,0}));
  connect(prescribedHeatFlow.Q_flow, Pheat)
    annotation (Line(points={{-38,-20},{-68,-20}}, color={0,0,127}));
  connect(temperatureSensor.T, T)
    annotation (Line(points={{0,6},{0,20},{46,20}}, color={0,0,127}));
  annotation (
    uses(Modelica(version="3.2.2")),
    Diagram(coordinateSystem(preserveAspectRatio=false, extent={{-100,-100},{
            100,100}})),
    experiment(StopTime=43200));
end ControlledRadiator;
