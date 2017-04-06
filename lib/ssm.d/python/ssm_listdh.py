#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ssm_listdh.py

# GPL--start
# This file is part of ssm (Simple Software Manager)
# Copyright (C) 2005-2012 Environment/Environnement Canada
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 2
# of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# GPL--end

"""Provides the 'listdh' subcommand.
"""

# system imports
import sys
import traceback

#
from ssm.constants import *
from ssm import globls
from ssm.domain import Domain
from ssm import utils

def get_all_subdomains(domain_home, level=0):
    if level >= 10:
        return []
        
    domain = Domain(domain_home)
    paths = []
    for path in domain.get_subdomains():
        paths.append([path, level])
        paths.extend(get_all_subdomains(path, level+1))
    return paths
    
def print_usage():
    print("""\
usage: ssm listdh [options]
       ssm listdh -h|--help

List a domain/subdomain hierarchy.

Options:
-d <path>       Path of the domain.

Miscellaneous options:
--debug         Enable debugging.
--verbose       Enable verbose output.""")

if __name__ == "__main__":
    try:
        domain_home = None

        args = sys.argv[1:]
        while args:
            arg = args.pop(0)
            if arg in ["-h", "--help"]:
                print_usage()
                sys.exit(0)

            elif arg in ["-d", "--domainHome"] and args:
                domain_home = args.pop(0)

            elif arg in ["--debug"]:
                globls.debug = True
            elif arg in ["--verbose"]:
                globls.verbose = True
            else:
                raise Exception()
    except SystemExit:
        raise
    except:
        if globls.debug:
            traceback.print_exc()
        utils.print_exit("error: bad/missing argument(s)")

    try:
        domain = Domain(domain_home)
        if not domain.is_compatible():
            utils.print_exit(MSG_INCOMPATIBLE_DOMAIN)
        paths = [[domain.path, 0]]
        paths.extend(get_all_subdomains(domain.path, 1))
        for path, level in paths:
            print "%s%s" % ("  "*level, path)
    except SystemExit:
        raise
    except utils.SSMExitException, detail:
        utils.print_exit(detail)
    except:
        if globls.debug:
            traceback.print_exc()
        utils.print_exit("error: could not access domain information")
        
    sys.exit(0)
