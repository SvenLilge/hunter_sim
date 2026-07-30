FROM utiasasrl/vtr3:latest

RUN curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] https://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
RUN apt-get update
RUN apt-get install -y ros-humble-gazebo-* ros-humble-joint-state-publisher ros-humble-joint-state-publisher-gui ros-humble-ackermann-steering-controller ros-humble-control-* ros-humble-rqt-robot-steering 