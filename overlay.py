import tkinter as tk
import psutil
import subprocess

def install_dependencies():
    try:
        subprocess.run(["pip", "install", "psutil"])  # Install psutil
        subprocess.run(["pip", "install", "nvidia-smi"])  # Install nvidia-smi
    except Exception as e:
        print(f"Failed to install dependencies: {str(e)}")

# Function to ask the user if they want to install dependencies
def ask_install_dependencies():
    while True:
        choice = input("Do you want to install dependencies (psutil and nvidia-smi)? (y/n): ").strip().lower()
        if choice in {'y', 'yes'}:
            install_dependencies()
            break
        elif choice in {'n', 'no'}:
            print("Skipping dependency installation.")
            break
        else:
            print("Invalid choice. Please enter 'y' (yes) or 'n' (no).")
            
# Function to read CPU temperature (Linux-specific)
def read_cpu_temperature():
    try:
        # Replace 'k10temp-pci-00c3' with your actual sensor name
        with open('/sys/class/hwmon/hwmon2/temp1_input', 'r') as file:
            temperature = int(file.read().strip()) / 1000.0  # Convert to Celsius
        return f'CPU Temperature: {temperature:.2f}°C'
    except FileNotFoundError:
        return 'CPU Temperature: N/A'

# Function to read CPU frequency and usage per core
def read_cpu_info():
    freqs = psutil.cpu_freq(percpu=True)
    usage = psutil.cpu_percent(interval=1, percpu=True)

    info = ''
    for i, (freq, u) in enumerate(zip(freqs, usage)):
        info += f'Core {i}: | {u:.1f}%, | {freq.current/1000:.2f} GHz\n'
    return info

# Function to read RAM utilization
def read_ram_info():
    ram = psutil.virtual_memory()
    return f'RAM Usage: {ram.percent:.2f}% ({ram.used / (1024 ** 3):.2f}GB used / {ram.total / (1024 ** 3):.2f}GB)'

# Function to read storage utilization
def read_storage_info():
    partitions = psutil.disk_partitions()
    storage_info = 'Storage Info:\n'
    for partition in partitions:
        usage = psutil.disk_usage(partition.mountpoint)
        storage_info += f'  Partition: {partition.device}\n'
        storage_info += f'    Usage: {usage.percent:.2f}% ({usage.used / (1024 ** 3):.2f}GB used / {usage.total / (1024 ** 3):.2f}GB)\n'
    return storage_info

# Function to read CPU name
def read_cpu_name():
    try:
        with open('/proc/cpuinfo', 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.strip().startswith('model name'):
                    return line.split(':')[1].strip()
        return 'CPU Name: N/A'
    except FileNotFoundError:
        return 'CPU Name: N/A'

# Function to read GPU info using nvidia-smi command
def read_gpu_info():
    try:
        result = subprocess.check_output(['nvidia-smi', '--query-gpu=name,driver_version,utilization.gpu,utilization.memory,memory.total,memory.free,memory.used,temperature.gpu', '--format=csv,noheader,nounits'])
        result = result.decode('utf-8').strip().split('\n')
        
        if len(result) == 0:
            return 'GPU INFO: N/A'

        gpu_info = 'GPU INFO:\n'
        for i, line in enumerate(result):
            info = line.split(', ')
            gpu_info += f'GPU {i + 1}:\n'
            gpu_info += f'  Name: {info[0]}\n'
            gpu_info += f'  Driver Version: {info[1]}\n'
            #gpu_info += f'  GPU Usage: {info[2]}%\n'
            total_memory = int(info[4]) / 1024  # Convert to MB
            used_memory = int(info[6]) / 1024   # Convert to MB
            memory_usage = (used_memory / total_memory) * 100 
            gpu_info += f'  GPU Memory Usage: {memory_usage:.2f}%\n'
            gpu_info += f'  Total Memory: {info[4]} MB\n'
            gpu_info += f'  Free Memory: {info[5]} MB\n'
            gpu_info += f'  Used Memory: {info[6]} MB\n\n'
            gpu_info += f'  GPU Temperature: {info[7]}°C\n'
        return gpu_info
    except subprocess.CalledProcessError:
        return 'GPU INFO: N/A'

# Function to update CPU and GPU information
def update_info():
    cpu_name = read_cpu_name()
    temperature_info = read_cpu_temperature()
    cpu_info = read_cpu_info()
    gpu_info = read_gpu_info()
    ram_info = read_ram_info()
    storage_info = read_storage_info()

    info_label.config(text=f'{cpu_name}\n{cpu_info}\n{temperature_info}\n_____________________________\n{gpu_info}\n_____________________________\n\n{ram_info}\n_____________________________\n{storage_info}')

    # Schedule the next update
    root.after(100, update_info)  # Update every 1 second

# Create the Tkinter window
root = tk.Tk()
root.title('CPU and GPU Information')

# Make the window slightly transparent (0.9 alpha)
root.attributes('-alpha', 0.9)

# Ask before Install Python dependencies
install_dependencies()

# Create a label for CPU and GPU information
info_label = tk.Label(root, text='CPU INFO:\nN/A\n\nCPU TEMPERATURE: N/A\n\nGPU INFO: N/A', font=("Ubuntu", 10))

# Pack the information label into the window
info_label.pack()

# Start updating CPU and GPU information
update_info()

# Start the Tkinter main loop
root.mainloop()
