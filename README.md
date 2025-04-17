**Clone repo:**

```console
cd $VTRROOT
git clone https://github.com/SvenLilge/hunter_sim.git
```

**Install dependencies:**

Launch vtr3 docker as root to install:

```console
apt-get install ros-humble-gazebo-*
apt-get install ros-humble-joint-state-publisher ros-humble-joint-state-publisher-gui
apt-get install ros-humble-ackermann-steering-controller
apt-get install ros-humble-control-*
apt-get install ros-humble-rqt-robot-steering 
```

**Build package:**

In the vtr3 docker run:

```console
source /opt/ros/humble/setup.bash
cd $VTRROOT/hunter_sim
colcon build
```

**Run Hunter LiDAR Sim:**

In the vtr3 docker run:

```console
cd $VTRROOT/hunter_sim
source install/setup.bash
source /usr/share/gazebo-11/setup.bash
source /opt/ros/humble/setup.bash
ros2 launch hunter2_gazebo hunter_lidar_sim.launch.py 
```

This should open Gazebo and RVIZ (visualizing the most relevant topics). The simulated robot in Gazebo takes velocity commands from /cmd_vel.
