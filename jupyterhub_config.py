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
c.JupyterHub.spawner_class = 'wakonpspawner.SwarmSpawner'
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

# c.SwarmSpawner.teachers = [os.environ.get('SWARMSPAWNER_TEACHERS')]
# c.SwarmSpawner.teacher_image = os.environ.get('SWARMSPAWNER_TNOTEBOOK_IMAGE')
# c.SwarmSpawner.student_image = os.environ.get('SWARMSPAWNER_SNOTEBOOK_IMAGE')


c.SwarmSpawner.container_spec = {
			'args' : ['start-singleuser.sh'],
            'Image' : os.environ.get('SWARMSPAWNER_NOTEBOOK_IMAGE'),
			'mounts' : mounts
          }

c.SwarmSpawner.resource_spec = {}

#SSL and Secret Config
#c.JupyterHub.ssl_key = os.environ['SSL_KEY']
#c.JupyterHub.ssl_cert = os.environ['SSL_CERT']

# Authenticate users with LDAP
c.JupyterHub.authenticator_class = 'ldapauthenticator.LDAPAuthenticator'
c.LDAPAuthenticator.server_address = os.environ.get('LDAPAUTHENTICATOR_SERVER_ADDRESS')
c.LDAPAuthenticator.server_port = int(os.environ.get('LDAPAUTHENTICATOR_SERVER_PORT'))
c.LDAPAuthenticator.lookup_dn = os.environ.get('LDAPAUTHENTICATOR_USE_SSL') == 'True'
c.LDAPAuthenticator.user_search_base = os.environ.get('LDAPAUTHENTICATOR_USER_SEARCH_BASE')
c.LDAPAuthenticator.user_attribute = os.environ.get('LDAPAUTHENTICATOR_USER_ATTRIBUTE')
c.LDAPAuthenticator.use_ssl = os.environ.get('LDAPAUTHENTICATOR_USE_SSL') == 'True'

#GET allowedgroups and bindDnTemplate config from files
allowedgroups = []
pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'allowedLDAPGroups')) as f:
   for line in f:
       if not line:
           continue
       allowedgroups.append(line)
c.LDAPAuthenticator.allowed_groups = allowedgroups

bindDnTemplate = []
pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'bindDnTemplate')) as f:
   for line in f:
       if not line:
           continue
       bindDnTemplate.append(line)
c.LDAPAuthenticator.bind_dn_template = str(bindDnTemplate)

# Persist hub data on volume mounted inside container
#data_dir = os.environ.get('JUPYTERHUB_DATA_VOLUME')
#c.JupyterHub.db_url = os.path.join('sqlite:///', data_dir, 'jupyterhub.sqlite')
#c.JupyterHub.cookie_secret_file = os.path.join(data_dir,'jupyterhub_cookie_secret')

# Whitlelist admins
c.Authenticator.admin_users = admin = set()
pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'adminusers')) as f:
    for line in f:
        if not line:
            continue
        admin.add(line)
