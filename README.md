# NYP-BOT
OU ECE Capestone Fall 2025 - Autonomous Robot Space Detector

# Features
The Navigating Your Property (NYP) is an autonomous robot designed to navigate a warehouse and detect used and unused storage space using LiDAR. The goal of this project is to create a platform capable of:
  - Navigating a warehouse autonomously (partial implementation)
  - Detect and map storage locations using LiDAR
  - Avoid collisions and cliffs using millimeter-wave (Not implemented)
  - Use a camera as a visual assistance for navigation (Not implemented)
  - Provide an accurate map of free space in the warehouse (Not implemented)

# Install Instructions
```bash
git clone https://github.com/milesb543-hub/Navigating_Your_Property.git
# See user manual for complete install

# Usage
cd ~
python3 launch_bot.py
```
# Known Issues
Odometry data from encoders is non-directional. Directionality is being pulled from cmd_vel topic.
