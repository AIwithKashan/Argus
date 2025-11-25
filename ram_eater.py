# ram_eater.py
# WARNING: This will fill your RAM up to 95% and might make your PC lag.
import time
import psutil
import os

def eat_memory():
    print(f"💾 RAM EATER STARTED (PID: {os.getpid()})")
    data = []
    while True:
        # Keep allocating 100MB chunks until we hit 95% RAM usage
        if psutil.virtual_memory().percent < 95:
            data.append(' ' * 100 * 1024 * 1024) # Allocate 100MB string
            print(f"Allocated... Current RAM: {psutil.virtual_memory().percent}%")
            time.sleep(1)
        else:
            print("RAM full. Holding...")
            time.sleep(5)

if __name__ == "__main__":
    try:
        eat_memory()
    except KeyboardInterrupt:
        print("Stopped.")
    except MemoryError:
        print("System ran out of memory completely!")