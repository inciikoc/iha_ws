import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class FlightController(Node):
    def __init__(self):
        super().__init__('flight_controller')

        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.status_pub = self.create_publisher(String, '/iha/status', 10)

        # Uçuş planı: (vx, vy, vz, süre_saniye)
        self.flight_plan = [
            (3.0, 0.0, 0.0, 30.0),  # 30 sn ileri git (pist boyunca)
            (0.0, 0.0, 0.0, 1.0),    # dur
        ]
        self.current_step = 0
        self.step_start_time = None

        self.timer = self.create_timer(0.02, self.control_loop)
        self.get_logger().info('Uçuş kontrol başlatıldı!')

    def control_loop(self):
    

        cmd = Twist()
        status = String()

        now = self.get_clock().now().nanoseconds / 1e9

        if self.current_step >= len(self.flight_plan):
            status.data = 'GÖREV TAMAMLANDI'
            self.cmd_vel_pub.publish(cmd)
            self.status_pub.publish(status)
            return

        if self.step_start_time is None:
            self.step_start_time = now

        step = self.flight_plan[self.current_step]
        vx, vy, vz, duration = step
        elapsed = now - self.step_start_time

        if elapsed >= duration:
            self.current_step += 1
            self.step_start_time = None
            self.get_logger().info(f'Adım {self.current_step} tamamlandı!')
        else:
            cmd.linear.x = vx
            cmd.linear.y = vy
            cmd.linear.z = vz
            remaining = duration - elapsed
            status.data = f'ADIM {self.current_step+1}/{len(self.flight_plan)} | Kalan: {remaining:.1f}s'

        self.cmd_vel_pub.publish(cmd)
        self.status_pub.publish(status)

def main(args=None):
    rclpy.init(args=args)
    node = FlightController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()