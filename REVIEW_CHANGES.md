# Second-pass Review Notes

Baseline: [`phase1-original`](https://github.com/Wonseok-ICSK/avone/tree/phase1-original). The updated source is tagged `phase2-reviewed`.

## Scope

English explanations were added to 10 application/example files. Existing Korean comments, user-facing strings, directory names and historical variants were retained. No large refactor or new runtime feature was introduced.

## Corrections

- `avone/motor_control.py`: Initialize the same throttle PWM attribute used by control and cleanup.
- `avone/motor_control.py`: Return zero throttle when the target speed is nonpositive instead of dividing by zero.
- `avone/motor_control.py`: Stop the steering PWM alongside the other channels during normal cleanup.
- `launch/auto_launch.py`: Use the vehicle detection executable actually registered in setup.py.
- `launch/auto_launch.py`: Launch motor_control once instead of launching a second vehicle detector.
- `avone/vehicle_publisher.py`: Explain the image-topic contract in English.
- `avone/vehicle_publisher.py`: Connect vehicle detection to the topic used by the active image publisher.
- `avone/vehicle_publisher.py`: Read bounding boxes from the Ultralytics Results list rather than the older YOLOv5 attribute.
- `avone/speed_publisher.py`: Skip an empty speedometer crop instead of passing it to OpenCV color conversion.

## Validation

Eight unittest methods passed with fake ROS, GPIO, OCR, camera and inference interfaces: throttle initialization, nonpositive target, PWM cleanup, registered launch executables, detector topic/results shape, no detections, empty OCR crop and valid OCR output.

```console
python -m unittest discover -s test -p test_review_fixes.py -v
```

These are host-side logic checks. The original ament lint templates require ROS tooling and were not run. No ROS graph, Jetson device, camera, downloaded weights, CUDA inference or physical PWM output was used.

## Remaining review items

Control gains, pin mapping and actuator calibration remain unverified. The detector retains its first-object policy, unfiltered classes and crop/full-frame coordinate mismatch; these require a separate behavior review. The curses node still needs an interactive terminal. package.xml retains its original incomplete dependency metadata; the root requirement.txt and README document the environment rather than migrating ROS versions or package metadata.

The detection result shape follows [Ultralytics prediction documentation](https://docs.ultralytics.com/modes/predict).

## Commented files

- `avone/cruise_control.py`
- `avone/image_publisher.py`
- `avone/lane_detector.py`
- `avone/motor_control.py`
- `avone/speed_publisher.py`
- `avone/vehicle_publisher.py`
- `avone/testLed.py`
- `avone/sampleCode.py`
- `launch/auto_launch.py`
- `setup.py`
