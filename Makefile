# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

include .env Makefiles/*

.DEFAULT_GOAL=run
#APPLICATION

start: nfs_start nfs_config jupyterhub_start
stop: jupyterhub_remove nfs_remove nginx_remove
restart: stop start
run: network_recreate nfs_run jupyterhub_run
remove: jupyterhub_remove nfs_remove volumes_nfs_delete volumes_jupyterhub_delete network_remove nginx_remove
rerun: remove run
rebuild: remove jupyterhub_build jupyterhub_push jupyternotebook_updatenodes run
	
.PHONY: rebuild rerun remove run restart stop start 
