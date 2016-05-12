""" Class for XML file validation with Xmllint. """

import os
import subprocess
import tempfile
from lxml import etree

from ipt.validator.basevalidator import BaseValidator

DEFAULT_CATALOG = os.path.join('/usr/share/information-package-tools',
                               'xmlobjectcatalog/catalog-local.xml')

XSI = 'http://www.w3.org/2001/XMLSchema-instance'
XS = '{http://www.w3.org/2001/XMLSchema}'

SCHEMA_TEMPLATE = """<?xml version = "1.0" encoding = "UTF-8"?>
    <xs:schema xmlns="http://dummy"
    targetNamespace="http://dummy"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    version="1.0"
    elementFormDefault="qualified"
    attributeFormDefault="unqualified">
    </xs:schema>"""


class Xmllint(BaseValidator):

    """This class implements a plugin interface for validator module and
    validates XML files using Xmllint tool.

    .. seealso:: http://xmlsoft.org/xmllint.html
    """

    _supported_mimetypes = {
        'text/xml': ['1.0']
    }

    def __init__(self, fileinfo):
        super(Xmllint, self).__init__(fileinfo)

        self.schema = fileinfo.get('schema', None)
        self.used_version = None
        self.has_constructed_schema = False

    def validate(self):
        """Validate XML file with Xmllint and return a tuple of results.
        Strategy for XML file validation is
            1) Try validate well-formedness by opening file.
            2) If there's DTD specified in file do DTD validation
            3) If there's no DTD and we have external XSD do validation againts
               that.
            4) If there's no external XSD read schemas used in file and do
               validation againts them with schema catalog.

        :returns: Tuple (status, report, errors) where
            status -- 0 is success, anything else failure
            report -- generated report
            errors -- errors if encountered, else None

        .. seealso:: https://wiki.csc.fi/wiki/KDK/XMLTiedostomuotojenSkeemat
        """

        # Try to validate well-formedness by opening file in XML parser
        try:
            fd = open(self.filename)
            parser = etree.XMLParser(dtd_validation=False, no_network=True)
            tree = etree.parse(fd, parser=parser)
            self.used_version = tree.docinfo.xml_version
            fd.close()
        except etree.XMLSyntaxError:
            self.not_valid()
            self.errors("Validation failed: document is not well formed.")

            return self.result()

        # Try validate against DTD
        if tree.docinfo.doctype:
            (exitcode, stdout, stderr) = self.exec_xmllint(validate=True)

        # Try validate againts XSD
        else:
            if not self.schema:
                self.schema = self.construct_xsd(tree)

                if not self.schema:
                    # No given schema and didn't find included schemas but XML
                    # was well formed.
                    self.messages("Validation success: Document is "
                                  "well-formed but does not contain schema.")
                    return self.result()

            (exitcode, stdout, stderr) = self.exec_xmllint(schema=self.schema)

        self.messages(stdout)
        self.errors(stderr)

        if exitcode != 0:
            self.not_valid()

            # Clean up constructed schemas
            if self.has_constructed_schema:
                    os.remove(self.schema)


        return self.result()

    def construct_xsd(self, document_tree):
        """This method constructs one schema file which collects all used
        schemas from given document tree and imports all of them in one file.


        :tree: XML tree (lxml.etree) where XSD is constructed
        :returns: Path to the constructed XSD schema
        """

        xsd_exists = False

        parser = etree.XMLParser(dtd_validation=False, no_network=True)
        schema_tree = etree.XML(SCHEMA_TEMPLATE, parser)

        schema_locations = set(document_tree.xpath(
            '//*/@xsi:schemaLocation', namespaces={'xsi': XSI}))
        for schema_location in schema_locations:
            xsd_exists = True

            namespaces_locations = schema_location.strip().split()
            # Import all found namspace/schema location pairs
            for namespace, location in zip(*[iter(namespaces_locations)] * 2):
                xs_import = etree.Element(XS + 'import')
                xs_import.attrib['namespace'] = namespace
                xs_import.attrib['schemaLocation'] = location
                schema_tree.append(xs_import)

        schema_locations = set(document_tree.xpath(
            '//*/@xsi:noNamespaceSchemaLocation', namespaces={'xsi': XSI}))
        for schema_location in schema_locations:
            xsd_exists = True

            # Check if XSD file is included in SIP
            local_schema_location = os.path.dirname(self.filename) + '/' + \
                schema_location
            if os.path.isfile(local_schema_location):
                schema_location = local_schema_location

            xs_import = etree.Element(XS + 'import')
            xs_import.attrib['schemaLocation'] = schema_location
            schema_tree.append(xs_import)
        if xsd_exists:
            # Contstruct the schema
            fd, schema = tempfile.mkstemp(
                prefix='information-package-tools-', suffix='.tmp')
            et = etree.ElementTree(schema_tree)
            et.write(schema)

            self.has_constructed_schema = True

            return schema

        return []

    def exec_xmllint(self, huge=True, no_output=True, no_network=True,
                     validate=False, catalog=DEFAULT_CATALOG, schema=None):

        option_validation = ['--valid'] if validate else []
        option_huge = ['--huge'] if huge else []
        option_no_output = ['--noout'] if no_output else []
        option_no_network = ['--nonet'] if no_network else []
        option_catalog = ['--catalogs'] if catalog else []
        option_schema = ['--schema', schema] if schema else []

        command = ['xmllint'] + option_huge + option_no_output + \
            option_no_network + option_catalog + option_schema + \
            option_validation + [self.filename]

        environment = {
            'SGML_CATALOG_FILES': catalog
        }

        proc = subprocess.Popen(
            command,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False)

        (stdout, stderr) = proc.communicate()
        returncode = proc.returncode

        return (returncode, stdout, stderr)


    def errors(self, error=None):
        """Remove the warning which we do not need to see from self.stderr.
        See KDKPAS-1190."""


        if error and "this namespace was already imported with the" in error:
            return []

        return super(Xmllint, self).errors(error)
