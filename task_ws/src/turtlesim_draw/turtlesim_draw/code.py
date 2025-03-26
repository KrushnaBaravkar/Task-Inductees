import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.srv import SetPen, Spawn, Kill
import math
import time

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

    def draw_circle(self, radius):
        msg = Twist()
        msg.linear.x = 1.0
        msg.angular.z = 1.0 / radius

        start_time = time.time()
        while time.time() - start_time < 6.28:
            self.publisher_.publish(msg)
            time.sleep(0.1)

        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.publisher_.publish(msg)

            
    def _rotate(self, angle_deg):
        """Rotates the turtle by a specified angle (in degrees)."""
        angle_rad = math.radians(angle_deg)  # Convert degrees to radians
        msg = Twist()
        msg.angular.z = 1.0 if angle_rad > 0 else -1.0  # Set direction

        start_time = time.time()
        duration = abs(angle_rad) / 1.0  # Since angular velocity is 1.0 rad/s

        # Keep rotating for the calculated duration
        while time.time() - start_time < duration:
            self.publisher_.publish(msg)
            time.sleep(0.1)  # Small delay for smooth movement

        # Stop rotation
        msg.angular.z = 0.0
        self.publisher_.publish(msg)

        # Update current orientation
        self.current_theta += angle_rad
        self.current_theta %= (2 * math.pi)  # Keep within [0, 2π]
        
     def _move(self, distance, speed=1.0):
        """Moves the turtle forward by a specified distance at a given speed."""
        msg = Twist()
        msg.linear.x = speed  # Set forward speed
        duration = abs(distance / speed)  # Calculate movement time

        start_time = time.time()

        # Publish velocity command continuously for the duration
        while time.time() - start_time < duration:
            self.publisher_.publish(msg)
            time.sleep(0.1)  # Small delay to maintain smooth movement

        # Stop the turtle after moving
        msg.linear.x = 0.0
        self.publisher_.publish(msg)
    
        # Update current position based on movement
        self.current_x += distance * math.cos(self.current_theta)
        self.current_y += distance * math.sin(self.current_theta)

        
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
        
    def draw_square(self):
        self.pen_up()
        self._move(2)
        self._rotate(135)
        self.pen_down()
        for _ in range(3):
            self._move(2.83)
            self._rotate(90)
        
        self._move(2.83)
            
        

    def draw_pattern(self):  # Renamed from draw_circle to avoid conflict
        for _ in range(4):
            self.pen_up()
            self._rotate(90)
            self._move(1.415)
            self._rotate(-90)
            self.pen_down()
            self._move(2.83)
            self._rotate(180)
            self._move(1)
            self._rotate(90)
            self.draw_circle(1)  # Fixed function call
            self._rotate(-90)
            self.pen_up()
            self._move(1.83)
            self._rotate(-90)
            self._move(1.38)

def main(args=None):
    rclpy.init(args=args)
    turtle_draw = TurtleDraw()
    
    # Execute drawing function
    turtle_draw.draw_square()
    turtle_draw.draw_pattern()  # Use renamed function
    
    turtle_draw.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
        
