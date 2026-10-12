# Consume ROS cruise, speed, steering and object-state commands to drive PWM.
# GPIO mappings and control gains require target-specific calibration.
import Jetson.GPIO as GPIO
from std_msgs.msg import Int32, String, Bool
import rclpy
import math
from rclpy.node import Node

# 아직 구현 시작도 안한거..

class MotorControl(Node):
    def __init__(self):
        super().__init__('motor_control')
        self.target_speed = 0
        self.current_speed = 0
        self.cruise_status = False
        self.steerCmd = 'center' # left, right, center
        self.frontVehicle = 'None' # None, Neutral, Brake

        self.frontVeh_subscriber = self.create_subscription(String, 'frontVeh', self.frontVeh_callback, 10)
        self.targetSpeed_subscriber = self.create_subscription(Int32, 'target_speed', self.targetspd_callback, 10)
        self.steerCmd_subscriber = self.create_subscription(String, 'steerCmd', self.steer_callback, 10)
        self.cruiseState_subscriber = self.create_subscription(Bool, 'cruiseCmd', self.cruiseStat_callback, 10)
        self.speed_subscriber = self.create_subscription(Int32, 'spd', self.speed_callback, 10)

        # 수정해야할 코드. 처음 GPIO 세팅
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.OUT)  # 스로틀 제어 PWM 핀 설정
        self.throttle_pwm = GPIO.PWM(18, 100)
        self.throttle_pwm.start(0)

        GPIO.setup(19, GPIO.OUT)  # 브레이크 제어 PWM 핀 설정
        self.brake_pwm = GPIO.PWM(19, 100)
        self.brake_pwm.start(0)

        GPIO.setup(20, GPIO.OUT)  # 스티어링 제어 PWM 핀 설정
        self.steer_pwm = GPIO.PWM(20, 50)  # 50Hz PWM (서보 모터에 적합)
        self.steer_pwm.start(7.5)  # 기본 중앙값 (7.5는 중앙 위치)

    def targetspd_callback(self, msg): 
        self.target_speed = msg.data

    def steer_callback(self, msg):
        self.steerCmd = msg.data

    def frontVeh_callback(self, msg):
        self.frontVehicle = msg.data

    def cruiseStat_callback(self, msg):
        self.cruise_status = msg.data

    def speed_callback(self, msg):
        self.current_speed = msg.data

    def calculate_throttle(self, speed_diff):
        """속도 차이를 기반으로 스로틀 개도량 계산"""
        # The target starts at zero and may be reduced to zero by the UI.
        if self.target_speed <= 0:
            return 0.0
        max_throttle = 100
        normalized_diff = min(max(speed_diff / self.target_speed, -1), 1)  # 속도 차이 정규화
        throttle_value = max_throttle * (0.5 * (math.tanh(normalized_diff) + 1))  # tanh로 자연스러운 가속 제어
        return throttle_value

    def apply_throttle(self, throttle_value):
        """스로틀 개도량 적용"""
        self.throttle_pwm.ChangeDutyCycle(throttle_value)
        self.get_logger().info(f'Applying throttle: {throttle_value}%')

    def apply_brake(self, brake_value):
        """브레이크 개도량 적용"""
        self.brake_pwm.ChangeDutyCycle(brake_value)
        self.get_logger().info(f'Applying brake: {brake_value}%')

    def apply_steering(self):
        """스티어링 제어 로직"""
        max_steering_angle = 15  # 최대 스티어링 각도 (예: -15도 ~ +15도)
        steering_factor = max(0.1, 1 - (self.current_speed / 100))  # 속도에 따라 조향 각도 감소. 적절히 조절할 것 --> 이건 기계과 애들 조향각 공식 같은거 도움 받을 필요 있음
        if self.steerCmd == 'left':
            steering_angle = -max_steering_angle * steering_factor
        elif self.steerCmd == 'right':
            steering_angle = max_steering_angle * steering_factor
        else:
            steering_angle = 0

        pwm_value = 7.5 + (steering_angle / 90) * 2.5 # 서보 모터 기준 0도 = 7.5, -15도 = 5, +15도 = 10으로 가정
        self.steer_pwm.ChangeDutyCycle(pwm_value)
        self.get_logger().info(f'Steering angle: {steering_angle} degrees, PWM: {pwm_value}')

    def control_vehicle(self):
        """차량 제어 로직: 스로틀 및 브레이크 개도량 결정"""
        if self.cruise_status:
            #turn led on
            pass

        if not self.cruise_status:
            # 크루즈 컨트롤이 비활성화된 경우, 아무 동작도 하지 않음
            self.get_logger().info('Cruise control is off. No action taken.')
            self.apply_throttle(0)  # 스로틀 해제
            self.apply_brake(0)     # 브레이크 해제
            
            # release LED Light

            return

        if self.frontVehicle == 'None' or self.frontVehicle == 'Neutral':
            self.apply_brake(0)  # 브레이크 해제
            # 앞에 차량이 없거나 멀리 있을 때, 스로틀 제어
            speed_diff = self.target_speed - self.current_speed
            throttle_value = self.calculate_throttle(speed_diff)
            self.apply_throttle(throttle_value)
        
        elif self.frontVehicle == 'Brake':
            # 앞 차량이 가까운 경우 브레이크 작동
            self.apply_throttle(0)  # 스로틀 해제
            self.apply_brake(100)  # 브레이크 100% 작동

        self.apply_steering()
    

def main(args=None):
    rclpy.init(args=args)
    motor_control = MotorControl()

    try:
        while rclpy.ok():
            motor_control.control_vehicle()  # 차량 제어 함수 호출
            rclpy.spin_once(motor_control, timeout_sec=0.1)  # 주기적으로 노드 처리 (10fps)
    except KeyboardInterrupt:
        pass
    finally:
        motor_control.throttle_pwm.stop()
        motor_control.brake_pwm.stop()
        motor_control.steer_pwm.stop()
        GPIO.cleanup()
        rclpy.shutdown()

if __name__ == '__main__':
    main()