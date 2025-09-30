
import psutil
import time

def main():
    # Initialize log file
    resource_log_file = open("system_resource_usage.txt", "w")
    resource_log_file.write("Timestamp,CPU (%),Memory (MB)\n")
    print("Monitoring system CPU and memory usage. Press Ctrl+C to stop.")

    try:
        while True:
            # Get CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            memory_mb = memory_info.used / 1024 / 1024  # Convert to MB

            # Log to file and console
            timestamp = time.strftime('%H:%M:%S')
            resource_log_file.write(f"{timestamp},{cpu_percent:.2f},{memory_mb:.2f}\n")
            print(f"[{timestamp}] CPU: {cpu_percent:.2f}%, Memory: {memory_mb:.2f} MB")

            # Wait 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        print("Stopped monitoring.")
        resource_log_file.close()
        print("Resource usage saved to system_resource_usage.txt")

if __name__ == "__main__":
    main()
