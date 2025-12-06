#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from gpiozero import PWMOutputDevice, DigitalOutputDevice
import math
import os

# --- CONFIG: adjust these to your pins + limits ---
# BCM numbers
PWMA_PIN = 13    # PWM for left motor (hardware PWM preferred)	pin 33
AIN1_PIN = 24	# pin 18
AIN2_PIN = 27	# pin 13

PWMB_PIN = 12    # PWM for right motor (or use another PWM pin) pin 32
BIN1_PIN = 23	# pin 16
BIN2_PIN = 17	# pin 11

STBY_PIN = 25    # or tie to 3.3V if you don't need to control standby

# Scaling: teleop default speeds (tweak for your robot)
MAX_LINEAR = 0.5    # m/s (conceptual; set to what you expect)
MAX_ANGULAR = 1.0   # rad/s

# Helper: map value in [-1,1] -> PWM duty 0..1 and direction bits
def mix_to_motors(linear, angular, gain_linear=1.0, gain_angular=1.0):
    # differential drive mixing (simple)
    left = gain_linear * linear - gain_angular * angular * 0.5
    right = gain_linear * linear + gain_angular * angular * 0.5
    return left, right

def sign_and_pwm(v, max_in):
    # clamp and return (direction, pwm_duty)
    if max_in == 0:
        return 1, 0.0
    val = max(-max_in, min(max_in, v))
    pwm = min(1.0, abs(val) / max_in)
    direction = 1 if val >= 0 else -1
    return direction, pwm

class CmdVelToTB6612(Node):
    def __init__(self):
        super().__init__('cmdvel_to_tb6612')

        # setup gpiozero devices
        self.pwma = PWMOutputDevice(PWMA_PIN, active_high=True, initial_value=0, frequency=1000)
        self.ain1 = DigitalOutputDevice(AIN1_PIN)
        self.ain2 = DigitalOutputDevice(AIN2_PIN)

        self.pwmb = PWMOutputDevice(PWMB_PIN, active_high=True, initial_value=0, frequency=1000)
        self.bin1 = DigitalOutputDevice(BIN1_PIN)
        self.bin2 = DigitalOutputDevice(BIN2_PIN)

        self.stby = DigitalOutputDevice(STBY_PIN)
        self.stby.on()  # take TB6612 out of standby

        self.max_linear = float(os.environ.get('MAX_LINEAR', MAX_LINEAR))
        self.max_angular = float(os.environ.get('MAX_ANGULAR', MAX_ANGULAR))

        self.sub = self.create_subscription(Twist, '/cmd_vel', self.cb, 10)
        self.get_logger().info('cmdvel_to_tb6612 started, listening on /cmd_vel')

    def set_motor(self, direction, pwm, in1: DigitalOutputDevice, in2: DigitalOutputDevice, pwm_dev: PWMOutputDevice):
        # direction: 1 => forward (IN1=1, IN2=0), -1 => reverse (IN1=0, IN2=1), 0 => stop (both low -> coast)
        if pwm <= 0.001:
            # stop/coast
            in1.off(); in2.off()
            pwm_dev.value = 0
            return
        if direction >= 0:
            in1.on(); in2.off()
        else:
            in1.off(); in2.on()
        pwm_dev.value = pwm

    def cb(self, msg: Twist):
        lin = msg.linear.x
        ang = msg.angular.z
        left_v, right_v = mix_to_motors(lin, ang)
        dir_l, pwm_l = sign_and_pwm(left_v, self.max_linear)
        dir_r, pwm_r = sign_and_pwm(right_v, self.max_linear)
        self.set_motor(dir_l, pwm_l, self.ain1, self.ain2, self.pwma)
        self.set_motor(dir_r, pwm_r, self.bin1, self.bin2, self.pwmb)
        self.get_logger().debug(f"cmd_vel l={lin:.3f} a={ang:.3f} -> L({dir_l},{pwm_l:.2f}) R({dir_r},{pwm_r:.2f})")

def main(args=None):
    rclpy.init(args=args)
    node = CmdVelToTB6612()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # stop motors
        node.pwma.value = 0
        node.pwmb.value = 0
        node.ain1.off(); node.ain2.off()
        node.bin1.off(); node.bin2.off()
        node.stby.off()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

