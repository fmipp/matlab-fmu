To run the example, proceed as follows:

- Use your favorite Modelica implementation (OpenModelica, Dymola, etc.) to translate file _ControlledRadiator.mo_ into an __FMU for Model Exchange__ (either version 1.0 or 2.0).
- Unzip the generated FMU (e.g., into subdirectory _ControlledRadiator_ in this directory).
- In MATLAB script _SimpleController.m_, change the URI in line 19 to point to the directory containing the extracted FMU from the previous step.
- Execute script _SimpleController.m_ in MATLAB.
