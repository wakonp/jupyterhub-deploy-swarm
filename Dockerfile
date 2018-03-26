# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
FROM jupyterhub/jupyterhub:0.8.1

# install docker on the jupyterhub container
RUN wget https://get.docker.com -q -O /tmp/getdocker && \
    chmod +x /tmp/getdocker && \
    sh /tmp/getdocker



# start juypterhub

# #Create Jupyterhubuser with access writes to /opt/conda
# USER root
ENV HUB_USER jupyter
RUN useradd -s /bin/bash $HUB_USER
RUN chown $HUB_USER -R /opt/conda

 #Install LDAP Authenticator
ADD ./ldapauthenticator/ ./ldapauthenticator
RUN chown -R jupyter ./ldapauthenticator
WORKDIR ./ldapauthenticator
#USER $HUB_USER
RUN python setup.py install
USER root
WORKDIR ..

#Install DockerSwarmSpawner
ADD ./SwarmSpawner ./SwarmSpawner
RUN chown -R $HUB_USER ./SwarmSpawner
WORKDIR ./SwarmSpawner
#USER $HUB_USER
RUN pip install -r requirements.txt
RUN python setup.py install
USER root
WORKDIR ..

CMD ["jupyterhub", "-f", "/srv/jupyterhub/jupyterhub_config.py"]


# # add $HUB_USER user to docker group
# RUN usermod -aG docker $HUB_USER
#
# # Copy TLS certificate and key
# ENV SSL_CERT /srv/jupyterhub/secrets/jupyterhub.crt
# ENV SSL_KEY /srv/jupyterhub/secrets/jupyterhub.key
# COPY ./secrets/*.crt $SSL_CERT
# COPY ./secrets/*.key $SSL_KEY
# RUN chmod 700 /srv/jupyterhub/secrets && \
#     chmod 600 /srv/jupyterhub/secrets/*

# COPY ./hubConfig /srv/jupyterhub/
# COPY start.sh /usr/local/bin
# RUN chown $HUB_USER -R /srv/jupyterhub/
#
# # docker-py causes an get_auth_header error
# RUN pip uninstall --yes docker docker-py ; pip install docker
#
# EXPOSE 8080
# EXPOSE 8081
#
# USER root
