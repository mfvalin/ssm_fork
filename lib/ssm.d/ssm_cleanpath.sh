#! /bin/bash
#
# ssm_cleanpath.sh

if [ "${BASH_VERSINFO[0]}" -lt 4 ]; then
	echo $1
	exit 0
fi

dropemptylib=0

while [ $# -gt 0 ]; do
	case $1 in
	--dropemptylib)
		dropemptylib=1; shift 1
		;;
	--*)
		# ignore
		shift 1
		;;
	*)
		break
		;;
	esac
done

typeset -A arr
typeset -a res
typeset -a res2
IFS=":"
for a in $1; do
	if [ -z "${arr[x$a]}" ]; then
		arr["x$a"]=1
		res+=("$a")
	fi
done
if [ "${1%%*:}" != "$1" -a "${arr[x]}" != "1" ]; then
	res+=("")
fi

if [ $dropemptylib -eq 1 ]; then
	res2=()
	for _res in ${res[*]}; do
		if [ -n "`ls ${_res}/*.{so,a} 2>/dev/null | head -1`" ]; then
			res2+=(${_res})
		fi
	done
	res=(${res2[*]})
fi

echo "${res[*]}"
