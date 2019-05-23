#!/bin/bash

set -e

bkp_dir=/local/backup

typedb='postgresql'
version='11'
port='5432'

date_str=$(date '+%Y%m%d%H%M')
dst_dir=${bkp_dir}/$(hostname -s).${typedb}_v${version}.${date_str}
lockfile=/var/run/lock/$(hostname -s).${typedb}_v${version}

parallel_dumps=${1:-4}
parallel_archs=$(( $(nproc --ignore=4) / parallel_dumps))

if [ ${parallel_archs} -lt 2 ]; then parallel_archs=2; fi
archiver="zstd -T${parallel_archs}"

function is_tty() {
	test -t 1
}

function do_backup() {
	db_name=$1
	if [ "$db_name" = "template0" ]; then return; fi
	pg_dump ${db_name} | $arch --compress - -o ${dst_dir}/${db_name}.sql.zstd
}

export archiver
export dst_dir
export -f do_backup

(
flock -n 9 || exit 1

mkdir ${dst_dir}

if [ ${parallel_dumps} -gt 1 ]; then
	pg_dumpall --globals-only --file=${dst_dir}/globals.sql
	psql -Upostgres --list --tuples-only | awk '($1 != "|" && $1 != "") { print $1 }' | \
		xargs -P ${parallel_dumps} -n1 -I {} bash -c 'do_backup "$@"' _ {}

else
	i=1
	sp="/-\|"
	is_tty && echo -n ' '

	is_tty && printf "\b${sp:i++%${#sp}:1}"
	pg_dumpall --globals-only --file=${dst_dir}/globals.sql

	for db in $(psql -Upostgres --list --tuples-only | awk '($1 != "|" && $1 != "") { print $1 }'); do
		is_tty 0 && printf "\b${sp:i++%${#sp}:1}"
		if [ "$db" = "template0" ]; then continue; fi
		pg_dump $db | $archiver --compress - -o ${dst_dir}/$db.sql.zstd
	done
	is_tty 0 && printf "\b"
fi
) 9>${lockfile}
