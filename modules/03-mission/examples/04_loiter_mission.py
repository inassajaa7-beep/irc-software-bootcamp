import drone
import time
import threading
import signal
import sys
import os

# PORT = '127.0.0.1:14550'
# PORT = 'tcp:127.0.0.1:5760'  # Mission Planner default
PORT = 'tcp:127.0.0.1:5762' # Mission Planner alternative
# PORT = '/dev/ttyACM0' # Serial Port

emergency_landing_triggered = False

def signal_handler(signum, frame):
    global emergency_landing_triggered
    
    if emergency_landing_triggered:
        print("\n" + "!"*60)
        print("[!!] DOUBLE Ctrl+C - FORCE TERMINATING PROGRAM")
        print("!"*60)
        os._exit(1)
    
    emergency_landing_triggered = True
    
    print("\n" + "!"*60)
    print("[!] Ctrl+C DETECTED - EMERGENCY LANDING INITIATED")
    print("!"*60)
    print("[!] LAND mode emergency landing starting...")
    print("[!] Press Ctrl+C AGAIN to force exit")
    print("!"*60)
    
    try:
        drone.emergency_shutdown.set()
        drone.shutdown_event.set()
        
        if hasattr(drone, 'vehicle') and drone.vehicle is not None:
            print("[!] Attempting immediate LAND mode emergency landing...")
            
            try:
                if drone.emergency_land_immediate():
                    print("[!] Emergency LAND mode successful!")
                    time.sleep(2)
                    sys.exit(0)
                else:
                    print("[!] Emergency LAND failed - using enhanced failsafe")
                    drone.enhanced_fail_safe()
            except Exception as e:
                print(f"[!] Emergency landing error: {e}")
                print("[!] Falling back to enhanced failsafe...")
                drone.enhanced_fail_safe()
                
        else:
            print("[!] No vehicle connected - safe to exit")
            
    except Exception as e:
        print(f"[!] Critical error during emergency: {e}")
        print("[!] Force terminating...")
    finally:
        print("[!] Emergency procedure completed - program terminating")
        time.sleep(1)
        sys.exit(0)

def safe_input(prompt):
    global emergency_landing_triggered
    
    if emergency_landing_triggered:
        return ""
        
    try:
        return input(prompt)
    except KeyboardInterrupt:
        return ""

# ========== LOITER MISSION ==========

def loiter_arm_only():
    """LOITER Option 1: Arm only"""
    global emergency_landing_triggered
    
    try:
        print("=== [LOITER MISSION 1: ARM ONLY] ===")
        print("[INFO] Press Ctrl+C anytime for emergency landing")
        
        drone.shutdown_event.clear()
        drone.connect_drone(PORT)
        
        print("=== [ARMING IN GUIDED MODE] ===")
        if not drone.arming():
            print("Arming failed!")
            return
            
        print("=== [ARMED - MONITORING 5s] ===")
        print("[INFO] Vehicle is now ARMED - Ctrl+C will trigger emergency landing")
        
        for i in range(5):
            if emergency_landing_triggered or drone.shutdown_event.is_set():
                print("[!] Emergency landing triggered!")
                return
            print(f"  ... armed and ready ({i+1}/5)")
            time.sleep(1)
        
        print("=== [DISARMING] ===")
        if drone.vehicle and drone.vehicle.armed:
            drone.vehicle.armed = False
            print("Vehicle disarmed")
            
        drone.disconnect()
        
    except Exception as e:
        print(f"[!] Mission error: {e}")
        if not emergency_landing_triggered:
            try:
                drone.enhanced_fail_safe()
            except Exception as fe:
                print(f"[!] Failsafe error: {fe}")
    finally:
        print("=== [MISSION COMPLETED] ===")

