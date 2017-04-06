#! /bin/bash
#
# ssm_domainhomes.sh

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

# new method for v9
get_subdomain_homes_from_file() {
	local domain_home path

	domain_home=$1
	path="${domain_home}/etc/ssm.d/subdomains"

	if [ -r "${path}" ]; then
		cat "${path}"
	fi
}

# follow subdomain_home and append self
follow_subdomain_homes() {
	local domain_home

	domain_home=$1

	if [ -d "${domain_home}/etc/ssm.d/domainHomes" ]; then
		# pre v9.0
		lines=`. "${domain_home}/lib/ssm.d/ssm_lib.sh"; getAllDomainHomes "${domain_home}" 0` 2> /dev/null
	else
		#lines=(`${0} "${domain_home}"`)
		lines=`"${domain_home}/lib/ssm.d/ssm_subdomains.sh"` 2> /dev/null
	fi
	echo "${lines}"
}

# gets own subdomain homes and calls out to subdomains to resolve
# their own subdomains
get_all_subdomain_homes() {
	local domain_home level all
	local subdomain_home subdomain_homes
	local section

	domain_home=$1
	level=$2
	all=()

	((level=level+1))
	if [ ${level} -ge 10 ]; then
		return
	fi

	OIFS="${IFS}"; IFS="${NEWLINE}"
	subdomain_homes=(`get_subdomain_homes_from_file "${domain_home}" ${level}`)
	IFS="${OIFS}"
	for subdomain_home in "${subdomain_homes[@]}"; do
		if [ "${subdomain_home}" != "" ]; then
			section=`follow_subdomain_homes "${subdomain_home}"`
			if [ "${section}" != "" ]; then
				all[${#all[@]}]="${section}"
			fi
		fi
		all[${#all[@]}]="${subdomain_home}"
	done
	OFS="${IFS}"; IFS="${NEWLINE}"
	echo "${all[*]}"
	IFS="${OIFS}"
}

print_usage() {
	echo "\
usage: ssm_subdomains.sh [<level>]

Warning: do not call this program directly or apart from within a
domain.

Recursively find subdomain homes from containing domain and return
an ordered list useful for proper sourcing.

Where:
<level>		Depth search has gone."
}

#
# main
#
NEWLINE='
'

level=0
if [ $# -gt 0 ]; then
	case $1 in
	-h|--help)
		print_usage
		exit 0
		;;
	*)
		level=$1; shift 1
		;;
	esac
fi

self_dir=`dirname $0`
self_dir=`(cd "${self_dir}"; pwd)`
self_domain_home=`(cd "${self_dir}/../.."; pwd)`
domain_home="${self_domain_home}"

if [ ! -d "${self_domain_home}/lib/ssm.d" ]; then
	echo "error: command not found in a domain"
	exit 1
fi

get_all_subdomain_homes "${self_domain_home}" ${level}
