# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
import os
c = get_config()

# TLS config
c.JupyterHub.ip = '0.0.0.0'
c.JupyterHub.port = 443
c.JupyterHub.proxy_api_ip = '0.0.0.0'
c.JupyterHub.proxy_api_port = 8081
c.DockerSpawner.hub_ip_connect = 'jupyterhub_jupyterhub'
c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.hub_port = 8080
c.DockerSpawner.container_ip = '0.0.0.0'

c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.container_image = os.environ['DOCKER_NOTEBOOK_IMAGE']

spawn_cmd = os.environ.get('DOCKER_SPAWN_CMD', "start-singleuser.sh")
c.DockerSpawner.extra_create_kwargs.update({ 'command': spawn_cmd })
network_name = 'jupyterhub-network'
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = network_name
c.DockerSpawner.extra_host_config = { 'network_mode': network_name }
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
c.DockerSpawner.notebook_dir = notebook_dir
c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': notebook_dir }
c.DockerSpawner.extra_create_kwargs.update({ 'volume_driver': 'local' })
c.DockerSpawner.remove_containers = True
c.DockerSpawner.debug = True


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
#c.Authenticator.whitelist = whitelist = set()
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
