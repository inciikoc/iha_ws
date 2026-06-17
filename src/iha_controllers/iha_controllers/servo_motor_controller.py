import math
import rclpy
from rclpy.node import Node

from std_msgs.msg import Float64
from actuator_msgs.msg import Actuators
from geometry_msgs.msg import Twist


class ServoMotorController(Node):

    def __init__(self):
        super().__init__('servo_motor_controller')

        self.servo0_pub = self.create_publisher(Float64, '/model/iha/servo_0', 10)
        self.servo1_pub = self.create_publisher(Float64, '/model/iha/servo_1', 10)
        self.servo2_pub = self.create_publisher(Float64, '/model/iha/servo_2', 10)
        self.servo3_pub = self.create_publisher(Float64, '/model/iha/servo_3', 10)

        self.motor_pub = self.create_publisher(
            Actuators,
            '/model/iha/command/motor_speed',
            10
        )
        
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )
        
        self.rotor_pub = self.create_publisher(
            Float64,
            '/model/iha/rotor_velocity',
            10
        )

        self.timer = self.create_timer(0.05, self.timer_callback)

        self.get_logger().info('Servo + Motor Controller Started')

    def timer_callback(self):
        servo0 = Float64()
        servo1 = Float64()
        servo2 = Float64()
        servo3 = Float64()

        servo0.data = 0.0
        servo1.data = 0.0
        servo2.data = 0.08
        servo3.data = 0.0

        self.servo0_pub.publish(servo0)
        self.servo1_pub.publish(servo1)
        self.servo2_pub.publish(servo2)
        self.servo3_pub.publish(servo3)

        #motor_msg = Actuators()
        #motor_msg.velocity = [-1050.0]
        #motor_msg.normalized = [1.0]
        #self.motor_pub.publish(motor_msg)
        
        rotor_msg = Float64()
        rotor_msg.data = -300.0
        self.rotor_pub.publish(rotor_msg)
        
        #cmd = Twist()
        #cmd.linear.x = 10.0
        #cmd.linear.y = 0.0
        #cmd.linear.z = 0.0
        #cmd.angular.x = 0.0
        #cmd.angular.y = 0.0
        #cmd.angular.z = 0.0
        #self.cmd_vel_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)

    node = ServoMotorController()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()