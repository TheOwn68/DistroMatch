import platform

def scan_system():
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine()
    }
