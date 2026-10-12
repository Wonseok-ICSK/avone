"""Regression checks with fake ROS, GPIO, camera and inference interfaces.

Run directly with unittest; no Jetson, ROS installation or network is needed.
"""
import ast
import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


class Message:
    def __init__(self, data=None): self.data = data


class FakeNode:
    def __init__(self, name):
        self.subscriptions = []
        self.publisher = types.SimpleNamespace(messages=[])
        self.publisher.publish = self.publisher.messages.append
        self.logger = Mock()

    def create_subscription(self, kind, topic, callback, depth):
        self.subscriptions.append(topic)
        return topic

    def create_publisher(self, *args): return self.publisher
    def get_logger(self): return self.logger
    def destroy_node(self): pass


class FakePWM:
    def __init__(self, pin, hz):
        self.pin, self.hz = pin, hz
        self.duty = None
        self.stopped = False

    def start(self, duty): self.duty = duty
    def ChangeDutyCycle(self, duty): self.duty = duty
    def stop(self): self.stopped = True


class ReviewFixTests(unittest.TestCase):
    def setUp(self):
        self.pwms = []
        self.gpio = types.ModuleType('Jetson.GPIO')
        self.gpio.BCM, self.gpio.OUT = 1, 2
        self.gpio.setmode = Mock()
        self.gpio.setup = Mock()
        self.gpio.cleanup = Mock()

        def pwm(pin, hz):
            obj = FakePWM(pin, hz)
            self.pwms.append(obj)
            return obj

        self.gpio.PWM = pwm
        self.cv2 = types.ModuleType('cv2')
        self.cv2.COLOR_BGR2GRAY = 1
        self.cv2.cvtColor = Mock(return_value=np.zeros((25, 38)))
        ros = types.ModuleType('rclpy')
        ros.init, ros.shutdown = Mock(), Mock()
        ros.ok = lambda: False
        ros_node = types.ModuleType('rclpy.node')
        ros_node.Node = FakeNode
        std = types.ModuleType('std_msgs.msg')
        std.Int32 = std.String = std.Bool = Message
        sensor = types.ModuleType('sensor_msgs.msg')
        sensor.Image = Message
        bridge = types.ModuleType('cv_bridge')
        bridge.CvBridge = lambda: types.SimpleNamespace(imgmsg_to_cv2=lambda frame, encoding: frame)
        ultra = types.ModuleType('ultralytics')
        ultra.YOLO = lambda weights: lambda frame: [types.SimpleNamespace(boxes=types.SimpleNamespace(data=[]))]
        ocr = types.ModuleType('pytesseract')
        ocr.image_to_string = Mock(return_value='42')
        launch = types.ModuleType('launch')
        launch.LaunchDescription = list
        actions = types.ModuleType('launch_ros.actions')
        actions.Node = lambda **kwargs: kwargs
        jetson = types.ModuleType('Jetson')
        jetson.GPIO = self.gpio
        self.modules = {
            'Jetson': jetson, 'Jetson.GPIO': self.gpio,
            'rclpy': ros, 'rclpy.node': ros_node,
            'std_msgs': types.ModuleType('std_msgs'), 'std_msgs.msg': std,
            'sensor_msgs': types.ModuleType('sensor_msgs'), 'sensor_msgs.msg': sensor,
            'cv_bridge': bridge, 'cv2': self.cv2, 'ultralytics': ultra,
            'pytesseract': ocr, 'launch': launch,
            'launch_ros': types.ModuleType('launch_ros'), 'launch_ros.actions': actions,
        }
        self.patch = patch.dict(sys.modules, self.modules)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def load(self, relative):
        spec = importlib.util.spec_from_file_location('review_' + Path(relative).stem, ROOT / relative)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_throttle_attribute_is_initialized_and_used(self):
        node = self.load('avone/motor_control.py').MotorControl()
        node.apply_throttle(25)
        self.assertEqual(node.throttle_pwm.duty, 25)
        self.assertEqual(node.throttle_pwm.pin, 18)

    def test_nonpositive_target_requests_zero_throttle(self):
        node = self.load('avone/motor_control.py').MotorControl()
        for target in (0, -5):
            node.target_speed = target
            self.assertEqual(node.calculate_throttle(10), 0)
        node.target_speed = 50
        self.assertAlmostEqual(node.calculate_throttle(0), 50)

    def test_normal_shutdown_stops_all_three_pwms(self):
        self.load('avone/motor_control.py').main()
        self.assertEqual(len(self.pwms), 3)
        self.assertTrue(all(pwm.stopped for pwm in self.pwms))
        self.gpio.cleanup.assert_called_once()

    def test_launch_matches_registered_executables_once_each(self):
        tree = ast.parse((ROOT / 'setup.py').read_text(encoding='utf-8-sig'))
        setup = next(n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, 'id', None) == 'setup')
        value = next(k.value for k in setup.keywords if k.arg == 'entry_points')
        expected = [s.split('=')[0].strip() for s in ast.literal_eval(value)['console_scripts']]
        launched = self.load('launch/auto_launch.py').generate_launch_description()
        self.assertCountEqual([n['executable'] for n in launched], expected)

    def test_vehicle_topic_and_ultralytics_results_list(self):
        node = self.load('avone/vehicle_publisher.py').VehiclePublisher()
        self.assertEqual(node.subscriptions, ['video_frames'])
        node.model = lambda frame: [types.SimpleNamespace(boxes=types.SimpleNamespace(data=[[0, 1, 10, 20, .9, 2]]))]
        node.image_callback(np.zeros((1080, 1920, 3), dtype=np.uint8))
        self.assertEqual(node.publisher.messages[-1].data, 'Neutral')

    def test_no_boxes_publishes_no_object(self):
        node = self.load('avone/vehicle_publisher.py').VehiclePublisher()
        node.image_callback(np.zeros((1080, 1920, 3), dtype=np.uint8))
        self.assertEqual(node.publisher.messages[-1].data, 'None')

    def test_small_frame_skips_empty_speed_crop(self):
        node = self.load('avone/speed_publisher.py').SpeedSubscriber()
        node.listener_callback(np.zeros((100, 100, 3), dtype=np.uint8))
        self.cv2.cvtColor.assert_not_called()
        self.assertEqual(node.publisher.messages, [])

    def test_valid_speed_crop_publishes_ocr_value(self):
        node = self.load('avone/speed_publisher.py').SpeedSubscriber()
        node.listener_callback(np.zeros((1080, 1920, 3), dtype=np.uint8))
        self.assertEqual(node.publisher.messages[-1].data, 42)


if __name__ == '__main__':
    unittest.main()
