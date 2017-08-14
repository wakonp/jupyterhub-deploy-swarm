# jupyterhub-deploy-swarm
This repository represents my parctical research project for my master thesis. I used the jupyterhub-deploy-docker as the base for this repository. The main difference between them is, that this jupyterhub-fhjoanneum is using SwarmSpawner, whereas the jupyterhub-deploy-docker is using the DockerSpawner to generate notebook servers in a docker environment. The DockerSpawner is able to deploy containers only. That means DockerSpawner does not support the service concept of Docker which comes with version [1.12.0](https://docs.docker.com/engine/swarm/), which is the reason why this projects uses [SwarmSpawner](https://github.com/cassinyio/SwarmSpawner).

Also please checkout the [wiki](https://github.com/wakonp/jupyterhub-fhjoanneum/wiki) for more information.

Many thanks to all contributers who made this possible.

Docu will be updated over time!

## Overview
![Application Overview](https://github.com/wakonp/jupyterhub-fhjoanneum/blob/master/docu/overview.jpeg)
## Authenticator
This project is using the [LDAPAuthenticator]() for jupyterhub.
## Spawner
As mentioned before, the project is using the [SwarmSpawner](https://github.com/cassinyio/SwarmSpawner) as the jupyterhub spawner class, which is able to create Docker services in a Docker swarm setup. It is necessary to provide a working Docker Swarm environment to run this jupyterhub-deploy-swarm example.
## nbgrader
Nbgrader is also installed on each spawned notebook server. While spawning the servers, the spawner can distinguish between a teacher or a student and uses different images for each type of group. The difference between these images is, that teacher can create and assign Assignments, whereas the students can attempt and submit them back to the teacher. 
## Persistant Storage
The basic approach to store data via Docker is to use Docker Volumes. The only problem with this solution is, that the volumes are only available on the host, which created the volume. There is no way to share the volumes in the Docker Swarm yet. That's the reason why the project uses Docker NFS Volumes. 

A single NFS-Server get started in a container on the main host. Every other host is able to communicate with this NFS-Container and therefore can create the Docker NFS Volumes. 

## Usage
The whole project is using the `Makefile` to perform actions, like creating a new Docker Volume or building a Docker Image. Here comes a detailed list of how to use the `Makefile`:

`make <command>`

Please make sure to clone this repository on the main node of a Docker Swarm. Then modify the `jupyterhub_config.py` and execute `make run` to start everything. This will trigger the `docker pull` command, which will load the `walki12/jupyterhub` Docker Image from Dockerhub, create a new `overlay` network for the application, the Docker Volumes for persistant storage and start the NFS-Container and the jupyterhub service.

### Maintasks Commands
These commands are used to control the whole project (NFS, jupyterhub).
- run
  - removes all running docker instancies (network/volumes/container/service) and creates and starts them again.
- start
  - starts the NFS container and the jupyterhub service. (Volumes and Network must be available) 
- stop
  - stops the NFS container and removes the jupyterhub service. (Volumes and Network are still availabe)
- remove
  - removes all running docker instancies (network/volumes/container/service)
- restart
  - runs `stop` and `start`.
- rerun
  - runs `remove` and `run`
- rebuild
  - runs `remove`, `jupyterhub_build`, `jupyterhub_push`, `jupyterhub_updatenodes` and `run`
  - it builds the jupyterhub Docker Image again and restarts the application with the new image.

### NFS tasks Commands
NFS specific commands, which will only effect the NFS Container and/or the underlaying volumes.
- nfs_run
  - calls `nfs_remove`, `nfs_start` and `nfs_config`
- nfs_config
  - connects into the NFS Container and executes commands (create group/user)
- nfs_start
  - starts the NFS Container like `docker start <nfs-container-name>` (Container must be available (stopped))
- nfs_stop
  - stops the NFS Container.
- nfs_remove
  - removes the NFS Container and the Docker NFS Container Volumes
- nfs_restart
  - runs `nfs_stop` and `nfs_start` (careful `nfs_config` did not get called)

### Jupyterhub tasks Commands
Jupyterhub specific commands, which will only effect the Jupyterhub Service and/or the underlaying volumes.
- jupyterhub_run
  - calls `jupyterhub_remove`, creates the volume and calls `jupyterhub_start`
- jupyterhub_start
  - starts the jupyterhub Service (Volumes/Network must be available)
- jupyterhub_remove
  - removes the jupyterhub service and the Docker Volumes of the service 
- jupyterhub_restart
- jupyterhub_build
  - builds a jupyterhub Docker Image
- jupyterhub_push
  - pushes the Docker Image of jupyterhub to Docker Hub
