#kinematics.py
#converts desk coords to motor commands for ORION
#breaks at extreme angles >60 degrees due to discrete joints
#constant curvature approximation for tendon driven continuum arm

# x = along rail - positive:right
# y = desk depth - positive = forward away from cabinet
# z = vertical - positive = up (arm hangs down in this case so Z is negative workspace)


import math

#rail constants
rail_length_mm = 1981.2 #78inches
rail_half_mm = rail_length_mm / 2 #around 990.6mm (center of the rail; "zero point")

steps_per_mm = 80

max_rail_speed = 800 #microsteps/sec so steps_per_mm * 10mm/s give or take
homing_speed = 200

#arm geometry
num_segments = 9
segment_length_mm = 55 #45 for joint+body + 10 for margins give or take
arm_length_mm = num_segments * segment_length_mm #around 495mm (55mm per segment*9segments)

arm_hang_height_mm = 190.5 #7.5 inches from cabinet bottom to monitor top

arm_reach_mm = 250.0

#tendon/servo contraints
servo_horn_radius_mm = 25.0

#cable travel per radian of servo rotation so it is equal to servo horn radius
cable_mm_per_rad = servo_horn_radius_mm #25mm per radian

#servo neutral = no tension and arm will hang straight down
#pulling = increasing angle from neutral position
servo_neutral_deg = 90
servo_max_pull_deg = 90
servo_min_deg = 0
servo_max_deg = 180

#max cable distance traveled
max_cable_travel_mm = cable_mm_per_rad * math.radians(servo_max_pull_deg)

#cable geometry
#orion has 3 cables at corners of equilateral triangle
#approximating 120 degree symmetric for constant curvature model
cable_angles_deg = [90.0, 210.0, 330.0]
cable_angles_rad = [math.radians(a) for a in cable_angles_deg]

#lazy susan
lazy_susan_min_deg = 0
lazy_susan_max_deg = 180
lazy_susan_neutral_deg = 90 #arm points straight forward

#constant curvature IK____________________________________

def target_to_bend(target_x_mm, target_y_mm):

    #distance from base to target in horizontal plane
    horizontal_dist = math.sqrt(target_x_mm**2 + target_y_mm**2)

    #clamp to reachable workspace
    horizontal_dist = min(horizontal_dist, arm_length_mm * 0.95)

    #bend direction, phi = 0 means arm bends toward positive y (singularity)
    if horizontal_dist < 1.0:
        phi = 0.0
    else:
        phi = math.atan2(target_x_mm, target_y_mm)

    #total bench angle from contant curvature
    #arm L reaching distance D -> D = L*sin(theta)/theta (precalc)
    theta = _solve_theta(horizontal_dist, arm_length_mm)

    #curvature kappa = theta/arm_length
    kappa = theta / arm_length_mm if arm_length_mm > 0 else 0

    return theta, kappa, phi

def _solve_theta(horizontal_dist, arm_length, iterations=20):
    
    if horizontal_dist < 1.0:
        return 0.0 #singularity - straight down
    
    ratio = horizontal_dist / arm_length
    ratio = min(ratio, 0.95) #prevent from going past reachable limit

    #guess
    theta = ratio * math.pi / 2

    for _ in range(iterations):
        if abs(theta) < 1e-6:
            break

        sin_t = math.sin(theta)
        cos_t = math.cos(theta)

        #f(theta) = sin(theta)/theta - ratio
        f = sin_t / theta - ratio

        df = (theta * cos_t - sin_t) / (theta ** 2)

        if abs(df) < 1e-10:
            break

        theta = theta - f / df
        theta = max(0.01, min(math.pi * 0.95, theta))

    return theta


