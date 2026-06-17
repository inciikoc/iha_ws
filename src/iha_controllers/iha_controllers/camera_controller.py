import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class CameraController(Node):
    def __init__(self):
        super().__init__('camera_controller')
        
        # Gazebo'dan ham görüntü al
        self.subscription = self.create_subscription(
            Image,
            '/iha_camera/image_raw',
            self.image_callback,
            10)
        
        # İşlenmiş görüntüyü yayınla
        self.publisher_ = self.create_publisher(
            Image,
            '/iha/camera/processed',
            10)
        
        self.bridge = CvBridge()
        self.get_logger().info('Kamera controller başlatıldı!')

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        
        # Buraya görüntü işleme kodların gelecek
        processed_msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        processed_msg.header = msg.header
        self.publisher_.publish(processed_msg)

def main(args=None):
    rclpy.init(args=args)
    node = CameraController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()