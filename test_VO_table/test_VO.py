# -*- coding: utf-8 -*-
__author__ = 'jsm'
import unittest
import StringIO
import urllib2
import os
from astropy.io.votable import parse_single_table
from astropy.io import ascii
from astropy import coordinates, units
from warnings import warn

# Workaround for PyCharm
os.environ['LC_CTYPE'] = 'es_ES.UTF-8'
####

# Workaround for issue #1
try:
    from astropy.coordinates.errors import IllegalSecondWarning
except ImportError,e:
    from astropy import version
    warn("global name 'IllegalSecondWarning' is not defined in astropy %s; some comparisons will not be made" % version.version)

# Auxiliary functions
def url_file(url):
    """
    Get a file from an URL into a StringIO object
    """
    return StringIO.StringIO(urllib2.urlopen(url).read())


def get_url(url,local_file):
    """
    Get a local copy of an online file
    """
    f = file(local_file,"w")
    f.write(urllib2.urlopen(url).read())
    f.close()


# class TestVOService(unittest.TestCase):
#     def setUp(self):
#         #self.vo_url = "http://amiga.iaa.csic.es/amigasearch/search?RA=180.567&DEC=30.45&SR=10"
#         self.vo_url = "http://amiga.iaa.csic.es/amigasearch/search?RA=180.&DEC=90.&SR=180."
#         self.vo_table_raw = url_file(self.vo_url)
#
#     def test_read_url(self):
#         self.assertEqual(self.vo_table_raw.readlines(),
#                          url_file(self.vo_url).readlines())
#
#     def test_read_table(self):
#         vo_table = parse(self.vo_table_raw)

class TestVOTableAMIGA0(unittest.TestCase):
    
    def setUp(self):
        ### Online version of the AMIGA VOTable
        # self.vo_url = "http://amiga.iaa.csic.es/amigasearch/search?RA=180.&DEC=90.&SR=180."
        # self.vo_table = parse_single_table(url_file(self.vo_url)).array
        
        ### Local cached version of the AMIGA VOTable
        self.vo_table = parse_single_table("../data/amigasearch.xml").array
        
        # Create temporary storage directory for online AMIGA CDS data
        self.local_cache = "data_AMIGA_CDS"
        if not os.path.exists(self.local_cache):
            os.makedirs(self.local_cache)
        
        #Load AMIGA0 data
        url_coordinates = "http://amiga.iaa.es/FCKeditor/UserFiles/File/ASCII/AMIGA_0/table1.dat"
        url_coordinates_readme = "http://amiga.iaa.es/FCKeditor/UserFiles/File/ASCII/AMIGA_0/ReadMe"
        local_coordinates = "%s/table1.dat"%self.local_cache
        local_coordinates_readme = "%s/Readme"%self.local_cache
        get_url(url_coordinates,local_coordinates)
        get_url(url_coordinates_readme,local_coordinates_readme)
        self.table = ascii.read(local_coordinates,readme=local_coordinates_readme)
    
    def tearDown(self):
        # Remove the temporary storage directory
        if os.path.exists(self.local_cache):
            os.system("rm -rf %s"%self.local_cache)
    
    def test_size(self):
        """
        Check that we have 1051 rows
        """
        self.assertEqual(self.vo_table.size,1051)
    
    def test_coordinates_J2000(self):
        """
        Compare the J2000 coordinates (AMIGA 0).
        Relevant columns in the VO table:
          * 'RA J2000'
          * 'DEC J2000'
        Relevant columns in the CDS table:
          * 'RAh'
          * 'RAm'
          * 'RAs'
          * 'DE-'
          * 'DEd'
          * 'DEm'
          * 'DEs'
        """
        # Number of decimal places to match
        n_places = 3
        # Separation in arcsec to match
        max_separation = 0.5
        
        # Workaround depending on the astropy version
        # <= 0.2 uses arrays and >= 0.3 uses masked arrays
        if int(version.major) == 0 and int(version.minor) <= 2:
            dec_sign = self.table['DE-']
        else:
            dec_sign = self.table['DE-'].filled('')
        
        for i in range(self.vo_table.size):
            coords = None
            coordsVO = None
            try:
                hexCoordStringTemplate = '%02ih%02im%05.2fs %s%02id%02im%04.1fs'
                coords = coordinates.FK5Coordinates(
                            hexCoordStringTemplate % (
                                    self.table['RAh'][i],
                                    self.table['RAm'][i],
                                    self.table['RAs'][i],
                                    dec_sign[i],
                                    self.table['DEd'][i],
                                    self.table['DEm'][i],
                                    self.table['DEs'][i]
                            )
                )
            except NameError,e:
                warn(str(e))
                warn("The coordinates for CIG %04d could not be tested" % i)
                continue
            
            coordsVO = coordinates.FK5Coordinates(
                            ra  = self.vo_table['RA J2000'][i],
                            dec = self.vo_table['DEC J2000'][i],
                            unit= (units.degree, units.degree)
            )
            
            self.assertAlmostEqual(
                    self.vo_table['RA J2000'][i],
                    coords.ra.degrees,
                    places=n_places
            )
            self.assertAlmostEqual(
                    self.vo_table['DEC J2000'][i],
                    coords.dec.degrees,
                    places=n_places
            )
            
            separation = coords.separation(coordsVO).degrees*3600. #arcseconds
            self.assertLess(separation,max_separation)
        


if __name__ == '__main__':
  unittest.main()