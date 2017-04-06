#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ssm_find.py

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

"""Provides the 'find' subcommand.
"""

# system imports
import fnmatch
import os
import os.path
import sys
import traceback

#
from ssm import globls
from ssm import utils
from ssm.domain import Domain
from ssm.package import Package

def find_domains(base_path, max_depth, hidden=False):
    """Find domain_homes under base_path.
    """
    domain_homes = []
    if Domain(base_path).is_domain():
        domain_homes.append(base_path)
    else:
        path_slash_count = base_path.count("/")
        for root, dirnames, _ in os.walk(base_path, followlinks=True):
            #print root.count("/"),path_slash_count, max_depth
            if root.count("/")-path_slash_count >= max_depth:
                del dirnames[:]
                continue
            for dirname in dirnames[:]:
                if dirname.startswith(".") and not hidden:
                    dirnames.remove(dirname)
                    continue
                if 0 and os.path.islink(os.path.join(root, dirname)):
                    # don't follow symlinks to domain homes!
                    dirnames.remove(dirname)
                    continue
                domain_home = os.path.join(root, dirname)
                if Domain(domain_home).is_domain():
                    domain_homes.append(domain_home)
                    dirnames.remove(dirname)
    return domain_homes

def find_in_bin(domain_home, term):
    return __find_in_component(domain_home, "bin", term)
    
def find_in_lib(domain_home, term):
    return __find_in_component(domain_home, "lib", term)

def find_name(domain_home, term, max_depth=10):
    return __find_in_path(domain_home, term, max_depth)

def match_domains(domain_homes, term):
    found_map = {}
    for domain_home in domain_homes:
        if fnmatch.fnmatch(os.path.basename(domain_home), term):
            found = [domain_home]
            found_map[domain_home] = found
    return found_map

#
# helpers
#
def __find_in_component(domain_home, prefix, term):
    """Find by "component" in domain packages, e.g.,
        x_1.0_all/bin where bin is the component
    """
    paths = []
    for package_name in Domain(domain_home).get_package_names():
        paths.extend(__find_in_path(os.path.join(domain_home, package_name, prefix), term))
    return paths

def __find_in_path(path, term, max_depth=10):
    """Find file under path.
    """
    found = []
    path_slash_count = path.count("/")
    for root, dirnames, filenames in os.walk(path):
        if max_depth and root.count("/")-path_slash_count >= max_depth:
            del dirnames[:]
            continue

        # TODO: limit to file|dir|both
        filenames = fnmatch.filter(filenames, term)
        found.extend([os.path.join(root, filename) for filename in filenames])
        dirnames = [dirname+"/" for dirname in dirnames]
        dirnames = fnmatch.filter(dirnames, term)
        found.extend([os.path.join(root, dirname) for dirname in dirnames])
    return sorted(found)

def print_usage():
    print("""\
usage: ssm find [options] <term> [<path> [...]]
       ssm find -h|--help

Search for <term> within a domain found at or below <path>. Prints
domain paths and the matches found in them.

Where:
<path> [...]    Path(s) under which to search. This may be a domain
                path. Default is $SSM_DOMAIN_BASE or
                $SSM_DOMAIN_HOME.
<term>          Term (e.g., filename, dirname, package name) to
                find. Wildcards (* and ?) are supported.

Options:
--depth <int>   Maximum depth below <path> to search for domains.
                For 'name' type only. Default is 4.
--long          Provides domain and package name info for each item.
--type <type>   Criteria for matching <term>:
                bin - match file under domain bin/ directory
                domain - match domain name
                lib - match file under domain lib/ directory
                name - match filename/dirname
                package - match package name; this is default

Miscellaneous options:
--debug             Enable debugging.""")

