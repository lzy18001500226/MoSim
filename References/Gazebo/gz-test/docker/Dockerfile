FROM ubuntu:focal

RUN apt-get update \
 && apt-get install -y \
      sudo wget lsb-release gnupg curl \
 && apt-get clean

ARG user_id
ENV USERNAME developer
RUN useradd -U --uid ${user_id} -ms /bin/bash $USERNAME \
 && echo "$USERNAME:$USERNAME" | chpasswd \
 && adduser $USERNAME sudo \
 && echo "$USERNAME ALL=NOPASSWD: ALL" >> /etc/sudoers.d/$USERNAME

# Commands below run as the developer user
USER $USERNAME

WORKDIR /home/$USERNAME

COPY scripts/enable_gz_stable.sh scripts/enable_gz_stable.sh
RUN sudo scripts/enable_gz_stable.sh

COPY scripts/install_common_deps.sh scripts/install_common_deps.sh
RUN scripts/install_common_deps.sh

# This is not strictly necessary, but makes things faster down the line.
COPY scripts/install_gz_deps.sh scripts/install_gz_deps.sh
RUN scripts/install_gz_deps.sh

COPY scripts/build_gz.sh scripts/build_gz.sh
COPY scripts/build.sh scripts/build.sh
RUN scripts/build.sh

ADD gz-test /home/$USERNAME/gz-test
RUN sudo chown -R $USERNAME:$USERNAME /home/$USERNAME/gz-test
RUN cd gz-test; mkdir build;
WORKDIR /home/$USERNAME/gz-test/build
RUN cmake ../ -DBUILD_TESTING=false; sudo make install

WORKDIR /home/$USERNAME
COPY --chmod=0755 --chown=$USERNAME:$USERNAME run.bash ./
ENTRYPOINT ["./run.bash"]
