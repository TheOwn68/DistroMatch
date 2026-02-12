import customtkinter as ctk
from tkinter import filedialog, messagebox
from scanner import full_scan
from engine.ranking import get_recommendations, load_profiles


class DistroMatchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DistroMatch – Linux Distro Recommender")
        self.root.geometry("1100x700")

        # Modern appearance
        ctk.set_appearance_mode("dark")   # "light" or "system"
        ctk.set_default_color_theme("blue")

        # Internal state
        self.last_explanation = ""
        self.last_results_text = ""
        self.last_hardware = {}
        self.top_distro_name = None
        self.top_distro_id = None
        self.details_visible = False

        # === MAIN LAYOUT ===
        self.sidebar = ctk.CTkFrame(self.root, width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.main_area = ctk.CTkFrame(self.root)
        self.main_area.pack(side="right", fill="both", expand=True)

        # === SIDEBAR CONTENT ===
        title = ctk.CTkLabel(self.sidebar, text="DistroMatch", font=("Arial", 24, "bold"))
        title.pack(pady=20)

        # Use-case selector
        ctk.CTkLabel(self.sidebar, text="Use-Case:", font=("Arial", 14)).pack(pady=(10, 5))
        self.usecase_var = ctk.StringVar(value="Gaming")
        self.usecase_dropdown = ctk.CTkComboBox(
            self.sidebar,
            values=["Gaming", "Work", "Browsing"],
            variable=self.usecase_var,
            width=200
        )
        self.usecase_dropdown.pack(pady=5)

        # Skill selector
        ctk.CTkLabel(self.sidebar, text="Skill Level:", font=("Arial", 14)).pack(pady=(20, 5))
        self.skill_var = ctk.StringVar(value="Beginner")
        self.skill_dropdown = ctk.CTkComboBox(
            self.sidebar,
            values=["Beginner", "Casual", "Intermediate", "Advanced"],
            variable=self.skill_var,
            width=200
        )
        self.skill_dropdown.pack(pady=5)

        # Run button
        self.run_button = ctk.CTkButton(
            self.sidebar,
            text="Find Best Distro",
            command=self.run_matcher,
            width=200
        )
        self.run_button.pack(pady=25)

        # Details + More Info
        self.details_button = ctk.CTkButton(
            self.sidebar,
            text="Show Details",
            command=self.toggle_details,
            width=200
        )
        self.details_button.pack(pady=5)

        self.moreinfo_button = ctk.CTkButton(
            self.sidebar,
            text="More Info",
            command=self.show_more_info,
            width=200
        )
        self.moreinfo_button.pack(pady=5)

        # Export buttons
        ctk.CTkLabel(self.sidebar, text="Export:", font=("Arial", 14)).pack(pady=(30, 5))

        ctk.CTkButton(self.sidebar, text="Copy Results", command=self.copy_results, width=200).pack(pady=3)
        ctk.CTkButton(self.sidebar, text="Save Results", command=self.save_results, width=200).pack(pady=3)
        ctk.CTkButton(self.sidebar, text="Save Hardware Info", command=self.save_hardware, width=200).pack(pady=3)

        # Appearance mode toggle
        ctk.CTkLabel(self.sidebar, text="Theme:", font=("Arial", 14)).pack(pady=(30, 5))
        self.theme_switch = ctk.CTkSegmentedButton(
            self.sidebar,
            values=["Light", "Dark"],
            command=self.change_theme
        )
        self.theme_switch.set("Dark")
        self.theme_switch.pack(pady=5)

        # === MAIN AREA: SCROLLABLE RESULTS ===
        self.textbox = ctk.CTkTextbox(self.main_area, wrap="word", font=("Arial", 14))
        self.textbox.pack(fill="both", expand=True, padx=20, pady=20)
        self.textbox.configure(state="disabled")  # READ-ONLY


    # === READ-ONLY TEXTBOX HELPERS ===
    def write_output(self, text):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.insert("end", text)
        self.textbox.configure(state="disabled")

    def append_output(self, text):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", text)
        self.textbox.configure(state="disabled")


    # === THEME SWITCH ===
    def change_theme(self, mode):
        ctk.set_appearance_mode(mode.lower())


    # === RUN MATCHER ===
    def run_matcher(self):
        self.details_visible = False
        self.details_button.configure(text="Show Details")

        usecase = self.usecase_var.get()
        skill = self.skill_var.get()

        hardware = full_scan()
        self.last_hardware = hardware

        results = get_recommendations(hardware, usecase, skill)

        # Store top distro
        self.top_distro_name = results["top_3"][0]["name"]
        self.top_distro_id = self.top_distro_name.lower().replace(" ", "").replace("!", "")

        self.last_explanation = results["explanation"]

        # Build results text
        header = "=== Top 3 Linux Distro Recommendations ===\n\n"
        self.write_output(header)

        for i, item in enumerate(results["top_3"], start=1):
            self.append_output(f"{i}. {item['name']} — Score: {item['score']}\n")

        self.append_output("\n(Click 'Show Details' for full explanation.)\n")

        # Save full text for export
        full_text = header
        for i, item in enumerate(results["top_3"], start=1):
            full_text += f"{i}. {item['name']} — Score: {item['score']}\n"
        full_text += "\n" + results["explanation"]

        self.last_results_text = full_text


    # === DETAILS TOGGLE ===
    def toggle_details(self):
        if not self.last_explanation:
            return

        if self.details_visible:
            self.run_matcher()
            self.details_button.configure(text="Show Details")
            self.details_visible = False
        else:
            self.append_output("\n\n=== Why This Distro Was Recommended ===\n\n")
            self.append_output(self.last_explanation)
            self.details_button.configure(text="Hide Details")
            self.details_visible = True


    # === MORE INFO POPUP ===
    def show_more_info(self):
        if not self.top_distro_id:
            messagebox.showinfo("No Data", "Run a recommendation first.")
            return

        profiles = load_profiles()

        if self.top_distro_id not in profiles:
            messagebox.showinfo("No Profile", f"No profile found for {self.top_distro_name}.")
            return

        profile = profiles[self.top_distro_id]

        popup = ctk.CTkToplevel(self.root)
        popup.title(f"{self.top_distro_name} — More Info")
        popup.geometry("600x500")

        textbox = ctk.CTkTextbox(popup, wrap="word", font=("Arial", 14))
        textbox.pack(fill="both", expand=True, padx=20, pady=20)

        textbox.insert("end", f"=== {self.top_distro_name} — Detailed Profile ===\n\n")

        if "pros" in profile:
            textbox.insert("end", "Pros:\n")
            for p in profile["pros"]:
                textbox.insert("end", f"- {p}\n")
            textbox.insert("end", "\n")

        if "cons" in profile:
            textbox.insert("end", "Cons:\n")
            for c in profile["cons"]:
                textbox.insert("end", f"- {c}\n")
            textbox.insert("end", "\n")

        if "best_for" in profile:
            textbox.insert("end", f"Best for: {profile['best_for']}\n\n")

        if "avoid_if" in profile:
            textbox.insert("end", f"Avoid if: {profile['avoid_if']}\n\n")

        if "package_manager" in profile:
            textbox.insert("end", f"Package manager: {profile['package_manager']}\n")

        if "release_cycle" in profile:
            textbox.insert("end", f"Release cycle: {profile['release_cycle']}\n")

        if "notes" in profile:
            textbox.insert("end", f"\nNotes:\n{profile['notes']}\n")

        textbox.configure(state="disabled")  # READ-ONLY


    # === EXPORT FUNCTIONS ===
    def copy_results(self):
        if not self.last_results_text:
            messagebox.showinfo("Nothing to Copy", "Run a recommendation first.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.last_results_text)
        messagebox.showinfo("Copied", "Results copied to clipboard.")

    def save_results(self):
        if not self.last_results_text:
            messagebox.showinfo("Nothing to Save", "Run a recommendation first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            with open(path, "w") as f:
                f.write(self.last_results_text)
            messagebox.showinfo("Saved", "Results saved successfully.")

    def save_hardware(self):
        if not self.last_hardware:
            messagebox.showinfo("Nothing to Save", "Run a recommendation first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            with open(path, "w") as f:
                for k, v in self.last_hardware.items():
                    f.write(f"{k}: {v}\n")
            messagebox.showinfo("Saved", "Hardware info saved successfully.")
