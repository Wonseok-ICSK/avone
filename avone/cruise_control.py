# Interactive ROS cruise-command UI; run curses in a real terminal.
# The current speed is sampled once when cruise is enabled.
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, Bool
import curses  # curses 라이브러리

class CruiseControl(Node):
    def __init__(self):
        super().__init__('cruise_control')
        self.target_speed = 0
        self.cruise_status = False  # 크루즈 컨트롤 상태

        self.speed_subscriber = None  # 구독자를 나중에 생성
        # 퍼블리셔
        self.cruise_publisher = self.create_publisher(Bool, 'cruiseCmd', 10)
        self.speed_publisher = self.create_publisher(Int32, 'target_speed', 10)

    def start_speed_subscription(self):
        # 'spd' 토픽에서 속도값을 한 번 구독하기 위해 구독자 생성
        if not self.speed_subscriber:
            self.get_logger().info('Speed Subscription Started')
            self.speed_subscriber = self.create_subscription(
                Int32,
                'spd',
                self.speed_callback,
                10
            )

    def stop_speed_subscription(self):
        # 구독 중지하여 더 이상 속도를 받아오지 않음
        if self.speed_subscriber:
            self.destroy_subscription(self.speed_subscriber)
            self.speed_subscriber = None
            self.get_logger().info('Speed Subscription Stopped')

    def speed_callback(self, msg):
        # 현재 주행 속도를 'spd' 토픽에서 구독하고, 5kph 단위로 반올림
        self.target_speed = round(msg.data / 5) * 5
        self.get_logger().info(f'Initial Speed Set (Rounded): {self.target_speed} kph')
        # 처음 크루즈 시작 시 속도 발행
        self.speed_publisher.publish(Int32(data=self.target_speed))
        # 구독을 중지하여 더 이상 속도 업데이트가 일어나지 않도록
        self.stop_speed_subscription()

    def process_command(self, key):
        """키 입력에 따라 크루즈 컨트롤 동작 제어"""
        if key == ord('s'):  # Start cruise control
            if not self.cruise_status:
                self.cruise_status = True
                self.start_speed_subscription()  # 속도 구독을 시작하여 속도를 가져옴
                self.cruise_publisher.publish(Bool(data=True))
                self.get_logger().info('Cruise control activated.')

        elif key == ord('x'):  # Stop cruise control
            if self.cruise_status:
                self.cruise_status = False
                self.cruise_publisher.publish(Bool(data=False))
                self.get_logger().info('Cruise control deactivated.')

        elif key == ord('u'):  # Increase speed
            if self.cruise_status:
                self.target_speed += 5
                self.speed_publisher.publish(Int32(data=self.target_speed))
                self.get_logger().info(f'Speed increased to {self.target_speed} kph.')
            else:
                self.get_logger().info('Cruise control deactivated.')

        elif key == ord('d'):  # Decrease speed
            if self.cruise_status:
                self.target_speed = max(0, self.target_speed - 5)
                self.speed_publisher.publish(Int32(data=self.target_speed))
                self.get_logger().info(f'Speed decreased to {self.target_speed} kph.')
            else:
                self.get_logger().info('Cruise control deactivated.')

def curses_main(stdscr, cruise_control):
    """curses 환경에서 키 입력을 처리하는 메인 함수"""
    stdscr.clear()
    stdscr.nodelay(True)  # 키 입력을 비차단 모드로 설정
    stdscr.addstr(0, 0, "Press 's' to Start, 'x' to Stop, 'u' to Speed Up, 'd' to Slow Down, 'q' to Quit")
   
    while rclpy.ok():
        try:
            key = stdscr.getch()  # 키 입력 읽기
            if key != -1:  # 키가 입력되었는지 확인
                if key == ord('q'):  # 'q'를 누르면 종료
                    break
                cruise_control.process_command(key)
            rclpy.spin_once(cruise_control, timeout_sec=0.1)  # ROS 노드 처리
        except KeyboardInterrupt:
            break

def main(args=None):
    rclpy.init(args=args)
    cruise_control = CruiseControl()

    try:
        curses.wrapper(curses_main, cruise_control)  # curses 환경 실행
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()




"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, String, Bool