def loiter_arm_takeoff():
    """LOITER Option 2: Arm + Takeoff 1.5m"""
    global emergency_landing_triggered
    TAKEOFF_ALT = 1.5
    
    try:
        print("=== [LOITER MISSION 2: ARM + TAKEOFF] ===")
        print("[INFO] Press Ctrl+C anytime for emergency landing")
        
        drone.shutdown_event.clear()
        drone.connect_drone(PORT)
        
        print("=== [TAKEOFF - LOITER MODE] ===")
        if not drone.takeoff_loiter(TAKEOFF_ALT):
            return
            
        if not drone.start_giving_thrust():
            return
        
        print(f"[INFO] Flying at {TAKEOFF_ALT}m - Ctrl+C will emergency land")
        
        print("=== [HOVERING 5s] ===")
        for i in range(5):
            if emergency_landing_triggered or drone.shutdown_event.is_set():
                print("[!] Emergency landing triggered!")
                return
            print(f"  ... hovering at {TAKEOFF_ALT}m ({i+1}/5)")
            time.sleep(1)
        
        print("=== [NORMAL LANDING] ===")
        drone.stop_giving_thrust()
        drone.landing_disconnect()
        
    except Exception as e:
        print(f"[!] Mission error: {e}")
        if not emergency_landing_triggered:
            try:
                drone.enhanced_fail_safe()
            except Exception as fe:
                print(f"[!] Failsafe error: {fe}")
    finally:
        print("=== [MISSION COMPLETED] ===")

def loiter_arm_takeoff_forward():
    """LOITER Option 3: Arm + Takeoff + Forward 3m"""
    global emergency_landing_triggered
    TAKEOFF_ALT = 1.5
    FORWARD_DIST = 3
    
    try:
        print("=== [LOITER MISSION 3: ARM + TAKEOFF + FORWARD] ===")
        print("[INFO] Press Ctrl+C anytime for emergency landing")
        
        drone.shutdown_event.clear()
        drone.connect_drone(PORT)
        
        print("=== [TAKEOFF - LOITER MODE] ===")
        if not drone.takeoff_loiter(TAKEOFF_ALT):
            return
            
        if not drone.start_giving_thrust():
            return
        
        print(f"=== [MOVING FORWARD {FORWARD_DIST}m] ===")
        print("[INFO] Moving forward - Ctrl+C will emergency land")
        
        if emergency_landing_triggered or drone.shutdown_event.is_set():
            return
            
        drone.move_forward_loiter(FORWARD_DIST, speed=1420)
        
        if emergency_landing_triggered or drone.shutdown_event.is_set():
            return
        
        print("=== [HOVERING 3s] ===")
        for i in range(3):
            if emergency_landing_triggered or drone.shutdown_event.is_set():
                print("[!] Emergency landing triggered!")
                return
            print(f"  ... hovering ({i+1}/3)")
            time.sleep(1)
        
        print("=== [NORMAL LANDING] ===")
        drone.stop_giving_thrust()
        drone.landing_disconnect()
        
    except Exception as e:
        print(f"[!] Mission error: {e}")
        if not emergency_landing_triggered:
            try:
                drone.enhanced_fail_safe()
            except Exception as fe:
                print(f"[!] Failsafe error: {fe}")
    finally:
        print("=== [MISSION COMPLETED] ===")

def loiter_arm_takeoff_forward_turn():
    """LOITER Option 4: Arm + Takeoff + Forward + Turn Right + Hover"""
    global emergency_landing_triggered
    TAKEOFF_ALT = 1.5
    FORWARD_DIST = 3
    
    try:
        print("=== [LOITER MISSION 4: ARM + TAKEOFF + FORWARD + TURN RIGHT] ===")
        print("[INFO] Press Ctrl+C anytime for emergency landing")
        
        drone.shutdown_event.clear()
        drone.connect_drone(PORT)
        
        print("=== [TAKEOFF - LOITER MODE] ===")
        if not drone.takeoff_loiter(TAKEOFF_ALT):
            return
        if not drone.start_giving_thrust():
            return
        
        print(f"=== [MOVING FORWARD {FORWARD_DIST}m] ===")
        if emergency_landing_triggered or drone.shutdown_event.is_set():
            return
        drone.move_forward_loiter(FORWARD_DIST, speed=1420)
        
        print("=== [HOVERING 5s BEFORE TURN] ===")
        for i in range(5):
            if emergency_landing_triggered or drone.shutdown_event.is_set():
                print("[!] Emergency landing triggered!")
                return
            print(f"  ... hovering before turn ({i+1}/5)")
            time.sleep(1)
        
        print("=== [TURN RIGHT 90°] ===")
        if emergency_landing_triggered or drone.shutdown_event.is_set():
            return
        drone.turn_right_loiter(90, speed=1550)
        
        print("=== [HOVERING 5s AFTER TURN] ===")
        for i in range(5):
            if emergency_landing_triggered or drone.shutdown_event.is_set():
                print("[!] Emergency landing triggered!")
                return
            print(f"  ... hovering after turn ({i+1}/5)")
            time.sleep(1)
        
        print("=== [NORMAL LANDING] ===")
        drone.stop_giving_thrust()
        drone.landing_disconnect()
        
    except Exception as e:
        print(f"[!] Mission error: {e}")
        if not emergency_landing_triggered:
            try:
                drone.enhanced_fail_safe()
            except Exception as fe:
                print(f"[!] Failsafe error: {fe}")
    finally:
        print("=== [MISSION COMPLETED] ===")

