# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

include .env

.DEFAULT_GOAL=build
#JUPYTERHUB NETWORK
network_create:
	@docker network inspect $(SWARMSPAWNER_NETWORK) >/dev/null 2>&1 || docker network  create --attachable -d overlay $(SWARMSPAWNER_NETWORK)
	@echo "NETWORK CREATED!"

network_remove:
	@docker network rm $(SWARMSPAWNER_NETWORK) >/dev/null 2>&1 || true
	@echo "NETWORK REMOVED!"

network_recreate: network_remove network_create

#JUPYTERHUB VOLUMES
volumes_nfs_create:
	@docker volume inspect $(NFSSERVER_VOLUME) >/dev/null 2>&1 || docker volume create $(NFSSERVER_VOLUME)
	@echo "NFS VOLUME CREATED!"
volumes_nfs_delete:
	@docker volume rm $(NFSSERVER_VOLUME) >/dev/null 2>&1 || true
	@echo "NFS VOLUME REMOVED!"
volumes_nfs_recreate: volumes_nfs_delete volumes_nfs_create
volumes_jupyterhub_create:
	@docker volume inspect $(NFSSERVER_HUBDATA_VOLUMENAME) >/dev/null 2>&1  ||  docker volume create --driver local --opt type=nfs4 --opt o=addr=$(NFSSERVER_IP),rw --opt device=:$(NFSSERVER_HUBDATA_SHARE) $(NFSSERVER_HUBDATA_VOLUMENAME)
	@docker volume inspect $(NFSSERVER_USERDATA_VOLUMENAME) >/dev/null 2>&1 ||  docker volume create --driver local --opt type=nfs4 --opt o=addr=$(NFSSERVER_IP),rw --opt device=:$(NFSSERVER_USERDATA_SHARE) $(NFSSERVER_USERDATA_VOLUMENAME)
	@echo "JUPYTERHUB VOLUMES CREATED!"
volumes_jupyterhub_delete:
	@docker volume rm $(NFSSERVER_HUBDATA_VOLUMENAME) >/dev/null 2>&1 || true
	@docker volume rm $(NFSSERVER_USERDATA_VOLUMENAME) >/dev/null 2>&1 || true
	@echo "JUPYTERHUB VOLUMES REMOVED!"
volumes_jupyterhub_recreate: volumes_jupyterhub_delete volumes_jupyterhub_create

#JUPYTERHUB 
jupyterhub_build:
	@docker-compose build
jupyterhub_push:
	@docker push walki12/jupyterhub
jupyterhub_start:
	@docker stack deploy -c docker-compose.yml  $(JUPYTERHUB_SERVICE_PREFIX) >/dev/null
jupyterhub_remove:
	@docker service rm jupyterhub_jupyterhub 2>/dev/null || true
jupyterhub_restart: jupyterhub_remove jupyterhub_start
jupyterhub_run: jupyterhub_remove volumes_jupyterhub_recreate jupyterhub_start

#JUPYTERHUBCERTFILES AND DEFAULT USER
self-signed-cert:
	# make a self-signed cert

secrets/jupyterhub.crt:
	@echo "Need an SSL certificate in secrets/jupyterhub.crt"
	@exit 1

secrets/jupyterhub.key:
	@echo "Need an SSL key in secrets/jupyterhub.key"
	@exit 1

userlist:
	@echo "Add usernames, one per line, to ./userlist, such as:"
	@echo "    zoe admin"
	@echo "    wash"
	@exit 1

# Do not require cert/key files if SECRETS_VOLUME defined
secrets_volume = $(shell echo $(SECRETS_VOLUME))
ifeq ($(secrets_volume),)
	cert_files=secrets/jupyterhub.crt secrets/jupyterhub.key
else
	cert_files=
endif

check-files: userlist $(cert_files)

#JUPYTERNOTEBOOKS
jupyternotebook_build:
	@docker build -t walki12/jupyternotebook -f Dockerfile.notebook .
	@docker build -t walki12/studentnotebook -f Dockerfile.studentnotebook .
	@docker build -t walki12/teachernotebook -f Dockerfile.teachernotebook .
jupyternotebook_push:
	@docker push walki12/jupyternotebook >/dev/null && echo "JUPYTERNOTEBOOK IMAGE PUSH COMPLETE"
	@docker push walki12/studentnotebook >/dev/null && echo "STUDENTNOTEBOOK IMAGE PUSH COMPLETE"
	@docker push walki12/teachernotebook >/dev/null && echo "TEACHERNOTEBOOK IMAGE PUSH COMPLETE"	

#NFSSERVER
nfs_start:
	@docker run -p 2049:2049 -v $(NFSSERVER_VOLUME):/exports -d --name jupyterhub_nfs --cap-add=SYS_ADMIN erezhorev/dockerized_nfs_server jupyterhub jupyterUsers jupyterAssignments
	@sleep 10
	@echo "NFS Server started"
nfs_config:
	@docker exec -d jupyterhub_nfs groupadd students && echo "Group 'students' added!"
	@docker exec -d jupyterhub_nfs groupadd teachers && echo "Group 'teachers' added!"
	#TODO MAKE SHARE PERMISSION STRUCTURE
nfs_stop:
	@docker stop jupyterhub_nfs 2>/dev/null || true
nfs_remove: nfs_stop
	@docker rm jupyterhub_nfs 2>/dev/null || true
nfs_restart: nfs_stop nfs_start
nfs_run: nfs_remove volumes_nfs_recreate nfs_start nfs_config

#APPLICATION
jupyterhub: jupyterhub_build jupyterhub_push
jupyternotebooks: jupyternotebook_build jupyternotebook_push
start: nfs_start jupyterhub_start
stop: jupyterhub_remove nfs_remove
restart: stop start
run: network_recreate nfs_run jupyterhub_run
remove: nfs_remove jupyterhub_remove network_remove
rerun: remove run
rebuild: remove jupyterhub run

exec-nfstest:
	docker exec -it jupyterhub_nfs cat /etc/passwd

all: remove jupyterhub jupyternotebooks run
docker_clean:
	docker rmi $$(docker images -q -f dangling=true)
nfs_testuser:
	@docker exec -d jupyterhub_nfs useradd -d /exports/jupyterUsers/test -s /bin/bash -N -g students test
	
.PHONY: docker_clean nfs_testuser exec-nfstest all rebuild rerun remove run restart stop start jupyternotebooks jupyterhub nfs_restart nfs_run jupyterhub_restart jupyterhub_run volumes_nfs_recreate volumes_jupyterhub_recreate
