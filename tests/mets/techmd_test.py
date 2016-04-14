import os
import lxml.etree

from tests.testcommon.settings import PROJECTDIR
from ipt.addml import to_dict

TESTDATADIR = os.path.join(PROJECTDIR, 'tests', 'data', 'mets', 'techmd')


def test_to_dict():
    """test for get_addml_dict()."""
    addml_path = os.path.join(TESTDATADIR, 'addml.xml')
    addml_tree = lxml.etree.parse(addml_path)
    expected = {"addml": {
        "charset": "UTF-8",
        "separator": "CR+LF",
        "delimiter": ";",
        "headers": ["Person name", "Person email"]}
        }

    assert to_dict(addml_tree) == expected