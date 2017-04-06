#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ssm_showd.py

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

"""Provides the 'showd' subcommand.
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
usage: ssm showd [options]
       ssm showd -h|--help

Show various domain-specific settings.

Options:
-d <path>       Path of the domain in which to install the package.
                Defaults to $SSM_DOMAIN_HOME.
-L              Show the descriptive text.
--installed     Show the paths of the packages installed.
--published     Show the paths of the packages published (to this
                domain).
--sources       Show the repository sources setting.
--subdomains    Show the ordered list of immediate subdomains.
--version       Show the version of the ssm support files.

Miscellaneous options:
--debug         Enable debugging.""")

if __name__ == "__main__":
    try:
        domain_home = None
        show_installed = False
        show_label = False
        show_published = False
        show_sources = False
        show_subdomains = False
        show_version = False

        args = sys.argv[1:]
        while args:
            arg = args.pop(0)
            if arg in ["-h", "--help"]:
                print_usage()
                sys.exit(0)

            elif arg in ["-d", "--domainHome"] and args:
                domain_home = args.pop(0)
            elif arg in ["--installed"]:
                show_installed = True
            elif arg in ["-L", "--label"]:
                show_label = True
            elif arg in ["--published"]:
                show_published = True
            elif arg in ["--sources"]:
                show_sources = True
            elif arg in ["--subdomains"]:
                show_subdomains = True
            elif arg in ["--version"]:
                show_version = True

            elif arg in ["--debug"]:
                globls.debug = True
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
        if show_installed:
            # TODO: should paths or names be shown for installed and published?
            print("%s" % "\n".join(domain.get_installed()))
        if show_label:
            print("%s" % str(domain.get_label()))
        if show_published:
            print("%s" % "\n".join(domain.get_published()))
        if show_sources:
            print("%s" % str(domain.get_sources()))
        if show_subdomains:
            print("\n".join(domain.get_subdomains()))
        if show_version:
            version = domain.get_version()
            version_string = ".".join(map(str, version))
            print("%s" % version_string)
    except SystemExit:
        raise
    except utils.SSMExitException, detail:
        utils.print_exit(detail)
    except:
        if globls.debug:
            traceback.print_exc()
        utils.print_exit("error: operation failed")
    sys.exit(0)
