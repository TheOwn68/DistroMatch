import psutil

def scan_ram():
    mem = psutil.virtual_memory()

    return {
        "total_gb": round(mem.total / (1024**3), 2)
    }
