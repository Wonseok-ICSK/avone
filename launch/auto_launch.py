# Launch the six executables registered by setup.py.
# The curses cruise UI still requires interactive-terminal handling at runtime.
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # img publissher
        Node(
            package='avone',
            executable='image_publisher',
            name='image_publisher', 
            output='screen'
        ),

        # 속도 인식 노드
        Node(
            package='avone',  # 패키지 이름
            executable='speed_publisher',  # 속도 인식 노드의 실행 파일 이름
            name='speed_publisher', 
            output='screen'
        ),
        
        # 차선 이탈 방지 노드
        Node(
            package='avone',
            executable='lane_detector',
            name='lane_detector', 
            output='screen'
        ),
        
        # 전방 차량 감지 노드
        Node(
            package='avone',
            executable='vehicle_publisher',
            name='vehicle_publisher',
            output='screen'
        ),
        
        # 크루즈 제어 노드
        Node(
            package='avone',
            executable='cruise_control',
            name='cruise_control', 
            output='screen'
        ),
        
        # Motor control uses its own registered entry point.
        Node(
            package='avone',
            executable='motor_control',
            name='motor_control',
            output='screen'
        ),
    ])