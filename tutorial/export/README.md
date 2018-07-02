To run the example, proceed as follows:

- In MATLAB script _create_fmu.m_, change the path in line 6 to match your installation of the FMI++ MATLAB Toolbox (i.e., the path should point to script _setup.m_).
- Execute script _create_fmu.m_ in MATLAB. This shoudl create an __FMU for Co-Simulation__ called _SimpleController.fmu_.
- Use your Dymola 2018 64-bit to load _SimpleController.fmu_ and _ControlledRadiator.mo_. Using other versions of Dymola requires slight modifications of _ControlledRadiator.mo_.
- Run _ControlledRadiator.mo_ in Dymola.
