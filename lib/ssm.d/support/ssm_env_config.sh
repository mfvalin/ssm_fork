#! /bin/bash
#
# ssm_env_config.sh

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

get_existent_platforms() {
	local domain_home="$1"
	local all_platforms platforms

	all_platforms=(`"${domain_home}/lib/ssm.d/ssm_platforms.sh" "${domain_home}"`)
	platforms=()
	for platform in "${all_platforms[@]}"; do
		if [ -d "${domain_home}/${platform}" ]; then
			platforms[${#platforms[@]}]="${platform}"
		fi
	done
	echo "${platforms[*]}"
}

prepend_path() {
	local newval="$1" oldvals="$2"
	local newvals

	if [ ! -e "${newval}" ]; then
		echo "${oldvals}"
	elif [ -z "${oldvals}" ]; then
		echo "${newval}"
	else
		newvals="${newval}:${oldvals}"
		echo "${newvals/:${newval}/}"
	fi
}

# update env vars
update_env_vars() {
	local shell_type="$1" base_dir="$2"
	local ld_library_path_part libpath_part manpath_part0 manpath_part1
	local path_part pythonpath_part ssm_include_path_part
	local tcl_library_part
	local cmds

	ld_library_path_part="${base_dir}/lib"
	libpath_part="${ld_library_path_part}"
	manpath_part0="${base_dir}/man"
	manpath_part1="${base_dir}/share/man"
	path_part="${base_dir}/bin"
	pythonpath_part="${base_dir}/lib/python"
	ssm_include_path_part="${base_dir}/include"
	tcl_library_part="${base_dir}/lib/tcl"

	case ${shell_type} in
	sh)
		cmds="
[ -d \"${ld_library_path_part}\" -a -n \"\`ls ${ld_library_path_part}/*.{so,a} 2>/dev/null | head -1\`\" ] && export LD_LIBRARY_PATH=\"${ld_library_path_part}\${LD_LIBRARY_PATH:+:\${LD_LIBRARY_PATH}}\" && export LIBPATH=\"${libpath_part}\${LIBPATH:+:\${LIBPATH}}\" || : ;
[ -d \"${manpath_part0}\" ] && export MANPATH=\"${manpath_part0}:\${MANPATH}\" || : ;
[ -d \"${manpath_part1}\" ] && export MANPATH=\"${manpath_part1}:\${MANPATH}\" || : ;
[ -d \"${path_part}\" ] && export PATH=\"${path_part}\${PATH:+:\${PATH}}\" || : ;
[ -d \"${pythonpath_part}\" ] && export PYTHONPATH=\"${pythonpath_part}\${PYTHONPATH:+:\${PYTHONPATH}}\" || : ;
[ -d \"${ssm_include_path_part}\" ] && export SSM_INCLUDE_PATH=\"${ssm_include_path_part}\${SSM_INCLUDE_PATH:+:\${SSM_INCLUDE_PATH}}\" || : ;
[ -d \"${tcl_library_part}\" ] && export TCL_LIBRARY=\"${tcl_library_part}\${TCL_LIBRARY:+:\${TCL_LIBRARY}}\" || : ;
"
		;;
	csh)
		# use printenv to avoid case of non-existent variable;
		# this _does_ allow for empty fields which can be a
		# security problem and should be cleaned up at the
		# end (csh is a pain!)
		cmds="
(-d \"${ld_library_path_part}\" -a -n \"\`ls ${ld_library_path_part}/*.{so,a} 2>/dev/null | head -1\`\") && setenv LD_LIBRARY_PATH \"${ld_library_path_part}:\`printenv LD_LIBRARY_PATH\`\" && setenv LIBPATH \"${libpath_part}:\`printenv LIBPATH\`\" || : ;
(-d \"${manpath_part0}\") && setenv MANPATH \"${manpath_part0}:\`printenv MANPATH\`\" || : ;
(-d \"${manpath_part1}\") && setenv MANPATH \"${manpath_part1}:\`printenv MANPATH\`\" || : ;
(-d \"${path_part}\") && setenv PATH \"${path_part}:\`printenv PATH\`\" || : ;
(-d \"${pythonpath_part}\") && setenv PYTHONPATH \"${pythonpath_part}:\`printenv PYTHONPATH\`\" || : ;
(-d \"${ssm_include_path_part}\") && setenv SSM_INCLUDE_PATH \"${ssm_include_path_part}:\`printenv SSM_INCLUDE_PATH\`\" || : ;
(-d \"${tcl_library_part}\") && setenv TCL_LIBRARY \"${tcl_library_part}:\`printenv TCL_LIBRARY\`\" || : ;
"
		;;
	esac
	echo "${cmds}"
}

print_usage() {
	echo "\
usage: ssm_env_config.sh <shell_type> [<package_name>]

Warning: do not call this program directly or apart from within a
domain.

Generate a shell-specific environment configuration script for the
full containing domain or a package within the domain.

Where:
<package_name>	Name of the package.
<shell_type>	sh or csh. Defaults to sh."
}

#
# main
#
NEWLINE='
'

case $# in
1)
	shell_type=$1
	;;
2)
	shell_type=$1
	package_name=$2
	;;
*)
	print_usage
	exit 1
esac

case ${shell_type} in
sh)
	source_cmd="."
	;;
csh)
	source_cmd="source"
	;;
*)
	echo "error: unsupported shell type (${shell_type})" 1>&2
	exit 1
esac

#
# assertions:
# * this should be called from:
# ** ssmuse
# ** ${domain_home}/etc/ssm.d/profile
# ** another ssm_env_config.sh/ssm_generateenvconfig.sh
# * this should be called using full path for $0
# * this should be run on own domain (i.e., ${domain_home}/lib/ssm.d/ssm_env_config.sh ... ${domain_home} ...)
# ** should the ${domain_home} parameter be eliminated because it is implicit?
# ** the ${domain_home} parameter was required by ssm_generateenvconfig.sh because
#	that program was used for its own domain and others; ssm_env_config.sh does
#	not work that way
#

# must be run with #! or full path
self_dir=`dirname $0`
self_dir=`(cd "${self_dir}"; pwd)`
self_domain_home=`(cd "${self_dir}/../.."; pwd)`
domain_home="${self_domain_home}"

if [ ! -d "${self_domain_home}/lib/ssm.d" ]; then
	echo "error: command not found in a domain"
	exit 1
fi

all_cmds=""

if [ "${package_name}" = "" ]; then
	# config for subdomains; prepend commands (b/c of subdomains order)!
	some_cmds=""
	OIFS="${IFS}"; IFS="${NEWLINE}"
	subdomain_homes=(`"${domain_home}/lib/ssm.d/ssm_subdomains.sh"`)
	IFS="${OIFS}"
	for subdomain_home in "${subdomain_homes[@]}"; do
		if [ -x "${subdomain_home}/lib/ssm.d/ssm_env_config.sh" ]; then
			cmds=`${subdomain_home}/lib/ssm.d/ssm_env_config.sh "${shell_type}"`
		elif [ -x "${subdomain_home}/lib/ssm.d/ssm_generateenvconfig.sh" ]; then
			cmds=`${subdomain_home}/lib/ssm.d/ssm_generateenvconfig.sh prepend ${shell_type} "${subdomain_home}"`
		else
			echo "error: domain (${subdomain_home}) does not exist" 1>&2
			# TODO: need to exit here!
		fi
		some_cmds="${cmds}
	
	
	
	${some_cmds}"
	done
	# subdomains of domain (${domain_home})
	all_cmds="${all_cmds}
	${some_cmds}"

	platforms=`get_existent_platforms "${domain_home}"`

	# config env vars; prepend commands (b/c of platforms order)
	some_cmds=""
	for platform in ${platforms}; do
		platform_dir="${domain_home}/${platform}"
		cmds=`update_env_vars "${shell_type}" "${platform_dir}"`
		some_cmds="${cmds}
${some_cmds}"
	done
	all_cmds="${all_cmds}
	${some_cmds}"

	# profiles for packages of domain (${domain_home})
	some_cmds=""
	for platform in ${platforms}; do
		OIFS="${IFS}"; IFS="${NEWLINE}"
		filenames=(`ls -1 "${domain_home}/${platform}/etc/profile.d/"*".${shell_type}" 2> /dev/null`)
		IFS="${OIFS}"
		for filename in "${filenames[@]}"; do
			some_cmds="${source_cmd} \"${filename}\" ;
	${some_cmds}"
		done
	done
	all_cmds="${all_cmds}
	${some_cmds}"
else
	# package only
	filename="${domain_home}/${package_name}/etc/profile.d/${package_name}.${shell_type}"
	if [ -r "${filename}" ]; then
		cmds0="${source_cmd} \"${filename}\""
	else
		cmds0=""
	fi
	cmds1=`update_env_vars "${shell_type}" "${domain_home}/${package_name}"`
	all_cmds="${all_cmds}
${cmds1}

${cmds0}"

fi

echo "${all_cmds}"
