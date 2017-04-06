#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ssm_unpublish.py

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

"""Provides the 'unpublish' subcommand.
"""

# system imports
import os
import os.path
import sys
import traceback

#
from ssm.constants import *
from ssm import globls
from ssm import utils
from ssm.domain import Domain
from ssm.package import Package
from ssm.repository import Repository

def print_usage():
    print("""\
usage: ssm unpublish [options] [required]
       ssm unpublish -h|--help

Unpublish a package from a domain.

Required:
-p <name>       Name of a package to publish.
-pp <platform>  Platform from which to unpublish package. Default is
                the package platform.

Options:
-d <path>       Path of the domain of the published package. Default
                is $SSM_DOMAIN_HOME.

Miscellaneous options:
--debug         Enable debugging.
--force         Force operation.
--verbose       Enable verbose output.""")
#-y|--yes        Automatically respond 'y' to prompts.""")

if __name__ == "__main__":
    try:
        domain_home = None
        package_name = None
        publish_platform = None

        args = sys.argv[1:]
        while args:
            arg = args.pop(0)
            if arg in ["-h", "--help"]:
                print_usage()
                sys.exit(0)

            elif arg in ["-d", "--domainHome"] and args:
                domain_home = args.pop(0)
            elif arg in ["-p", "--packageName"] and args:
                package_name = args.pop(0)
            elif arg in ["-pp"] and args:
                publish_platform = args.pop(0)

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

    if not package_name:
        utils.print_exit("error: missing package name")

    try:
        domain = Domain(domain_home)
        if not domain.is_compatible():
            utils.print_exit(MSG_INCOMPATIBLE_DOMAIN)
        package = Package(domain, package_name)
        if publish_platform == None:
            _, _, publish_platform = package.name.split("_", 2)
        if not domain.is_published(package_name, publish_platform) and not globls.force:
            utils.print_exit("error: package not published")
        domain.unpublish_package(package, publish_platform)
    except SystemExit:
        raise
    except utils.SSMExitException, detail:
        utils.print_exit(detail)
    except:
        if globls.debug:
            traceback.print_exc()
        utils.print_exit("error: operation failed")
    sys.exit(0)
