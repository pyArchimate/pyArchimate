#!/usr/bin/env python

import argparse
import os
import zipfile
from getpass import getuser, getpass
from time import sleep
import requests

from AMLparser import AML
from logger import *


__mod__ = __name__.split('.')[len(__name__.split('.')) - 1]
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


log_to_file('out.log')


def main():
    """
    Read the XML file given as first argument and convert it to Open Exchange File format
    """

    parser = argparse.ArgumentParser("Convert ARIS AML to Archimate Open Exchange File")
    parser.add_argument('file',
                        help="AML input file")
    parser.add_argument('-s', '--scale', required=False,
                        help='Diagram scale factor')
    parser.add_argument('-xO', '--noOrgs', required=False, action='store_true',
                        help='Exclude organizations structure')
    parser.add_argument('-xE', '--noEmbed', required=False, action='store_true',
                        help="Exclude embedding in visual nodes")
    parser.add_argument('-xV', '--noView', required=False, action='store_true',
                        help="Exclude views and report only concepts & relationships")
    parser.add_argument('-xo', '--noOptimization', required=False, action='store_true',
                        help='Do not remove elements and relationships that are not used in views')
    parser.add_argument('-o', '--outputfile', required=False, help="Output converted file")
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
                        help="Display DEBUG & INFO log messages")
    parser.add_argument('-cp', '--checkPattern', required=False, action='store_true',
                        help="Check compliance with ING patterns")
    parser.add_argument('-csv', '--csv', required=False, action='store_true',
                        help="Generate model csv files")
    args = parser.parse_args()

    if args.verbose:
        log_set_level(logging.DEBUG)
        log_to_stderr()

    if args.scale:
        scale = eval(args.scale)
        if isinstance(scale, tuple):
            scale_x, scale_y = scale
        else:
            scale_x = scale
            scale_y = scale
    else:
        scale_x = 0.3
        scale_y = 0.4

    if 'TMP' in os.environ:
        tmpdir = os.environ['TMP']
    else:
        tmpdir = os.curdir

    if os.path.exists(os.path.join(tmpdir, '$parseAML.zip')):
        os.remove(os.path.join(tmpdir, '$parseAML.zip'))
    if os.path.exists(os.path.join(tmpdir, "ARISAMLExport.xml")):
        os.remove(os.path.join(tmpdir, "ARISAMLExport.xml"))

    if 'http' in args.file:
        TMPFILE = os.path.join(tmpdir, '$parseAML.zip')
        cacerts = os.path.join(os.environ['USERPROFILE'], '.ssh', 'certs.pem')
        # PROXY_URL = 'giba-proxy.wps.ing.net:8080'
        user = getuser()
        pwd = getpass('Enter password for user ' + user + ": ")
        auth = (user, pwd)
        # proxy = {'proxy_url': PROXY_URL, 'proxy_user': user, 'proxy_pwd': pwd}
        r = requests.get(args.file, verify=cacerts, auth=auth, allow_redirects=True, stream=False)  # proxies=proxy,
        sleep(3)
        # while not os.path.exists(os.path.join(tmpdir, '$parseAML.zip')):
        #    sleep(1)
        open(TMPFILE, 'wb').write(r.content)

        with zipfile.ZipFile(TMPFILE, "r") as zip_ref:
            zip_ref.extractall(tmpdir)
            args.file = os.path.join(tmpdir, "ARISAMLExport.xml")

    elif '.zip' in args.file:
        with zipfile.ZipFile(args.file, "r") as zip_ref:
            zip_ref.extractall(tmpdir)
            args.file = os.path.join(tmpdir, "ARISAMLExport.xml")

    aris = AML(open(args.file, 'r').read(), name='arisExport', scale_x=scale_x, scale_y=scale_y, skip_bendpoint=False,
               include_organization=False if args.noOrgs else True,
               optimize=False if args.noOptimization else True,
               no_view=True if args.noView else False,
               check_pattern=True if args.checkPattern else False
               )
    result = aris.convert()

    # TODO Expand properties before writing the result

    if args.outputfile:
        result.write(args.outputfile)

    else:
        #  print(result)
        out_file = args.file[:-4] + "_OEF.xml"
        result.write(out_file)

    if args.csv:
        from toCSV import to_csv
        to_csv()

    print('Done.')


if __name__ == "__main__":
    main()
