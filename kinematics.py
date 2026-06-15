#kinematics.py
#converts desk coords to motor commands for ORION
#breaks at extreme angles >60 degrees due to discrete joints
#constant curvature approximation for tendon driven continuum arm


import math

num_segments = 9
arm_length = 457.2 #1.5feet into mm
segment_length = arm_length / num_segments

base_height_mm = 76.2 #3inch base to mm

#servo stuff
servo_horn_radius = 27.0 #tune (needs to be atleast 27mm bc otherwise there cant be full RoM)
cable_mm_per_rad = servo_horn_radius

#new desk mount needs pretension to hold arm against gravity
servo_neutral = 75 #needs to be less than 90 (hanging mount neutral)
servo_max_pull = 75
servo_min = 0
servo_max = 180

#cable geometry
cable_angles_deg = [0.0, 120.0, 240.0]
cable_angles_rad = [math.radians(a) for a in cable_angles_deg]

max_cable_travel = cable_mm_per_rad * math.radians(servo_max_pull) #35.3mm (delta_L)

#lazy susan
lazy_susan_min = 0
lazy_susan_max = 180
lazy_susan_neutral = 90

#workspace limits
singularity = 20.0 #within 2cm of base = singularity

min_reach = 100.0 #10cm minimum
max_reach = arm_length * 0.95 #roughly 435mm (max before joints start being weird)

#constant curvature IK functions
def _solve_theta(horizontal_dist, arm_length, iterations=20):

    if horizontal_dist < singularity:
        return 0.0
    
    ratio = horizontal_dist / arm_length
    #clamp ratio
    ratio = min(ratio, 0.95)

    #guess
    theta = ratio * math.pi / 2

    for _ in range(iterations):
        if abs(theta) < 1e-6:
            break
        sin_t = math.sin(theta)
        cos_t = math.cos(theta)
        f = sin_t / theta - ratio
        df = (theta * cos_t - sin_t) / (theta ** 2)
        if abs(df) < 1e-10:
            break
        theta = theta - f / df
        theta = max(0.01, min(math.pi * 0.95, theta))
    
    return theta

def target_to_bend(horizontal_dist_mm):
    
    if horizontal_dist_mm < singularity:
        return 0.0, 0.0, 0.0
    
    horizontal_dist_mm = max(min_reach, min(horizontal_dist_mm, max_reach))

    phi = 0.0
    theta = _solve_theta(horizontal_dist_mm, arm_length)
    kappa = theta / arm_length if arm_length > 0 else 0

    return kappa, phi, theta

def bend_to_cable_lengths(kappa, phi, theta):
    #delta_l negative -> cable shortens = servo pulls = angle decreases from neutral
    #delta_l positive -> cable lengthens = servo releases = angle increases toward neutral
    
    cable_offset = 70.0 / math.sqrt(3) #roughly 40.4mm
    
    delta_lengths = []

    for alpha in cable_angles_rad:
        if abs(theta) < 1e-6:
            delta_l = 0.0
        else:
            delta_l = -cable_offset * theta * math.cos(phi - alpha)
        
        delta_lengths.append(delta_l)

    
    return delta_lengths

def cable_lengths_to_servo_angles(delta_lengths):

    angles = []

    max_delta = max(abs(d) for d in delta_lengths) if delta_lengths else 1.0
    #use scale factor so cable doesnt die if it exceeds travel limit
    scale = min(1.0, max_cable_travel / max_delta) if max_delta > 0 else 1.0

    for delta_l in delta_lengths:
        scaled = delta_l * scale
        angle = servo_neutral - (scaled / max_cable_travel) * servo_max_pull #could be servo_max (test)
        angle = max(servo_min, min(servo_max, int(angle)))
        angles.append(angle)

    return angles

#lazy susan function
def desk_to_lazy_susan(desk_x, desk_y):

    if abs(desk_x) < 0.1 and abs(desk_y) < 0.1:
        return lazy_susan_neutral
    
    angle_rad = math.atan2(desk_x, desk_y)
    angle_deg = math.degrees(angle_rad)

    servo_angle = int(lazy_susan_neutral + angle_deg)
    return max(lazy_susan_min, min(lazy_susan_max, servo_angle))

#main function

def desk_to_motor_functions(desk_x, desk_y):

    target_x = desk_x * 10.0
    target_y = desk_y * 10.0

    horizontal_dist = math.sqrt(target_x**2 + target_y**2)
    lazy_susan_angle = desk_to_lazy_susan(desk_x, desk_y)

    #handle singularity
    if horizontal_dist < singularity:
        return {
            "tendon_angles" : [servo_neutral] * 3,
            "lazy_susan_angle" : lazy_susan_neutral
        }
    
    kappa, phi, theta = target_to_bend(horizontal_dist)
    delta_lengths = bend_to_cable_lengths(kappa, phi, theta)
    tendon_angles = cable_lengths_to_servo_angles(delta_lengths)

    #normal stuff
    return {
        "tendon_angles" : tendon_angles,
        "lazy_susan_angle" : lazy_susan_angle
    }

#stow function because arm now needs to be angled at rest position to minimize torque by gravity
def stow_angles():
    
    stow_theta = math.radians(30) #30 degrees (tune)
    kappa = stow_theta / arm_length

    delta_lengths = bend_to_cable_lengths(kappa, 0.0, stow_theta)
    return cable_lengths_to_servo_angles(delta_lengths)

#testing

def test_kinematics():
    print("Desk Mounted Kinematics Test")

    print(f"Arm length: {arm_length}mm")
    print(f"Max reach: {max_reach}mm")
    print(f"Min reach: {min_reach}mm")
    print(f"Servo neutral: {servo_neutral}")
    print(f"Max cable delta_l: {max_cable_travel}mm\n")

    positions = [
        (0, 20, "forward 20cm"),
        (20, 20, "diagonal right 20cm"),
        (-20, 20, "diagonal left 20cm"),
        (0, 35, "max forward"),
        (25, 25, "far right diagonal"),
        (0, 0, "singularity"),
        (0, 5, "close range"), #clamps to 10cm
        (0, 43, "beyond max range"), #clamps to 43.4cm
        (0, -10, "behind base"),
        (20, 0, "only right"),
        (-20, 0, "only left"),
    ]


    for x, y, desc in positions:
        cmds = desk_to_motor_functions(x,y)
        print(f"Tendons: {cmds['tendon_angles']}")
        print(f"Lazy Susan: {cmds['lazy_susan_angle']}")

    print(f"Stow angles: {stow_angles()}")

if __name__ == "__main__":
    test_kinematics()









