#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ssm_subscribe.py

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

"""Provides the 'subscribe' subcommand.
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

SSM_PROFILE_STAMP_START = "# -- ssm profile/login start -- automatically added"
SSM_PROFILE_STAMP_END = "# -- ssm profile/login end -- automatically added"
SSM_PROFILE_TEMPLATE = """
%s
if [ -r {0} ]; then
    . {0}
fi
%s
""" % (SSM_PROFILE_STAMP_START, SSM_PROFILE_STAMP_END)
SSM_LOGIN_TEMPLATE = """
%s
if ( -r {0} ) then
    source {0}
endif
%s
""" % (SSM_PROFILE_STAMP_START, SSM_PROFILE_STAMP_END)

def print_usage():
    print("""\
usage: ssm subscribe [options] [required]
       ssm subscribe -h|--help

Update shell startup profiles to automatically configure access to
a domain. This operation is often unnecessary if a system
administrator has already configured the system.

Required:
-d <path>       Path of the domain to use at login.

Options:
--user|--system Configure the user or system (admin only)
                profile files. Default is --user.
                    
Miscellaneous options:
--debug         Enable debugging.
--force         Force operation.
--verbose       Enable verbose output.
-y|--yes        Automatically respond 'y' to prompts.""")

if __name__ == "__main__":
    try:
        domain_home = None
        subscribe_type = "user"

        args = sys.argv[1:]
        while args:
            arg = args.pop(0)
            if arg in ["-h", "--help"]:
                print_usage()
                sys.exit(0)

            elif arg in ["-d", "--domainHome"] and args:
                domain_home = args.pop(0)
            elif arg in ["--system"]:
                subscribe_type = "system"
            elif arg in ["--user"]:
                subscribe_type = "user"

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

    if not domain_home:
        utils.print_exit("error: missing a domain home")
    if not subscribe_type:
        utils.print_exit("error: must specify --user or --system")

    try:
        login_path, profile_path = utils.get_profile_paths(subscribe_type)
        ssmd_dir_path, ssmd_login_path, ssmd_profile_path = utils.get_ssmd_profile_paths(subscribe_type)

        # update profile/login files
        if SSM_PROFILE_STAMP_END not in utils.loads(login_path):
            open(login_path, "a+").write(SSM_LOGIN_TEMPLATE.format(ssmd_login_path))
        if SSM_PROFILE_STAMP_END not in utils.loads(profile_path):
            open(profile_path, "a+").write(SSM_PROFILE_TEMPLATE.format(ssmd_profile_path))

        # point to domain-specific profile/login files
        if not os.path.isdir(ssmd_dir_path):
            utils.makedirs(ssmd_dir_path)
        if not globls.force and not globls.auto_yes \
                and (os.path.exists(ssmd_login_path) or os.path.exists(ssmd_profile_path)):
            # should unsubscribe first!
            if utils.prompt("Overwrite the current subscription (y/n)?").lower() not in ["y"]:
                utils.print_exit("operation aborted")
                
        utils.remove(ssmd_login_path)
        utils.remove(ssmd_profile_path)
        utils.symlink(os.path.join(domain_home, "etc/ssm.d/login"), ssmd_login_path)
        utils.symlink(os.path.join(domain_home, "etc/ssm.d/profile"), ssmd_profile_path)
    except SystemExit:
        raise
    except utils.SSMExitException, detail:
        utils.print_exit(detail)
    except:
        if globls.debug:
            traceback.print_exc()
        utils.print_exit("error: operation failed")
    sys.exit(0)
