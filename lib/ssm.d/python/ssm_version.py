#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ssm_version.py

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

"""Provides the 'version' subcommand.
"""

# system imports
import sys
import traceback

#
from ssm.constants import *
from ssm import globls
from ssm import utils

def print_usage():
    print("""\
usage: ssm version [options]
       ssm version -h|--help

Show the SSM version.

Miscellaneous options:
--debug         Enable debugging.""")

if __name__ == "__main__":
    try:
        args = sys.argv[1:]
        while args:
            arg = args.pop(0)
            if arg in ["-h", "--help"]:
                print_usage()
                sys.exit(0)

            elif arg in ["--debug"]:
                globls.debug = True
            elif arg:
                raise Exception()
    except SystemExit:
        raise
    except:
        if globls.debug:
            traceback.print_exc()
        utils.print_exit("error: bad/missing argument(s)")
    
    print VERSION_STRING
