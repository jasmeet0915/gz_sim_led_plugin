# LED Gazebo Plugin

A Gazebo system plugin for simulating LED systems using visuals and lights. This plugin allows you create realistic LED behavior such as blinking patterns, color changes, and intensity control for simulating status indicators on models like robots, tower lamps, and signal beacons.

The plugin introduces the concept of LED modes, allowing users to define different LED behaviors in SDF. A runtime mode change service is provided to switch between these modes dynamically (for example, transitioning from an idle mode to a fault or emergency mode).

![LED Plugin Demo world](media/gazebo_led_plugin_demo.gif)
_Demo gif from the [led_plugin.sdf](examples/led_plugin.sdf) example world showing 2 robots and an industrial tower lamp model each having different LED group with different modes._

![Dance Party Demo Party mode](media/dance_party_party_mode.gif)
_Demo gif from the [dance_party.sdf](examples/dance_party.sdf) example world which creates a Disco Light model for, well, a dance party._

> BTW: The Tom model was taken from [Sketchfab](https://sketchfab.com/3d-models/tom-multiversus-tom-and-jerry-4996154491b14356a8ebc40ab62179ab) and animated using Mixamo and Blender. The SDF model is available in this repo and on [Gazebo Fuel](https://app.gazebosim.org/jasmeetsingh/fuel/models/Dancing%20Tom%20Cat) as well ;)

## Terminology

- **LED**: A logical LED unit defined by a visual, a light, or both.
- **LED Mode**: A named behavior (e.g., idle, warning, emergency) describing how one or more LEDs should act.
- **LED Step**: A single step within a mode defining color, intensity, and duration.

## Features

- **Visual and Light entity-based LEDs**: Define an LED using a visual, a light, or both via the `<led>` element. Visuals control the LED appearance, while lights provide realistic illumination effects.
- **Mode-based LED behavior**: Describe LED behavior using named modes defined with the `<mode>` element.
- **Model-level LED definition**: Define all LEDs for a model within a single plugin instance. Each mode can control all LEDs by default or selectively activate specific LEDs using the `<active_leds>` element.
- **Multi-step LED sequences**: Create blinking or animation patterns using one or more `<step>` elements, each specifying color, intensity, and timing.
- **Always-on mode**: Define static LED behavior using the `always_on` attribute on a `<step>` element.
- **LED grouping**: Organize multiple LEDs into logical groups.
- **Runtime mode switching**: Change LED behavior dynamically at runtime via a Gazebo Transport service.

## Installation

### Requirements

1. Gazebo Jetty (Binary install or Source install, both should work)
2. Ubuntu 24.04
3. `colcon` for building the workspace

> **Note**: Ideally, the plugin should work fine on other verions of Gazebo and Ubuntu but I have not tested it personally with other configurations yet. If you are planning to run the plugin on any other configuration, feel free to open up a PR with required fixes (if any) and update this part of the README.

### From Source

1. Clone the repository into your ROS workspace:
   ```bash
   cd your_workspace_dir
   git clone https://github.com/jasmeet0915/gz_sim_led_plugin.git src/gz_led_plugin
   ```

2. Build the plugin:
   ```bash
   colcon build --packages-select gz_led_plugin
   ```

3. Source the workspace:
   ```bash
   source install/setup.bash
   ```

4. Run the demo worlds:
   ```bash
   gz sim -v 4 src/gz_led_plugin/examples/led_plugin.sdf
   ```
    or
   ```bash
   gz sim -v 4 src/gz_led_plugin/examples/dance_party.sdf
   ```

## Usage

### Basic Example

The following snippet is from the [led_plugin.sdf](examples/led_plugin.sdf) tower lamp model:

```xml
<plugin name="led" filename="libLedPlugin.so">
  <led_group_name>tower_lamp</led_group_name>

  <!-- LED Descriptions -->
  <led name="emergency_led">
    <visual_name>lamp_red::lamp_red_visual</visual_name>
    <light_name>lamp_red::emergency_light</light_name>
    <default_state>
      <color>0.3 0.0 0.0 1</color>
      <intensity>0.0</intensity>
    </default_state>
  </led>

  <led name="warning_led">
    <visual_name>lamp_yellow::lamp_yellow_visual</visual_name>
    <light_name>lamp_yellow::warning_light</light_name>
    <default_state>
      <color>0.3 0.3 0.0 1</color>
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

  <!-- Mode Descriptions -->
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

  <mode name="warning">
    <active_leds>
      <led>warning_led</led>
    </active_leds>
    <step always_on="false">
      <color>0.8 0.8 0.0 1</color>
      <on_time>1.0</on_time>
      <intensity>2.0</intensity>
    </step>
    <step always_on="false">
      <color>0.3 0.3 0.0 1</color>
      <on_time>1.0</on_time>
      <intensity>0.0</intensity>
    </step>
  </mode>

</plugin>
```

### Brief Explanations
```xml
<plugin name="led" filename="libLedPlugin.so">
  <led_group_name>tower_lamp</led_group_name>
```

This snippet loads the plugin and set the `<led_group_name>`. This name is used for namespacing the `change_mode` service for the LED. If this tag is absent, `led_{model_name}` is used as the namespace by default.

```xml
  <!-- LED Descriptions -->
  <led name="emergency_led">
    <visual_name>lamp_red::lamp_red_visual</visual_name>
    <light_name>lamp_red::emergency_light</light_name>
    <default_state>
      <color>0.3 0.0 0.0 1</color>
      <intensity>0.0</intensity>
    </default_state>
  </led>
```

The snippet above describes an LED using the `<led>` element. Each LED can be described using a visual and/or light entity by specifying the entity's scoped name in `<visual_name>` and `<light_name>` elements

A `<default_state>` element is used when the LED is inactive or .reset

```xml
  <startup_mode>ready</startup_mode>

  <!-- Mode Descriptions -->
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
```

This snippet specifies the `<startup_mode>` which is set by default and used when the simulation starts. If no startup mode is specified, the first described mode is used as the startup mode by default.

An LED Mode (in this case "ready" mode) is defined using a `<mode>` tag. This specific mode specifies the `ready_led` as the only active LED using the `<active_leds>` tag. If no active LEDs are specified, all the LEDs are used by default. The actual behavior of the mode is defined using the `<step>` tags which are played sequentially by the plugin in the order they are described.

A `<step>` can be described using the following 4 properties:
- **`always_on` attribute**: If set to true, this step stays on indefinitely and the mode does not move on to the next step. This can be used to define static LED behaviours.
- **`<color>`**: This is the color which is set to the LED (visual and/or light) during this step.
- **`<intensity>`**: This is the intensity which is set to the light during the step. This has no effect on the visual element of the LED. Intensity can be set to 0.0 if no light illumination is required during a step.
- **`<on_time>`**: This is the duration in seconds for which the step stays on. For instance, in this scenario the ready mode defines 2 steps both which stay on for 1 second giving a blinking behavior for the LED.

### Changing LED Modes at Runtime

You can use the `gz service` command to call the service from a CLI:

```bash
gz service -s /led_group_name/change_led_mode --req-type gz.msgs.StringMsg --rep-type gz.msgs.Boolean -r "data: 'mode_name'"
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Jasmeet Singh - jasmeet0915@gmail.com

## Support

For issues, questions, or suggestions, please open an issue on the project repository.
