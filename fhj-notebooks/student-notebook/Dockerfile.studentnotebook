# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
FROM walki12/teachernotebook:latest

USER $NB_USER

RUN jupyter nbextension disable --user create_assignment/main
RUN jupyter nbextension disable --user formgrader/main --section=tree
RUN jupyter serverextension disable --user nbgrader.server_extensions.formgrader

USER root