def loiter_arm_takeoff_forward_turn_forward():
    """LOITER Option 5: Arm + Takeoff + Forward + Turn Right + Forward 2m"""
    global emergency_landing_triggered
    TAKEOFF_ALT = 1.5
    FORWARD_DIST1 = 3
    FORWARD_DIST2 = 2
    
    try:
        print("=== [LOITER MISSION 5: FULL SEQUENCE] ===")
        print("[INFO] Press Ctrl+C anytime for emergency landing")
        
        drone.shutdown_event.clear()
        drone.connect_drone(PORT)
        
        print("=== [TAKEOFF - LOITER MODE] ===")
        if not drone.takeoff_loiter(TAKEOFF_ALT):
            return
        if not drone.start_giving_thrust():
            return
        
        print(f"=== [MOVING FORWARD {FORWARD_DIST1}m] ===")
        if emergency_landing_triggered or drone.shutdown_event.is_set():
            return
        drone.move_forward_loiter(FORWARD_DIST1, speed=1420)
        
        print("=== [HOVERING 3s] ===")
        for i in range(3):
            if emergency_landing_triggered or drone.shutdown_event.is_set():
                print("[!] Emergency landing triggered!")
                return
            print(f"  ... hover ({i+1}/3)")
            time.sleep(1)
        
        print("=== [TURN RIGHT 90°] ===")
        if emergency_landing_triggered or drone.shutdown_event.is_set():
            return
        drone.turn_right_loiter(90, speed=1550)
        
        print("=== [HOVERING 3s] ===")
        for i in range(3):
            if emergency_landing_triggered or drone.shutdown_event.is_set():
                print("[!] Emergency landing triggered!")
                return
            print(f"  ... hover ({i+1}/3)")
            time.sleep(1)
        
        print(f"=== [MOVING FORWARD {FORWARD_DIST2}m] ===")
        if emergency_landing_triggered or drone.shutdown_event.is_set():
            return
        drone.move_forward_loiter(FORWARD_DIST2, speed=1420)
        
        print("=== [HOVERING 3s] ===")
        for i in range(3):
            if emergency_landing_triggered or drone.shutdown_event.is_set():
                print("[!] Emergency landing triggered!")
                return
            print(f"  ... final hover ({i+1}/3)")
            time.sleep(1)
        
        print("=== [NORMAL LANDING] ===")
        drone.stop_giving_thrust()
        drone.landing_disconnect()
        
    except Exception as e:
        print(f"[!] Mission error: {e}")
        if not emergency_landing_triggered:
            try:
                drone.enhanced_fail_safe()
            except Exception as fe:
                print(f"[!] Failsafe error: {fe}")
    finally:
        print("=== [MISSION COMPLETED] ===")

# ========== INDOOR MISSIONS ==========