class CruiseControl(Node):
    def __init__(self):
        super().__init__('cruise_control')
        self.current_speed = 0
        self.target_speed = 50  # 초기 속도는 50으로 설정 (혹시 구독이 좀 늦게 오더라도 일단.. 구독한 속도로 갱신됨)
        self.cruise_active = False  # 크루즈 컨트롤 활성화 상태
        
        self.speed_subscriber = None  # 구독자를 나중에 생성

        # 퍼블리셔: 크루즈 상태 발행
        self.cruise_publisher = self.create_publisher(Bool, 'cruise_status', 10)
        
        # 퍼블리셔: 속도 설정 발행
        self.speed_publisher = self.create_publisher(Int32, 'target_speed', 10)

        self.get_logger().info(f'Cruise Control Initialized')

    def start_speed_subscription(self):
        # 'spd' 토픽에서 속도값을 한 번 구독하기 위해 구독자 생성
        if not self.speed_subscriber:
            self.get_logger().info('Speed Subscription Started')
            self.speed_subscriber = self.create_subscription(
                Int32,
                'spd',
                self.speed_callback,
                10
            )

    def stop_speed_subscription(self):
        # 구독 중지하여 더 이상 속도를 받아오지 않음
        if self.speed_subscriber:
            self.destroy_subscription(self.speed_subscriber)
            self.speed_subscriber = None
            self.get_logger().info('Speed Subscription Stopped')

    def speed_callback(self, msg):
        # 현재 주행 속도를 'spd' 토픽에서 구독하고, 5kph 단위로 반올림
        self.target_speed = round(msg.data / 5) * 5
        self.get_logger().info(f'Initial Speed Set (Rounded): {self.target_speed} kph')
        # 처음 크루즈 시작 시 속도 발행
        self.speed_publisher.publish(Int32(data=self.target_speed))
        # 구독을 중지하여 더 이상 속도 업데이트가 일어나지 않도록
        self.stop_speed_subscription()

    def set_cruise_control(self, command):
        if command == 's':  # Start
            if not self.cruise_active:
                self.cruise_active = True
                self.get_logger().info('Activating Cruise Control...')
                self.start_speed_subscription()  # 속도 구독을 시작하여 속도를 가져옴
                # 크루즈 시작 시 현재 속도 먼저 발행 (속도 구독이 끝난 후 발행됨)
                self.cruise_publisher.publish(Bool(data=True))
        elif command == 'x':  # Stop
            if self.cruise_active:
                self.cruise_active = False
                self.cruise_publisher.publish(Bool(data=False))
                self.get_logger().info('Cruise Control Deactivated')

    def adjust_speed(self, adjustment):
        if adjustment == 'u':  # Speed Up
            self.target_speed += 5  # 5kph 증가
            self.get_logger().info(f'Speed Increased to {self.target_speed} kph')
            self.speed_publisher.publish(Int32(data=self.target_speed))  # 업데이트된 속도 발행
        elif adjustment == 'd':  # Speed Down
            self.target_speed = max(0, self.target_speed - 5)  # 5kph 감소, 0 이하로는 줄이지 않음
            self.get_logger().info(f'Speed Decreased to {self.target_speed} kph')
            self.speed_publisher.publish(Int32(data=self.target_speed))  # 업데이트된 속도 발행

def main(args=None):
    rclpy.init(args=args)
    cruise_control = CruiseControl()

    def handle_input():
        while rclpy.ok():
            command = input("Enter command (s: start, x: stop, u: increase, d: decrease): ").strip().lower()
            if command == 's' or command == 'x':
                cruise_control.set_cruise_control(command)
            elif command == 'u' or command == 'd':
                cruise_control.adjust_speed(command)
            else:
                print("Invalid command. Use 's', 'x', 'u', or 'd'.")

    try:
        # 비동기식으로 입력 처리
        import threading
        input_thread = threading.Thread(target=handle_input, daemon=True)
        input_thread.start()

        rclpy.spin(cruise_control)

    except KeyboardInterrupt:
        cruise_control.get_logger().info('Shutting down Cruise Control')
    finally:
        cruise_control.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
