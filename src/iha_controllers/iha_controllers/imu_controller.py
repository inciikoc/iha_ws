import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

class ImuController(Node):
    def __init__(self):
        super().__init__('imu_controller')
        
        # Gazebo'dan IMU verisi al
        self.subscription = self.create_subscription(
            Imu,
            '/iha/imu',
            self.imu_callback,
            10)
        
        # İşlenmiş IMU verisini yayınla
        self.publisher_ = self.create_publisher(
            Imu,
            '/iha/imu/processed',
            10)
        
        self.get_logger().info('IMU controller başlatıldı!')

    def imu_callback(self, msg):
        # Açısal hız
        self.get_logger().info(
            f'Açısal hız -> x: {msg.angular_velocity.x:.3f}, '
            f'y: {msg.angular_velocity.y:.3f}, '
            f'z: {msg.angular_velocity.z:.3f}')
        
        # İvme
        self.get_logger().info(
            f'İvme -> x: {msg.linear_acceleration.x:.3f}, '
            f'y: {msg.linear_acceleration.y:.3f}, '
            f'z: {msg.linear_acceleration.z:.3f}')
        
        # Veriyi yayınla
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ImuController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()