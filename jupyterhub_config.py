# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
import os
import subprocess
import os
import errno
import stat

c = get_config()
pwd = os.path.dirname(__file__)

# TLS config
c.JupyterHub.ip = '0.0.0.0'
c.JupyterHub.port = 443
c.JupyterHub.hub_ip = '0.0.0.0'

c.JupyterHub.spawner_class = 'cassinyspawner.SwarmSpawner'
c.JupyterHub.cleanup_servers = False
c.SwarmSpawner.start_timeout = 60 * 10
c.SwarmSpawner.jupyterhub_service_name = 'jupyterhub_jupyterhub'
c.SwarmSpawner.service_prefix = "jupyterhub"
c.SwarmSpawner.networks = ["jupyterhub-network"]
notebook_dir = os.environ.get('NOTEBOOK_DIR') or '/home/jovyan/work'
c.SwarmSpawner.notebook_dir = notebook_dir	
c.SwarmSpawner.container_spec = {
			'args' : ['start-singleuser.sh'],
            'Image' :'jupyter/scipy-notebook:bb222f49222e',
			'mounts' : [{'type' : 'volume',
			'source' : 'jupyterhub-user-{username}',
            'target' : '/home/jovyan/work'}]
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
#c.JupyterHub.proxy_auth_token = '0bc02bede919e99a26de1e2a7a5aadfaf6228de836ec39a05a6c6942831d8fe5'

# Authenticate users with GitHub OAuth
c.LocalAuthenticator.create_system_users = True
c.JupyterHub.authenticator_class = 'ldapauthenticator.LDAPAuthenticator'
c.LDAPAuthenticator.server_address = '10.25.1.6'
c.LDAPAuthenticator.server_port = 636
c.LDAPAuthenticator.lookup_dn = True
c.LDAPAuthenticator.user_search_base = 'OU=technikum,DC=technikum,dc=fh-joanneum,dc=local'
c.LDAPAuthenticator.user_attribute = 'sAMAccountName'
c.LDAPAuthenticator.use_ssl = True
c.JupyterHub.log_level = 'DEBUG'

# Persist hub data on volume mounted inside container
data_dir = os.environ.get('DATA_VOLUME_CONTAINER', '/data')
c.JupyterHub.db_url = os.path.join('sqlite:///', data_dir, 'jupyterhub.sqlite')
c.JupyterHub.cookie_secret_file = os.path.join(data_dir,
    'jupyterhub_cookie_secret')

# Whitlelist users and admins
#c.Authenticator.whitelist = {'mal', 'zoe', 'inara', 'kaylee'}
c.Authenticator.admin_users = admin = set()
c.JupyterHub.admin_access = True
pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'userlist')) as f:
    for line in f:
        if not line:
            continue
        parts = line.split()
        name = parts[0]
        #whitelist.add(name)
        if len(parts) > 1 and parts[1] == 'admin':
            admin.add(name)
