import platform
import cpuinfo

def scan_cpu():
    info = cpuinfo.get_cpu_info()

    return {
        "cpu_model": info.get("brand_raw", "Unknown CPU"),
        "architecture": platform.machine(),
        "cores": info.get("count", 0),
        "flags": info.get("flags", []),
    }
