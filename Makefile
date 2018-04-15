# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

include Makefiles/*

.DEFAULT_GOAL=run
#APPLICATION

remove: jupyterhub_remove nfs_remove nginx_remove volumes_nfs_delete volumes_jupyterhub_delete network_remove
run: network_recreate nfs_run jupyterhub_run nginx_run

.PHONY: remove run

