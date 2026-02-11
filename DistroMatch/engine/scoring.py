import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "distros.json"


def load_distros():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------
# GPU Vendor Detection
# ---------------------------------------------------------
def detect_gpu_vendor(gpu_model: str) -> str:
    model = gpu_model.lower()
    if any(x in model for x in ["nvidia", "geforce", "rtx", "gtx"]):
        return "nvidia"
    if any(x in model for x in ["amd", "radeon"]):
        return "amd"
    if any(x in model for x in ["intel", "uhd", "iris"]):
        return "intel"
    return "unknown"


# ---------------------------------------------------------
# RAM + Storage Helpers
# ---------------------------------------------------------
def get_ram_gb(hardware: dict) -> float:
    try:
        return float(hardware.get("ram", {}).get("total_gb", 0))
    except:
        return 0.0


def get_storage_type(hardware: dict) -> str:
    return hardware.get("storage", {}).get("type", "unknown").lower()


# ---------------------------------------------------------
# Hardware Score (Base)
# ---------------------------------------------------------
def hardware_score(distro: dict, hardware: dict, usecase: str) -> float:
    gpu_model = hardware.get("gpu", {}).get("gpu_model", "Unknown GPU")
    vendor = detect_gpu_vendor(gpu_model)
    ram_gb = get_ram_gb(hardware)
    storage = get_storage_type(hardware)

    gpu_support = distro.get("gpu_support", {})
    gpu_score = gpu_support.get(vendor, 5)

    # Work/Browsing: GPU barely matters
    if usecase.lower() in ["work", "browsing"]:
        gpu_score *= 0.1

    # RAM scoring
    ram_min = distro.get("ram_min", 2)
    ram_opt = distro.get("ram_optimal", 4)

    if ram_gb < ram_min:
        ram_score = 2
    elif ram_min <= ram_gb < ram_opt:
        ram_score = 7
    else:
        ram_score = 10

    # Storage scoring
    storage_bonus = 0
    if "hdd" in storage:
        if distro.get("desktop", "").lower() in ["gnome", "cosmic"]:
            storage_bonus -= 2
        else:
            storage_bonus += 1
    elif "ssd" in storage or "nvme" in storage:
        storage_bonus += 1

    score = (gpu_score * 0.2) + (ram_score * 0.8) + storage_bonus
    return max(0, min(10, score))


# ---------------------------------------------------------
# Phase 7 — Hardware Intelligence (Moderate Influence)
# ---------------------------------------------------------
def hardware_intelligence_bonus(distro: dict, hardware: dict) -> float:
    bonus = 0
    desktop = distro.get("desktop", "").lower()
    categories = [c.lower() for c in distro.get("category", [])]

    # Laptop → prefer distros with good power management
    if hardware.get("is_laptop"):
        if "work" in categories:
            bonus += 2
        if desktop in ["gnome", "kde", "cosmic"]:
            bonus += 1

    # Touchscreen → GNOME / KDE / COSMIC
    if hardware.get("touchscreen"):
        if desktop in ["gnome", "kde", "cosmic"]:
            bonus += 2
        else:
            bonus -= 1

    # HiDPI → GNOME / KDE / COSMIC
    if hardware.get("hidpi"):
        if desktop in ["gnome", "kde", "cosmic"]:
            bonus += 2
        else:
            bonus -= 1

    # NVIDIA Optimus → Pop!_OS, Fedora, Ubuntu
    if hardware.get("optimus"):
        name = distro.get("name", "").lower()
        if any(x in name for x in ["pop", "fedora", "ubuntu"]):
            bonus += 3
        if "gaming" in categories:
            bonus -= 2

    # AMD APU → Mesa-friendly distros (Fedora, Ubuntu, Mint)
    if hardware.get("amd_apu"):
        name = distro.get("name", "").lower()
        if any(x in name for x in ["fedora", "ubuntu", "mint"]):
            bonus += 2

    # eGPU → Fedora / Ubuntu best Thunderbolt support
    if hardware.get("egpu"):
        name = distro.get("name", "").lower()
        if any(x in name for x in ["fedora", "ubuntu"]):
            bonus += 2

    return bonus


# ---------------------------------------------------------
# Use-case Score
# ---------------------------------------------------------
def usecase_score(distro: dict, usecase: str) -> float:
    usecase = usecase.lower()
    categories = [c.lower() for c in distro.get("category", [])]

    # HARD BAN gaming distros for Work/Browsing
    if usecase in ["work", "browsing"] and "gaming" in categories:
        return -999

    if usecase == "work":
        if "work" in categories:
            return 15
        if "general" in categories:
            return 10
        if "lightweight" in categories:
            return 8
        return 5

    if usecase == "browsing":
        if "lightweight" in categories:
            return 15
        if "general" in categories:
            return 10
        if "work" in categories:
            return 8
        return 5

    if usecase == "gaming":
        if "gaming" in categories:
            return 15
        if "general" in categories:
            return 10
        return 5

    return 5


# ---------------------------------------------------------
# Skill Score
# ---------------------------------------------------------
def skill_score(distro: dict, skill_level: str, usecase: str) -> float:
    skill_level = skill_level.lower()
    skill_map = distro.get("skill", {})
    base = skill_map.get(skill_level, 0)
    categories = [c.lower() for c in distro.get("category", [])]

    # Work/Browsing: boost work distros
    if usecase.lower() in ["work", "browsing"]:
        if "work" in categories:
            base += 15
        if "lightweight" in categories and usecase == "browsing":
            base += 15
        if "gaming" in categories:
            base -= 20

    return base


# ---------------------------------------------------------
# Stability + Performance
# ---------------------------------------------------------
def stability_score(distro: dict) -> float:
    return float(distro.get("stability", 7))


def performance_score(distro: dict, usecase: str) -> float:
    if usecase.lower() in ["work", "browsing"]:
        return 0
    return float(distro.get("performance", 7))


# ---------------------------------------------------------
# FINAL SCORE
# ---------------------------------------------------------
def compute_final_score(distro: dict, hardware: dict, usecase: str, skill_level: str) -> float:

    if usecase.lower() in ["work", "browsing"]:
        weights = {
            "hardware": 0.10,
            "usecase":  0.45,
            "skill":    0.40,
            "stab":     0.05,
            "perf":     0.00
        }
    else:
        weights = {
            "hardware": 0.35,
            "usecase":  0.30,
            "skill":    0.20,
            "stab":     0.10,
            "perf":     0.05
        }

    h = hardware_score(distro, hardware, usecase)
    h2 = hardware_intelligence_bonus(distro, hardware)
    u = usecase_score(distro, usecase)
    s = skill_score(distro, skill_level, usecase)
    stab = stability_score(distro)
    perf = performance_score(distro, usecase)

    final = (
        (h + h2) * weights["hardware"] +
        u * weights["usecase"] +
        s * weights["skill"] +
        stab * weights["stab"] +
        perf * weights["perf"]
    )

    return round(final, 2)
