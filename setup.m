function setup()
   fmippPath = getenv( 'MATLAB_FMIPP_ROOT' );

   if strcmp( fmippPath, '' ) == true
      error( 'System variable MATLAB_FMIPP_ROOT has not been set!' )
   end

   addpath( genpath( fullfile( fmippPath, 'packages' ) ) );
end