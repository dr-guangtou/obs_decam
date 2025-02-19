#
# LSST Data Management System
# Copyright 2016 LSST Corporation.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <http://www.lsstcorp.org/LegalNotices/>.
#

import os
import unittest
import warnings

import lsst.daf.persistence as dafPersist
import lsst.utils.tests
from lsst.ip.isr import Linearizer, LinearizeLookupTable
from lsst.utils import getPackageDir


class ButlerTestCase(unittest.TestCase):
    """Testing butler policy setup"""

    def setUp(self):
        try:
            datadir = getPackageDir("testdata_decam")
        except LookupError:
            message = "testdata_decam not setup. Skipping."
            warnings.warn(message)
            raise unittest.SkipTest(message)

        self.repoPath = os.path.join(datadir, "rawData")
        self.butler = dafPersist.Butler(root=self.repoPath)

    def tearDown(self):
        del self.butler

    def testButlerSubsetLevel(self):
        """Test if subset is gathered correctly for the specified level"""
        subset = self.butler.subset("raw", level="sensor", visit=229388, ccdnum=1)
        print("ButlerSubset.cache: %s" % subset.cache)
        self.assertEqual(len(subset), 1)

        subset = self.butler.subset("raw", level="sensor", visit=229388)
        print("ButlerSubset.cache: %s" % subset.cache)
        self.assertEqual(len(subset), 2)

        subset = self.butler.subset("raw", level="visit", visit=229388)
        print("ButlerSubset.cache: %s" % subset.cache)
        self.assertEqual(len(subset), 1)

    def testGetCamera(self):
        """Test that we can get a camera"""
        camera = self.butler.get("camera")
        self.assertEqual(len(camera), 62)
        self.assertEqual(camera[1].getName(), "S29")
        self.assertEqual(camera[62].getName(), "N31")

    def testGetLinearizer(self):
        """Test that we can get a linearizer"""
        camera = self.butler.get("camera")
        for ccdnum in (1, 62):
            detector = camera[ccdnum]
            linearizer = Linearizer(table=self.butler.get("linearizer",
                                                          dataId=dict(ccdnum=ccdnum),
                                                          immediate=True),
                                    detector=detector)
            for amp in detector:
                self.assertEqual(linearizer.linearityType[amp.getName()], LinearizeLookupTable.LinearityType)
            linearizer.validate(detector=detector)
        for badccdnum in (0, 63):
            with self.assertRaises(Exception):
                self.butler.get("linearizer", dataId=dict(ccdnum=badccdnum), immediate=True)


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