if __name__ == "__main__":
    try:
        base_paths = os.environ.get("SSM_DOMAIN_BASE") \
            or os.environ.get("SSM_DOMAIN_HOME") \
            or os.environ.get("SSMDOMAINHOME") \
            or os.environ.get("SSM_SYSTEM_DOMAIN_HOME") \
            or os.environ.get("SSM_SYSTEM__DOMAIN_HOME") \
            or os.environ.get("SSM_USER_DOMAIN_HOME") \
            or os.environ.get("SSMUSERDOMAINHOME") \
            or ""
        base_paths = base_paths.split(":")
        depth = 4
        find_type = "package"
        output_type = "summary"
        term = None

        args = sys.argv[1:]
        while args:
            arg = args.pop(0)
            if arg in ["-h", "--help"]:
                print_usage()
                sys.exit(0)

            elif arg in ["--depth"] and args:
                depth = int(args.pop(0))
            elif arg in ["--long", "-l"]:
                output_type = "long"
            elif arg in ["--type"] and args:
                find_type = args.pop(0)

            elif arg in ["--debug"]:
                globls.debug = True
            else:
                term = arg
                if args:
                    base_paths = args[:]
                    args = []
                break
    except SystemExit:
        raise
    except:
        if globls.debug:
            traceback.print_exc()
        utils.print_exit("error: bad/missing argument(s)")

    if term == None:
        utils.print_exit("error: bad/missing argument(s)")
    if base_paths == [""]:
        utils.print_exit("error: no place to search")

    #print "find_type (%s)" % (find_type,)
    #print "term (%s)" % (term,)
    #print "base_paths (%s)" % (base_paths,)

    if find_type == "package":
        if not ("*" in term or "?" in term or "_" in term):
            term += "_*"

    try:
        _, ncols = utils.get_terminal_size()
    except:
        ncols = 80

    for base_path in base_paths:
        try:
            domain_homes = sorted(find_domains(base_path, depth))
            if find_type == "domain" and output_type == "summary":
                fmt = "%-30s"
                lines = domain_homes
                utils.print_columns(lines, None, ncols)
                if lines:
                    print
            else:
                for domain_home in domain_homes:
                    domain = Domain(domain_home)
                    package_names = []
                    paths = []

                    # get package_names or paths; force output_type if necessary
                    if find_type in ["bin", "domain", "lib", "name"]:
                        output_type = "long"
                        if find_type == "bin":
                            paths = find_in_bin(domain_home, term)
                        elif find_type == "domain":
                            paths = domain_homes
                        elif find_type == "lib":
                            paths = find_in_lib(domain_home, term)
                        elif find_type == "name":
                            paths = find_name(domain_home, term, depth)
                    elif find_type == "package":
                        package_names = domain.get_package_names(term)
                        if output_type == "long":
                            paths = sorted([os.path.join(domain_home, name) for name in package_names])
                    else:
                        utils.print_exit("error: unknown find type")

                    if package_names or paths:
                        print "==========  %s (%s)  ==========" % (domain_home, domain.get_label())

                    if output_type == "long":
                        for path in paths:
                            if find_type == "package":
                                package_name = path[len(domain_home)+1:].split("/", 1)[0]
                                print "%s" % (package_name,)
                            else:
                                print "%s" % (path,)
                        if paths:
                            print
                    elif output_type == "summary":
                        fmt = "%-2s %-30s"
                        lines = []
                        published_platforms = domain.get_published_platforms()
                        for package_name in package_names:
                            package = Package(domain, package_name)
                            if package.platform in published_platforms:
                                for publish_platform in published_platforms:
                                    state = domain.get_package_state(package_name, publish_platform)
                                    if state in ["", "I"]:
                                        continue
                                    if package.platform == publish_platform:
                                        lines.append(fmt % (state, package_name))
                                    else:
                                        lines.append(fmt % (state, "%s (%s)" % (package_name, publish_platform)))
                            else:
                                state = domain.get_package_state(package_name, None)
                                lines.append(fmt % (state, package_name))
                        utils.print_columns(lines, None, ncols)
                        if lines:
                            print
        except SystemExit:
            raise
        except utils.SSMExitException, detail:
            utils.print_exit(detail)
        except:
            if globls.debug:
                traceback.print_exc()
            utils.print_exit("error: operation failed")
    sys.exit(0)
