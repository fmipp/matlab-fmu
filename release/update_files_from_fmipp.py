# ------------------------------------------------------------------------
# Copyright (c) 2015, AIT Austrian Institute of Technology GmbH.
# All rights reserved. See file TRNSYS_FMU_LICENSE.txt for details.
# ------------------------------------------------------------------------

##########################################################################
#
# This script copies the source files from a checked-out FMI++ repository.
#
##########################################################################

import sys, os, shutil


# Import module with lists of files for release.
from release_file_list import *


def checkPathsExist( path_list ):
    # Check if files exist.
    for path in path_list:
        if ( False == os.path.isfile( path ) ) and ( False == os.path.isdir( path ) ):
            print path, 'not found'
            return False
    
    return True


if __name__ == "__main__":

    if len( sys.argv ) != 3:
        print 'Usage:\n\tpython update_files_from_fmipp.py <fmipp_repository_dir> <fmipp_build_dir>\n'
        print 'Attention: Be sure to execute this script from subfolder \'release\'\n'
        sys.exit()
    
    # Path to checked-out FMI++ repository.
    fmipp_repository_dir = sys.argv[1]

    # Path to checked-out FMI++ repository.
    fmipp_build_dir = sys.argv[2]

    # List of files/directories to be copied.
    file_list = []

    for file_name in files_from_fmipp:
        # Construct list of names.
        if ( file_name[0:7] == 'sources' ):
            file_list.append( fmipp_repository_dir + '\\' + file_name[8:] )
        elif ( file_name[0:8] == 'packages' ):
            file_list.append( fmipp_repository_dir + '\\scripts\\' + file_name[9:] )

    for file_name in resources_from_fmipp_swig.keys():
        # Construct list of names.
        file_list.append( fmipp_build_dir + '\\' + resources_from_fmipp_swig[file_name] )

    # Check if files exist.
    if ( False == checkPathsExist( file_list ) ): sys.exit(1)

    # Copy files.
    for file_src, file_dst in zip( file_list, files_from_fmipp + resources_from_fmipp_swig.keys() ):
        if os.path.isfile( file_src ):
            print 'Copy file: ' + file_src + '\n\t--> ..\\' + file_dst
            shutil.copyfile( file_src, '..\\' + file_dst )
        elif os.path.isdir( file_src ):
            print 'Copy directory: ' + file_src + '\n\t--> ..\\' + file_dst
            shutil.rmtree( '..\\' + file_dst, ignore_errors = True )
            shutil.copytree( file_src, '..\\' + file_dst )
    
