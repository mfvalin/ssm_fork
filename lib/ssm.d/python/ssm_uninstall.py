#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ssm_uninstall.py

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

"""Provides the 'uninstall' subcommand.
"""

# system imports
import os
import sys
import traceback

#
from ssm.constants import *
from ssm import globls
from ssm import utils
from ssm.domain import Domain
from ssm.package import Package

def print_usage():
    print("""\
usage: ssm uninstall [options] [required]
       ssm uninstall -h|--help

Install package to domain.

Required:
-p <name>       Name of a package to uninstall.

Options:
-d <path>       Path of the domain from which to uninstall the
                package. Default is $SSM_DOMAIN_HOME.
                    
Miscellaneous options:
--debug         Enable debugging.
--force         Force operation.
--verbose       Enable verbose output.""")
#-y|--yes        Automatically respond 'y' to prompts.""")

if __name__ == "__main__":
    try:
        domain_home = None
        package_name = None

        args = sys.argv[1:]
        while args:
            arg = args.pop(0)
            if arg in ["-h", "--help"]:
                print_usage()
                sys.exit(0)

            if arg in ["-d", "--domainHome"] and args:
                domain_home = args.pop(0)
            elif arg in ["-p", "--packageName"] and args:
                package_name = args.pop(0)

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
        pkg = Package(domain, package_name)
        if domain.is_published(package_name):
            utils.print_exit("error: package is published")
        if not pkg.exists() and not domain.is_installed(package_name):
            utils.print_exit("error: package is not installed")
        pkg.uninstall()
    except SystemExit:
        raise
    except utils.SSMExitException, detail:
        utils.print_exit(detail)
    except Exception, detail:
        if globls.debug:
            traceback.print_exc()
        utils.print_exit("error: operation failed")
    sys.exit(0)
