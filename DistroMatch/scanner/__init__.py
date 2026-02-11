from .cpu import scan_cpu
from .gpu import scan_gpu
from .ram import scan_ram
from .storage import scan_storage
from .system import scan_system

def full_scan():
    return {
        "cpu": scan_cpu(),
        "gpu": scan_gpu(),
        "ram": scan_ram(),
        "storage": scan_storage(),
        "system": scan_system()
    }
