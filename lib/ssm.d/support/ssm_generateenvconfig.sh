#! /bin/bash
#
# ssm_generatenvconfig.sh
#
# converts call to use ssm_env_config.sh

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

self_dir=`dirname ${0}`
self_domain_home=`(cd "${self_dir}/../.."; pwd)`
shift 1 # ignore order
shell_type=$1; shift 1
shift 1 # ignore domain (it is now implicit)
exec "${self_domain_home}/lib/ssm.d/ssm_env_config.sh" ${shell_type} "${@}"
