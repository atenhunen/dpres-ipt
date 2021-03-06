# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest
import testcommon.settings

# Module to test
import ipt.fileutils.filefinder

# Other imports
import os

SIPDIR = os.path.abspath(os.path.dirname(__file__) + '../../data/test-sips')


class TestGetFilesInTree:

    def test_filelist_with_chdir(self):
        testset = set([
            "kuvat/P1020137.JPG",
            "kuvat/PICT0081.JPG",
            "kuvat/PICT0102.JPG",
            "mets.xml",
            "varmiste.sig"])
        cwd = os.getcwd()
        os.chdir(os.path.join(SIPDIR, 'CSC_test001'))
        gotset = set(ipt.fileutils.filefinder.get_files_in_tree())
        os.chdir(cwd)
        assert gotset == testset

    def test_filelist_with_tree(self):

        testset = set([
            "kuvat/P1020137.JPG",
            "kuvat/PICT0081.JPG",
            "kuvat/PICT0102.JPG",
            "mets.xml",
            "varmiste.sig"])
        relpath = os.path.relpath(os.path.join(SIPDIR, 'CSC_test001'))
        assert set(
            ipt.fileutils.filefinder.get_files_in_tree(relpath)) == testset
