import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix

class GpsController(Node):
    def __init__(self):
        super().__init__('gps_controller')
        
        self.subscription = self.create_subscription(
            NavSatFix,
            '/iha/gps',
            self.gps_callback,
            10)
        
        self.publisher_ = self.create_publisher(
            NavSatFix,
            '/iha/gps/processed',
            10)
        
        self.get_logger().info('GPS controller başlatıldı!')

    def gps_callback(self, msg):
        self.get_logger().info(
            f'Konum -> Lat: {msg.latitude:.6f}, '
            f'Lon: {msg.longitude:.6f}, '
            f'Alt: {msg.altitude:.2f}')
        
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = GpsController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()