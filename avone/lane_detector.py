# Detect lane segments inside a fixed image ROI and publish a steering direction.
# Pixel thresholds and debug image output reflect the original capture layout.
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
from std_msgs.msg import String

OFFSET = 50
# 사다리꼴 ROI 좌표 (이미지에 맞게 조정 필요)
TRAPEZOID_POINTS = np.array([
    (525, 725),  # 왼쪽 아래
    (825, 570),  # 왼쪽 위
    (1125, 570),  # 오른쪽 위
    (1425, 725)   # 오른쪽 아래
], dtype=np.int32)

MIN_SLOPE = 0.5
MAX_SLOPE = 5.0

class LaneSubscriber(Node):
    def __init__(self):
        super().__init__('lane_detector')
        self.subscription = self.create_subscription(
            Image,
            'video_frames',  # 'image_publisher'에서 발행하는 영상 토픽
            self.listener_callback,
            10)
        self.publisher_ = self.create_publisher(String, 'steerCmd', 10)
        self.bridge = CvBridge()

    def listener_callback(self, msg):
        # ROS Image 메시지를 OpenCV 이미지로 변환
        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

        # 사다리꼴 ROI 적용
        mask = np.zeros_like(frame)  # 원본 이미지와 동일한 크기의 빈 마스크 생성
        cv2.fillPoly(mask, [TRAPEZOID_POINTS], (255, 255, 255))  # 사다리꼴을 흰색으로 채움
        roi = cv2.bitwise_and(frame, mask)  # 마스크를 원본 이미지에 적용

        # 이미지 전처리: 그레이스케일로 변환 후 Canny 엣지 검출
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)  # Threshold 조정

        # Hough 변환으로 차선 검출
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=50, maxLineGap=30)

        # 차선의 중심을 추정하고 차선을 그리기
        if lines is not None:
            left_line_x = []
            right_line_x = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                slope = (y2 - y1) / (x2 - x1 + 1e-6)  # 기울기 계산 (0으로 나누기 방지)

                # 기울기 필터링 (차선으로 간주되는 기울기 범위 내의 선만 선택)
                if abs(slope) < MIN_SLOPE or abs(slope) > MAX_SLOPE:
                    continue

                if slope < 0:  # 왼쪽 차선
                    left_line_x.append(x1)
                    left_line_x.append(x2)
                else:  # 오른쪽 차선
                    right_line_x.append(x1)
                    right_line_x.append(x2)

                # 검출된 차선을 원본 프레임에 그림
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 녹색으로 차선 시각화

            # 왼쪽과 오른쪽 차선의 평균 X좌표 계산
            if left_line_x and right_line_x:
                left_avg_x = np.mean(left_line_x)
                right_avg_x = np.mean(right_line_x)

                # 차선의 중심 계산
                lane_center = (left_avg_x + right_avg_x) / 2
               
                # 차량의 현재 위치 (이미지의 중심 X좌표)
                frame_center = frame.shape[1] / 2

                # 차선 중심과 차량 중심의 차이 계산
                offset = lane_center - frame_center

                # 오프셋 값에 따라 조향 결정
                if offset > OFFSET:  # 차량이 왼쪽으로 치우쳐 있음 -> 오른쪽으로 조향 필요
                    self.publisher_.publish(String(data='right'))
                    self.get_logger().info('Steering Right')
                elif offset < -OFFSET:  # 차량이 오른쪽으로 치우쳐 있음 -> 왼쪽으로 조향 필요
                    self.publisher_.publish(String(data='left'))
                    self.get_logger().info('Steering Left')
                else:  # 차량이 차선 중심에 있음
                    self.publisher_.publish(String(data='center'))
                    self.get_logger().info('Steering Center')

            # 현재 프레임을 파일로 저장
            filename = f"lane_frame_{self.get_clock().now().to_msg().sec}.jpg"
            cv2.imwrite(filename, frame)
            #self.get_logger().info(f'Saved lane image: {filename}')
        #else:
            #self.get_logger().warn('No lanes detected')

def main(args=None):
    rclpy.init(args=args)
    lane_subscriber = LaneSubscriber()
    rclpy.spin(lane_subscriber)
    rclpy.shutdown()

if __name__ == '__main__':
    main()