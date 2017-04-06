#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ssm_publish.py

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

"""Provides the 'publish' subcommand.
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
usage: ssm publish [options] [required]
       ssm publish -h|--help

Publish a package to a domain. To publish a package from one domain
to an alternate domain, use the -P option.

Required:
-p <name>       Name of a package to publish.

Options:
-d <path>       Path of the domain of the installed package. Also
                serves as the default domain in which to publish the
                package. Default is $SSM_DOMAIN_HOME.
-pp <platform>  Platform to which to publish package. Default is the
                package platform.
-P <path>       Path of an alternate domain in which to publish the
                package.

Miscellaneous options:
--debug         Enable debugging.
--force         Force operation.
--verbose       Enable verbose output.
-y|--yes        Automatically respond 'y' to prompts.""")

if __name__ == "__main__":
    try:
        domain_home = None
        package_name = None
        publish_home = None
        publish_platform = None
        #force_publish = False
        skip_on_published = False

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
            elif arg in ["-P", "--publishHome"] and args:
                publish_home = args.pop(0)
            elif arg in ["--skipOnPublished"]:
                skip_on_published = True

            elif arg in ["--debug"]:
                globls.debug = True
            elif arg in ["--force"]:
                globls.force = True
            elif arg in ["--verbose"]:
                globls.verbose = True
            elif arg in ["-y", "--yes"]:
                globls.auto_yes = True
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
        if not domain.is_domain():
            utils.print_exit("error: cannot find domain (%s)" % domain_home)
        if not domain.is_compatible():
            utils.print_exit(MSG_INCOMPATIBLE_DOMAIN)
        if publish_home == None:
            publish_home = domain_home
        publish_domain = Domain(publish_home)
        if not publish_domain.is_domain():
            utils.print_exit("error: cannot find domain (%s)" % publish_domain)
        package = Package(domain, package_name)
        publish_platform = publish_platform or package.platform

        # check for package
        if not package.domain.is_installed(package_name):
            utils.print_exit("error: cannot find package (%s)" % package_name)

        # unpublish named package if necessary
        if publish_domain.is_published(package_name, publish_platform):
            if skip_on_published:
                utils.print_exit("skipping published package", 0)
            if not globls.force and not globls.auto_yes:
                if utils.prompt("unpublish current package (y/n)?").lower() not in ["y"]:
                    utils.print_exit("operation aborted")
            publish_domain.unpublish_package(package, publish_platform)

        # unpublish "similar" package
        for pp_path in publish_domain.get_published(publish_platform):
            pp_name = os.path.basename(pp_path)
            if package.is_similar(pp_name):
                publish_domain.unpublish_package(Package(domain, pp_name), publish_platform)

        # ready to publish
        publish_domain.publish_package(package, publish_platform)
    except SystemExit:
        raise
    except utils.SSMExitException, detail:
        utils.print_exit(detail)
    except:
        if globls.debug:
            traceback.print_exc()
        utils.print_exit("error: operation failed")
    sys.exit(0)