"""

'''
이건 리펙토링용 코드? 위 코드가 작동되지 않을떄 사용함직한 코드
주요 변경 사항:
1. current_speed: spd 토픽을 구독한 결과를 저장하는 변수입니다. 구독한 현재 속도가 이 변수에 실시간으로 업데이트됩니다.
2. target_speed: 크루즈 컨트롤이 활성화될 때(s 입력) 현재 속도를 target_speed로 설정합니다. 이후 속도는 u나 d 명령을 통해서만 변경되며, 구독된 현재 속도에는 영향을 받지 않습니다.
3. 구독 유지: 속도 구독(speed_subscriber)은 계속 유지되며, 구독된 속도는 current_speed에 반영되지만, target_speed에는 영향을 미치지 않도록 분리되어 있습니다.


import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, String

class CruiseControl(Node):
    def __init__(self):
        super().__init__('cruise_control')
        
        self.target_speed = 0  # 크루즈 컨트롤을 위한 목표 속도
        self.current_speed = 0  # 현재 속도를 저장하는 변수
        self.cruise_active = False  # 크루즈 컨트롤 활성화 상태
        self.speed_subscriber = None  # 구독자 (지속적으로 구독 유지)

        # 퍼블리셔: 크루즈 상태 발행
        self.cruise_publisher = self.create_publisher(String, 'cruise_status', 10)
        
        # 퍼블리셔: 속도 설정 발행
        self.speed_publisher = self.create_publisher(Int32, 'target_speed', 10)

        # 현재 속도 구독 (항상 구독)
        self.speed_subscriber = self.create_subscription(
            Int32,
            'spd',
            self.speed_callback,
            10
        )

        self.get_logger().info(f'Cruise Control Initialized')

    def speed_callback(self, msg):
        # 'spd' 토픽에서 현재 속도를 구독하고 current_speed에 저장
        self.current_speed = msg.data
        self.get_logger().info(f'Current Speed: {self.current_speed} kph')

    def set_cruise_control(self, command):
        if command == 's':  # Start
            if not self.cruise_active:
                self.cruise_active = True
                self.get_logger().info('Activating Cruise Control...')
                # 크루즈 시작 시 현재 속도를 목표 속도로 설정
                self.target_speed = round(self.current_speed / 5) * 5  # 5km/h 단위로 반올림
                self.get_logger().info(f'Initial Target Speed Set: {self.target_speed} kph')
                self.cruise_publisher.publish(String(data='Cruise Started'))
                self.speed_publisher.publish(Int32(data=self.target_speed))  # 목표 속도 발행
        elif command == 'x':  # Stop
            if self.cruise_active:
                self.cruise_active = False
                self.cruise_publisher.publish(String(data='Cruise Stopped'))
                self.get_logger().info('Cruise Control Deactivated')

    def adjust_speed(self, adjustment):
        if adjustment == 'u':  # Speed Up
            self.target_speed += 5  # 5kph 증가
            self.get_logger().info(f'Speed Increased to {self.target_speed} kph')
            self.speed_publisher.publish(Int32(data=self.target_speed))  # 업데이트된 속도 발행
        elif adjustment == 'd':  # Speed Down
            self.target_speed = max(0, self.target_speed - 5)  # 5kph 감소, 0 이하로는 줄이지 않음
            self.get_logger().info(f'Speed Decreased to {self.target_speed} kph')
            self.speed_publisher.publish(Int32(data=self.target_speed))  # 업데이트된 속도 발행

def main(args=None):
    rclpy.init(args=args)
    cruise_control = CruiseControl()

    def handle_input():
        while rclpy.ok():
            command = input("Enter command (s: start, x: stop, u: increase, d: decrease): ").strip().lower()
            if command == 's' or command == 'x':
                cruise_control.set_cruise_control(command)
            elif command == 'u' or command == 'd':
                cruise_control.adjust_speed(command)
            else:
                print("Invalid command. Use 's', 'x', 'u', or 'd'.")

    try:
        # 비동기식으로 입력 처리
        import threading
        input_thread = threading.Thread(target=handle_input, daemon=True)
        input_thread.start()

        rclpy.spin(cruise_control)

    except KeyboardInterrupt:
        cruise_control.get_logger().info('Shutting down Cruise Control')
    finally:
        cruise_control.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()



'''