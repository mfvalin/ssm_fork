#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ssm_cloned.py

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

"""Provides the 'cloned' subcommand.
"""

# system imports
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
usage: ssm cloned [options] <src> <dst>
       ssm cloned -h|--help

Clone an existing domain. Default is to clone installed and
published packages.

Required:
<dst>           Path of a new domain.
<src>           Path of an existing domain to be cloned.

Options:
-L <string>     Descriptive text for the new domain.
-s <domain>     Alternate source for installed packages from which to
                publish. Overrides src domain used for publishing;
                domain must contain the package.
-u <url>        URL of an alternate repository from which to obtain
                packages.
--domain        Clone domain files: support, subdomains, sources.
--installed     Clone only installed packages.
--published     Clone published packages.

Miscellaneous options:
--debug         Enable debugging.
--force         Force operation.
--verbose       Enable verbose output.
-y|--yes        Automatically respond 'y' to prompts.""")

if __name__ == "__main__":
    try:
        src_domain_home = None
        dst_domain_home = None
        alt_src_domain_home = None
        clone_domain = False
        clone_installed = False
        clone_published = False
        repo_url = None
        republish = False
        label = DEFAULT_DOMAIN_LABEL

        args = sys.argv[1:]
        while args:
            arg = args.pop(0)
            if arg in ["-h", "--help"]:
                print_usage()
                sys.exit(0)

            elif arg in ["--domain"]:
                clone_domain = True
            elif arg in ["--installed"]:
                clone_installed = True
            elif arg in ["--published"]:
                clone_published = True
            elif arg == "-L" and args:
                label = args.pop(0)
            elif arg == ["--republish"]:
                republish = True
            elif arg == "-s" and args:
                alt_src_domain_home = args.pop(0)
            elif arg in ["-u"] and args:
                repo_url = args.pop(0)

            elif arg in ["--debug"]:
                globls.debug = True
            elif arg in ["--force"]:
                globls.force = True
            elif arg in ["--verbose"]:
                globls.verbose = True
            elif arg in ["-y", "--yes"]:
                globls.auto_yes = True
            elif len(args) == 1:
                src_domain_home = arg
                dst_domain_home = args.pop(0)
            else:
                raise Exception()
    except SystemExit:
        raise
    except:
        if globls.debug:
            traceback.print_exc()
        utils.print_exit("error: bad/missing argument(s)")

    if src_domain_home == dst_domain_home == None:
        utils.print_exit("error: missing argument(s)")

    if not clone_domain and not clone_installed and not clone_published:
        clone_domain = clone_installed = clone_published = True

    try:
        src_domain = Domain(src_domain_home)
        dst_domain = Domain(dst_domain_home)
        alt_src_domain = alt_src_domain_home and Domain(alt_src_domain_home)
        if not src_domain.is_compatible():
            utils.print_exit(MSG_INCOMPATIBLE_DOMAIN)
        if alt_src_domain and not alt_src_domain.is_compatible():
            utils.print_exit(MSG_INCOMPATIBLE_DOMAIN)

        sources = repo_url or (alt_src_domain or src_domain).get_sources()
        repo = Repository(sources)

        if clone_domain:
            # create new domain
            utils.print_verbose("creating new domain (%s)" % dst_domain_home)
            dst_domain.create(label, sources)

            # populating subdomains
            utils.print_verbose("setting subdomains")
            dst_domain.set_subdomains(src_domain.get_subdomains())

        if clone_installed:
            # populate with installed
            src_installed_map = src_domain.get_packages_with_state("installed")
            for src_package_name, src_package in src_installed_map.items():
                utils.print_verbose("installing package (%s)" % src_package_name)
                tarf = repo.get(src_package_name)
                if tarf == None:
                    utils.print_warning("warning: could not find package (%s)" % src_package_name)
                dst_package = Package(dst_domain, src_package_name)
                try:
                    dst_package.install(tarf, None, None, False)
                except:
                    utils.print_warning("warning: could not install package (%s)" % src_package_name)

        if clone_published:
            # populate with published
            for publish_platform in src_domain.get_published_platforms():
                src_published_map = src_domain.get_packages_with_state("published", publish_platform)
                for src_package_name, src_package in src_published_map.items():
                    if alt_src_domain:
                        # publish from alt src domain
                        src_package = Package(alt_src_domain, src_package_name)
                        utils.print_verbose("publishing package (%s) from alt src domain (%s)" % (src_package_name, alt_src_domain.path))
                        if not src_package.exists():
                            utils.print_warning("warning: cannot find package in alternate source domain")
                            continue
                    elif src_package.domain.path == src_domain.path:
                        # same domain
                        utils.print_verbose("publishing package (%s) from src domain (%s)" % (src_package_name, src_domain.path))
                        dst_package = Package(dst_domain, src_package_name)
                    else:
                        # other domain
                        utils.print_verbose("publishing package (%s) from alt src domain (%s)" % (src_package_name, src_package.domain.path))
                        dst_package = src_package

                    if dst_domain.is_published(src_package_name, publish_platform):
                        if republish:
                            dst_domain.unpublish_package(dst_package, published_platform)
                        else:
                            utils.print_warning("warning: skipping published package (%s)" % (src_package_name,))
                            continue
                    dst_domain.publish_package(dst_package, publish_platform)

        # set frozen?
        if src_domain.is_frozen():
            utils.print_verbose("freezing domain (%s)" % dst_domain_home)
            dst_domain.freeze()
    except SystemExit:
        raise
    except utils.SSMExitException, detail:
        utils.print_exit(detail)
    except:
        if globls.debug:
            traceback.print_exc()
        utils.print_exit("error: operation failed")
    sys.exit(0)
