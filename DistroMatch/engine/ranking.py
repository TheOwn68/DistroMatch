import json
from pathlib import Path
from .scoring import load_distros, compute_final_score

# Path to distro profiles (Phase 8)
PROFILE_PATH = Path(__file__).resolve().parent.parent / "data" / "profiles.json"


def load_profiles():
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


# ---------------------------------------------------------
# MAIN RECOMMENDATION FUNCTION
# ---------------------------------------------------------
def get_recommendations(hardware: dict, usecase: str, skill_level: str) -> dict:
    distros = load_distros()
    scored = []

    for key, distro in distros.items():

        # CATEGORY LIST
        categories = [c.lower() for c in distro.get("category", [])]

        # HARD EXCLUSION RULES
        # Work + Browsing should NEVER show gaming distros
        if usecase.lower() in ["work", "browsing"] and "gaming" in categories:
            continue

        # Browsing should avoid heavy desktops unless lightweight
        if usecase.lower() == "browsing":
            if distro.get("desktop", "").lower() in ["gnome", "cosmic"] and "lightweight" not in categories:
                continue

        # Compute score normally
        score = compute_final_score(distro, hardware, usecase, skill_level)

        scored.append({
            "id": key,
            "name": distro.get("name", key),
            "score": score,
            "data": distro
        })

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Top 3
    top_3 = scored[:3] if len(scored) >= 3 else scored

    # Explanation
    explanation = build_explanation(top_3, hardware, usecase, skill_level)

    return {
        "top_3": [{"name": d["name"], "score": d["score"]} for d in top_3],
        "explanation": explanation
    }


# ---------------------------------------------------------
# EXPLANATION ENGINE (Phase 7 + Phase 8)
# ---------------------------------------------------------
def build_explanation(top_3: list, hardware: dict, usecase: str, skill_level: str) -> str:
    if not top_3:
        return "No suitable distros were found based on your hardware and preferences."

    best = top_3[0]
    distro = best["data"]
    name = best["name"]

    lines = []
    lines.append(f"{name} is the best match for your system based on your hardware, skill level, and selected use-case.\n")

    # --- User choices ---
    lines.append(f"Use-case selected: {usecase}")
    lines.append(f"Skill level: {skill_level}\n")

    # --- Hardware summary ---
    gpu = hardware.get("gpu", {}).get("gpu_model", "Unknown GPU")
    ram = hardware.get("ram", {}).get("total_gb", "Unknown")
    storage = hardware.get("storage", {}).get("type", "Unknown")

    lines.append("=== Hardware Detected ===")
    lines.append(f"- GPU: {gpu}")
    lines.append(f"- RAM: {ram} GB")
    lines.append(f"- Storage: {storage}")

    # --- Phase 7 Hardware Intelligence Explanations ---
    lines.append("\n=== Hardware-Based Reasoning ===")

    # Laptop
    if hardware.get("is_laptop"):
        lines.append("- Laptop detected: prioritizing distros with strong power management and good laptop support.")

    # Touchscreen
    if hardware.get("touchscreen"):
        lines.append("- Touchscreen detected: recommending distros with excellent touch support (GNOME, KDE, COSMIC).")

    # HiDPI
    if hardware.get("hidpi"):
        lines.append("- HiDPI display detected: prioritizing distros with strong scaling support (GNOME, KDE, COSMIC).")

    # NVIDIA Optimus
    if hardware.get("optimus"):
        lines.append("- NVIDIA Optimus hybrid GPU detected: recommending distros with reliable hybrid graphics support (Pop!_OS, Fedora, Ubuntu).")

    # AMD APU
    if hardware.get("amd_apu"):
        lines.append("- AMD APU detected: prioritizing distros with strong Mesa support (Fedora, Ubuntu, Mint).")

    # eGPU
    if hardware.get("egpu"):
        lines.append("- External GPU detected: recommending distros with strong Thunderbolt/eGPU support (Fedora, Ubuntu).")

    # If no hardware intelligence triggered
    if not any([
        hardware.get("is_laptop"),
        hardware.get("touchscreen"),
        hardware.get("hidpi"),
        hardware.get("optimus"),
        hardware.get("amd_apu"),
        hardware.get("egpu")
    ]):
        lines.append("- No special hardware conditions detected; using general scoring rules.")

    # --- Distro details ---
    lines.append("\n=== Distro Characteristics ===")
    categories = ", ".join(distro.get("category", []))
    desktop = distro.get("desktop", "Unknown")

    lines.append(f"- Category: {categories}")
    lines.append(f"- Desktop environment: {desktop}")

    # --- Phase 8: Distro Profile Integration ---
    profiles = load_profiles()
    key = distro.get("id", "").lower()

    if key in profiles:
        p = profiles[key]

        lines.append("\n=== Additional Distro Information ===")

        if "pros" in p:
            lines.append("\nPros:")
            for item in p["pros"]:
                lines.append(f"- {item}")

        if "cons" in p:
            lines.append("\nCons:")
            for item in p["cons"]:
                lines.append(f"- {item}")

        if "best_for" in p:
            lines.append(f"\nBest for: {p['best_for']}")

        if "avoid_if" in p:
            lines.append(f"Avoid if: {p['avoid_if']}")

        if "package_manager" in p:
            lines.append(f"Package manager: {p['package_manager']}")

        if "release_cycle" in p:
            lines.append(f"Release cycle: {p['release_cycle']}")

        if "notes" in p:
            lines.append(f"Notes: {p['notes']}")

    lines.append(f"\nOverall, {name} scored highest for your selected use-case and hardware profile.")

    return "\n".join(lines)
