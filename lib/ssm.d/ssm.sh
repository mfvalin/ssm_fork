#! /bin/bash
#
# ssm.sh (linked to bin/ssm)
#
# Front end to all ssm operations which are served from an ssm_*.py
# or ssm_*.sh program

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
	echo "\
usage: ${PROG_NAME} <subcommand> [<args>]

Simple Software Manager (ssm).

List operations:
    ssm diffd|find|listd|listdh|listr [<args>]

Package management:
    ssm install|publish|uninstall|unpublish [<args>]
        
Domain management:
    ssm created|freezed|showd|unfreezed|updated [<args>]

System/user profile management:
    ssm subscribe|unsubscribe [<args>]

Other:
    ssm platforms
    ssm version

For help, specify -h or --help to the subcommand."
}

#
# main
#

# must be run with #! or full path
PROG_NAME=${0##*/}
PROG_DIR=${0%/*}
case ${PROG_NAME} in
ssm)
	LIB_DIR=`cd "${PROG_DIR}/../lib/ssm.d"; pwd`
	;;
ssm.sh)
	LIB_DIR=${PROG_DIR}
	;;
esac

if [ $# -lt 1 ]; then
	echo "error: missing subcommand" 1>&2
	exit 1
fi

subcommand=$1; shift 1

case ${subcommand} in
-h|--help)
	print_usage
	exit 0
	;;
cloned)
	exec ${LIB_DIR}/python/ssm_cloned.py "$@" ;;
created)
	exec ${LIB_DIR}/python/ssm_created.py "$@" ;;
diffd)
	exec ${LIB_DIR}/ssm_diffd.sh "$@" ;;
find)
	exec ${LIB_DIR}/python/ssm_find.py "$@" ;;
freezed)
	exec ${LIB_DIR}/python/ssm_freezed.py "$@" ;;
install)
	exec ${LIB_DIR}/python/ssm_install.py "$@" ;;
listd)
	exec ${LIB_DIR}/python/ssm_listd.py "$@" ;;
listdh)
	exec ${LIB_DIR}/python/ssm_listdh.py "$@" ;;
listr)
	exec ${LIB_DIR}/python/ssm_listr.py "$@" ;;
platforms)
	# use domain lib/ssm.d
	exec "${LIB_DIR}/../../../lib/ssm.d/ssm_platforms.sh" "$@" ;;
publish)
	exec ${LIB_DIR}/python/ssm_publish.py "$@" ;;
showd)
	exec ${LIB_DIR}/python/ssm_showd.py "$@" ;;
subscribe)
	exec ${LIB_DIR}/python/ssm_subscribe.py "$@" ;;
unfreezed)
	exec ${LIB_DIR}/python/ssm_unfreezed.py "$@" ;;
uninstall)
	exec ${LIB_DIR}/python/ssm_uninstall.py "$@" ;;
unpublish)
	exec ${LIB_DIR}/python/ssm_unpublish.py "$@" ;;
updated)
	exec ${LIB_DIR}/python/ssm_updated.py "$@" ;;
unsubscribe)
	exec ${LIB_DIR}/python/ssm_unsubscribe.py "$@" ;;
version)
	exec ${LIB_DIR}/python/ssm_version.py "$@" ;;
*)
	echo "error: unknown subcommand" 1>&2
	exit 1
esac

