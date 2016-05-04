function setup()
   fmippPath = getenv( 'MATLAB_FMIPP_ROOT' );
   if strcmp( fmippPath, '' ) == true
      error( 'System variable MATLAB_FMIPP_ROOT has not been set!' )
   end

   addpath( genpath( fullfile( fmippPath, 'packages' ) ) );

   fmipputils.deactivateInterface();
   
   global fmippexRealInputNames;
   fmippexRealInputNames = {};

   global fmippexIntegerInputNames;
   fmippexIntegerInputNames = {};

   global fmippexBooleanInputNames;
   fmippexBooleanInputNames = {};

   global fmippexStringInputNames;
   fmippexStringInputNames = {};

   global fmippexRealOutputNames;
   fmippexRealOutputNames = {};

   global fmippexIntegerOutputNames;
   fmippexIntegerOutputNames = {};

   global fmippexBooleanOutputNames;
   fmippexBooleanOutputNames = {};

   global fmippexStringOutputNames;
   fmippexStringOutputNames = {};
end