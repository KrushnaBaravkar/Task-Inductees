import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.srv import SetPen, Spawn, Kill
import math

class TurtleDraw(Node):
    def __init__(self):
        super().__init__('turtle_draw')
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        self.spawn_client = self.create_client(Spawn, 'spawn')
        self.kill_client = self.create_client(Kill, 'kill')    
        self.current_x = 0
        self.current_y = 0
        self.current_theta = 0.0  # radians, facing right
        self.pen_is_down = True

    def set_pen(self, r=255, g=255, b=255, width=2, off=False):
        while not self.pen_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for pen service...')
        req = SetPen.Request()
        req.r = r
        req.g = g
        req.b = b
        req.width = width
        req.off = off
        self.pen_is_down = not off
        self.pen_client.call_async(req)

    def draw_line(self, end_x, end_y, speed=1.0):
        """Draw line from current position to specified end coordinates"""
        dx = end_x - self.current_x
        dy = end_y - self.current_y
        distance = math.sqrt(math.pow(dx,2)+math.pow(dy,2))
        target_angle = math.atan2(dy, dx)
        
        # Calculate required rotation
        angle_diff = target_angle - self.current_theta
        angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi  # Normalize to [-π, π]
        
        # Rotate to face target
        if abs(angle_diff) > 1e-3:
            self._rotate(angle_diff)

        # Move forward
        self._move_straight(distance, speed)
        
        # Update position
        self.current_x = end_x
        self.current_y = end_y

    def draw_circle(self, center_x, center_y, radius, speed=1.0):
        """Draw circle around specified center coordinates with given radius"""
        was_pen_down = self.pen_is_down
        """
            Write your logic for drawing circle here.
            Below is a code segment just to guide you, how to execute your logic
        """
            # Move to the starting point (rightmost of the circle)
        self.pen_up()  # Lift pen before teleporting
        self.teleport(center_x + radius, center_y, 0.0)  
        self.set_pen(off=not was_pen_down)  # Restore pen state

         # Set up circular motion
        angular_speed = speed / radius  # ω = v / r
        duration = (2 * math.pi * radius) / speed  # Time to complete one full circle

         # Publish movement command
        msg = Twist()
        msg.linear.x = speed  # Forward speed
        msg.angular.z = angular_speed  # Angular velocity
        self.publisher_.publish(msg)

           # Allow movement to continue for the duration of the circle
        rclpy.spin_once(self, timeout_sec=duration)

           # Stop movement after the circle is complete
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.publisher_.publish(msg)

          # Restore original pen state
        if not was_pen_down:
            self.pen_up()
            
    def _rotate(self, angle):
        """
            Rotate by specified radians (positive counter-clockwise)
            Write code by yourself
        """
        msg = Twist()
        msg.angular.z = 1.0 if angle > 0 else -1.0
        duration = abs(angle) / msg.angular.z
        start_time = time.time()
        while time.time() - start_time < duration:
            self.publisher_.publish(msg)
            time.sleep(0.1)
        msg.angular.z = 0.0
        self.publisher_.publish(msg)
        self.current_theta += angle
        
    def _move_straight(self, distance, speed=1.0):
        """
            Move straight for specified distance
            Write code by yourself
        """
        msg = Twist()
        msg.linear.x = speed
        duration = distance / speed
        start_time = time.time()
        while time.time() - start_time < duration:
            self.publisher_.publish(msg)
            time.sleep(0.1)
        msg.linear.x = 0.0
        self.publisher_.publish(msg)
        
    def _face_angle(self, target_angle):
        """
            Rotate to face specified angle (radians)
            Write code by yourself
        """
        # Calculate required rotation
        angle_diff = target_angle - self.current_theta
    
        # Normalize angle to the range [-π, π]
        angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi  
    
        # Rotate by the computed angle
        self._rotate(angle_diff)
    
        # Update current orientation
        self.current_theta = target_angle   

    def pen_up(self):
        self.set_pen(off=True)

    def pen_down(self):
        self.set_pen(off=False)
        
    def draw_drone(self):
        """Draw the drone as per the given specifications."""
        
        # Diamond shape
        points = [(5,7), (7,5), (5,3), (3,5), (5,7)]
        self.pen_down()
        for x, y in points:
            self.draw_line(x, y)
        
        # Extending lines
        extensions = [(2,8), (8,8), (8,2), (2,2)]
        center_points = [(3,5), (7,5), (5,3), (5,7)]
        
        for (cx, cy), (ex, ey) in zip(center_points, extensions):
            self.draw_line(ex, ey)
        
        # Circles
        circles = [(2,8), (8,8), (8,2), (2,2)]
        for cx, cy in circles:
            self.draw_circle(cx, cy, 1)

def main(args=None):
    rclpy.init(args=args)
    turtle_draw = TurtleDraw()
    #Sample template to execute functions
    turtle_draw.draw_drone()
    
    turtle_draw.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
        
