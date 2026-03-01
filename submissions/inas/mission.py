from dronekit import connect, VehicleMode
from pymavlink import mavutil
import time

# =========================
# CONNECT
# =========================
print("Connecting to vehicle...")
vehicle = connect('udp:127.0.0.1:14550', wait_ready=True)

# =========================
# ARM & TAKEOFF
# =========================
def arm_and_takeoff(target_altitude):

    while not vehicle.is_armable:
        time.sleep(1)

    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        time.sleep(1)

    vehicle.simple_takeoff(target_altitude)

    while True:
        alt = vehicle.location.global_relative_frame.alt
        if alt >= target_altitude * 0.95:
            print("Reached 3 meters")
            break
        time.sleep(0.5)

# =========================
# SMOOTH VELOCITY FUNCTION
# =========================
def send_velocity(vx, vy, vz, duration):

    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,
        0, 0,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b0000111111000111,
        0, 0, 0,
        vx, vy, vz,
        0, 0, 0,
        0, 0)

    end_time = time.time() + duration

    while time.time() < end_time:
        vehicle.send_mavlink(msg)
        time.sleep(0.1)   # 10 Hz supaya lurus & halus

# =========================
# SPRAYING MISSION
# =========================
def spraying_mission():

    field_length = 40      # meter
    field_width = 10       # meter
    spacing = 4            # meter
    speed = 4              # m/s

    row_time = field_length / speed     # 10 detik
    spacing_time = spacing / speed      # 1 detik

    rows = 3
    direction = 1  # 1 = Timur (→), -1 = Barat (←)

    print("Starting spraying pattern...")

    for i in range(rows):

        print(f"\n===== BARIS {i+1} =====")

        if direction == 1:
            print("Terbang ke TIMUR (→)")
        else:
            print("Terbang ke BARAT (←)")

        send_velocity(speed * direction, 0, 0, row_time)

        print("Hover 3 detik...")
        time.sleep(3)

        if i < rows - 1:
            print("Geser ke SELATAN (↓)")
            send_velocity(0, -speed, 0, spacing_time)

            print("Hover 3 detik...")
            time.sleep(3)

        direction *= -1

    print("Spraying selesai!")

# =========================
# MAIN
# =========================
arm_and_takeoff(3)

spraying_mission()

print("LOITER...")
vehicle.mode = VehicleMode("LOITER")
time.sleep(5)

print("LANDING...")
vehicle.mode = VehicleMode("LAND")

while vehicle.armed:
    time.sleep(1)

print("Mission Complete 🌾🚁")
vehicle.close()