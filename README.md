# LED Gazebo Plugin

A Gazebo system plugin for simulating LEDs using visuals and lights. Define LED modes (blinking patterns, colors, intensity) in SDF and switch between them at runtime via a Gazebo Transport topic (bridgable with ROS 2).

![LED Plugin Demo world](media/gazebo_led_plugin_demo.gif)
_Demo from [led_plugin.sdf](examples/gazebo/led_plugin.sdf) — 2 robots and a tower lamp with different LED groups/modes._

![Dance Party Demo](media/dance_party_party_mode.gif)
_Demo from [dance_party.sdf](examples/gazebo/dance_party.sdf) — a disco light model for a dance party._

> The Tom model is from [Sketchfab](https://sketchfab.com/3d-models/tom-multiversus-tom-and-jerry-4996154491b14356a8ebc40ab62179ab), animated with Mixamo/Blender. Also on [Gazebo Fuel](https://app.gazebosim.org/jasmeetsingh/fuel/models/Dancing%20Tom%20Cat).

## Features

- **Visual + Light LEDs**: Define LEDs using visuals, lights, or both
- **Named modes**: Describe LED behaviors (idle, warning, emergency, etc.) with multi-step sequences
- **Selective activation**: Modes can target specific LEDs via `<active_leds>` or all LEDs by default
- **Always-on support**: Static LED states via `always_on="true"`
- **Runtime mode switching**: Change modes via a Gazebo Transport topic (ROS 2 bridgable)
- **Reset/Off**: Send `"reset"` or `"off"` to turn all LEDs to default state
- **Case-insensitive**: Mode name matching is case-insensitive

## Installation

**Requirements**: Gazebo Harmonic+, Ubuntu 24.04, `colcon`

```bash
cd your_workspace_dir
git clone https://github.com/jasmeet0915/gz_sim_led_plugin.git src/gz_led_plugin
colcon build --packages-select gz_led_plugin
source install/setup.bash
```

Run examples:
```bash
gz sim -v 4 src/gz_led_plugin/examples/gazebo/led_plugin.sdf
# or
gz sim -v 4 src/gz_led_plugin/examples/gazebo/dance_party.sdf
```

## Usage

### SDF Example

From the [led_plugin.sdf](examples/gazebo/led_plugin.sdf) tower lamp model:

```xml
<plugin name="led" filename="libLedPlugin.so">
  <led_group_name>tower_lamp</led_group_name>

  <led name="emergency_led">
    <visual_name>lamp_red::lamp_red_visual</visual_name>
    <light_name>lamp_red::emergency_light</light_name>
    <default_state>
      <color>0.3 0.0 0.0 1</color>
      <intensity>0.0</intensity>
    </default_state>
  </led>

  <led name="ready_led">
    <visual_name>lamp_green::lamp_green_visual</visual_name>
    <light_name>lamp_green::ready_light</light_name>
    <default_state>
      <color>0.0 0.3 0.0 1</color>
      <intensity>0.0</intensity>
    </default_state>
  </led>

  <startup_mode>ready</startup_mode>

  <mode name="ready">
    <active_leds>
      <led>ready_led</led>
    </active_leds>
    <step always_on="false">
      <color>0.0 1.0 0.0 1</color>
      <intensity>2.0</intensity>
      <on_time>1.0</on_time>
    </step>
    <step always_on="false">
      <color>0.0 0.3 0.0 1</color>
      <intensity>0.0</intensity>
      <on_time>1.0</on_time>
    </step>
  </mode>

  <mode name="emergency">
    <active_leds>
      <led>emergency_led</led>
    </active_leds>
    <step always_on="false">
      <color>1.0 0.0 0.0 1</color>
      <intensity>2.0</intensity>
      <on_time>1.0</on_time>
    </step>
    <step always_on="false">
      <color>0.3 0.0 0.0 1</color>
      <intensity>0.0</intensity>
      <on_time>1.0</on_time>
    </step>
  </mode>
</plugin>
```

### SDF Reference

| Element | Description |
|---|---|
| `<led_group_name>` | Namespace for the mode change topic. Defaults to `led_{model_name}` |
| `<led name="...">` | Define an LED with `<visual_name>`, `<light_name>`, and optional `<default_state>` |
| `<startup_mode>` | Mode to activate on startup. Defaults to first defined mode |
| `<mode name="...">` | Named mode with optional `<active_leds>` and one or more `<step>` elements |
| `<step>` | `always_on` (attr), `<color>`, `<intensity>`, `<on_time>` (seconds) |

### Changing Modes at Runtime

**Gazebo CLI** (publish to topic):
```bash
gz topic -t /tower_lamp/change_led_mode -m gz.msgs.StringMsg -p "data: 'emergency'"
```

**Reset/turn off LEDs**:
```bash
gz topic -t /tower_lamp/change_led_mode -m gz.msgs.StringMsg -p "data: 'off'"
```

**ROS 2** (via `ros_gz_bridge`):

Bridge the topic (see [example launch file](examples/ros/launch/example_led_robot.launch.py)):
```python
Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    arguments=['/led_robot/change_led_mode@std_msgs/msg/String]gz.msgs.StringMsg'],
)
```

Then publish from ROS 2:
```bash
ros2 topic pub --once /led_robot/change_led_mode std_msgs/msg/String "{data: 'emergency'}"
```

## Using with URDF

Two things to keep in mind when using this plugin with URDF:

### 1. Preserve fixed joints with `<preserveFixedJoint>`

URDF-to-SDF conversion merges links connected by fixed joints into a single link by default. Add this for your fixed joint you want to preserve:

```xml
<gazebo reference="top_to_front_led_joint">
  <preserveFixedJoint>true</preserveFixedJoint>
</gazebo>
```

### 2. Visual/collision name suffix from URDF→SDF conversion

The URDF→SDF conversion appends `_visual` and `_collision` suffixes to visual and collision names. So if your URDF visual is named `back_led_visual`, the SDF name becomes `back_led_visual_visual`. Account for this in the plugin config:

```xml
<!-- URDF has: <visual name="back_led_visual"> -->
<!-- SDF converts to: back_led_visual_visual -->
<led name="back_led">
  <visual_name>back_led::back_led_visual_visual</visual_name>
</led>
```

>**Note:** An issue is up for this over at the [sdformat](https://github.com/gazebosim/sdformat/issues/333#issuecomment-4127304040) repo.

See the [ROS example URDF](examples/ros/urdf/led_robot.urdf.xacro) and its [gazebo xacro](examples/ros/urdf/led_robot.gazebo.xacro) for a complete working example.

## Blog Posts

For an in-depth guide on this plugin and Gazebo system plugins in general:

- [Beginner Gazebo System Plugin Guide - Part 1](https://jasmeetsingh.io/blogs/beginner-gazebo-system-plugin-guide-1/)
- [Beginner Gazebo System Plugin Guide - Part 2](https://jasmeetsingh.io/blogs/beginner-gazebo-system-plugin-guide-2/)

## License

Apache License 2.0 — see [LICENSE](LICENSE).

## Author

Jasmeet Singh — jasmeet0915@gmail.com
