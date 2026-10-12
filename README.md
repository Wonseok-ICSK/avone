# avone: ROS 2 Vision and Actuator Prototype

Python ROS 2 package for capture-card image input, speed OCR, lane detection, YOLO object detection, keyboard cruise commands and Jetson GPIO actuator experiments.

## Package map

| Path | Purpose |
| --- | --- |
| `avone/image_publisher.py` | Capture frames and publish `video_frames` |
| `avone/speed_publisher.py` | OCR a fixed speedometer ROI and publish `spd` |
| `avone/lane_detector.py` | Lane detection and `steerCmd` publication |
| `avone/vehicle_publisher.py` | YOLO detections and `frontVeh` publication |
| `avone/cruise_control.py` | Interactive curses UI; publishes `cruiseCmd` and `target_speed` |
| `avone/motor_control.py` | Subscribe to commands and drive GPIO PWM |
| `launch/auto_launch.py` | Combined launch description |
| `setup.py`, `package.xml`, `resource/avone` | ROS package metadata and executable registration |
| `avone/instruction.xml` | Original installation notes (plain text despite the extension) |
| `docs/README.original.ko.md` | Original Korean README, preserved byte for byte |

## Target environment

The existing notes target Linux on NVIDIA Jetson with ROS 2 Foxy. ROS packages `rclpy`, `std_msgs`, `sensor_msgs`, `cv_bridge`, `launch` and `launch_ros` must come from a compatible ROS installation. The system Tesseract executable is also required for OCR.

`requirement.txt` lists Python package dependencies inferred from imports. Install them within a Jetson/ROS-compatible environment, keeping OpenCV, NumPy, PyTorch/CUDA and `cv_bridge` ABI compatibility in mind. It is not a tested Jetson environment lockfile. A preinstalled Jetson OpenCV build may be preferable to a generic pip wheel.

```console
python -m pip install -r requirement.txt
# Place this package under a configured ROS 2 workspace's src directory.
colcon build --packages-select avone
source install/setup.bash
```

## Baseline integration issues

The imported launch file requests an unregistered `vehicle_detector` executable and uses `vehicle_publisher` where the motor node is described. The vehicle subscriber listens on `camera_frame`, unlike the active image publisher. The detector uses an older results access pattern with `ultralytics.YOLO`. Motor initialization creates `self.pwm`, whereas throttle control expects `self.throttle_pwm`; normalization also divides by a target speed initially set to zero.

These issues are preserved in `phase1-original` and are candidates for the second, limited correction pass. Pixel ROIs, GPIO pins, actuator calibration, steering/throttle formulas and detection policy remain application-specific. The curses UI requires a real interactive terminal; a combined launch is not a verified replacement for that terminal.

This is a prototype for code review. No connected actuators, camera, ROS graph or GPU inference were exercised during preparation. Review and calibrate the hardware configuration before runtime validation.

## Review history

- `phase1-original`: the selected source files were imported byte for byte; only repository documentation, dependency lists and Git housekeeping files were added.
- A subsequent update adds English review comments and narrowly scoped fixes. Compare it with `phase1-original` to review the changes.
- Original directory names and sample variants are retained. Source extracted from top-level ZIP files is under `archived-examples/` when present.
- Build outputs, local IDE state, packet captures, datasets, model weights and generated analysis results are excluded. This is a source review repository, not a complete runtime distribution.

## Validation scope

Python source was syntax-checked with Python 3.13 without executing the scripts. Device communication, network traffic, Vehicle Spy integration, Jetson GPIO and full dataset analyses were not run during import. The dependency list, where supplied, is inferred from imports rather than a recovered environment lockfile.

Existing vendor copyright and license notices are retained. No new project-wide license has been assigned.
