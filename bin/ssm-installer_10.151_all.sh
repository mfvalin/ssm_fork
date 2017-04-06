#! /bin/bash
#
# ssm-installer
#
# Basic utility to install ssm.

# GPL--start
# This file is part of ssm (Simple Software Manager)
# Copyright (C) 2005-2010 Environment/Environnement Canada
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

printUsage() {
	echo "\
usage: ssm-installer.sh [options]

Options:
    -h|--help
    --chownDomainHome
        Change ownership of the domain home to current user.
        Default:
            ${changeDomainHome}
    --defaultRepositorySource <string>
        The default repository source that will be used
        by ssm unless overridden. This will be put into
        ${domain_home}/etc/ssm.d/sources.list .
    -d|--domainHome <path>
        Domain home to contain the ssm package and
        configuration info for other domain homes.
        Default:
            ${domain_home}
    -G|--groupName <name>
        Owner (group) of the domain home.
        Default:
            ${groupname}
    --installAndPublishPython
        Install and publish required python package
        under ssm. This is typically done on systems on
        which python is not already available.
        Default:
            ${installAndPublishPython}
    --L|--label <label>
        The label to associate with the domain.
    --pythonPackageName <name>
        The python package name to install and publish.
        Default:
            ${pythonPackageName}
    --pythonRepositoryUrl <url>
        Repository URL to use to access python package
        to install and publish.
        Default:
            ${pythonRepositoryUrl}
    --ssmPackageName <name>
        Name of the ssm package to be installed.
        Default:
            ${ssmPackageName}
    --ssmRepositoryUrl <name>
        Repository URL to use to access the ssm package.
        Default:
            ${ssmRepositoryUrl}
    --system
        Subscribe the system to the domain being
        created.
        Default:
            ${subscribeSystem}
    --user
        Subscribe the user to the domain being created.
        Default:
            ${subscribeUser}
    -U|--userName <name>
        Owner (user) of the domain home directory.
        Default:
            ${username}
    --debug
        Print debugging informatoin.
    --force
        Force operation. Do not ask questions.
    -v|--verbose
        Print progress information.

Note: This program is not intended to be run as root user.
      Authorization will be requested if required.
"
}

check_for_wget() {
	${WGET} --help 2>1 > /dev/null
	if [ $? -ne 0 ]; then
		echo "Cannot find wget. Install it or use the local filesystem."
		exit -1
	fi
}

download_package() {
	local package_name=$1
	local package_url=$2

	if [ "`echo ${package_url} | ${GREP} -E '^http:|^ftp:'`" != "" ]; then
		echo "Loading ${package_name} from repository ${package_url}."
		check_for_wget
		${WGET} ${package_url} 2>1 > /dev/null
	else
		echo "Loading ${package_name} from local."
		${CP} ${package_url} ${tmpDir}
	fi
}

#
# main
#

# initial settings
chownDomainHome="no"
debug="no"
sources="http://scaweb.sca.uqam.ca/armnlib/repository/"
domain_home="$(pwd -P)"
groupname="ssm"
force="no"
label="Default system domain"
mkdirMode="0755"
pythonExec="python"
subscribeSystem="no"
subscribeUser="no"
tarVerboseFlag=""
uid=`id`
uid=${uid##uid=}
uid=${uid%%\(*}
username="ssm"
verbose="no"
whoami="`whoami`"

ssmPackageName="ssm_10.151_all"
ssmRepositoryUrl="${sources}"

installAndPublishPython="no"
pythonPackageName="python_2.3.5_linux24-i386"
pythonRepositoryUrl="${sources}"

CP=\cp
GREP=\grep
MKDIR=\mkdir
printfExec=\printf
RM=\rm
SHELL=/bin/bash
SU=\su
WGET=\wget

# parse command line
while [ $# -gt 0 ]; do
	case $1 in
	"--chownDomainHome")
		chownDomainHome="yes"; shift 1
		;;
	"-D"|"--defaultRepositorySource")
		shift 1
		sources="$1"; shift 1
		;;
	"-d"|"--domainHome")
		shift 1
		domain_home="$1"; shift 1
		if [ "${domain_home:0:1}" != "/" ]; then
			domain_home="$PWD/${domain_home}"
		fi
		;;
	"-G"|"--groupName")
		shift 1
		groupname="$1"; shift 1
		;;
	"--installAndPublishPython")
		installAndPublishPython="yes"; shift 1
		;;
	"-L"|"--label")
		shift 1
		label="$1"; shift 1
		;;
	"--pythonPackageName")
		shift 1
		pythonPackageName="$1"; shift 1
		;;
	"--pythonRepositoryUrl")
		shift 1
		pythonRepositoryUrl="$1"; shift 1
		;;
	"--ssmPackageName")
		shift 1
		ssmPackageName="$1"; shift 1
		;;
	"--ssmRepositoryUrl")
		shift 1
		ssmRepositoryUrl="$1"; shift 1
		;;
	"--system")
		subscribeSystem="yes"; shift 1
		;;
	"--user")
		subscribeUser="yes"; shift 1
		;;
	"-U"|"--userName")
		shift 1
		username="$1"; shift 1
		;;
	"--debug")
		debug="yes"; shift 1
		;;
	"--force")
		force="yes"; shift 1
		;;
	"-v"|"--verbose")
		verbose="yes"; shift 1
		tarVerboseFlag="v"
		;;
	"-h"|"--help")
		printUsage
		exit 1
		;;
	*)
		echo "Error: Cannot recognize parameter '$1'"
		echo
		printUsage
		exit 1
	;;
	esac
done

