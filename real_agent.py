# real_agent.py
# V11 FINAL: SMART HUNTER + EXECUTION REPORTING
# Protects dashboard/server by checking command line arguments.

import timeit
import requests
import psutil
import os
import socket
import wmi
import pythoncom
import time # Import time module

SERVER_URL = "http://127.0.0.1:5000"
REPORT_URL = f"{SERVER_URL}/report"
COMMAND_URL = f"{SERVER_URL}/get_command"
EXEC_URL = f"{SERVER_URL}/report_execution"
MACHINE_ID = socket.gethostname()
MY_PID = os.getpid()

# --- SAFETY LIST ---
SAFE_LIST_NAMES = [
    "System Idle Process", "System", "Registry", "smss.exe", "csrss.exe", 
    "wininit.exe", "services.exe", "lsass.exe", "svchost.exe", "explorer.exe",
    "Code.exe", "devenv.exe", "taskmgr.exe",
    "chrome.exe", "msedge.exe", "firefox.exe", "brave.exe"
]
SAFE_LIST_PIDS = [0, 4]

# --- METRICS ---
def get_real_windows_temp():
    try:
        pythoncom.CoInitialize()
        w = wmi.WMI(namespace="root\\wmi")
        temp = w.MSAcpi_ThermalZoneTemperature()[0].CurrentTemperature
        return (temp / 10.0) - 273.15
    except: return 35.0

def get_real_metrics():
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().percent
    temp = get_real_windows_temp()
    if temp < 40: temp = temp + (cpu / 100.0) * 30.0 
    return cpu, ram, temp, 0

# --- THE SMART HUNTER ---
def kill_highest_consumer(command_id):
    print("\n========================================")
    print(f"💀 PREDATOR MODE ACTIVATED (CMD ID: {command_id})")
    print("========================================")
    
    psutil.cpu_percent()
    time.sleep(1)
    highest_usage = 0
    target_proc = None
    reason_str = ""
    
    print("🔎 Finding top consumer (Threshold: >15%)...")
    
    # Iterate over processes, getting cmdline too
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'cmdline']):
        try:
            p_info = proc.info
            pid = p_info['pid']
            name = p_info['name']
            c_use = p_info['cpu_percent']
            m_use = p_info['memory_percent']
            cmdline = p_info['cmdline'] # This is a list of arguments

            usage_score = c_use + m_use 

            if usage_score > 15.0:
                # --- BASIC SAFETY CHECKS ---
                if pid == MY_PID or pid in SAFE_LIST_PIDS: continue
                if name in SAFE_LIST_NAMES:
                    print(f"   -> [SAFE] Skipping whitelist app: {name} ({c_use:.0f}%)")
                    continue
                
                # --- SMART PYTHON CHECK ---
                # If it's python, check what script it's running
                if 'python' in name.lower() and cmdline:
                    cmd_str = " ".join(cmdline).lower()
                    # If it's running dashboard, server, or agent, skip it!
                    if 'dashboard.py' in cmd_str or 'server.py' in cmd_str or 'real_agent.py' in cmd_str or 'streamlit' in cmd_str:
                        print(f"   -> [SAFE] Skipping Argus component: {cmd_str} ({c_use:.0f}%)")
                        continue
                        
                # Valid Target found
                print(f"   -> [UNSAFE] Found target: {name} (PID:{pid}) | CPU:{c_use:.1f}% RAM:{m_use:.1f}%")
                
                if usage_score > highest_usage:
                    highest_usage = usage_score
                    target_proc = proc
                    if c_use > m_use: reason_str = f"High CPU ({c_use:.1f}%)"
                    else: reason_str = f"High RAM ({m_use:.1f}%)"

        except (psutil.NoSuchProcess, psutil.AccessDenied): continue

    if target_proc and highest_usage > 15.0:
        proc_name = target_proc.info['name']
        pid = target_proc.info['pid']
        print(f"\n🎯 TARGET LOCKED: {proc_name} (PID: {pid})")
        print("⏳ TERMINATING IN 3 SECONDS...")
        time.sleep(3)
        print("💥 TERMINATING NOW...")
        try:
            target_proc.terminate()
            print("✅ THREAT ELIMINATED.")
            details_msg = f"Terminated {proc_name} (PID: {pid}) due to {reason_str}."
            requests.post(EXEC_URL, json={'id': command_id, 'details': details_msg})
        except Exception as e:
            print(f"❌ FAILED TO KILL: {e}")
            requests.post(EXEC_URL, json={'id': command_id, 'details': f"Failed to terminate {proc_name}: {e}"})
    else:
        print("❓ Scan complete. No unsafe targets found.")
        requests.post(EXEC_URL, json={'id': command_id, 'details': "Scan complete. No unsafe targets found."})


def main():
    print(f"🛡️ Argus Smart Agent Online: {MACHINE_ID}")
    try:
        while True:
            cpu, ram, temp, net = get_real_metrics()
            try:
                requests.post(REPORT_URL, json={'machine_id': MACHINE_ID, 'cpu': cpu, 'ram': ram, 'temp': temp, 'network': net})
                print(f"Reported: C:{cpu:.0f}% R:{ram:.0f}% | Waiting...")
            except: print("Server connection lost.")

            try:
                res = requests.get(f"{COMMAND_URL}/{MACHINE_ID}", timeout=1)
                if res.status_code == 200:
                    data = res.json()
                    cmd_id = data.get('id')
                    if data.get('command') == "KILL_PROCESS" and cmd_id is not None:
                        print(f"\n🚨 COMMAND {cmd_id} RECEIVED: EXECUTE KILL PROTOCOL")
                        kill_highest_consumer(cmd_id)
                        time.sleep(3)
            except Exception as e: pass
            time.sleep(1)
    except KeyboardInterrupt: print("Agent stopping.")

if __name__ == "__main__":
    main()