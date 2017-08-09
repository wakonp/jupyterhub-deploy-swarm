# jupyterhub-fhjoanneum
A DockerSwarm Jupyterhub setup, which uses a NFS Server for persistent storage
This repository is based on the jupyterhub-deploy-docker repo but is modified to use the LDAPAuthenticator and DockerSwarmSpawner.
Unfortunaly the DockerSpawner does not support the DockerSwarm Service concept and could not be used in this setup. The 
DockerSwarmSpawner was used for this compatibility and tested on 3 Nodes (2 Manager 1 Worker). The LDAPAuthenticator was 
configured as descripted in its repo to communicate with the FH-Joanneum LDAP System.

Furthermore, I used the dockerized_nfs_server repository to run a nfs-container on the main swarm node and publish the tcp
port through out the host. At this point it was possible to create new Docker volumes with the type nfs4 which pointed at 
the nfs-container.

In the configuration for the NotebookServerContainer (jupyterhub-config.py - container_spec), I added two volumes from type 
nfs4 (therefore I had to add a few lines of code to the SwarmSpawner). The first one stores all Notebookdata and the second one 
will be needed for nbgrader (not yet tested). 

Before starting up the jupyterhub-service, an overlay network (jupyterhub-network) and named nfs volume are created. The network
and the named-volumes are configured to be used by the jupyterhub-service in the docker-compose file.

Starting the jupyterhub-service with 'docker stack deploy -c docker-compose.yml jupyterhub' creates the service. At this 
point the nfs-container on the main host need to be up and running, because jupyterhub stores data (cookie-secrete, database,...)
in this volume. Increases the startup speed the following times enormes.

Now the juypterhub-service should be up and running (if you configured it right :D) and you can access the hub on the https 
port of the main node. There you can perform the login. If you enter the correct username/password, the LDAPAuthenticator 
returns the username to the DockerSpawner. The DockerSpawner then uses the configured container_spec (image,network,..) to 
start a new notebook-service.

Here comes the cool part. If the User authenticates correct, the username of the LDAPAuthenticator is used to create a new 
User in the nfs-server container (adding it to a group students-teachers needs to be added). After this interception of the
Jupyterhub Spawn Process, the DockerSwarmSpawner gets the UID as well as the GID from the previous created user in the 
nfs-container. These two values are put into the enviroment of the not-yet-started NotebookServerService. I had to modify 
the notebook images for providing multiple kernels and for running the whole server with User "root". But dont worry the 
'start.sh' script of any jupyter/base-notebook based DockerNotebookImage checks if the current User is root and does something
amazing. It uses the UID and GID of the environment and changes the UID & GID of the jovyan User (default User) and changes 
the permissions for directories which needed to be accecable while run-time (chown UID:GID -R /opt/conda, /home/jovyan). 
This is pretty amazing, but if you use multiple kernels (my setup - all-spark-notebook +Haskell - 10Gb DockerImage :D), 
this command takes AGGGEESSSS. 

Solution(not tested): In the base-notebook-image before creating this jovyan user, I created a nbbuild group and assign it 
while creating the jovyan user. I also need to modify the umask of the user, so the buildgroup gets fullaccess(rwx) on all
files jovyan creates while building the dependencies of the notebook. Coming back to the start script, the UID and GID will 
be modifiy, but the nbbuild group will be added as a secondary group (or stay as primary, me dont know yet).

Summing up, the Notebook User needs full access to all dependencies for running the NotebookServer, but also need to write 
on the nfs-server with a specific UID and GID. Therefore, the nfs-server UID:GID will be injected via environment variables 
into the Service. The service will be started as USER root to trigger the change UID:GID steps in the start.sh. There the 
UID of the jovyan user gets changed to the UID of the nfs-user. The GID of the nfs-user will be added as a secondary || primary
group of jovyan. At this point jovyan should have the UID of the nfs-user and two groups (nbbuild and GID of the nfs-group). 
Through the nbbuild group jovyan should still have full access on all prebuild dependencies.

If this concept works, notebook users will alwas write with their nfs-user and can be managed on the nfs-system seperatly. 

Long Story short, if you like to test this repo, just check it out and make sure you check out the submodules too and run make run

Many thanks to all contributers how made this possible.

I will update this docu, when all steps are tested and working :D
