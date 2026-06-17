import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

class LidarController(Node):
    def __init__(self):
        super().__init__('lidar_controller')
        
        self.subscription = self.create_subscription(
            LaserScan,
            '/iha/lidar',
            self.lidar_callback,
            10)
        
        self.publisher_ = self.create_publisher(
            LaserScan,
            '/iha/lidar/processed',
            10)
        
        self.get_logger().info('LiDAR controller başlatildi!')

    def lidar_callback(self, msg):
        # En yakın engel mesafesi
        min_distance = min(r for r in msg.ranges if r > msg.range_min)
        self.get_logger().info(f'En yakın engel: {min_distance:.2f} m')
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = LidarController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()