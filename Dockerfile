# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
FROM jupyterhub/jupyterhub-onbuild:0.7.2


#Install LDAP Authenticator
ADD ./ldapauthenticator/ ldapauthenticator
WORKDIR ./ldapauthenticator
RUN python setup.py install
WORKDIR ..

#Install DockerSwarmSpawner
ADD ./SwarmSpawner ./SwarmSpawner
WORKDIR ./SwarmSpawner
RUN pip install -r requirements.txt
RUN python setup.py install
WORKDIR ..

# install docker on the jupyterhub container
RUN wget https://get.docker.com -q -O /tmp/getdocker && \
    chmod +x /tmp/getdocker && \
    sh /tmp/getdocker

# Copy TLS certificate and key
ENV SSL_CERT /srv/jupyterhub/secrets/jupyterhub.crt
ENV SSL_KEY /srv/jupyterhub/secrets/jupyterhub.key
COPY ./secrets/*.crt $SSL_CERT
COPY ./secrets/*.key $SSL_KEY
RUN chmod 700 /srv/jupyterhub/secrets && \
    chmod 600 /srv/jupyterhub/secrets/*

COPY ./hubConfig /srv/jupyterhub/

# docker-py causes an get_auth_header error
RUN pip uninstall --yes docker docker-py ; pip install docker

EXPOSE 8080
EXPOSE 8081