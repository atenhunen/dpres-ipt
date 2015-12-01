"""Utility functions."""

import subprocess


def run_command(cmd, stdout=subprocess.PIPE):
    """Execute command. Validator specific error handling is supported
    by forwarding exceptions.

    :returns: Tuple (statuscode, stdout, stderr)
    """
    proc = subprocess.Popen(cmd,
                            stdout=stdout,
                            stderr=subprocess.PIPE,
                            shell=False)

    (stdout, stderr) = proc.communicate()
    statuscode = proc.returncode

    if statuscode != 0:
        if 'IOError' in stderr:
            raise IOError(stderr)
        if 'Exception' in stderr:
            raise Exception(stderr)

    return statuscode, stdout, stderr