#!/usr/bin/python
# vim:ft=python

import os
import sys
import optparse
import ipt.validator.filelist
import ipt.mets.parser
import ipt.version
from ipt.premis import premis


def main(arguments=None):

    usage = "usage: %prog <sip-path> <linking-sip-object-id>"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-c", "--configfile", dest="config_filename",
                      default=None,
                      help="JSON configuration file",
                      metavar="PATH")
    (options, args) = parser.parse_args(arguments)

    if(len(args) != 3):
        parser.print_help()
        return 1

    sip_path = args[0]
    mets_filename = os.path.abspath(os.path.join(sip_path, 'mets.xml'))
    basepath = os.path.abspath(os.path.dirname(mets_filename))
    linking_sip_id = args[2]
    linking_sip_type = args[1]

    validate = ipt.validator.filelist.Validator(basepath)
    validate.load_config(options.config_filename)
    mets_parser = ipt.mets.parser.LXML(mets_filename)
    filelist = mets_parser.get_fileinfo_iterator()

    statuses, reports, errors, validators = validate.validate_files(filelist)

    return_status = 0
    return_message = ""

    prem = premis.Premis()

    filelist = mets_parser.get_fileinfo_array()

    for fileinfo, status, report, error, _validator in \
            zip(filelist, statuses, reports, errors, validators):

        if not _validator:
            return_status = 1
        elif status != 0:
            return_status = 117

        ff = ipt.validator.filelist.FileInfo(fileinfo)
        ff.from_dict(fileinfo)

        related_object = premis.Object()
        related_object.identifier = ""
        related_object.identifierType = linking_sip_type
        related_object.identifierValue = linking_sip_id

        agent_name = str(
            os.path.basename(__file__)) + "-" + ipt.version.__version__

        linking_agent = premis.Agent()
        linking_agent.fromvalidator(agentIdentifierType="preservation-agent-id",
                                    agentIdentifierValue=agent_name,
                                    agentName=agent_name)
        linking_agent.type = "software"
        prem.insert(linking_agent)

        linking_object = premis.Object()
        linking_object.fromvalidator(fileinfo=ff, relatedObject=related_object)

        validation_event = premis.Event()
        validation_event.fromvalidator(status, report, error,
                                       linkingObject=linking_object,
                                       linkingAgent=linking_agent)

        prem.insert(linking_object)
        prem.insert(validation_event)

    return_message = prem.serialize()
    sys.stdout.write(return_message)

    return return_status

if __name__ == '__main__':
    RETVAL = main()
    sys.exit(RETVAL)
