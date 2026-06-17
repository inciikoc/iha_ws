import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from std_msgs.msg import Float64

class BaroController(Node):
    def __init__(self):
        super().__init__('baro_controller')
        
        # IMU verisinden irtifa hesapla
        self.subscription = self.create_subscription(
            Imu,
            '/iha/imu',
            self.imu_callback,
            10)
        
        self.publisher_ = self.create_publisher(
            Float64,
            '/iha/baro/altitude',
            10)
        
        self.altitude = 0.0
        self.velocity_z = 0.0
        self.last_time = None
        
        self.get_logger().info('Barometre controller başlatıldı!')

    def imu_callback(self, msg):
        current_time = self.get_clock().now().nanoseconds / 1e9
        
        if self.last_time is not None:
            dt = current_time - self.last_time
            self.velocity_z += msg.linear_acceleration.z * dt
            self.altitude += self.velocity_z * dt
        
        self.last_time = current_time
        
        alt_msg = Float64()
        alt_msg.data = self.altitude
        self.publisher_.publish(alt_msg)
        
        self.get_logger().info(f'İrtifa: {self.altitude:.2f} m')

def main(args=None):
    rclpy.init(args=args)
    node = BaroController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()