def indoor_arm_only():
    """INDOOR Option 1: Arm only"""
    global emergency_landing_triggered
    
    try:
        print("=== [INDOOR MISSION 1: ARM ONLY] ===")
        print("[INFO] Press Ctrl+C anytime for emergency landing")
        
        drone.shutdown_event.clear()
        drone.connect_drone(PORT)
        
        print("=== [ARMING IN ALT_HOLD MODE] ===")
        if not drone.arming_althold():
            print("ALT_HOLD arming failed!")
            return
            
        print("=== [ARMED - MONITORING 5s] ===")
        for i in range(5):
            if emergency_landing_triggered or drone.shutdown_event.is_set():
                print("[!] Emergency landing triggered!")
                return
            print(f"  ... armed and ready in ALT_HOLD ({i+1}/5)")
            time.sleep(1)
        
        print("=== [DISARMING] ===")
        if drone.vehicle and drone.vehicle.armed:
            drone.vehicle.armed = False
            print("Vehicle disarmed")
            
        drone.disconnect()
        
    except Exception as e:
        print(f"[!] Mission error: {e}")
        if not emergency_landing_triggered:
            try:
                drone.enhanced_fail_safe()
            except Exception as fe:
                print(f"[!] Failsafe error: {fe}")
    finally:
        print("=== [MISSION COMPLETED] ===")

def indoor_arm_takeoff():
    """INDOOR Option 2: Arm + Takeoff 1.5m (time-based)"""
    global emergency_landing_triggered
    TAKEOFF_ALT = 1.5
    
    try:
        print("=== [INDOOR MISSION 2: ARM + TAKEOFF] ===")
        print("[INFO] Press Ctrl+C anytime for emergency landing")
        
        drone.shutdown_event.clear()
        drone.connect_drone(PORT)
        
        print("=== [TAKEOFF - ALT_HOLD MODE] ===")
        if not drone.takeoff_indoor(TAKEOFF_ALT):
            return
        
        if not drone.start_giving_thrust():
            return
            
        print(f"[INFO] Flying at {TAKEOFF_ALT}m - Ctrl+C will emergency land")
        
        print("=== [HOVERING 5s] ===")
        for i in range(5):
            if emergency_landing_triggered or drone.shutdown_event.is_set():
                print("[!] Emergency landing triggered!")
                return
            print(f"  ... hovering at {TAKEOFF_ALT}m ({i+1}/5)")
            time.sleep(1)
        
        print("=== [LANDING] ===")
        drone.stop_giving_thrust()
        drone.landing_disconnect()
        
    except Exception as e:
        print(f"[!] Mission error: {e}")
        if not emergency_landing_triggered:
            try:
                drone.enhanced_fail_safe()
            except Exception as fe:
                print(f"[!] Failsafe error: {fe}")
    finally:
        print("=== [MISSION COMPLETED] ===")

def indoor_arm_takeoff_forward():
    """INDOOR Option 3: Arm + Takeoff + Forward 3s"""
    global emergency_landing_triggered
    TAKEOFF_ALT = 1.5
    FORWARD_TIME = 3
    
    try:
        print("=== [INDOOR MISSION 3: ARM + TAKEOFF + FORWARD] ===")
        print("[INFO] Press Ctrl+C anytime for emergency landing")
        
        drone.shutdown_event.clear()
        drone.connect_drone(PORT)
        
        print("=== [TAKEOFF - ALT_HOLD MODE] ===")
        if not drone.takeoff_indoor(TAKEOFF_ALT):
            return
            
        if not drone.start_giving_thrust():
            return
        
        print("=== [HOVERING 3s] ===")
        if emergency_landing_triggered or drone.shutdown_event.is_set():
            return
        drone.hover_indoor_time(3.0)
        
        print(f"=== [MOVING FORWARD {FORWARD_TIME}s] ===")
        if emergency_landing_triggered or drone.shutdown_event.is_set():
            return
            
        drone.move_forward_indoor_time(FORWARD_TIME, speed=1420)
        
        print("=== [HOVERING 3s] ===")
        if emergency_landing_triggered or drone.shutdown_event.is_set():
            return
        drone.hover_indoor_time(3.0)
        
        print("=== [LANDING] ===")
        drone.stop_giving_thrust()
        drone.landing_disconnect()
        
    except Exception as e:
        print(f"[!] Mission error: {e}")
        if not emergency_landing_triggered:
            try:
                drone.enhanced_fail_safe()
            except Exception as fe:
                print(f"[!] Failsafe error: {fe}")
    finally:
        print("=== [MISSION COMPLETED] ===")

