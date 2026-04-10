# EXERCISES

Dieses Repository ist als ROS-2-colcon-Workspace fuer die Session-2-Uebungen vorbereitet.

## Struktur

- src/turtle_rgb: Service-Interface aus Exercise 2
- src/turtle_rgb_server: Python-Service-Server aus Exercise 3
- src/action_msg: Action-Definition fuer Exercise 4
- src/reach_edge_action_server: Action-Server fuer Exercise 4
- src/turtle_spawner: Launch und TF-Broadcaster fuer Exercise 5
- src/turtle_follower: TF-basierter Follower fuer Exercise 5
- src/urdf_tutorial: URDF/Xacro-Dateien und Launches fuer Exercise 6

## Build

Voraussetzung: Eine ROS-2-Umgebung, zum Beispiel Humble.

```bash
source /opt/ros/humble/setup.bash
cd /workspaces/EXERCISES
colcon build
source install/setup.bash
```

## Exercise 2 und 3

```bash
ros2 interface show turtle_rgb/srv/SetRGB
ros2 run turtle_rgb_server turtle_rgb_server
ros2 service call /set_rgb turtle_rgb/srv/SetRGB "{r: 255, g: 0, b: 0}"
```

## Exercise 4

Terminal 1:

```bash
ros2 run turtlesim turtlesim_node
```

Terminal 2:

```bash
ros2 run reach_edge_action_server reach_edge_action_server
```

Terminal 3:

```bash
ros2 action send_goal /reach_edge_and_return action_msg/action/ReachEdgeAndReturn "{}"
```

## Exercise 5

Terminal 1:

```bash
ros2 launch turtle_spawner turtle_spawner.launch.py
```

Terminal 2:

```bash
ros2 run turtle_follower turtle_follower
```

## Exercise 6

URDF anzeigen:

```bash
ros2 launch urdf_tutorial display.launch.py
```

Xacro anzeigen:

```bash
ros2 launch urdf_tutorial display_xacro.launch.py
```

Human-Body-Modell anzeigen:

```bash
ros2 launch urdf_tutorial display_human.launch.py
```