#!/bin/sh

set -e

dst_node="node1,node2,node3"
base="/var/lib/cassandra/data"
tmp_prefix="cass_restore" # Keep it on same fs with ${base} so hardlinks could be created

do_table() {
	keyspace=$1
	table_uuid=$2

	table=$(basename "$table_uuid")
	table=${table%%-*}
	out="${keyspace}/${table}"
	echo "Restoring ${keyspace}/${table}"
	snapshot_name=$(ls -1t ${base}/${keyspace}/${table_uuid}/snapshots/ | head -n1)
	pushd ${tmp_prefix}
	sudo -u cassandra mkdir -p ${out}
	sudo -u cassandra cp -Rfl ${base}/${keyspace}/${table_uuid}/snapshots/${snapshot_name}/* ${out}
	sudo -u cassandra sstableloader -d ${dst_nodes} ${out}
	sudo -u cassandra rm -Rf ${out}
	popd
}

do_keyspace() {
	keyspace=$1

	for snapshot_path in $(find ${base}/${keyspace} -name snapshots -type d); do
		table_path=$(dirname ${snapshot_path})
    table_uuid=$(basename ${table_path})
		do_table ${keyspace} ${table_uuid}
	done
}

# Restore to another cluster so ignore system keyspaces
keyspaces_list=$(du -sm ${base}/* | awk '($2 !~ "^system")' | sort -g)
# for example:
# 14860   profile
# 39977   userdata
for keyspace in "${keyspaces_list}"; do
	do_keyspace $keyspace
done

