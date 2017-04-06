#! /bin/bash
#
# ssm_diffd.sh

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

print_usage() {
	echo "usage: ssm diffd [options] <path0> <path1>

Perform a diff on the domains at <path0> and <path1>.

Options:
-r		Recursive diff (for domains).
-u		Unified format.
-y		Side-by-side."
}

trap "rm -f ${out0_path} ${out1_path} > /dev/null 2>&1" ERR EXIT HUP INT TERM QUIT

while [ $# -gt 2 ]; do
	case $1 in
	-r)
		r_opt=-r; shift 1
		;;
	-u)
		u_opt=-u; shift 1
		;;
	-y)
		y_opt=-y; shift 1
		;;
	*)
		break
		;;
	esac
done

if [ $# -ne 2 ]; then
	print_usage
	exit 1
fi

if [ -n "${u_opt}" -a -n "${y_opt}" ]; then
	echo "error: conflicting output style options"
	exit 1
fi

path0=$1; shift 1
path1=$1; shift 1

out0_path=/tmp/ssm_diffd0.$$.out
out1_path=/tmp/ssm_diffd1.$$.out

if [ -z "${r_opt}" ]; then
	ssm listd -d "${path0}" -o name,state | sort > "${out0_path}"
	ssm listd -d "${path1}" -o name,state | sort > "${out1_path}"
	diff ${u_opt} ${y_opt} "${out0_path}" "${out1_path}"
else
	diff ${r_opt} ${u_opt} ${y_opt} "${path0}" "${path1}"
fi

# auto cleanup
exit 0
