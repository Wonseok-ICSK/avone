import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
from ultralytics import YOLO

class VehiclePublisher(Node):
    def __init__(self):
        super().__init__('vehicle_publisher')

        # 퍼블리셔 생성: 'frontVeh' 토픽으로 차량 상태 발행
        self.publisher_ = self.create_publisher(String, 'frontVeh', 10)

        # YOLOv8 모델 로드 (사전 훈련된 가중치 사용)
        self.model = YOLO("yolov8n.pt")  # YOLOv8 모델 로드

        # cv_bridge 객체 생성
        self.bridge = CvBridge()

        # 'camera_frame' 토픽에서 이미지 구독
        self.subscription = self.create_subscription(
            Image,
            'camera_frame',
            self.image_callback,
            10
        )
        self.subscription  # 방금 구독한 내용을 기록하기 위한 변수
        
        self.get_logger().info('Vehicle Publisher Node Initialized')

    def image_callback(self, msg):
        # ROS Image 메시지를 OpenCV 이미지로 변환
        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")

        # 프레임 크기 얻기
        height, width, _ = frame.shape

        # 차선 영역(ROI) 설정: 차선 밖 좌우 영역 제외, 하단 1/3은 후드라서 제외
        roi_top = 500 # 상단 1/3
        roi_bottom = 593
        roi_left = 530  # 좌측 1/3
        roi_right = 1390

        # ROI 적용하여 관심 영역 자르기
        roi = frame[roi_top:roi_bottom, roi_left:roi_right]

        # YOLOv8로 객체 탐지
        results = self.model(roi)

        vehicle_detected = False  # 객체 탐지 여부 플래그

        # 탐지된 객체 처리 (클래스 ID 필터링 제거)
        for result in results.xyxy[0]:
            xmin, ymin, xmax, ymax, conf, cls = result

            # 객체의 y좌표 비율을 기준으로 화면 상의 위치를 판단
            vehicle_y_center = (ymin + ymax) / 2

            # 상단 1/3에 객체가 있으면 멀리 있음
            if vehicle_y_center < height / 3:
                self.publisher_.publish(String(data="Neutral"))  # 멀리 있는 경우
                self.get_logger().info('Object detected in upper third: Neutral')

            # 중간 1/3에 객체가 있으면 가까움
            elif height / 3 <= vehicle_y_center < 2 * height / 3:
                self.publisher_.publish(String(data="Brake"))  # 가까운 경우
                self.get_logger().warn('Object detected in middle third: Brake')

            vehicle_detected = True
            break  # 첫 번째 객체만 처리하고 종료

        # 객체가 감지되지 않았을 때
        if not vehicle_detected:
            self.publisher_.publish(String(data="None"))
            self.get_logger().info('No object detected: None')

def main(args=None):
    rclpy.init(args=args)
    vehicle_publisher = VehiclePublisher()

    try:
        rclpy.spin(vehicle_publisher)
    except KeyboardInterrupt:
        vehicle_publisher.get_logger().info('Shutting down Vehicle Publisher')
    finally:
        vehicle_publisher.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
