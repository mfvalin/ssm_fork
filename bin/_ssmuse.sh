#! /bin/bash
#
# _ssmuse.sh

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

# iterate through ssm_domain_base_paths to find an object at
# rel_path
_match_domain_base() {
	local rel_path=$1
	local base_path
	local ssm_domain_base

	for base_path in "${ssm_domain_base_paths[@]}"; do
		if [ -d "${base_path}/${rel_path}" ]; then
			echo "${base_path}"
			return
		fi
	done
	echo ""
}

# echo suitable for eval
_eecho() {
	echo "echo \"$1\" ;"
}

# unify call to ssm_env_config.sh/ssm_generateconfig.sh
_ssm_env_config() {
	local shell_type="$1" domain_home="$2"
	local package_name

	# shift; following code depends on this
	shift 2

	if [ $# -eq 0 ]; then
		if [ -f "${domain_home}/lib/ssm.d/ssm_env_config.sh" ]; then
			"${domain_home}/lib/ssm.d/ssm_env_config.sh" ${shell_type}
		elif [ -f "${domain_home}/lib/ssm.d/ssm_generateenvconfig.sh" ]; then
			"${domain_home}/lib/ssm.d/ssm_generateenvconfig.sh" prepend ${shell_type} "${domain_home}"
		else
			_eecho "error: no domain at (${domain_home})"
		fi
	else
		package_name=$1
		if [ -f "${domain_home}/lib/ssm.d/ssm_env_config.sh" ]; then
			"${domain_home}/lib/ssm.d/ssm_env_config.sh" ${shell_type} "${package_name}"
		elif [ -f "${domain_home}/lib/ssm.d/ssm_generateenvconfig.sh" ]; then
			"${domain_home}/lib/ssm.d/ssm_generateenvconfig.sh" prepend ${shell_type} "${domain_home}" "${package_name}"
		else
			_eecho "error: no package at (${domain_home}/${package_name})"
		fi
	fi
}

# get platforms for domain
get_platforms() {
	local domain_home="$1"

	if [ -f "${domain_home}/lib/ssm.d/ssm_platforms.sh" ]; then
		"${domain_home}/lib/ssm.d/ssm_platforms.sh" "${domain_home}"
	else
		# pre v9.0
		(. "${domain_home}/lib/ssm.d/ssm_lib.sh"; getSystemPlatforms "${domain_home}")
	fi
}

# resolve package home to a fully specified path
resolve_package_home() {
	local package_home="$1"
	local domain_home package_home2 package_name package_platform
	local platform platforms

	if [ -d "${package_home}" ]; then
		domain_home=`(cd "${package_home}/.."; echo $PWD)`
		package_name=`basename "${package_home}"`
		package_home="${domain_home}/${package_name}"
	else
		domain_home=`dirname "${package_home}"`
		package_name=`basename "${package_home}"`
		package_platform="${package_name#*_*_}"
		package_home="${domain_home}/${package_name}"

		if [ "${package_platform}" == "${package_name}" ]; then
			# does not have platform component
			platforms=`get_platforms "${domain_home}"`
			for platform in ${platforms}; do
				package_home2="${domain_home}/${package_name}_${platform}"
				if [ -d "${package_home2}" ]; then
					echo "${package_home2}"
					return
				fi
			done
		fi
	fi
	echo "${package_home}"
}

# Note
# * use return rather than exit to stop processing
# * use break to interrupt processing for item
# * use function to allow for return call
_ssmuse() {
	local base_path
	local domain_home package_home filename
	local arg text

	text=()
	while [ $# -gt 0 ]; do
		arg=$1; shift 1
		case ${arg} in
		"-d")
			domain_home=$1; shift 1
			if [[ "${domain_home}" = /* || "${domain_home}" = ./* || "${domain_home}" = ../* || "${domain_home}" = . ]]; then
				# is a path, not a domain relative to SSM_DOMAIN_BASE
				:
			else
				if [ "${SSM_DOMAIN_BASE}" = "" ]; then
					_eecho "error: missing SSM_DOMAIN_BASE"
					return
				fi
				base_path=`_match_domain_base "${domain_home}"`
				if [ "${base_path}" = "" ]; then
					_eecho "error: no match for domain (${domain_home})"
					break
				fi
				domain_home="${base_path}/${domain_home}"
			fi
			if [ -d "${domain_home}" ]; then
				text[${#text[@]}]=`_ssm_env_config ${shell_type} "${domain_home}"`
			else
				_eecho "error: cannot find domain (${domain_home})"
			fi
			;;
		"-p")
			package_home=$1; shift 1
			if [[ "${package_home}" = /* || "${package_home}" = ./* || "${package_home}" = ../* ]]; then
				# is a path, not a package name relative to SSM_DOMAIN_BASE
				:
			else
				if [ "${SSM_DOMAIN_BASE}" = "" ]; then
					_eecho "error: missing SSM_DOMAIN_BASE"
					return
				fi
				base_path=`_match_domain_base "${package_home}"`
				if [ "${base_path}" = "" ]; then
					base_path="${ssm_domain_base_paths[0]}"
					if [ "${base_path}" = "" ]; then
						_eecho "error: no match for package (${package_home})"
						break
					fi
				fi
				package_home="${base_path}/${package_home}"
			fi
			package_home=`resolve_package_home "${package_home}"`
			#if [ "${arg}" = "-pp" ]; then
				#package_home=`resolve_package_home "${package_home}"`
			#fi
			if [ -d "${package_home}" ]; then
				domain_home="${package_home%/*}"
				package_name="${package_home##*/}"
				text[${#text[@]}]=`_ssm_env_config ${shell_type} "${domain_home}" "${package_name}"`
			else
				_eecho "error: cannot find package (${package_home})"
			fi
			;;
		"-f")
			filename="$1"; shift 1
			if [[ "${filename}" = /* || "${filename}" = ./* || "${filename}" = ../* ]]; then
				# actual path, not relative to SSM_DOMAIN_BASE
				:
			else
				if [ "${SSM_DOMAIN_BASE}" = "" ]; then
					_eecho "error: missing SSM_DOMAIN_BASE"
					return
				fi
				base_path=`_match_domain_base "${filename}"`
				if [ "${base_path}" = "" ]; then
					_eecho "error: no match for filename (${filename})"
					break
				fi
				filename="${base_path}/${filename}"
			fi
			if [ -r "${filename}" ]; then
				# source works for sh and csh
				text[${#text[@]}]="

source '${filename}' ;
"
			else
				_eecho "error: cannot read file at (${filename})"
			fi
			;;
		*)
			_eecho "error: unexpected parameter (${arg})"
			return
			;;
		esac
	done

	echo "${text[@]}"
}

# if available, call a cleanpath script to clean up (remove useless
# duplicates) a :-separated value (e.g., PATH, LD_LIBRARY_PATH,
# etc.)
_cleanpaths() {
        local libdir cleanpath

        cleanpath=echo

        libdir=$(cd `dirname $0`/../lib/ssm.d; pwd)
        if [ -d "${libdir}" ]; then
                if [ "${BASH_VERSINFO[0]}" != "" -a ${BASH_VERSINFO[0]} -ge 4 ]; then
                        cleanpath="${libdir}/ssm_cleanpath.sh"
                elif [ -x /bin/ksh93 ]; then
                        cleanpath="${libdir}/ssm_cleanpath.ksh" 
                fi
        fi

	case ${shell_type} in
	sh)
		echo "
export LD_LIBRARY_PATH=\"\`${cleanpath} \$LD_LIBRARY_PATH\`\" ;
export LIBPATH=\"\`${cleanpath} \$LIBPATH\`\" ;
export MANPATH=\"\`${cleanpath} \$MANPATH\`\" ;
export PATH=\"\`${cleanpath} \$PATH\`\" ;
export PYTHONPATH=\"\`${cleanpath} \$PYTHONPATH\`\" ;
export SSM_INCLUDE_PATH=\"\`${cleanpath} \$SSM_INCLUDE_PATH\`\" ;
export TCL_LIBRARY=\"\`${cleanpath} \$TCL_LIBRARY\`\" ;
"
		;;
	csh)
		echo "
setenv LD_LIBRARY_PATH \"\`${cleanpath} --dropemptylib \$LD_LIBRARY_PATH\`\" ;
setenv LIBPATH \"\`${cleanpath} --dropemptylib \$LIBPATH\`\" ;
setenv MANPATH \"\`${cleanpath} \$MANPATH\`\" ;
setenv PATH \"\`${cleanpath} \$PATH\`\" ;
setenv PYTHONPATH \"\`${cleanpath} \$PYTHONPATH\`\" ;
setenv SSM_INCLUDE_PATH \"\`${cleanpath} \$SSM_INCLUDE_PATH\`\" ;
setenv TCL_LIBRARY \"\`${cleanpath} \$TCL_LIBRARY\`\" ;
"
		;;
	*)
		echo "# cannot find/use cleanpath script"
		;;
	esac
}

#usage: ssmuse [--noeval] <shell_type> {-d <domain_home>}|{-p <package_home>} [...]
print_usage() {
	_eecho "\
usage: ssmuse-sh  [--noeval] {-d <path>}|{-p <path>} [...]
       ssmuse-csh [--noeval] {-d <path>}|{-p <path>} [...]
                   -h|--help

Generate and eval commands for configuring a shell environment from
one or more domains and/or packages. Domains and packages are
specified using paths. Absolute paths are not resolved; relative
paths are resolved using the SSM_DOMAIN_BASE environment variable.
SSM_DOMAIN_BASE is a list of :-separated paths used as a prefix to
relative domain and package paths.

sh:
	\$ . ssmuse-sh -d /opt/ssm
and for csh:
	% eval \`ssmuse-csh -d /opt/ssm\`

Where:
--noeval	Do not evaluate configuration commands.
-d <path>	Path of the domain.
-p <path>	Path of the package (within a domain); also supports
			partial path (e.g., abc_1.0 instead of abc_1.0_all),
			selecting the package best matching the platform.
		
To see what is being generated, for sh do:
    \$ ssmuse-sh --noeval -d /opt/ssm
and for csh:
    \$ ssmuse-csh --noeval -d /opt/ssm"
}

domain_home=""
package_home=""
shell_type=""
ssm_domain_base_paths=(`IFS=':'; echo "${SSM_DOMAIN_BASE}"`)

if [ $# -lt 1 ]; then
	print_usage
	exit 1
elif [ $1 = "-h" -o $1 = "--help" ]; then
	print_usage
	exit 0
fi

if [ $# -lt 1 ]; then
	_eecho "error: missing shell type"
	exit 1
fi

shell_type=$1; shift 1

case "${shell_type}" in
sh|csh)
	;;
*)
	_eecho "error: bad shell type"
	exit 1
esac

_eecho "warning: deprecated; use new ssmuse v1 and after"
_ssmuse "${@}"
_cleanpaths
