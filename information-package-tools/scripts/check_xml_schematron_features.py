#!/usr/bin/python
# vim:ft=python

import os
import sys
import optparse

import validator.plugin.schematron
import mets.search

def main(arguments=None):
    """Main loop"""
    usage = "usage: %prog [options] <mets filename|sip path>"
    sharepath = "/usr/share/information-package-tools/"

    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-s", "--schemapath", dest="schemapath",
                default=os.path.join(sharepath, "kdk-schematron"),
                help="Path to KDK-PAS schematron schemas",
                metavar="PATH")


    (options, args) = parser.parse_args(arguments)

    if len(args) != 1:
        parser.error("Must give XML filename or SIP directory as argument")

    filename = mets.search.search_mets(args[0])

    if filename == None:
        print >> sys.stderr, "ERROR: mets.xml not found"
        return 1
        
    validate = validator.plugin.schematron.XSLT()

    result = validate.validate_file(options.schemapath, filename)

    print result.messages
    
    if len(result.errors.strip('\n \t')) > 0:
        print >>sys.stderr, result.errors
    
    if result.has_errors():
        print result
        return 1

    return 0