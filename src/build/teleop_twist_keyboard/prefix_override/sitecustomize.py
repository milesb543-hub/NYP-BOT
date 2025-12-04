import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/nyp-bot/ydlidar_ros2_ws/src/install/teleop_twist_keyboard'
