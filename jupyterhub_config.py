# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
import os
import subprocess
import errno
import stat

c = get_config()
pwd = os.path.dirname(__file__)

# TLS config
c.JupyterHub.ip = os.environ.get('JUPYTERHUB_IP')
c.JupyterHub.port = int(os.environ.get('JUPYTERHUB_PORT'))
c.JupyterHub.hub_ip = os.environ.get('JUPYTERHUB_HUB_IP')
c.JupyterHub.hub_port = int(os.environ.get('JUPYTERHUB_HUB_PORT'))
c.JupyterHub.spawner_class = 'cassinyspawner.SwarmSpawner'
c.JupyterHub.cleanup_servers = False
c.JupyterHub.log_level = os.environ.get('JUPYTERHUB_LOG_LEVEL')

c.SwarmSpawner.start_timeout = 60 * 60
c.SwarmSpawner.jupyterhub_service_name = os.environ.get('SWARMSPAWNER_HUB_SERVICE_NAME')
c.SwarmSpawner.service_prefix = os.environ.get('SWARMSPAWNER_SERVICE_PREFIX')
c.SwarmSpawner.networks = [os.environ.get('SWARMSPAWNER_NETWORK')]
c.SwarmSpawner.notebook_dir = os.environ.get('SWARMSPAWNER_NOTEBOOK_DIR')
mounts = [{'type' : 'volume',
'target' : os.environ.get('SWARMSPAWNER_NOTEBOOK_DIR'),
'source' : 'jupyterhub-user-{username}',
'no_copy' : True,
'driver_config' : {
  'name' : 'local',
  'options' : {
     'type' : 'nfs4',
	 'o' : 'addr='+os.environ.get('NFSSERVER_IP')+',rw',
	 'device' : ':'+os.environ.get('NFSSERVER_USERDATA_DEVICE')
   }
}},{
'type' : 'volume',
'target' : '/srv/nbgrader/exchange',
'source' : 'jupyter-exchange-volume',
'no_copy' : True,
'driver_config' : {
  'name' : 'local',
  'options' : {
     'type' : 'nfs4',
	 'o' : 'addr='+os.environ.get('NFSSERVER_IP')+',rw',
	 'device' : ':'+os.environ.get('NFSSERVER_ASSIGNMENTDATA_DEVICE')
   }
}}]


c.SwarmSpawner.container_spec = {
			'args' : ['start-singleuser.sh'],
            'Image' : os.environ.get('SWARMSPAWNER_NOTEBOOK_IMAGE'),
			'mounts' : mounts
          }

c.SwarmSpawner.resource_spec = {}

# Authenticate users with LDAP
c.JupyterHub.authenticator_class = 'ldapauthenticator.LDAPAuthenticator'
c.LDAPAuthenticator.server_address = os.environ.get('LDAPAUTHENTICATOR_SERVER_ADDRESS')
c.LDAPAuthenticator.server_port = int(os.environ.get('LDAPAUTHENTICATOR_SERVER_PORT'))
c.LDAPAuthenticator.lookup_dn = os.environ.get('LDAPAUTHENTICATOR_USE_SSL') == 'True'
c.LDAPAuthenticator.user_search_base = os.environ.get('LDAPAUTHENTICATOR_USER_SEARCH_BASE')
c.LDAPAuthenticator.user_attribute = os.environ.get('LDAPAUTHENTICATOR_USER_ATTRIBUTE')
c.LDAPAuthenticator.use_ssl = os.environ.get('LDAPAUTHENTICATOR_USE_SSL') == 'True'

#GET allowedgroups and bindDnTemplate config from files
c.LDAPAuthenticator.allowed_groups = allowedgroups = []
pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'allowedLDAPGroups')) as f:
   for line in f:
       if not line:
           continue
       allowedgroups.append(line.replace("\n",""))

c.LDAPAuthenticator.bind_dn_template = bindDnTemplate = []
pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'bindDnTemplate')) as f:
    for line in f:
        if not line:
            continue
        bindDnTemplate.append(line.replace("\n",""))

def create_dir_hook(spawner):
    username = spawner.user.name # get the username
    os.system('docker exec -d jupyterhub_nfs useradd -d /exports/jupyterUsers/'+username.lower()+' -s /bin/bash -N -g students '+username.lower())
    os.system('docker exec -d jupyterhub_nfs bash -c "mkdir -p /exports/jupyterUsers/'+username.lower()+' ; chown '+username.lower()+':students -R /exports/jupyterUsers/'+username.lower()+'"')

    spawner.environment["NB_UID"] = subprocess.check_output(["docker","exec","jupyterhub_nfs","id","-u",username.lower()]);
    spawner.environment["NB_GID"] = subprocess.check_output(["docker","exec","jupyterhub_nfs","id","-g",username.lower()]);
    if any(spawner.user.name in teacher for teacher in [os.environ.get('SWARMSPAWNER_TEACHERS')]):
        spawner.container_spec['Image'] = os.environ.get('SWARMSPAWNER_TNOTEBOOK_IMAGE')
    else:
        spawner.container_spec['Image'] = os.environ.get('SWARMSPAWNER_SNOTEBOOK_IMAGE')

c.Spawner.pre_spawn_hook = create_dir_hook

# Whitlelist admins
c.Authenticator.admin_users = admin = set()
pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'adminusers')) as f:
    for line in f:
        if not line:
            continue
        admin.add(line.replace("\n",""))
