"""
Görev 1: Figure-8 (Sonsuz / ∞) Uçuşu — ROS2 versiyonu
"""

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from tf2_msgs.msg import TFMessage

# === KULLANICI AYARLARI ===
POLE1_X = -150.0
POLE1_Y = 100.0
POLE2_X = 0.0
POLE2_Y = 100.0

LOBE_RADIUS_M = 110.0
ARC_SEGMENTS = 8
WP_ACCEPT_RADIUS_M = 45.0
NUM_LAPS = 2
BASE_CRUISE_SPEED = 6.0

# İrtifa kontrolü
TARGET_ALTITUDE_M = 22.0
ALT_KP = 0.5
MAX_CLIMB_SPEED = 3.0


# === GEOMETRİ YARDIMCILARI ===
def arc_waypoints(cx, cy, radius, start_angle, sweep, segments):
    pts = []
    for i in range(1, segments + 1):
        ang = start_angle + sweep * i / segments
        pts.append((cx + radius * math.cos(ang),
                    cy + radius * math.sin(ang)))
    return pts


def build_figure8_waypoints():
    p1x, p1y = POLE1_X, POLE1_Y
    p2x, p2y = POLE2_X, POLE2_Y

    dx = p2x - p1x
    dy = p2y - p1y
    axis_angle = math.atan2(dy, dx)

    waypoints = []
    for lap in range(NUM_LAPS):
        start1 = axis_angle + math.pi
        sweep1 = -2 * math.pi
        pts1 = arc_waypoints(p2x, p2y, LOBE_RADIUS_M,
                             start1, sweep1, ARC_SEGMENTS)
        waypoints.extend(pts1)

        start2 = axis_angle
        sweep2 = 2 * math.pi
        pts2 = arc_waypoints(p1x, p1y, LOBE_RADIUS_M,
                             start2, sweep2, ARC_SEGMENTS)
        waypoints.extend(pts2)

    return waypoints


# === ROS2 NODE ===
class GorevNode(Node):
    def __init__(self):
        super().__init__('gorev1_node')

        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.status_pub = self.create_publisher(String, '/iha/status', 10)

        self.tf_sub = self.create_subscription(
            TFMessage, '/world/competition/pose/info',
            self.tf_callback, 10)

        self.x = None
        self.y = None
        self.z = None
        self.current_angle = 0.0

        self.waypoints = build_figure8_waypoints()
        self.current_wp = 0

        self.get_logger().info(
            f'Görev 1 başlatıldı! Toplam {len(self.waypoints)} waypoint.')

        self.timer = self.create_timer(0.02, self.control_loop)

    def tf_callback(self, msg):
        for transform in msg.transforms:
            if transform.child_frame_id == 'iha':
                self.x = transform.transform.translation.x
                self.y = transform.transform.translation.y
                self.z = transform.transform.translation.z
                q = transform.transform.rotation
                siny = 2.0 * (q.w * q.z + q.x * q.y)
                cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
                self.current_angle = math.atan2(siny, cosy)
                break

    def control_loop(self):
        cmd = Twist()
        status = String()

        if self.x is None:
            status.data = 'POZİSYON BEKLENİYOR...'
            self.status_pub.publish(status)
            return

        if self.current_wp >= len(self.waypoints):
            status.data = 'GÖREV TAMAMLANDI - Figure-8 bitti!'
            self.get_logger().info('Figure-8 görevi tamamlandı!')
            self.cmd_vel_pub.publish(cmd)
            self.status_pub.publish(status)
            return

        wp_x, wp_y = self.waypoints[self.current_wp]

        dx = wp_x - self.x
        dy = wp_y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < WP_ACCEPT_RADIUS_M:
            self.current_wp += 1
            self.get_logger().info(
                f'WP {self.current_wp}/{len(self.waypoints)} tamamlandı!')
        else:
            target_angle = math.atan2(dy, dx)
            angle_diff = math.atan2(
                math.sin(target_angle - self.current_angle),
                math.cos(target_angle - self.current_angle))

            cmd.linear.x = BASE_CRUISE_SPEED
            cmd.linear.y = 0.0
            alt_error = TARGET_ALTITUDE_M - self.z
            cmd.linear.z = max(-MAX_CLIMB_SPEED,
                              min(MAX_CLIMB_SPEED, alt_error * ALT_KP))
            cmd.angular.z = max(-0.5, min(0.5, angle_diff * 1.0))

        lap = self.current_wp // (ARC_SEGMENTS * 2) + 1
        status.data = (f'FIGURE-8 | Tur: {min(lap, NUM_LAPS)}/{NUM_LAPS} | '
                       f'WP: {self.current_wp}/{len(self.waypoints)} | '
                       f'İrtifa: {self.z:.1f}m | Mesafe: {distance:.1f}m')

        self.cmd_vel_pub.publish(cmd)
        self.status_pub.publish(status)


def main(args=None):
    rclpy.init(args=args)
    node = GorevNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()