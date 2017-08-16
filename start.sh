#!/bin/bash
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

set -e

# Handle special flags if we're root
if [ $(id -u) == 0 ] ; then
    # Change GID of HUB_USER to DOCKER_GID if DOCKER_GID is passed as a parameter
    if [ "$DOCKER_GID" ] ; then
        echo "Change GID to $DOCKER_GID"
        groupmod -g $DOCKER_GID -o docker
    fi

    # Exec the command as HUB_USER
    echo "Execute the command as $HUB_USER"
    exec su $HUB_USER -c "export PATH=/opt/conda/bin:${PATH} && jupyterhub -f /srv/jupyterhub/jupyterhub_config.py"
else
    # Exec the command
    echo "Execute the command"
    exec jupyterhub -f /srv/jupyterhub/jupyterhub_config.py
fi
