# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
FROM jupyter/scipy-notebook

USER $NB_USER

#Install nbgrader
RUN conda install nbgrader

RUN jupyter nbextension install --user --py nbgrader
RUN jupyter nbextension enable --user --py nbgrader
RUN jupyter serverextension enable --user --py nbgrader

USER root
RUN apt-get update && apt-get install -y curl \
	libtinfo-dev \
	libzmq3-dev \
	libcairo2-dev \
	libpango1.0-dev \
	libmagic-dev \
	libblas-dev \
	python3-pip \
	netbase \
	liblapack-dev && \
	apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 575159689BEFB442 && \
    echo 'deb http://download.fpcomplete.com/ubuntu trusty main' > /etc/apt/sources.list.d/fpco.list && \
	curl -sSL https://get.haskellstack.org/ | sh && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

ENV PATH="/home/$NB_USER/.local/bin:${PATH}"

USER $NB_USER
#JavaScript Installation
RUN git clone https://github.com/notablemind/jupyter-nodejs.git && cd jupyter-nodejs && \
	umask 0002 && mkdir -p ~/.ipython/kernels/nodejs/ && \
	npm install && node install.js && \
	npm run build && npm run build-ext

#Haskell Installation
RUN PATH=//home/jovyan/.local/bin/:$PATH
RUN export PATH


# Install stack from Stackage
USER root
RUN curl -L https://www.stackage.org/stack/linux-x86_64 | tar xz --wildcards --strip-components=1 -C /usr/bin '*/stack'
USER $NB_USER

WORKDIR /home/jovyan

RUN stack --version


# Installing iHaskell from sources
RUN mkdir ihaskell
RUN git clone https://github.com/gibiansky/IHaskell.git --depth 1

WORKDIR ihaskell

RUN cp  ../IHaskell/stack.yaml ./
# Fix for problem with cryptonite (https://github.com/gibiansky/IHaskell/issues/636)
RUN echo "ghc-options:" >> stack.yaml
RUN echo "  cryptonite: -opta-Wa,-mrelax-relocations=no" >> stack.yaml
RUN cat stack.yaml
RUN stack setup
RUN cp  ../IHaskell/ihaskell.cabal ./ && cp -R ../IHaskell/ipython-kernel \
	../IHaskell/ghc-parser ../IHaskell/ihaskell-display  ./
RUN stack build --only-snapshot
RUN cp -r ../IHaskell/src ../IHaskell/html ../IHaskell/main ../IHaskell/LICENSE ./
RUN stack build
RUN stack install
#Now rebuild cryptonite in order to fix problems
RUN stack exec -- ghc-pkg unregister cryptonite --force
RUN stack build

RUN ihaskell install

# Install additional Haskell packages required for exercises
RUN stack install http-conduit
RUN stack install cassava


# Install Java Kernel
#USER root
#RUN echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | tee /etc/apt/sources.list.d/webupd8team-java.list && \
#	echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | tee -a /etc/apt/sources.list.d/webupd8team-java.list && \
#	apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886 && \
#	apt-get update
#RUN echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections && \
#	echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections
#RUN apt-get install -y oracle-java9-installer

#USER $NB_USER
#WORKDIR /home/jovyan
#RUN git clone https://github.com/SpencerPark/jupyter-jvm-basekernel.git --depth 1 ./jupyter-jvm-basekernel && \
#	cd jupyter-jvm-basekernel && ls -al
#WORKDIR /home/jovyan/jupyter-jvm-basekernel
#RUN echo "Currently (should be /home(jovyan/jupyter-jvm-basekernel) in $(pwd)"
#RUN echo $(ls -al)
#RUN chmod u+x gradlew && ./gradlew publishToMavenLocal && cd /home/jovyan

#RUN cd /home/jovyan

#WORKDIR /home/jovyan
#RUN echo "Currently in $(pwd)"

#RUN git clone https://github.com/SpencerPark/IJava.git --depth 1 && \
#	cd IJava/

#WORKDIR /home/jovyan/IJava
#RUN echo "Currently in $(pwd)"
#RUN ls -al $(pwd)
#RUN chmod u+x ./gradlew && ./gradlew installKernel

#Installing C#
WORKDIR /home/jovyan
USER root
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF && \
	echo "deb http://download.mono-project.com/repo/ubuntu xenial main" | sudo tee /etc/apt/sources.list.d/mono-official.list && \
	apt-get update
RUN apt-get install -y binutils mono-devel ca-certificates-mono fsharp nuget referenceassemblies-pcl && \
	rm -rf /var/lib/apt/lists/* /tmp/*
RUN cert-sync /etc/ssl/certs/ca-certificates.crt \
	&& yes | certmgr -ssl -m https://go.microsoft.com \
	&& yes | certmgr -ssl -m https://nugetgallery.blob.core.windows.net \
	&& yes | certmgr -ssl -m https://nuget.org

RUN chown -R $NB_USER $HOME/.config/

USER $NB_USER
RUN git clone --recursive https://github.com/zabirauf/icsharp.git --depth 1 ./icsharp

# Build scriptcs
WORKDIR /home/jovyan/icsharp/Engine
RUN mozroots --import --sync --quiet
RUN mono ./.nuget/NuGet.exe restore ./ScriptCs.sln
RUN mkdir -p artifacts/Release/bin

# Build iCSharp
WORKDIR /home/jovyan/icsharp
RUN mozroots --import --sync --quiet
RUN mono ./.nuget/NuGet.exe restore ./iCSharp.sln
RUN mkdir -p build/Release/bin
RUN xbuild ./iCSharp.sln /property:Configuration=Release /nologo /verbosity:normal
# Copy files safely
RUN for line in $(find ./*/bin/Release/*); do cp $line ./build/Release/bin; done
# Install kernel
RUN sed -i 's_"<.*>/icsharp_"mono","/home/jovyan/icsharp_g'  kernel-spec/kernel.json
RUN mv kernel-spec csharp
USER root
RUN jupyter-kernelspec install --user csharp

# Install jupyter-scala
USER root
RUN apt-get update && apt-get install -y default-jdk
USER $NB_USER
WORKDIR /home/jovyan
RUN  curl -L -o jupyter-scala https://raw.githubusercontent.com/jupyter-scala/jupyter-scala/master/jupyter-scala \
	&& chmod +x jupyter-scala \
	&& ./jupyter-scala \
	&& rm -f jupyter-scala

WORKDIR /home/jovyan/work
USER root
RUN chmod -R g=u /home/jovyan

ENV PATH /home/jovyan/ihaskell/.stack-work/install/x86_64-linux/lts-9.21/8.0.2/bin:/home/jovyan/.stack/snapshots/x86_64-linux/lts-9.21/8.0.2/bin:/home/jovyan/.stack/programs/x86_64-linux/ghc-8.0.2/bin:$PATH
#RUN echo "PATH = $NEWPATH"

#USER $NB_USER


WORKDIR /home/jovyan/ihaskell
RUN echo "Test"
COPY start.sh /usr/local/bin
RUN chmod +x /usr/local/bin/start.sh

#COPY start-singleuser.sh /usr/local/bin
