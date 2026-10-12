
"""
# Test code, using video img to lauch programs
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge
import os

class VideoPublisher(Node):
    def __init__(self):
        super().__init__('video_publisher')

        # 퍼블리셔 생성: 'camera_frame' 토픽에 이미지 발행
        self.publisher_ = self.create_publisher(Image, 'camera_frame', 10)

        # OpenCV와 ROS 간의 이미지 변환을 위한 CvBridge 객체
        self.bridge = CvBridge()
        print(os.getcwd())
        # 비디오 파일 경로 (테스트용 녹화된 영상 경로 설정)
        video_path = '/home/user/ros2_ws/src/avone/avone/video/video.mp4' # 경로를 실제 파일 경로로 바꿔주세요

        # 비디오 캡처 객체
        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            self.get_logger().error(f"Cannot open video file: {video_path}")
            return

        # 타이머 설정: 1초에 2번씩 프레임을 발행 (0.5초 간격)
        self.timer = self.create_timer(0.5, self.publish_frame)

        self.get_logger().info("Video Publisher Node Initialized")

    def publish_frame(self):
        ret, frame = self.cap.read()

        if ret:
            # OpenCV 이미지 -> ROS 메시지로 변환
            ros_image = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            cv2.imshow('windows', frame)
            # 이미지 퍼블리시
            self.publisher_.publish(ros_image)
            self.get_logger().info('Publishing video frame')

        else:
            # 영상이 끝났다면 타이머 중지
            self.get_logger().info('End of video stream')
            self.timer.cancel()
            self.cap.release()

def main(args=None):
    rclpy.init(args=args)
    video_publisher = VideoPublisher()

    try:
        rclpy.spin(video_publisher)
    except KeyboardInterrupt:
        video_publisher.get_logger().info('Shutting down Video Publisher')
    finally:
        video_publisher.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()





""" #Real Code

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class ImagePublisher(Node):
    def __init__(self):
        super().__init__('image_publisher')
        self.publisher_ = self.create_publisher(Image, 'video_frames', 10) # 10 == queue (5sec queue)
        self.timer = self.create_timer(0.2, self.timer_callback)  # 2fps (0.5초 간격) 나중에 반응 속도 문제되면 올릴 것..
        self.device_index = 0
        self.cap = cv2.VideoCapture(self.device_index)  # 캡처카드로부터 영상 입력
        self.bridge = CvBridge()  # OpenCV 이미지 -> ROS 이미지 변환용
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    def timer_callback(self):
        ret, frame = self.cap.read()  # 영상 프레임 읽기
        if ret: # 뭔갈 읽어옴
            # cv2.imshow('test', frame)
            # OpenCV 이미지 -> ROS 메시지로 변환
            image_message = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            self.publisher_.publish(image_message)  # 'video_frames' 토픽에 퍼블리시
            #self.get_logger().info('Publishing video frame')
            self.get_logger().info(f"Frame received: {frame.shape}")
        else:
            self.get_logger().warn('Can not reading a image from capture card')

def main(args=None):
    rclpy.init(args=args)
    image_publisher = ImagePublisher()
    rclpy.spin(image_publisher)
    image_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()