#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ssm/constants.py

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

"""Provides constants. Does not import any non-system packages.
"""

# system imports
import os.path
import sys

VERSION_STRING = "10.151"
VERSION = tuple(VERSION_STRING.split("."))

PROG_NAME = os.path.basename(sys.argv[0])
SSM_PKG_DIR = os.path.normpath(os.path.realpath(sys.argv[0])+"/../../../..")

DEFAULT_DOMAIN_LABEL = "No label"
DEFAULT_REPO_SOURCE = "http://ssm/main"

MSG_INCOMPATIBLE_DOMAIN = "error: one or more incompatible domains"