def indoor_arm_takeoff_forward_turn():
    """INDOOR Option 4: Arm + Takeoff + Forward + Turn Right + Hover"""
    global emergency_landing_triggered
    TAKEOFF_ALT = 1.5
    FORWARD_TIME = 3
    TURN_TIME = 2
    
    try:
        print("=== [INDOOR MISSION 4: ARM + TAKEOFF + FORWARD + TURN] ===")
        print("[INFO] Press Ctrl+C anytime for emergency landing")
        
        drone.shutdown_event.clear()
        drone.connect_drone(PORT)
        
        print("=== [TAKEOFF - ALT_HOLD MODE] ===")
        if not drone.takeoff_indoor(TAKEOFF_ALT):
            return
        
        if not drone.start_giving_thrust():
            return
        
        print(f"=== [MOVING FORWARD {FORWARD_TIME}s] ===")
        if emergency_landing_triggered or drone.shutdown_event.is_set():
            return
        drone.move_forward_indoor_time(FORWARD_TIME, speed=1420)
        
        print("=== [HOVERING 5s BEFORE TURN] ===")
        if emergency_landing_triggered or drone.shutdown_event.is_set():
            return
        drone.hover_indoor_time(5.0)
        
        print(f"=== [TURN RIGHT {TURN_TIME}s] ===")
        if emergency_landing_triggered or drone.shutdown_event.is_set():
            return
        drone.turn_right_indoor_time(TURN_TIME, speed=1550)
        
        print("=== [HOVERING 5s AFTER TURN] ===")
        if emergency_landing_triggered or drone.shutdown_event.is_set():
            return
        drone.hover_indoor_time(5.0)
        
        print("=== [LANDING] ===")
        drone.stop_giving_thrust()
        drone.landing_disconnect()
        
    except Exception as e:
        print(f"[!] Mission error: {e}")
        if not emergency_landing_triggered:
            try:
                drone.enhanced_fail_safe()
            except Exception as fe:
                print(f"[!] Failsafe error: {fe}")
    finally:
        print("=== [MISSION COMPLETED] ===")

def indoor_arm_takeoff_forward_turn_forward():
    """INDOOR Option 5: Arm + Takeoff + Forward + Turn Right + Forward 2s"""
    global emergency_landing_triggered
    TAKEOFF_ALT = 1.5
    FORWARD_TIME1 = 3
    TURN_TIME = 2
    FORWARD_TIME2 = 2
    
    try:
        print("=== [INDOOR MISSION 5: FULL SEQUENCE] ===")
        print("[INFO] Press Ctrl+C anytime for emergency landing")
        
        drone.shutdown_event.clear()
        drone.connect_drone(PORT)
        
        print("=== [TAKEOFF - ALT_HOLD MODE] ===")
        if not drone.takeoff_indoor(TAKEOFF_ALT):
            return
        
        if not drone.start_giving_thrust():
            return
        
        print(f"=== [MOVING FORWARD {FORWARD_TIME1}s] ===")
        if emergency_landing_triggered or drone.shutdown_event.is_set():
            return
        drone.move_forward_indoor_time(FORWARD_TIME1, speed=1420)
        
        print(f"=== [TURN RIGHT {TURN_TIME}s] ===")
        if emergency_landing_triggered or drone.shutdown_event.is_set():
            return
        drone.turn_right_indoor_time(TURN_TIME, speed=1550)
        
        print(f"=== [MOVING FORWARD {FORWARD_TIME2}s] ===")
        if emergency_landing_triggered or drone.shutdown_event.is_set():
            return
        drone.move_forward_indoor_time(FORWARD_TIME2, speed=1420)
        
        print("=== [HOVERING 3s] ===")
        if emergency_landing_triggered or drone.shutdown_event.is_set():
            return
        drone.hover_indoor_time(3.0)
        
        print("=== [LANDING] ===")
        drone.stop_giving_thrust()
        drone.landing_disconnect()
        
    except Exception as e:
        print(f"[!] Mission error: {e}")
        if not emergency_landing_triggered:
            try:
                drone.enhanced_fail_safe()
            except Exception as fe:
                print(f"[!] Failsafe error: {fe}")
    finally:
        print("=== [MISSION COMPLETED] ===")

# ========== UTILITY FUNCTIONS ==========

