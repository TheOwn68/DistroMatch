import psutil
import subprocess
import platform
import os


def detect_laptop():
    # Battery present = laptop
    try:
        battery = psutil.sensors_battery()
        return battery is not None
    except:
        return False


def detect_touchscreen():
    try:
        output = subprocess.check_output("xinput --list", shell=True).decode().lower()
        return "touchscreen" in output or "touch screen" in output
    except:
        return False


def detect_hidpi():
    try:
        output = subprocess.check_output("xdpyinfo | grep dots", shell=True).decode()
        # Example: resolution:    3840x2160 dots (163x163 dots per inch)
        if "dots per inch" in output:
            dpi = int(output.split("per inch")[0].split()[-1])
            return dpi >= 140
    except:
        pass
    return False


def detect_nvidia_optimus():
    try:
        output = subprocess.check_output("lspci", shell=True).decode().lower()
        return ("nvidia" in output and "intel" in output)
    except:
        return False


def detect_amd_apu():
    try:
        output = subprocess.check_output("lspci", shell=True).decode().lower()
        # AMD APU = AMD GPU integrated into CPU, usually shows as "AMD graphics"
        return ("amd" in output and "graphics" in output and "radeon" not in output)
    except:
        return False


def detect_egpu():
    try:
        output = subprocess.check_output("lsusb", shell=True).decode().lower()
        # Thunderbolt + GPU vendor = likely eGPU
        return "thunderbolt" in output and ("nvidia" in output or "amd" in output)
    except:
        return False


def full_scan():
    return {
        "gpu": {
            "gpu_model": platform.uname().machine
        },
        "ram": {
            "total_gb": round(psutil.virtual_memory().total / (1024**3), 2)
        },
        "storage": {
            "type": "ssd"  # placeholder, can be improved later
        },

        # Phase 7 hardware intelligence
        "is_laptop": detect_laptop(),
        "touchscreen": detect_touchscreen(),
        "hidpi": detect_hidpi(),
        "optimus": detect_nvidia_optimus(),
        "amd_apu": detect_amd_apu(),
        "egpu": detect_egpu()
    }
