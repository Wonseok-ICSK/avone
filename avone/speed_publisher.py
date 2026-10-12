# todo. Improve accuracy

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import pytesseract
from std_msgs.msg import Int32

class SpeedSubscriber(Node):
    def __init__(self):
        super().__init__('speed_publisher')
        self.get_logger().info('Starting speed publisher')
        self.subscription = self.create_subscription(
            Image,
            'video_frames',  # 'image_publisher' 노드에서 퍼블리시하는 토픽
            self.listener_callback,
            10)
        self.publisher_ = self.create_publisher(Int32, 'spd', 10)
        self.bridge = CvBridge()

    def listener_callback(self, msg): # 뭔갈 구독
        # ROS Image 메시지를 OpenCV 이미지로 변환
        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        
        x, y, w, h = 1732, 1019, 38, 25
        # 속도계가 화면의 우측 하단에 있다고 가정하고 해당 영역을 ROI로 설정
        roi = frame[y:y+h, x:x+w]  # 속도계 위치 추출 (적절히 조정 필요)
        
        # 이미지를 그레이스케일로 변환하여 OCR 처리
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        #cv2.imshow('window', frame)
        speed_text = pytesseract.image_to_string(gray, config='--psm 7')  # OCR로 숫자 추출
        try:
            speed = int(speed_text)
            self.publisher_.publish(Int32(data=speed))  # 'spd' 토픽에 속도 발행
            self.get_logger().info(f'Published speed: {speed}')
        except ValueError:
            self.get_logger().warn('Speed conversion failed')
            filename = f"frame_{self.get_clock().now().to_msg().sec}.jpg"  # Use timestamp for unique filenames
            # cv2.imwrite(filename, gray)
        

def main(args=None):
    rclpy.init(args=args)
    speed_subscriber = SpeedSubscriber()
    rclpy.spin(speed_subscriber)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
