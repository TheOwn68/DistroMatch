import platform
import subprocess
import os

def scan_storage():
    system = platform.system()

    # === Windows ===
    if system == "Windows":
        try:
            output = subprocess.check_output(
                "wmic diskdrive get Model,MediaType",
                shell=True
            ).decode(errors="ignore")

            if "SSD" in output.upper():
                return {"type": "SSD"}
            else:
                return {"type": "HDD"}

        except:
            return {"type": "Unknown"}

    # === Linux ===
    if system == "Linux":
        # Check NVMe
        if os.path.exists("/sys/block/nvme0n1"):
            return {"type": "NVMe SSD"}

        # Check rotational flag
        try:
            with open("/sys/block/sda/queue/rotational") as f:
                rotational = f.read().strip()
                if rotational == "0":
                    return {"type": "SSD"}
                else:
                    return {"type": "HDD"}
        except:
            return {"type": "Unknown"}

    return {"type": "Unknown"}
