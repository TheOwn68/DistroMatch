import platform
import subprocess

def scan_gpu():
    system = platform.system()

    # === Windows ===
    if system == "Windows":
        try:
            output = subprocess.check_output(
                "wmic path win32_videocontroller get name",
                shell=True
            ).decode(errors="ignore").split("\n")

            gpus = [line.strip() for line in output if line.strip() and "Name" not in line]

            return {
                "gpu_model": gpus[0] if gpus else "Unknown GPU"
            }

        except:
            return {"gpu_model": "Unknown GPU"}

    # === Linux ===
    if system == "Linux":
        try:
            output = subprocess.check_output(
                "lspci | grep -E 'VGA|3D'",
                shell=True
            ).decode(errors="ignore")

            return {
                "gpu_model": output.strip()
            }

        except:
            return {"gpu_model": "Unknown GPU"}

    return {"gpu_model": "Unknown GPU"}
