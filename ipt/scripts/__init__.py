"""Command line tools / scripts for *information-package-tools* libraries.

This package provides command line utilites for handling SIP, AIP and DIP
packages. Command line scripts are autogenerated from these modules.

All modules have common interface::

    def main(arguments=None):


            ... parse arguments ..

        ... do the stuff, maybe print something ...

        return 0   # Note use return here, not exit()


Command line tool modules are named with underscores:
:file:`scripts/command_with_long_name.py`

Setuptools / setup.py will create according command line tool with name:
:file:`/usr/bin/command-with-long-name`.

Automatically generated script will just call the main function from our
module and returns it's return value::

    retval = scripts.command_with_long_name()
    exit retval

This code layout makes unit testing easier and makes Linux / Windows
installation possible.

For testing we just inject optparse options/arguments as function
parameters, and capture stdout/stderr with some Python magic::

    (returncode, stdout, stderr) = testcommon.shell.run_main(
        scripts.command_with_long_name.main,
        {"named_option":"some option value"},
        ['some parameter', 'other parameter'])

    assert returncode == 0
    assert stdout.find('something')

"""
