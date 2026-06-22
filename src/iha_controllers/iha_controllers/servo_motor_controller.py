import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist
from tf2_msgs.msg import TFMessage
from actuator_msgs.msg import Actuators

# Görev1 komutu -> hedef tutum
TURN_TO_BANK   = 0.6
CLIMB_TO_PITCH = 0.05
MAX_BANK       = 0.35
MAX_PITCH      = 0.20

# İç denge çevrimi
ROLL_KP,  ROLL_KD  = 0.6, 0.10
PITCH_KP, PITCH_KD = 0.8, 0.12
MAX_SURF = 0.5          # servo limiti (joint limiti ±0.78)

CRUISE_OMEGA = 1000.0   # motor hızı (0..1050). İleri gitmezse işareti/değeri değiştir.


def clamp(v, lim):
    return max(-lim, min(lim, v))


def quat_to_rpy(w, x, y, z):
    roll = math.atan2(2*(w*x + y*z), 1 - 2*(x*x + y*y))
    pitch = math.asin(clamp(2*(w*y - z*x), 1.0))
    yaw = math.atan2(2*(w*z + x*y), 1 - 2*(y*y + z*z))
    return roll, pitch, yaw


class ServoMotorController(Node):
    def __init__(self):
        super().__init__('servo_motor_controller')

        self.servo0_pub = self.create_publisher(Float64, '/model/iha/servo_0', 10)  # sol aileron
        self.servo1_pub = self.create_publisher(Float64, '/model/iha/servo_1', 10)  # sağ aileron
        self.servo2_pub = self.create_publisher(Float64, '/model/iha/servo_2', 10)  # elevator
        self.servo3_pub = self.create_publisher(Float64, '/model/iha/servo_3', 10)  # rudder
        self.motor_pub  = self.create_publisher(Actuators, '/model/iha/command/motor_speed', 10)

        self.create_subscription(Twist, '/cmd_vel', self.cmd_callback, 10)
        self.create_subscription(TFMessage, '/world/competition/pose/info', self.pose_callback, 10)

        self.cmd = Twist()
        self.roll = self.pitch = 0.0
        self.prev_roll = self.prev_pitch = 0.0

        self.timer = self.create_timer(0.02, self.timer_callback)
        self.get_logger().info('Mixer hazir: dogru servo haritasi + itki')

    def cmd_callback(self, msg):
        self.cmd = msg

    def pose_callback(self, msg):
        for t in msg.transforms:
            if t.child_frame_id == 'iha':
                q = t.transform.rotation
                self.roll, self.pitch, _ = quat_to_rpy(q.w, q.x, q.y, q.z)
                break

    def timer_callback(self):
        dt = 0.02
        target_roll  = clamp(self.cmd.angular.z * TURN_TO_BANK, MAX_BANK)
        target_pitch = clamp(self.cmd.linear.z  * CLIMB_TO_PITCH, MAX_PITCH)

        roll_rate  = (self.roll  - self.prev_roll)  / dt
        pitch_rate = (self.pitch - self.prev_pitch) / dt
        self.prev_roll, self.prev_pitch = self.roll, self.pitch

        aileron  = clamp(ROLL_KP*(target_roll - self.roll)    - ROLL_KD*roll_rate,  MAX_SURF)
        elevator = clamp(PITCH_KP*(target_pitch - self.pitch) - PITCH_KD*pitch_rate, MAX_SURF)

        # === DOĞRU SERVO HARİTASI (model.sdf'ten) ===
        s0 = Float64(); s0.data =  aileron    # servo_0 = sol aileron
        s1 = Float64(); s1.data = -aileron    # servo_1 = sağ aileron (ters -> roll)
        s2 = Float64(); s2.data =  elevator   # servo_2 = ELEVATOR (pitch)
        s3 = Float64(); s3.data =  0.0        # servo_3 = rudder (şimdilik 0)

        self.servo0_pub.publish(s0)
        self.servo1_pub.publish(s1)
        self.servo2_pub.publish(s2)
        self.servo3_pub.publish(s3)

        # İtki -> MulticopterMotorModel (gerçek thrust)
        m = Actuators()
        m.velocity = [CRUISE_OMEGA if self.cmd.linear.x > 0.1 else 0.0]
        self.motor_pub.publish(m)


def main(args=None):
    rclpy.init(args=args)

    node = ServoMotorController()

    rclpy.spin(node)

    node.destroy_node()
    
    rclpy.shutdown()


if __name__ == '__main__':
    main()