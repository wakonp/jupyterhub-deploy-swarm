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
c.JupyterHub.spawner_class = 'cassinyspawner.SwarmSpawner'
c.JupyterHub.cleanup_servers = False
c.JupyterHub.log_level = os.environ.get('JUPYTERHUB_LOG_LEVEL')

c.SwarmSpawner.start_timeout = 60 * 10
c.SwarmSpawner.jupyterhub_service_name = os.environ.get('SWARMSPAWNER_HUB_SERVICE_NAME')
c.SwarmSpawner.service_prefix = os.environ.get('SWARMSPAWNER_SERVICE_PREFIX')
c.SwarmSpawner.networks = [os.environ.get('SWARMSPAWNER_NETWORK')]
c.SwarmSpawner.notebook_dir = os.environ.get('SWARMSPAWNER_NOTEBOOK_DIR')	
c.SwarmSpawner.container_spec = {
			'args' : ['start-singleuser.sh'],
            'Image' : os.environ.get('SWARMSPAWNER_NOTEBOOK_IMAGE'),
			'mounts' : [{'type' : 'volume',
			'source' : 'jupyterhub-user-{username}',
            'target' : os.environ.get('SWARMSPAWNER_NOTEBOOK_DIR')}]
          }

c.SwarmSpawner.resource_spec = {}
#c.SwarmSpawner.resource_spec = {
#                'cpu_limit' : 1000, 
#                'mem_limit' : int(512 * 1e6),
#                'cpu_reservation' : 1000, 
#                'mem_reservation' : int(512 * 1e6)
#                }

#SSL and Secret Config
c.JupyterHub.ssl_key = os.environ['SSL_KEY']
c.JupyterHub.ssl_cert = os.environ['SSL_CERT']

# Authenticate users with LDAP
c.LocalAuthenticator.create_system_users = True
c.JupyterHub.authenticator_class = 'ldapauthenticator.LDAPAuthenticator'
c.LDAPAuthenticator.server_address = os.environ.get('LDAPAUTHENTICATOR_SERVER_ADDRESS')
c.LDAPAuthenticator.server_port = int(os.environ.get('LDAPAUTHENTICATOR_SERVER_PORT'))
c.LDAPAuthenticator.lookup_dn = os.environ.get('LDAPAUTHENTICATOR_USE_SSL') == 'True'
c.LDAPAuthenticator.user_search_base = os.environ.get('LDAPAUTHENTICATOR_USER_SEARCH_BASE')
c.LDAPAuthenticator.user_attribute = os.environ.get('LDAPAUTHENTICATOR_USER_ATTRIBUTE')
c.LDAPAuthenticator.use_ssl = os.environ.get('LDAPAUTHENTICATOR_USE_SSL') == 'True'
#templateList = os.environ.get('LDAPAUTHENTICATOR_BIND_DN_TEMPLATE').replace(';',',').encode('utf-8')
c.LDAPAuthenticator.bind_dn_template = ['CN={username},OU=AIM15,OU=AIM,OU=Studenten,OU=Benutzer,OU=Graz,OU=Technikum,DC=technikum,DC=fh-joanneum,DC=local','CN={username},OU=AIM,OU=Studenten,OU=Benutzer,OU=Graz,OU=Technikum,DC=technikum,DC=fh-joanneum,DC=local','cn={username},ou=IMA,ou=Personal,ou=Benutzer,ou=Graz,ou=Technikum,dc=technikum,dc=fh-joanneum,dc=local','cn={username},OU=IMA16,OU=IMA,OU=Studenten,OU=Benutzer,OU=Graz,OU=Technikum,DC=technikum,DC=fh-joanneum,DC=local','cn={username},OU=IMA,OU=Studenten,OU=Benutzer,OU=Graz,OU=Technikum,DC=technikum,DC=fh-joanneum,DC=local']
#allowedGroups = os.environ.get('LDAPAUTHENTICATOR_ALLOWED_GROUPS').replace("'","").split(';') or ''
#c.LDAPAuthenticator.allowed_groups = allowedGroups
c.LDAPAuthenticator.valid_username_rege
x = os.environ.get('LDAPAUTHENTICATOR_VALID_USERNAME_REGEX')


# Persist hub data on volume mounted inside container
data_dir = os.environ.get('JUPYTERHUB_DATA_VOLUME')
c.JupyterHub.db_url = os.path.join('sqlite:///', data_dir, 'jupyterhub.sqlite')
c.JupyterHub.cookie_secret_file = os.path.join(data_dir,'jupyterhub_cookie_secret')

# Whitlelist users and admins
c.Authenticator.admin_users = admin = set()
c.JupyterHub.admin_access = True
pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'userlist')) as f:
    for line in f:
        if not line:
            continue
        parts = line.split()
        name = parts[0]
        if len(parts) > 1 and parts[1] == 'admin':
            admin.add(name)
