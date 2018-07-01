@ECHO OFF

SET BUILD_DIR=%~dp0\build_vc140_x64
SET MATLAB_FMIPP_DIR=C:\Production\matlab-fmipp
SET FMIPP_DIR=C:\Production\fmipp
SET CMAKE_BIN_DIR="C:\Program Files\CMake\bin"
SET CMAKE_TARGET="Visual Studio 14 2015 Win64"
SET BOOST_INCLUDE_DIR=C:\Tools\boost_1_68_0
SET BOOST_LIBRARY_DIR=C:\Tools\boost_1_68_0\lib64-msvc-14.0
SET BOOST_VERSION=vc140-mt-x64-1_68
SET SUNDIALS_INCLUDE_DIR=C:\Tools\sundials-2.5.0\include
SET SUNDIALS_LIBRARY_DIR=C:\Tools\sundials-2.5.0\lib64-msvc-14.0
SET SWIG_DIR=C:\Tools\swig-3.0.9-mingw32-incl_matlab


REM ##################################################################################################
REM Build FMI++ and MATLAB wrapper.
REM ##################################################################################################

SET PWD=%CD%

ECHO Create build directory ...

RMDIR %BUILD_DIR% /S /Q 2> NUL
MKDIR %BUILD_DIR%
CD %BUILD_DIR%

ECHO Run CMake ...

%CMAKE_BIN_DIR%\cmake.exe %FMIPP_DIR% -G %CMAKE_TARGET% -DCMAKE_CONFIGURATION_TYPES="Release" -DBUILD_SWIG_MATLAB=ON -DBUILD_SWIG_JAVA=OFF -DBUILD_SWIG_PYTHON=OFF -DSWIG_EXECUTABLE=%SWIG_DIR%\swig.exe -DINCLUDE_SUNDIALS=ON -DSUNDIALS_INCLUDEDIR=%SUNDIALS_INCLUDE_DIR% -DSUNDIALS_LIBRARYDIR=%SUNDIALS_LIBRARY_DIR% -DBOOST_INCLUDEDIR=%BOOST_INCLUDE_DIR% 1> %BUILD_DIR%\cmake.out 2>&1

ECHO Build FMI++ ...

CALL "%VS140COMNTOOLS%vsvars32.bat" 
msbuild /p:Configuration=Release /verbosity:minimal /nologo fmipp.sln 1> %BUILD_DIR%\msbuild_vs140.out 2>&1

REM ECHO Run tests ...
REM %CMAKE_BIN_DIR%\ctest.exe --no-compress-output -C "Release" -T Test || verify > NUL


REM ##################################################################################################
REM Copy binaries
REM ##################################################################################################

COPY "%BUILD_DIR%\export\swig\Release\fmippexMEX.mexw64" "%MATLAB_FMIPP_DIR%\packages\lib"
COPY "%BUILD_DIR%\import\swig\Release\fmippimMEX.mexw64" "%MATLAB_FMIPP_DIR%\packages\lib"
COPY "%BUILD_DIR%\Release\fmippim.dll" "%MATLAB_FMIPP_DIR%\packages\lib"
COPY "%BUILD_DIR%\Release\fmippex.dll" "%MATLAB_FMIPP_DIR%\packages\lib"
XCOPY /E /Y "%BUILD_DIR%\import\swig\+fmippim" "%MATLAB_FMIPP_DIR%\packages\+fmippim"
XCOPY /E /Y "%BUILD_DIR%\export\swig\+fmippex" "%MATLAB_FMIPP_DIR%\packages\+fmippex"
COPY "%BUILD_DIR%\import\swig\SwigMem.m" "%MATLAB_FMIPP_DIR%\packages\SwigMem.m"
COPY "%BUILD_DIR%\import\swig\SwigRef.m" "%MATLAB_FMIPP_DIR%\packages\SwigRef.m"
COPY "%BUILD_DIR%\Release\libfmipp_fmu_frontend.lib" "%MATLAB_FMIPP_DIR%\binaries\libfmipp_fmu_frontend.lib"


REM ##################################################################################################
REM Copy external libraries.
REM ##################################################################################################

ECHO Copy external libraries ...

COPY %BOOST_LIBRARY_DIR%\libboost_date_time-vc140-mt-x64-1_68.lib %MATLAB_FMIPP_DIR%\binaries
COPY %BOOST_LIBRARY_DIR%\libboost_filesystem-vc140-mt-x64-1_68.lib %MATLAB_FMIPP_DIR%\binaries
COPY %BOOST_LIBRARY_DIR%\libboost_system-vc140-mt-x64-1_68.lib %MATLAB_FMIPP_DIR%\binaries
COPY %SUNDIALS_LIBRARY_DIR%\sundials_cvode.dll %MATLAB_FMIPP_DIR%\packages\lib\
COPY %SUNDIALS_LIBRARY_DIR%\sundials_nvecserial.dll %MATLAB_FMIPP_DIR%\packages\lib\
COPY %BOOST_LIBRARY_DIR%\boost_filesystem-vc140-mt-x64-1_68.dll %MATLAB_FMIPP_DIR%\packages\lib\
COPY %BOOST_LIBRARY_DIR%\boost_system-vc140-mt-x64-1_68.dll %MATLAB_FMIPP_DIR%\packages\lib\
COPY C:\Windows\System32\msvcp140.dll %MATLAB_FMIPP_DIR%\packages\lib\
COPY C:\Windows\System32\vcruntime140.dll %MATLAB_FMIPP_DIR%\packages\lib\

ECHO Done.

CD %PWD%