# Delivery 2 — Actions + Follower + URDF

---

## Exercise 4: Reach the Edge and Return (Action)

### Code

- **Action definition:** `src/action_msg/action/ReachEdgeAndReturn.action`
- **Action server:** `src/reach_edge_action_server/reach_edge_action_server/reach_edge_action_server.py`

### How to run

```bash
source /opt/ros/jazzy/setup.bash
cd /workspaces/EXERCISES
colcon build --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3
source install/setup.bash

# Terminal 1
ros2 run turtlesim turtlesim_node

# Terminal 2
ros2 run reach_edge_action_server reach_edge_action_server

# Terminal 3
ros2 action send_goal --feedback /reach_edge_and_return action_msg/action/ReachEdgeAndReturn "{}"
```

### Explanation: What is an action and why is it useful?

An action in ROS 2 is a communication pattern designed for long-running tasks that require progress monitoring. Unlike a service call, which blocks until the server responds, an action allows a client to send a goal, receive continuous feedback while the task executes, and obtain a final result upon completion. Actions also support goal cancellation, meaning the client can abort an ongoing task at any time. This makes actions ideal for robotics tasks like "drive to a position" or "follow a path," where execution takes several seconds and the operator needs to observe progress or intervene if something goes wrong.

---

## Exercise 5: Turtle Follower (TF)

### Code

- **Follower node:** `src/turtle_follower/turtle_follower/turtle_follower.py`
- **TF Broadcaster:** `src/turtle_tf_broadcaster/turtle_tf_broadcaster/turtle_tf_broadcaster.py`
- **Spawner:** `src/turtle_spawner/turtle_spawner/turtle_spawner.py`
- **Launch file:** `src/turtle_spawner/launch/turtle_spawner.launch.py`

### How to run

```bash
source /opt/ros/jazzy/setup.bash
cd /workspaces/EXERCISES
source install/setup.bash

# Terminal 1
ros2 launch turtle_spawner turtle_spawner.launch.py

# Terminal 2
ros2 run turtle_follower turtle_follower
```

### Description: What does turtle_follower do?

The `turtle_follower` node uses the ROS 2 TF tree to make turtle2 follow turtle1 in real time. Every 100 ms it calls `lookup_transform('turtle2', 'turtle1', ...)` to find where turtle1 is located relative to turtle2's own frame. The translational offset (`dx`, `dy`) is then converted into a linear velocity (proportional to the distance) and an angular velocity (proportional to `atan2(dy, dx)`). This means turtle2 does not need to know any global coordinates directly — it only "sees" the leader through the TF tree. As a result, turtle2 continuously steers toward and follows turtle1 around the turtlesim window.

---

## Exercise 6: URDF Human Body

### Code

- **URDF xacro file:** `src/urdf_tutorial/urdf/human_body.urdf.xacro`
- **Launch file:** `src/urdf_tutorial/launch/display_human.launch.py`

### How to run

```bash
source /opt/ros/jazzy/setup.bash
cd /workspaces/EXERCISES
source install/setup.bash

ros2 launch urdf_tutorial display_human.launch.py
```

Then in RViz:
1. Set **Fixed Frame** to `base_link` (or `map`).
2. Click **Add** → select **RobotModel**.
3. Expand RobotModel → set **Description Topic** to `/robot_description`.

### Model structure

| Link             | Geometry   | Connected via            |
|------------------|------------|--------------------------|
| `base_link`      | Cylinder   | (root)                   |
| `head_link`      | Sphere     | `neck_joint` (fixed)     |
| `left_arm_link`  | Cylinder   | `left_shoulder_joint`    |
| `right_arm_link` | Cylinder   | `right_shoulder_joint`   |
| `left_leg_link`  | Cylinder   | `left_hip_joint`         |
| `right_leg_link` | Cylinder   | `right_hip_joint`        |

---

## Screen Recording — Schritt-für-Schritt

### 1. Display aufrufen (noVNC)

Die GUI läuft über noVNC auf **Port 6080**:
1. Klicke in VS Code unten auf den **PORTS**-Tab.
2. Finde **Port 6080** und klicke auf das Globus-Symbol (oder die URL).
3. Im Browser auf **Connect** klicken — du siehst den virtuellen Desktop.

> **Tipp:** Nutze den Vollbild-Modus des Browsers und starte ein Screen-Recording-Tool deines OS (OBS Studio, Windows Game Bar `Win+G`, macOS `Cmd+Shift+5`).

### 2. Exercise 4 aufnehmen

Stelle sicher, dass die noVNC-Ansicht und ein Terminal gleichzeitig zu sehen sind:

```bash
# Jedes in einem eigenen VS Code Terminal:
export DISPLAY=:99

# Terminal 1
source /opt/ros/jazzy/setup.bash && source install/setup.bash
ros2 run turtlesim turtlesim_node

# Terminal 2
source /opt/ros/jazzy/setup.bash && source install/setup.bash
ros2 run reach_edge_action_server reach_edge_action_server

# Terminal 3 — Recording starten BEVOR du diesen Befehl ausführst!
source /opt/ros/jazzy/setup.bash && source install/setup.bash
ros2 action send_goal --feedback /reach_edge_and_return action_msg/action/ReachEdgeAndReturn "{}"
```

Du siehst im turtlesim: Turtle fährt zur Wand → dreht → fährt zurück zur Mitte.
Im Terminal: `Goal finished with status: SUCCEEDED`.
**Recording stoppen.**

### 3. Exercise 5 aufnehmen

```bash
export DISPLAY=:99

# Terminal 1
source /opt/ros/jazzy/setup.bash && source install/setup.bash
ros2 launch turtle_spawner turtle_spawner.launch.py

# Terminal 2 — Recording starten BEVOR du diesen Befehl ausführst!
source /opt/ros/jazzy/setup.bash && source install/setup.bash
ros2 run turtle_follower turtle_follower
```

Du siehst im turtlesim: turtle1 fährt im Kreis, turtle2 folgt.
**15-20 Sekunden aufnehmen, dann stoppen.**

### 4. Exercise 6 Screenshot

```bash
export DISPLAY=:99
source /opt/ros/jazzy/setup.bash && source install/setup.bash
ros2 launch urdf_tutorial display_human.launch.py
```

In RViz (sichtbar in noVNC):
1. Fixed Frame → `base_link`
2. Add → RobotModel → Description Topic `/robot_description`
3. **Screenshot machen** (z.B. mit `Cmd+Shift+4` / `Win+Shift+S` / direkt im Browser).

---

## Checklist

- [x] `reach_edge_action_server.py` — komplett, getestet, `SUCCEEDED`
- [x] `turtle_follower.py` — komplett, getestet, turtle2 folgt turtle1
- [x] `human_body.urdf.xacro` — 6 Links (Torso, Kopf, 2 Arme, 2 Beine)
- [x] Action-Erklärung (3-5 Sätze)
- [x] Follower-Beschreibung (3-5 Sätze)
- [ ] Screen Recording Exercise 4 (**du musst aufnehmen**)
- [ ] Screen Recording Exercise 5 (**du musst aufnehmen**)
- [ ] RViz Screenshot Exercise 6 (**du musst aufnehmen**)
