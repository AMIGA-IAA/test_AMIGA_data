# -*- coding: utf-8 -*-
__author__ = 'jsm'
import unittest
import StringIO
import urllib2
import os
from astropy.io.votable import parse_single_table
from astropy.io import ascii
from astropy import coordinates

# Workaround for PyCharm
os.environ['LC_CTYPE'] = 'es_ES.UTF-8'
####


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

class TestVOTable(unittest.TestCase):

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

    def test_size(self):
        """
        Check that we have 1051 rows
        """
        self.assertEqual(self.vo_table.size,1051)

    def test_coordinates(self):
        """
        Compare the coordinates (AMIGA 0).
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
        n_places = 6

        url_coordinates = "http://amiga.iaa.es/FCKeditor/UserFiles/File/ASCII/AMIGA_0/table1.dat"
        url_coordinates_readme = "http://amiga.iaa.es/FCKeditor/UserFiles/File/ASCII/AMIGA_0/ReadMe"
        local_coordinates = "%s/table1.dat"%self.local_cache
        local_coordinates_readme = "%s/Readme"%self.local_cache
        get_url(url_coordinates,local_coordinates)
        get_url(url_coordinates_readme,local_coordinates_readme)
        table = ascii.read(local_coordinates,readme=local_coordinates_readme)

        for i in range(self.vo_table.size):
            coords = coordinates.FK5Coordinates('%02ih%02im%05.2fs %s%02id%02im%04.1fs'%
                                                (table['RAh'][i],table['RAm'][i],
                                                 table['RAs'][i],table['DE-'][i],
                                                 table['DEd'][i],table['DEm'][i],
                                                 table['DEs'][i]))
            #self.assertEqual(self.vo_table['RA J2000'][i],coords.ra.degrees)
            #self.assertEqual(self.vo_table['DEC J2000'][i],coords.dec.degrees)
            self.assertAlmostEqual(self.vo_table['RA J2000'][i],coords.ra.degrees,places=n_places)
            self.assertAlmostEqual(self.vo_table['DEC J2000'][i],coords.dec.degrees,places=n_places)

    def tearDown(self):
        # Remove the temporary storage directory
        if os.path.exists(self.local_cache):
            os.system("rm -rf %s"%self.local_cache)

if __name__ == '__main__':
  unittest.main()