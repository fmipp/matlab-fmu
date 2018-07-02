# ----------------------------------------------------------------------
# Copyright (c) 2018, AIT Austrian Institute of Technology GmbH.
# All rights reserved. See file MATLAB_FMU_LICENSE.txt for details.
# ----------------------------------------------------------------------

########################################################################
#
# This script provides the list of files included into a release of
# the FMI++ MATLAB Export Utility.
#
########################################################################

# List of source files (including relative path) that are originally from FMI++.
files_from_fmipp = [
   'sources\\common\\FMIPPConfig.h',
   'sources\\common\\FMUType.h',
   'sources\\common\\fmi_v1.0\\fmi_cs.h',
   'sources\\common\\fmi_v1.0\\fmiModelTypes.h',
   'sources\\common\\fmi_v2.0\\fmi_2.h',
   'sources\\common\\fmi_v2.0\\fmi2ModelTypes.h',
   'sources\\export\\functions\\fmi_v1.0\\fmiFunctions.cpp',
   'sources\\export\\functions\\fmi_v1.0\\fmiFunctions.h',
   'sources\\export\\functions\\fmi_v2.0\\fmi2Functions.cpp',
   'sources\\export\\functions\\fmi_v2.0\\fmi2Functions.h',
   'sources\\export\\include\\FMIComponentFrontEnd.h',
   'sources\\export\\include\\FMIComponentFrontEndBase.h',
   'sources\\export\\include\\ScalarVariable.h'
   ]

# Additional list of files (including relative path) from the repository that are part of the release.
additional_files = [
   'setup.m', # setup script
   'matlab_fmu_create.py', # script for creating an FMU
   'license\\BOOST_SOFTWARE_LICENSE.txt',
   'license\\FMIPP_LICENSE.txt',
   'license\\MATLAB_FMU_LICENSE.txt',
   'packages\\+fmipputils\\createFMU.m',
   'packages\\+fmipputils\\FMIAdapter.m',
   'packages\\+fmipputils\\licenseInfo.m',
   'scripts\\fmi1_build.bat', # batch script for FMU compilation (FMI 1.0)
   'scripts\\__init__.py',
   'scripts\\fmi1.py', # Python script for generating FMUs (FMI 1.0)
   'scripts\\fmi2.py', # Python script for generating FMUs (FMI 2.0)
   'scripts\\generate_fmu.py', # Python script for generating FMUs
   'scripts\\utils.py', # Python helper script for generating FMUs
   'tutorial\\tutorial.pdf',
   'tutorial\\export\\ControlledRadiator.mo',
   'tutorial\\export\\create_fmu.m',
   'tutorial\\export\\debug_controller.m',
   'tutorial\\export\\README.md',
   'tutorial\\export\\SimpleController.m',
   'tutorial\\export\\html\\create_fmu.html',
   'tutorial\\export\\html\\debug_controller.html',
   'tutorial\\export\\html\\SimpleController.html',
   'tutorial\\import\\ControlledRadiator.mo',
   'tutorial\\import\\README.md',
   'tutorial\\import\\SimpleController.m',
   'tutorial\\import\\html\\SimpleController.html',
   'tutorial\\import\\html\\SimpleController.png',
   'tutorial\\import\\html\\SimpleController_01.png',
   ]

# List of files (without binaries and docs) that are part of the release.
files_for_release = files_from_fmipp + additional_files

# List of swig resources (including relative path).
resources_from_fmipp_swig = {
   'packages\\SwigMem.m' : 'import\\swig\\SwigMem.m', # helper scripts generated by SWIG
   'packages\\SwigRef.m' : 'import\\swig\\SwigRef.m', # helper scripts generated by SWIG
   'packages\\lib\\fmippex.dll' : 'Release\\fmippex.dll', # complete FMI++ export library
   'packages\\lib\\fmippim.dll' : 'Release\\fmippim.dll', # complete FMI++ import library
   'packages\\lib\\fmippexMEX.mexw64' : 'export\\swig\\Release\\fmippexMEX.mexw64', # MEX wrapper for FMI++ export library
   'packages\\lib\\fmippimMEX.mexw64' : 'import\\swig\\Release\\fmippimMEX.mexw64', # MEX wrapper for FMI++ import library
   'packages\\+fmippex' : 'export\\swig\\+fmippex', # scripts for accessing MEX wrapper
   'packages\\+fmippim' : 'import\\swig\\+fmippim', # scripts for accessing MEX wrapper
   'binaries\\fmi2.dll' : 'Release\\fmi2.dll', # dynamic library containing a complete front end (FMI 2.0)
   'binaries\\libfmipp_fmu_frontend.lib' : 'Release\\libfmipp_fmu_frontend.lib', # static library containing pre-compiled parts of the front end (FMI 1.0)
   }

# List of binaries that are not provided by the repository (see also README in 'binaries' subfolder).
required_external_binaries = [
   'binaries\\libboost_date_time-vc140-mt-x64-1_68.lib', # static BOOST date-time library
   'binaries\\libboost_filesystem-vc140-mt-x64-1_68.lib', # static BOOST Filesystem library
   'binaries\\libboost_system-vc140-mt-x64-1_68.lib', # static BOOST System library
   'packages\\lib\\sundials_cvode.dll', # SUNDIALS library
   'packages\\lib\\sundials_nvecserial.dll', # SUNDIALS library
   'packages\\lib\\boost_filesystem-vc140-mt-x64-1_68.dll', # BOOST library
   'packages\\lib\\boost_system-vc140-mt-x64-1_68.dll', # BOOST library
   'packages\\lib\\msvcp140.dll', # Visual Studio 2015 Redistributable library
   'packages\\lib\\vcruntime140.dll', # Visual Studio 2015 Redistributable library
   ]

# The compiled documentation in PDF format (not part of the repository).
doc_file = 'doc\\matlab-fmu-doc.pdf'

