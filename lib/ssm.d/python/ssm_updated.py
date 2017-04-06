#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ssm_updated.py

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

"""Provides the 'updated' subcommand.
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
usage: ssm updated [options]
       ssm updated -h|--help

Update various domain-specific settings.

Options:
-d <path>       Path of the domain to update. Default is
                $SSM_DOMAIN_HOME.
-L <string>     Set the descriptive text.
--published     Update the published directory to support the new
                v10 published/ layout.
--sources <string>
                Set the repository sources setting.
--subdomains <filename>
                Set the ordered list of immediate subdomains from a
                file. A filename of '-' reads from the stdin.
--support       Update the support files (from the version of ssm
                being executed). See 'ssm showd --version' for the
                version of the domain and 'ssm version' for the ssm
                version being executed.

Miscellaneous options:
--debug         Enable debugging.
--force         Force operation.
--verbose       Enable verbose output.
-y|--yes        Automatically respond 'y' to prompts.""")

if __name__ == "__main__":
    try:
        domain_home = None
        label = None
        sources = None
        subdomains_filename = None
        update_published = False
        update_support = False

        args = sys.argv[1:]
        while args:
            arg = args.pop(0)
            if arg in ["-h", "--help"]:
                print_usage()
                sys.exit(0)

            elif arg in ["-d", "--domainHome"] and args:
                domain_home = args.pop(0)
            elif arg in ["-L", "--label"] and args:
                label = args.pop(0)
            elif arg in ["--sources"] and args:
                sources = args.pop(0)
            elif arg in ["--published"]:
                update_published = True
            elif arg in ["--subdomains"] and args:
                subdomains_filename = args.pop(0)
            elif arg in ["--support"]:
                update_support = True

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

    try:
        domain = Domain(domain_home)
        if not domain.is_compatible():
            utils.print_exit(MSG_INCOMPATIBLE_DOMAIN)
        if label != None:
            domain.set_label(label)
        if sources != None:
            domain.set_sources(sources)
        if subdomains_filename != None:
            if subdomains_filename == "-":
                f = sys.stdin
            elif subdomains_filename == "--":
                # open editor
                pass
            else:
                f = open(subdomains_filename)
            subdomains = [s for s in f if s.strip() != ""]
            domain.set_subdomains(subdomains)
        if update_published:
            try:
                root = domain.published_path
                filenames = os.listdir(root)
            except:
                utils.print_exit("error: cannot update published/ directory")

            for filename in filenames:
                file_path = "%s/%s" % (root, filename)
                if os.path.islink(file_path):
                    try:
                        _, _, platform = filename.split("_", 2)
                        dir_path = "%s/%s" % (root, platform)
                        utils.makedirs(dir_path)
                        utils.rename(file_path, "%s/%s" % (dir_path, filename))
                    except:
                        utils.print_warning("warning: skipping file (%s)" % filename)
        if update_support:
            domain_version = domain.get_version()
            if VERSION < domain_version:
                if not globls.force and not globls.auto_yes:
                    if utils.prompt("downgrade from %s to %s (y/n)?" % (VERSION, domain_version)).lower() not in ["y"]:
                        utils.print_exit("operation aborted")
            domain.update_support()
    except SystemExit:
        raise
    except utils.SSMExitException, detail:
        utils.print_exit(detail)
    except:
        if globls.debug:
            traceback.print_exc()
        utils.print_exit("error: operation failed")
    sys.exit(0)