def show_safety_info():
    """Show comprehensive safety information"""
    print("="*70)
    print("EMERGENCY LANDING SYSTEM")
    print("="*70)
    print("• Press Ctrl+C ONCE for emergency landing")
    print("• Press Ctrl+C TWICE for force exit")
    print("• Emergency landing works during any flight phase")
    print("• Pilot can always override via remote control")
    print("• LOITER mode requires GPS lock")
    print("• INDOOR mode works tanpa GPS (ALT_HOLD)")
    print("="*70)

def show_loiter_menu():
    """Show LOITER mode menu"""
    print("\n" + "="*50)
    print("LOITER MODE MISSIONS (OUTDOOR - GPS REQUIRED)")
    print("="*50)
    print("1. Arm only")
    print("2. Arm + Takeoff 1.5m")
    print("3. Arm + Takeoff + Forward 3m")
    print("4. Arm + Takeoff + Forward + Turn Right + Hover")
    print("5. Arm + Takeoff + Forward + Turn Right + Forward 2m")
    print("="*50)
    print("[INFO] Ctrl+C will emergency land at any time")

def show_indoor_menu():
    """Show INDOOR mode menu"""
    print("\n" + "="*50)
    print("INDOOR MODE MISSIONS (ALT_HOLD - NO GPS)")
    print("="*50)
    print("1. Arm only")
    print("2. Arm + Takeoff 1.5m")
    print("3. Arm + Takeoff + Forward 3s")
    print("4. Arm + Takeoff + Forward + Turn Right + Hover")
    print("5. Arm + Takeoff + Forward + Turn Right + Forward 2s")
    print("="*50)
    print("[INFO] Ctrl+C will emergency land at any time")

def run_loiter_mission(choice):
    """Execute LOITER mission based on choice"""
    missions = {
        "1": loiter_arm_only,
        "2": loiter_arm_takeoff,
        "3": loiter_arm_takeoff_forward,
        "4": loiter_arm_takeoff_forward_turn,
        "5": loiter_arm_takeoff_forward_turn_forward
    }
    
    if choice in missions:
        missions[choice]()
    else:
        print("Invalid choice! Running default: Arm only")
        loiter_arm_only()

def run_indoor_mission(choice):
    """Execute INDOOR mission based on choice"""
    missions = {
        "1": indoor_arm_only,
        "2": indoor_arm_takeoff,
        "3": indoor_arm_takeoff_forward,
        "4": indoor_arm_takeoff_forward_turn,
        "5": indoor_arm_takeoff_forward_turn_forward
    }
    
    if choice in missions:
        missions[choice]()
    else:
        print("Invalid choice! Running default: Arm only")
        indoor_arm_only()

# ========== MAIN PROGRAM ==========

if __name__ == "__main__":
    
    signal.signal(signal.SIGINT, signal_handler)
    
    show_safety_info()
    
    print("\nSelect flight mode:")
    print("1. LOITER mode (Outdoor - GPS)")
    print("2. INDOOR mode (ALT_HOLD - No GPS)")
    
    mode_choice = safe_input("Enter mode (1-2): ").strip()
    
    if emergency_landing_triggered:
        print("Program terminated during selection")
        sys.exit(0)
    
    if mode_choice == "1":
        # LOITER MODE
        show_loiter_menu()
        mission_choice = safe_input("Enter LOITER mission (1-5): ").strip()
        
        if not emergency_landing_triggered:
            print(f"\nExecuting LOITER mission {mission_choice}...")
            run_loiter_mission(mission_choice)
        
    elif mode_choice == "2":
        # INDOOR MODE
        show_indoor_menu()
        mission_choice = safe_input("Enter INDOOR mission (1-5): ").strip()
        
        if not emergency_landing_triggered:
            print(f"\nExecuting INDOOR mission {mission_choice}...")
            run_indoor_mission(mission_choice)
        
    else:
        if not emergency_landing_triggered:
            print("Invalid mode selection!")
            print("Running default: LOITER mode, Arm only...")
            loiter_arm_only()
    
    if not emergency_landing_triggered:
        print("\n" + "="*60)
        print("MISSION PROGRAM COMPLETED SUCCESSFULLY")
        print("="*60)