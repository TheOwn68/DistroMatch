V1.0.0
# DistroMatch  
A smart, hardware-aware Linux distribution recommendation engine with a clean Tkinter GUI.

DistroMatch analyzes your hardware, skill level, and intended use-case to recommend the best Linux distributions for **gaming**, **work**, or **browsing**.  
It provides detailed explanations, hardware reasoning, and full distro profiles to help users make informed decisions.

---

## 🚀 Features

### 🔍 Hardware-Aware Scanning
DistroMatch intelligently detects:
- Laptop vs Desktop
- Touchscreen support
- HiDPI displays
- NVIDIA Optimus hybrid GPUs
- AMD APUs
- External GPUs (eGPU)

These signals influence scoring to produce smarter, more personalized recommendations.

---

### 🧠 Smart Scoring Engine
The scoring system considers:
- Hardware compatibility
- User skill level
- Use-case (Gaming, Work, Browsing)
- Stability and performance
- Desktop environment suitability

Gaming distros are automatically excluded from Work/Browsing use-cases.

---

### 📝 Detailed Explanations
Each recommendation includes:
- Why the distro fits your hardware
- Why it matches your use-case
- Why it suits your skill level
- Desktop environment notes
- Category and stability details

---

### 📚 Distro Profiles (Phase 8)
Every supported distro includes:
- Pros
- Cons
- Best for
- Avoid if
- Package manager
- Release cycle
- Notes

Accessible through the **More Info** popup.

---

### 🖥️ Clean Tkinter GUI
- Top-right controls (Show Details, More Info)
- Scrollable output window
- Export toolbar (Copy, Save Results, Save Hardware Info)
- Professional layout and spacing

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/DistroMatch.git
cd DistroMatch
