"""
06_threaded_telemetry.py
------------------------
Contoh pemakaian thread untuk telemetry bersamaan dengan eksekusi misi.

Fitur:
- Thread telemetry yang membaca battery + altitude setiap detik
- Contoh penggunaan attribute listener untuk attitude
- Main thread menjalankan misi sederhana (arm, takeoff, maju, mundur, landing)
- Menggunakan Event untuk memberhentikan thread dengan rapi

Pastikan Mission Planner SITL berjalan (tcp:127.0.0.1:5762) sebelum menjalankan.
"""

import threading
import time
import math
from dronekit import connect, VehicleMode, LocationGlobalRelative

# ---- Helper functions (sama pola dengan contoh misi lain) ----

def switch_mode(vehicle, mode_name, timeout=10):
    vehicle.mode = VehicleMode(mode_name)
    start = time.time()
    while vehicle.mode.name != mode_name:
        if time.time() - start > timeout:
            print(f"[WARN] Timeout pindah mode ke {mode_name}")
            return False
        time.sleep(0.5)
    print(f"[MODE] {mode_name} aktif")
    return True

def arm_and_takeoff(vehicle, target_altitude):
    print("[INFO] Menunggu is_armable...")
    while not vehicle.is_armable:
        time.sleep(1)

    switch_mode(vehicle, "GUIDED")

    print("[INFO] Arming...")
    vehicle.armed = True
    while not vehicle.armed:
        time.sleep(1)
    print("[INFO] Armed")

    print(f"[INFO] Takeoff => {target_altitude} m")
    vehicle.simple_takeoff(target_altitude)
    while True:
        alt = vehicle.location.global_relative_frame.alt
        print(f"  Ketinggian: {alt:.2f} m")
        if alt >= target_altitude * 0.95:
            print("[INFO] Target altitude reached")
            break
        time.sleep(1)

def get_offset_location(original, d_north, d_east, alt):
    earth_radius = 6378137.0
    d_lat = d_north / earth_radius
    d_lon = d_east / (earth_radius * math.cos(math.radians(original.lat)))
    new_lat = original.lat + math.degrees(d_lat)
    new_lon = original.lon + math.degrees(d_lon)
    return LocationGlobalRelative(new_lat, new_lon, alt)

def get_distance(loc1, loc2):
    d_lat = loc2.lat - loc1.lat
    d_lon = loc2.lon - loc1.lon
    return math.sqrt(d_lat ** 2 + d_lon ** 2) * 1.113195e5

def goto(vehicle, d_north, d_east, altitude, label="target", threshold=1.5):
    if vehicle.mode.name != "GUIDED":
        switch_mode(vehicle, "GUIDED")
    current = vehicle.location.global_relative_frame
    target = get_offset_location(current, d_north, d_east, altitude)
    print(f"[NAV] Menuju {label}...")
    vehicle.simple_goto(target)
    while True:
        dist = get_distance(vehicle.location.global_relative_frame, target)
        alt = vehicle.location.global_relative_frame.alt
        print(f"  Jarak ke {label}: {dist:.1f} m | Alt: {alt:.2f} m")
        if dist <= threshold:
            print(f"[NAV] Tiba di {label}")
            break
        time.sleep(1)

# ---- Telemetry thread ----

def telemetry_worker(vehicle, stop_event, lock=None, interval=1.0):
    """
    Thread background: membaca battery dan altitude secara periodik.
    stop_event: threading.Event untuk menghentikan thread.
    lock: optional threading.Lock jika akses vehicle perlu disinkronkan.
    """
    while not stop_event.is_set():
        if lock:
            lock.acquire()
        try:
            alt = vehicle.location.global_relative_frame.alt
            batt = vehicle.battery
            # battery bisa None pada beberapa konfigurasi; cek terlebih dahulu
            if batt is not None:
                print(f"[TELEMETRY] Alt: {alt:.2f} m | Battery: {batt.voltage:.2f} V / {batt.level}%")
            else:
                print(f"[TELEMETRY] Alt: {alt:.2f} m | Battery: (tidak tersedia)")
        except Exception as e:
            print(f"[TELEMETRY] Error membaca telemetry: {e}")
        finally:
            if lock:
                lock.release()
        stop_event.wait(interval)

# ---- DroneKit attribute listener example ----

def attitude_callback(self, attr_name, value):
    # Callback dijalankan oleh DroneKit saat attribute berubah
    # value adalah objek Attitude (roll, pitch, yaw)
    try:
        print(f"[LISTENER] Attitude update: roll={value.roll:.3f}, pitch={value.pitch:.3f}, yaw={value.yaw:.3f}")
    except Exception as e:
        print(f"[LISTENER] Error in attitude callback: {e}")

# ---- Main mission with telemetry thread ----

def main():
    print("Connecting to SITL...")
    vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True)
    print(f"Connected. Mode: {vehicle.mode.name}")

    # Event dan Lock untuk koordinasi thread
    stop_event = threading.Event()
    vehicle_lock = threading.Lock()

    # Tambahkan attribute listener (opsional)
    vehicle.add_attribute_listener('attitude', attitude_callback)

    # Mulai telemetry thread
    t = threading.Thread(target=telemetry_worker, args=(vehicle, stop_event, vehicle_lock), daemon=True)
    t.start()
    print("[INFO] Telemetry thread started")

    try:
        # Jalankan misi sederhana sambil telemetry berjalan di background
        arm_and_takeoff(vehicle, target_altitude=10)

        # Terbang maju 20 m
        goto(vehicle, d_north=20, d_east=0, altitude=10, label="Forward 20m")
        time.sleep(2)

        # Kembali 20 m
        goto(vehicle, d_north=-20, d_east=0, altitude=10, label="Back 20m")
        time.sleep(2)

        # Land
        switch_mode(vehicle, "LAND")
        while vehicle.location.global_relative_frame.alt > 0.2:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        # Beri sinyal stop pada telemetry thread dan tunggu selesai
        stop_event.set()
        t.join(timeout=5)
        print("[INFO] Telemetry thread stopped")

        # Hapus listener jika masih terpasang
        try:
            vehicle.remove_attribute_listener('attitude', attitude_callback)
        except Exception:
            # jika listener sudah terhapus atau tidak didukung, lewati
            pass

        vehicle.close()
        print("Vehicle connection closed. Program keluar")

if __name__ == "__main__":
    main()