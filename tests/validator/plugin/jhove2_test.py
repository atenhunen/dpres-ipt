# Common boilerplate
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import re
import json
import pytest
import testcommon.settings

# Module to test
import ipt.validator.plugin.jhove2

PROJECTDIR = testcommon.settings.PROJECTDIR

TESTDATADIR_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '../../data'))

TESTDATADIR = os.path.abspath(os.path.join(TESTDATADIR_BASE,
                                           '02_filevalidation_data'))

@pytest.mark.usefixtures("monkeypatch_Popen")
def test_validate():

    testcasefile = os.path.join(PROJECTDIR, TESTDATADIR,
                                'jhove2_testcases.json')
    print "\nLoading test configuration from %s\n" % testcasefile

    json_data = open(testcasefile)
    testcases = json.load(json_data)
    json_data.close()

    for testcase in testcases["test_validate"]:

        print "Testcase: ", testcase["testcase"]

        testcase["fileinfo"]["filename"] = os.path.join(
            testcommon.settings.TESTDATADIR,
            testcase["fileinfo"]["filename"])
        val = ipt.validator.plugin.jhove2.Jhove2(testcase["fileinfo"])

        (status, stdout, stderr) = val.validate()

        if testcase["expected_result"]["status"] == 0:
            assert testcase["expected_result"]["status"] == status
        else:
            assert testcase["expected_result"]["status"] != 0

        for match_string in testcase["expected_result"]["stdout"]:
            message = "\n".join(
                ["got:", stdout.decode('utf-8'), "expected:",
                match_string])
            assert re.match('(?s).*' + match_string, stdout), message

        for match_string in testcase["expected_result"]["stderr"]:
            message = "\n".join(
                ["got:", stderr.decode('utf-8'), "expected:",
                match_string])
            assert re.match('(?s).*' + match_string, stderr), message


@pytest.mark.usefixtures("monkeypatch_Popen")
def test_check_charset():

    fileinfo = {
        "filename": "tests/data/02_filevalidation_data/text/utf8.txt",
        "format": {
            "mimetype": "text/plain",
            "version": "1.0",
            "charset": "UTF-8"
        }
    }
    validator =  ipt.validator.plugin.jhove2.Jhove2(fileinfo)
    validator.validate()
    assert validator.check_charset()


@pytest.mark.usefixtures("monkeypatch_Popen")
def test_check_charset_failure():

    fileinfo = {
        "filename": "tests/data/02_filevalidation_data/text/utf8.txt",
        "format": {
            "mimetype": "text/plain",
            "version": "1.0",
            "charset": "WRONG_CHARSET"
        }
    }
    validator =  ipt.validator.plugin.jhove2.Jhove2(fileinfo)
    validator.validate()

    assert not validator.check_charset()

