"""Module for validating files with warc-tools warc validator"""
import gzip

from validator.basevalidator import BaseValidator

class WarcTools(BaseValidator):

    """ Initializes warctools validator and set ups everything so that
        methods from base class (BaseValidator) can be called, such as
        validate() for file validation.
    
    
    .. seealso:: http://code.hanzoarchives.com/warc-tools
    """
        
    def __init__(self, mimetype, fileversion, filename):
        super(WarcTools, self).__init__()
        self.exec_cmd = ['warcvalid.py']
        self.filename = filename
        self.fileversion = fileversion
        self.mimetype = mimetype
        
        if mimetype != "application/warc":
            raise Exception("Unknown mimetype: %s" % mimetype)

    def check_validity(self):
        return None

    def check_version(self, version):
        """ Check the file version of given file. In WARC format version string
            is stored at the first line of file so this methdos read the first
            line and check that it matches.
        """
        warc_fd = gzip.open(self.filename)
        try:
            warc_content = warc_fd.read()
        except IOError:
            warc_fd.close()
            warc_fd = open(self.filename)
            warc_content = warc_fd.read()

        split_list = warc_content.splitlines()
        if split_list[0].find("WARC/%s" % version) != -1:
            check_done = "File version checked"
            print check_done
            return None
        else:
            return "File version check error"

    def check_profile(self, profile):
        """ WARC file format does not have profiles """
        return None