# (re)configure settings based on command line
ssmPackageUrl="${ssmRepositoryUrl}/${ssmPackageName}.ssm"
pythonPackageUrl="${pythonRepositoryUrl}/${pythonPackageName}.ssm"

debugOption=""
if [ ${debug} = "yes" ]; then
	debugOption="--debug"
fi

if [ ${verbose} = "yes" ]; then
	verboseOption="--verbose"
else
	verboseOption=""
fi

#
# main
#

# show settings
echo "                       Domain home: ${domain_home}"
echo "                             Label: ${label}"
echo "         Default repository source: ${sources}"
echo "        Master Domain Owner (user): ${username}"
echo "       Master Domain Owner (group): ${groupname}"
echo "                  Subscribe System: ${subscribeSystem}"
echo "                    Subscribe User: ${subscribeUser}"
echo
echo "                SSM Repository URL: ${ssmRepositoryUrl}"
echo "                  SSM package Name: ${ssmPackageName}"
echo
echo "       Install and publish python?: ${installAndPublishPython}"
echo "             Python repository URL: ${pythonRepositoryUrl}"
echo "               Python package Name: ${pythonPackageName}"
echo
echo "                Running as user/id: ${whoami}/${uid}"
echo

# get authorization (must use sh)
if [ ${force} != "yes" ]; then
	#read "Continue [y/n]? " reply
	${printfExec} "Continue [y/n]? "
	read reply

	if [ ${reply} != "y" -a ${reply} != "Y" ]; then
		echo "Exiting."
		exit 1
	fi
fi

# setup su command
#if [ ${whoami} = "root" ]; then
if [ ${uid} = "0" ]; then
	userSuCmd="${SU} ${username} -c"
else
	userSuCmd="${SHELL} -c"
fi

# create temporary working area
tmpDir="/tmp/ssm-install.$$"
${MKDIR} ${tmpDir}
cd ${tmpDir}

# download ssm
download_package "${ssmPackageName}" "${ssmPackageUrl}"
ssmPackageFilePath="${tmpDir}/${ssmPackageName}.ssm"

# download python
if [ "${installAndPublishPython}" = "yes" ]; then
	download_package "${pythonPackageName}" "${pythonPackageUrl}"
	pythonPackageFilePath="${tmpDir}/${pythonPackageName}.ssm"
fi

# create domain home (need to be root?)
echo "Creating partial domain at ${domain_home} (executing as root)."
if [ ${chownDomainHome} = "yes" ]; then
	${SU} root -c "${MKDIR} -p ${domain_home}; chown ${username}:${groupname} ${domain_home}"
else
	${MKDIR} -p ${domain_home}
fi

# install ssm
echo "Installing ssm."
${userSuCmd} "cd ${domain_home}; gzip -dc ${ssmPackageFilePath} | tar xf${tarVerboseFlag} -"
#echo "Adding ssm to PATH."
#export PATH=${domain_home}/${ssmPackageName}/bin:${PATH}

# install python
if [ "${installAndPublishPython}" = "yes" ]; then
	echo "Installing python."
	${userSuCmd} "cd ${domain_home}; gzip -dc ${pythonPackageFilePath} | tar xf${tarVerboseFlag} -; mv ${pythonPackageName} ${pythonPackageName}_x"
	#echo "Adding python to PATH."
	#export PATH=${domain_home}/${pythonPackageName}_x/bin:${PATH}
	pythonExec="${domain_home}/${pythonPackageName}_x/bin/python"
fi

# configure for ssm executable
SSM="${domain_home}/${ssmPackageName}/bin/ssm"

# create domain using ssm
echo "Creating full domain at ${domain_home}."
export SSM_SYSTEM_DOMAIN_HOME=${domain_home} # special case for installer, force to use domain_home
${userSuCmd} "${SSM} created -d \"${domain_home}\" -L \"${label}\" --sources \"${sources}\" --force ${verboseOption} ${debugOption}"
if [ $? -ne 0 ]; then
	echo "Error: Exiting."
	exit -1
fi

if [ "${subscribeSystem}" = "yes" ]; then
	echo "Subscribing domain with system (executing as root)."
	# hack to compile ssm_subscribe as user, not root
	${userSuCmd} "${SSM} subscribe -h > /dev/null 2>&1"
	${SU} root -c "${SSM} subscribe -d \"${domain_home}\" --system --force ${verboseOption} ${debugOption}"
elif [ "${subscribeUser}" = "yes" ]; then
	echo "Subscribing domain with user."
	${userSuCmd} "${SSM} subscribe -d \"${domain_home}\" --user --force ${verboseOption} ${debugOption}"
fi

# re-install ssm
echo "Reinstalling ssm."
${userSuCmd} "${SSM} install -d \"${domain_home}\" -p \"${ssmPackageName}\" -u \"${ssmRepositoryUrl}\" --force --clobber ${verboseOption} ${debugOption}"
echo "Publishing ssm."
${userSuCmd} "${SSM} publish -d \"${domain_home}\" -p \"${ssmPackageName}\" --force ${verboseOption} ${debugOption}"

# re-install python
if [ "${installAndPublishPython}" = "yes" ]; then
	echo "Reinstalling python."
	${userSuCmd} "${SSM} install -d \"${domain_home}\" -p \"${pythonPackageName}\" -u \"${pythonRepositoryUrl}\" --force --clobber ${verboseOption} ${debugOption}"
	echo "Publishing python."
	${userSuCmd} "${SSM} publish -d \"${domain_home}\" -p \"${pythonPackageName}\" --force ${verboseOption} ${debugOption}"
fi

# clean up
echo "Cleaning up."
cd /tmp
${RM} -rf "${domain_home}/${pythonPackageName}_x"
${RM} -rf "${tmpDir}"
