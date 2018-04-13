#!/bin/bash
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

set -e

# Handle special flags if we're root
if [ $(id -u) == 0 ] ; then
    # Change UID of NB_USER to NB_UID if it does not match
    if [ "$NB_UID" != $(id -u $NB_USER) ] ; then
        echo "Creaing group students with ID $NB_UID"
	groupadd -g $NB_GID students
	echo "Creating user $JPY_USER"
	adduser --uid $NB_UID --no-create-home --disabled-password --gecos "" --gid $NB_GID $JPY_USER
	#echo "Change ownership of jovyan's home folder"
	#chown -R $JPY_USER:$NB_UID /home/jovyan
	NB_USER_GROUP=$(id -gn jovyan)
	echo "Adding $JPY_USER to group $NB_USER_GROUP"
	usermod -a -G $NB_USER_GROUP $JPY_USER
	echo "Setting home directory of user $JPY_USER to /home/jovyan"
	usermod -d /home/jovyan $JPY_USER

    fi

    # Change GID of NB_USER to NB_GID if NB_GID is passed as a parameter
    #if [ "$NB_GID" ] ; then
        #echo "Change GID to $NB_GID"
        #groupmod -g $NB_GID -o $(id -g -n $NB_USER)
    #fi

    # Enable sudo if requested
    if [ ! -z "$GRANT_SUDO" ]; then
	echo "$JPY_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook
    fi

    # Exec the command as NB_USER
    echo "Execute the command as $NB_USER"
    echo "Command is:  exec sudo -E -H -u $JPY_USER PATH=$PATH PYTHONPATH=$PYTHONPATH stack exec $*"
    echo "Arguments: $*"
    echo "Programm: $1"
    echo "Programm Arguments: ${@:2}"

    exec sudo -E -H -u $JPY_USER PATH=$PATH PYTHONPATH=$PYTHONPATH stack exec --allow-different-user $1 -- ${@:2}
    #exec su $JPY_USER -c 'env PATH="$PATH:/opt/conda/bin" stack exec "$1" -- "${@:2}"' -- "$@"
else
    # Exec the command
    echo "Execute the command"
    exec $*
fi
