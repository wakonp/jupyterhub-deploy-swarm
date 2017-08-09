# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

include .env

.DEFAULT_GOAL=build
#JUPYTERHUB NETWORK
network_create:
	@(docker network inspect $(SWARMSPAWNER_NETWORK) >/dev/null 2>&1 && echo "NETWORK IS ALREADY PRESENT") || (docker network  create --attachable -d overlay $(SWARMSPAWNER_NETWORK) >/dev/null && echo "NETWORK CREATED!")

network_remove:
	@(docker network rm $(SWARMSPAWNER_NETWORK) >/dev/null 2>&1 && echo "NETWORK REMOVED!") || echo "NETWORK WAS NOT PRESENT!"

network_recreate: network_remove network_create

#JUPYTERHUB VOLUMES
volumes_nfs_create:
	@(docker volume inspect $(NFSSERVER_VOLUME) >/dev/null 2>&1 && echo "NFS VOLUME ALREADY THERE!") || (docker volume create $(NFSSERVER_VOLUME) && echo "NFS VOLUME CREATED!")
volumes_nfs_delete:
	@(docker volume rm $(NFSSERVER_VOLUME) >/dev/null 2>&1 &&  echo "NFS VOLUME REMOVED!") || echo "NFS VOLUME NOT PRESENT!"
volumes_nfs_recreate: volumes_nfs_delete volumes_nfs_create
volumes_jupyterhub_create:
	@(docker volume inspect $(NFSSERVER_HUBDATA_VOLUMENAME) >/dev/null 2>&1 &&  echo "HUBDATA VOLUME ALREADY THERE!")  ||  (docker volume create --driver local --opt type=nfs4 --opt o=addr=$(NFSSERVER_IP),rw --opt device=:$(NFSSERVER_HUBDATA_SHARE) $(NFSSERVER_HUBDATA_VOLUMENAME) && echo "JUPYTERDATA VOLUMES CREATED!")
	@(docker volume inspect $(NFSSERVER_USERDATA_VOLUMENAME) >/dev/null 2>&1 && echo "USERDATA VOLUME ALREADY THERE!") ||  (docker volume create --driver local --opt type=nfs4 --opt o=addr=$(NFSSERVER_IP),rw --opt device=:$(NFSSERVER_USERDATA_SHARE) $(NFSSERVER_USERDATA_VOLUMENAME) && echo "USERDATA VOLUMES CREATED!")
volumes_jupyterhub_delete:
	@(docker volume rm $(NFSSERVER_HUBDATA_VOLUMENAME) >/dev/null 2>&1 && echo "HUBDATA VOLUME REMOVED" ) || echo "THERE IS NO HUBDATA VOLUME!"
	@(docker volume rm $(NFSSERVER_USERDATA_VOLUMENAME) >/dev/null 2>&1 echo "USERDATA VOLUME REMOVED" ) || echo "THERE IS NO USERDATA VOLUME!"
volumes_jupyterhub_recreate: volumes_jupyterhub_delete volumes_jupyterhub_create

#JUPYTERHUB 
jupyterhub_build:
	@docker-compose build
jupyterhub_push:
	@docker push walki12/jupyterhub
jupyterhub_start:
	@docker stack deploy -c docker-compose.yml  $(JUPYTERHUB_SERVICE_PREFIX) >/dev/null 2>&1 && echo "JUPYTERHUB STARTED!"
jupyterhub_remove:
	-docker service rm jupyterhub_jupyterhub
	@sleep 5
jupyterhub_restart: jupyterhub_remove jupyterhub_start
jupyterhub_run: jupyterhub_remove volumes_jupyterhub_recreate jupyterhub_start

#JUPYTERNOTEBOOKS
jupyternotebook_build:
	@docker build -t walki12/teachernotebook -f ./fhj-notebooks/teacher-notebook/Dockerfile.teachernotebook ./fhj-notebooks/teacher-notebook/
	@docker build -t walki12/studentnotebook -f ./fhj-notebooks/student-notebook/Dockerfile.studentnotebook ./fhj-notebooks/student-notebook/
jupyternotebook_push:
	@docker push walki12/studentnotebook
	@docker push walki12/teachernotebook
jupyternotebook_updatenodes: node1-updateDocker node2-updateDocker
jupyternotebook_notify:
	@echo "Docker Images wurden erfolgreich erstellt und auf allen Nodes gepullt!" | mail -s "Jupyterhub@FH" philipp.wakonigg@edu.fh-joanneum.at
#NFSSERVER
nfs_start:
	@docker run -p 2049:2049 -v $(NFSSERVER_VOLUME):/exports -d --name jupyterhub_nfs --cap-add=SYS_ADMIN --env-file=.envNFS walki12/nfs-server jupyterhub jupyterUsers jupyterAssignments
	@sleep 5
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
#notifyme:
#	mail -s "JupyterHub@FH" philipp.wakonigg@edu.fh-joanneum.at 
node1:
	ssh root@10.15.200.217
node1-updateDocker:
	ssh root@10.15.200.217 "docker pull walki12/teachernotebook && docker pull walki12/studentnotebook && docker system prune -f"
node2:
	ssh root@10.15.200.222
node2-updateDocker:
	ssh root@10.15.200.222 "docker pull walki12/teachernotebook && docker pull walki12/studentnotebook && docker system prune -f"

jupyterhub: jupyterhub_build jupyterhub_push jupyternotebook_updatenodes
jupyternotebooks: jupyternotebook_build jupyternotebook_push jupyternotebook_updatenodes
jupyternotebooks-notify: jupyternotebook_build jupyternotebook_push jupyternotebook_notify
jupyternotebooks-hiddennotify:
	@nohup make jupyternotebooks-notify >.makelog 2>&1 || tail .makelog | mail -s "JupyterHub@FH" philipp.wakonigg@edu.fh-joanneum.at &

start: nfs_start nfs_config jupyterhub_start
stop: jupyterhub_remove nfs_remove
restart: stop start
run: network_recreate nfs_run jupyterhub_run
remove: jupyterhub_remove nfs_remove volumes_nfs_delete volumes_jupyterhub_delete network_remove
rerun: remove run
rebuild: remove jupyterhub run

exec-nfstest:
	docker exec -it jupyterhub_nfs cat /etc/passwd

all: remove jupyterhub jupyternotebooks run
docker_clean:
	docker rmi $$(docker images -q -f dangling=true)
nfs_testuser:
	docker exec jupyterhub_nfs useradd -d /exports/jupyterUsers/test -s /bin/bash -N -g students test
	
.PHONY: node1-updateDocker node1 node2 jupyternotebooks-hiddennotify jupyternotebooks-notify jupyterhub_push docker_clean nfs_testuser exec-nfstest all rebuild rerun remove run restart stop start jupyternotebooks jupyterhub nfs_restart nfs_run jupyterhub_restart jupyterhub_run volumes_nfs_recreate volumes_jupyterhub_recreate
