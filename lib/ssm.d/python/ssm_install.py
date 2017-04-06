#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ssm_install.py

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

"""Provides the 'install' subcommand.
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
usage: ssm install [options] [required]
       ssm install -h|--help

Install a package to a domain.

Required (either):
-f <filename>   Package filename (ending with .ssm).
-p <name>       Name of a packages to install.

Options:
-d <path>       Path of the domain in which to install the package.
                Default is $SSM_DOMAIN_HOME.
-u <url>[,...]  Comma-separate list of URL(s) from which to search
                for the package. The default is to look at the
                sources.list settings.
--clobber       Permit any exiting files to be overwritten. Default
                is a non-destructive overlay.
--skipOnInstalled
                Skip if the package has already been installed.

Miscellaneous options:
--debug         Enable debugging.
--force         Force operation.
--verbose       Enable verbose output.""")
#-y|--yes        Automatically respond 'y' to prompts.""")

if __name__ == "__main__":
    try:
        clobber = False
        domain_home = None
        filename = None
        groupname = utils.groupname()
        package_name = None
        skip_on_installed = False
        sources = None
        username = utils.username()

        args = sys.argv[1:]
        while args:
            arg = args.pop(0)
            if arg in ["-h", "--help"]:
                print_usage()
                sys.exit(0)

            if arg in ["--clobber"]:
                clobber = True
            elif arg in ["-d", "--domainHome"] and args:
                domain_home = args.pop(0)
            elif arg in ["-f"] and args:
                filename = args.pop(0)
            elif arg in ["-G", "--groupName"] and args:
                groupname = args.pop(0)
            elif arg in ["-p", "--packageName"] and args:
                package_name = args.pop(0)
            elif arg in ["--skipOnInstalled"]:
                skip_on_installed = True
            elif arg in ["-u", "--repositoryUrl"] and args:
                sources = args.pop(0).split(",")
            elif arg in ["-U", "--userName"] and args:
                username = args.pop(0)

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

    if filename:
        if filename.endswith(".ssm"):
            sources = [os.path.realpath(os.path.dirname(filename))]
            package_name = os.path.basename(filename)[:-4]
        else:
            utils.print_exit("error: bad filename")
    if not package_name:
        utils.print_exit("error: missing package name")

    try:
        domain = Domain(domain_home)
        if not domain.is_compatible():
            utils.print_exit(MSG_INCOMPATIBLE_DOMAIN)

        if domain.is_installed(package_name) and skip_on_installed:
            utils.print_verbose("skipping installed package")
        else:
            if sources == None:
                sources = domain.get_sources().split("\n")
            for source in sources:
                source = source.strip()
                if source == "":
                    continue
                repo = Repository(source)
                tarf = repo.get(package_name)
                if tarf != None:
                    utils.print_verbose("installing package (%s) from repository (%s)" % (package_name, source))
                    pkg = Package(domain, package_name)
                    pkg.install(tarf, username, groupname, clobber)
                    break
            else:
                utils.print_exit("error: could not find package")
    except SystemExit:
        raise
    except utils.SSMExitException, detail:
        utils.print_exit(detail)
    except Exception, detail:
        if globls.debug:
            traceback.print_exc()
        utils.print_exit("error: operation failed")
    #finally:
        #if tarf:
            #tarf.close()
    sys.exit(0)
