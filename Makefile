# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

include .env Makefiles/*

.DEFAULT_GOAL=run
#APPLICATION

remove: jupyterhub_remove nfs_remove nginx_remove volumes_nfs_delete volumes_jupyterhub_delete network_remove
run: network_recreate nfs_run jupyterhub_run nginx_run

nfsENVFile=testNFS
nfsConfigHosts=NFS_CONFIG_HOSTS

check_nfs_config:
	ifneq ($(findstring $(nfsConfigHosts),$(nfsENVFile)))
		echo "found"
	else
		echo "not found"
	endif

update_nfs_swarm_node_ips:
	@echo -n "$(nfsConfigHosts)=" >> $(nfsENVFile)
	@for NODE in $(shell docker node ls --format '{{.Hostname}}') ; do \
		docker node inspect --format '{{.Status.Addr}}' $$NODE | tr -d '\n' >> $(nfsENVFile) ; \
		echo -n "," >> $(nfsENVFile) ; \
	done
	@truncate -s-1 $(nfsENVFile)
	@echo "" >> $(nfsENVFile)

test: check_nfs_config

.PHONY: remove run test
