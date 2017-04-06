#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ssm_created.py

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

"""Provides the 'created' subcommand.
"""

# system imports
import sys
import traceback

#
from ssm.constants import *
from ssm import globls
from ssm import utils
from ssm.domain import Domain

def print_usage():
    print("""\
usage: ssm created [options] [required]
       ssm created -h|--help

Create a new domain, and optionally set domain-specific settings.

Required:
-d <path>       Path of the domain in which to install the package.

Options:
-L <string>     Descriptive text for the domain.
--sources <string>
                The repository sources setting.

Miscellaneous options:
--debug         Enable debugging.
--force         Force operation.
--verbose       Enable verbose output.""")
#-y|--yes        Automatically respond 'y' to prompts.""")

if __name__ == "__main__":
    try:
        domain_home = None
        repo_source = DEFAULT_REPO_SOURCE
        label = DEFAULT_DOMAIN_LABEL

        args = sys.argv[1:]
        while args:
            arg = args.pop(0)
            if arg in ["-h", "--help"]:
                print_usage()
                sys.exit(0)

            elif arg in ["-d", "--domainHome"] and args:
                domain_home = args.pop(0)
            elif arg in ["--sources"] and args:
                repo_source = args.pop(0)
            elif arg in ["-L", "--label"] and args:
                label = args.pop(0)

            elif arg in ["--debug"]:
                globls.debug = True
            elif arg in ["--force"]:
                globls.force = True
            elif arg in ["--verbose"]:
                globls.verbose = True
            #elif arg in ["-y", "--yes"]:
                #globls.auto_yes = True
            else:
                raise Exception()
    except SystemExit:
        raise
    except:
        if globls.debug:
            traceback.print_exc()
        utils.print_exit("error: bad/missing argument(s)")

    # TODO: this does not check properly
    if not domain_home:
        utils.print_exit("error: cannot do a create over an existing domain")

    try:
        domain = Domain(domain_home)
        domain.create(label, repo_source)
    except SystemExit:
        raise
    except utils.SSMExitException, detail:
        utils.print_exit(detail)
    except:
        if globls.debug:
            traceback.print_exc()
        utils.print_exit("error: operation failed")
    sys.exit(0)
