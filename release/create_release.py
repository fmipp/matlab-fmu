# ----------------------------------------------------------------------
# Copyright (c) 2015, AIT Austrian Institute of Technology GmbH.
# All rights reserved. See file TRNSYS_FMU_LICENSE.txt for details.
# ----------------------------------------------------------------------

########################################################################
#
# This script creates a new release of the FMI++ TRNSYS Export Utility.
#
# Before running this scrip, do the following:
#   - compile the documentation (doc\trnsys-fmu-doc.tex)
#   - compile the FMI++ related binaries (release\CMakeLists.txt)
#   - copy the external BOOST libraries (see binaries\README.txt)
#
# Execute this script from subdirectory "release".
#
########################################################################


import sys, os, zipfile, zlib


# Import module with lists of files for release.
from release_file_list import *


def zipfolder( path, relname, archive ):
    paths = os.listdir( path )
    for p in paths:
        p1 = os.path.join( path, p )
        p2 = os.path.join( relname, p )
        if os.path.isdir( p1 ):
            zipfolder( p1, p2, archive )
        else:
            archive.write( p1, p2 )


def checkFilesExist( doc_file, required_binaries, cwd ):
    # Check if files from repository are available.
    for file in files_for_release:
        full_file_name = cwd + '\\..\\' + file
        if ( False == os.path.isfile( full_file_name ) ) and ( False == os.path.isdir( full_file_name ) ):
            print file, 'not found'
            return False
    
    # Check if additional binaries are available.
    for file in required_binaries:
        full_file_name = cwd + '\\..\\' + file
        if ( False == os.path.isfile( full_file_name ) ):
            print file, 'not found'
            return False

    # Check if the SWIG wrapper files are available.
    for path in resources_from_fmipp_swig.keys():
        full_path = cwd + '\\..\\' + path
        if ( False == os.path.isfile( full_path ) ) and ( False == os.path.isdir( full_path ) ):
            print path, 'not found'
            return False

			# Check if documentation is available.
    if ( False == os.path.isfile( cwd + '\\..\\' + doc_file ) ):
        print doc_file, 'not found'
        return False
    
    return True


def createRelease( release_file, release_name, cwd ):
    base_name = '\\' + release_name + '\\'
    for path in files_for_release:
        if os.path.isdir( cwd + '\\..\\' + path ):
            zipfolder( cwd + '\\..\\' + path, base_name + path, release_file )
        else:
            release_file.write( cwd + '\\..\\' + path, base_name + path )
    
    for file in required_binaries:
        release_file.write( cwd + '\\..\\' + file, base_name + file )
    
    for path in resources_from_fmipp_swig:
        if os.path.isdir( cwd + '\\..\\' + path ):
            zipfolder( cwd + '\\..\\' + path, base_name + path, release_file )
        else:
            release_file.write( cwd + '\\..\\' + path, base_name + path )

    release_file.write( cwd + '\\..\\' + doc_file, base_name + 'documentation\\matlab-fmu-doc.pdf' )


if __name__ == "__main__":

    if len( sys.argv ) != 2:
        print 'Usage:\n\tpython create-release.py <release-name>\n'
        print 'Attention: Be sure to execute this script from subfolder \'release\'\n'
        sys.exit()
    
    # Get current working directory (should be subfolder 'release').
    cwd = os.getcwd()
    if ( 'release' != os.path.basename( cwd ) ):
        print 'Attention: Be sure to execute this script from subfolder \'release\'\n'
        sys.exit()
    
    # Check if files exist.
    if ( False == checkFilesExist( doc_file, required_binaries, cwd ) ):
        sys.exit()
    
    # Define release name.
    release_name = 'matlab-fmipp-' + sys.argv[1]

    # Define release file name.
    release_file_name = release_name + '.zip'
    
    # Create release archive.
    release_file = zipfile.ZipFile( release_file_name, 'w', compression = zipfile.ZIP_DEFLATED )
    
    # Copy files to release archive.
    createRelease( release_file, release_name, cwd )
    
    # Close release archive.
    release_file.close()
