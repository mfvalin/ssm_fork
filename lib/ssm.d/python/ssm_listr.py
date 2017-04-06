#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ssm_listr.py

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

"""Provides the 'listr' subcommand.
"""

# system imports
import fnmatch
import os.path
import sys
import traceback

#
from ssm import globls
from ssm import utils
from ssm.domain import Domain
from ssm.repository import Repository

def print_usage():
    print("""\
usage: ssm listr [options] [required]
       ssm listr -h|--help

List/find packages in a repository.

Options:
-d <path>       Path of the domain from which to get repository
                information. Default is $SSM_DOMAIN_HOME.
-p <pattern>    Package name to match. Wildcards (* and ?) are
                supported. Defaults to match all.
-u <url>        URL of repository to search.
--platforms <pattern>
                Platforms to match. Wildcards (* and ?) are
                supported. Defaults to match all.

Miscellaneous options:
--debug         Enable debugging.
--verbose       Enable verbose output.""")

if __name__ == "__main__":
    try:
        domain_home = None
        package_name_pattern = None
        platforms_pattern = None
        repo_url = None

        args = sys.argv[1:]
        while args:
            arg = args.pop(0)
            if arg in ["-h", "--help"]:
                print_usage()
                sys.exit(0)

            if arg in ["-d", "--domainHome"] and args:
                domain_home = args.pop(0)
            elif arg in ["-p", "--packageName"] and args:
                package_name_pattern = args.pop(0)
            elif arg in ["--platforms"] and args:
                platforms_pattern = args.pop(0)
            elif arg in ["-u", "--repositoryUrl"] and args:
                repo_url = args.pop(0)

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
        if repo_url:
            sources = repo_url
        else:
            domain = Domain(domain_home)
            sources = domain.get_sources()

        repo = Repository(sources)
        package_map = {}
        package_urls = repo.list()
        for url in repo.list():
            filename = os.path.basename(url)
            if not filename.endswith(".ssm"):
                continue
            package_name = filename[:-4]
            if package_name_pattern and not fnmatch.fnmatch(package_name, package_name_pattern):
                continue
            if platforms_pattern:
                t = package_name.split("_", 3)
                if len(t) != 3 or not fnmatch.fnmatch(t[2], platforms_pattern):
                    continue
            package_map[package_name] = url

        fmt = "%-40s %s"
        print(fmt % ("Package Name", "Url"))
        print(fmt % ("------------", "---"))
        for package_name in sorted(package_map.keys()):
            url = package_map[package_name]
            print(fmt % (package_name, url))
    except SystemExit:
        raise
    except utils.SSMExitException, detail:
        utils.print_exit(detail)
    except Exception, detail:
        if globls.debug:
            traceback.print_exc()
        utils.print_exit("error: operation failed")
    sys.exit(0)
