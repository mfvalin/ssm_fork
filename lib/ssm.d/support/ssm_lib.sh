#! /bin/bash
#
# ssm_lib.sh
#

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

#
# for pre v9.0 compatiblity (deprecated)
#
getAllDomainHomes() {
	local domain_home=$1
	
	${domain_home}/lib/ssm.d/ssm_subdomains.sh "${domain_home}"
}

getDomainVersion() {
	local domain_home=$1

	if [ -r "${domain_home}/etc/ssm.d/version" ]; then
		cat "${domain_home}/etc/ssm.d/version"
	else
		echo 0
	fi
}

getInstalledDir() {
	local domainHome=$1

	echo "${domainHome}/etc/ssm.d/installed"
}

getPackageVersions() {
# return package versions under given directory
	local dirPath=$1
	local shortPackageName=$2

	local packageName
	local version
	local versions=""

	# match for name
	for packageName in `\ls -1 ${dirPath}`; do
		version=${packageName#${shortPackageName}_}
		if [ "${version}" != "${packageName}" ]; then
			version=${version%_*}
			versions="${versions} ${version}"
		fi
	done

	echo ${versions}
}

getSystemPlatforms() {
	local domain_home=$1
	
	${domain_home}/lib/ssm.d/ssm_platforms.sh "${domain_home}"
}

matchPackagePlatform() {
# match a package (name_version) with a supported platform under given directory
	local dirPath=$1
	local packageName=$2
	local platforms=$3

	local newPackageName=""
	local platform

	for platform in ${platforms}; do
	if [ -e "${dirPath}/${packageName}_${platform}" ]; then
		newPackageName="${packageName}_${platform}"
		break
	fi
	done

	echo ${newPackageName}
}
