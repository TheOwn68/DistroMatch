import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel

from scanner import full_scan
from engine.ranking import get_recommendations, load_profiles


class DistroMatchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DistroMatch - Linux Distro Recommender")

        # Bigger window so everything fits
        self.root.geometry("1000x700")

        # === Use-case selector ===
        ttk.Label(root, text="Select Your Use-Case:", font=("Arial", 12)).pack(pady=10)

        self.usecase_var = tk.StringVar()
        self.usecase_dropdown = ttk.Combobox(
            root,
            textvariable=self.usecase_var,
            values=["Gaming", "Work", "Browsing"],
            width=40,
            state="readonly"
        )
        self.usecase_dropdown.pack()
        self.usecase_dropdown.current(0)

        # === Skill level selector ===
        ttk.Label(root, text="Select Your Skill Level:", font=("Arial", 12)).pack(pady=10)

        self.skill_var = tk.StringVar()
        self.skill_dropdown = ttk.Combobox(
            root,
            textvariable=self.skill_var,
            values=["Beginner", "Casual", "Intermediate", "Advanced"],
            width=40,
            state="readonly"
        )
        self.skill_dropdown.pack()
        self.skill_dropdown.current(0)

        # === Scan button ===
        ttk.Button(root, text="Find Best Distro", command=self.run_matcher).pack(pady=20)

        # === Top-right button container ===
        top_right_frame = ttk.Frame(root)
        top_right_frame.pack(fill="x", padx=10)

        ttk.Label(top_right_frame, text="").pack(side="left", expand=True)

        # More Info button
        self.moreinfo_button = ttk.Button(top_right_frame, text="More Info", command=self.show_more_info)
        self.moreinfo_button.pack(side="right", padx=5)

        # Show Details button
        self.details_visible = False
        self.details_button = ttk.Button(top_right_frame, text="Show Details", command=self.toggle_details)
        self.details_button.pack(side="right", pady=5)

        self.last_explanation = ""
        self.last_results_text = ""
        self.last_hardware = {}
        self.top_distro_name = None
        self.top_distro_id = None

        # === Toolbar for Phase 6 ===
        toolbar = ttk.Frame(root)
        toolbar.pack(fill="x", padx=10, pady=5)

        ttk.Button(toolbar, text="Copy Results", command=self.copy_results).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Save Results", command=self.save_results).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Save Hardware Info", command=self.save_hardware).pack(side="left", padx=5)

        # === Scrollable output box ===
        output_frame = ttk.Frame(root)
        output_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.output_box = tk.Text(
            output_frame,
            height=20,
            width=110,
            wrap="word",
            font=("Arial", 11)
        )
        self.output_box.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_box.yview)
        scrollbar.pack(side="right", fill="y")

        self.output_box.configure(yscrollcommand=scrollbar.set)


    def run_matcher(self):
        self.output_box.delete("1.0", tk.END)
        self.details_visible = False
        self.details_button.config(text="Show Details")

        usecase = self.usecase_var.get()
        skill = self.skill_var.get()

        # Phase 2: hardware scan
        hardware = full_scan()
        self.last_hardware = hardware

        # Phase 3–4: scoring + ranking
        results = get_recommendations(hardware, usecase, skill)

        # Store top distro for More Info popup
        self.top_distro_name = results["top_3"][0]["name"]
        self.top_distro_id = self.top_distro_name.lower().replace(" ", "").replace("!", "")

        # Save explanation for toggle
        self.last_explanation = results["explanation"]

        # Build results text for export/copy
        text = "=== Top 3 Linux Distro Recommendations ===\n\n"
        for i, item in enumerate(results["top_3"], start=1):
            text += f"{i}. {item['name']} — Score: {item['score']}\n"
        text += "\n" + results["explanation"]

        self.last_results_text = text

        # === Display Top 3 ===
        self.output_box.insert(tk.END, "=== Top 3 Linux Distro Recommendations ===\n\n")

        for i, item in enumerate(results["top_3"], start=1):
            name = item["name"]
            score = item["score"]
            self.output_box.insert(tk.END, f"{i}. {name} — Score: {score}\n")

        self.output_box.insert(tk.END, "\n(Click 'Show Details' to see why #1 was chosen.)\n")


    def toggle_details(self):
        if not self.last_explanation:
            return

        if self.details_visible:
            # Hide details
            self.run_matcher()
            self.details_button.config(text="Show Details")
            self.details_visible = False

        else:
            # Show details
            self.output_box.insert(tk.END, "\n\n=== Why This Distro Was Recommended ===\n\n")
            self.output_box.insert(tk.END, self.last_explanation)

            self.details_button.config(text="Hide Details")
            self.details_visible = True


    # === Phase 6: Copy to Clipboard ===
    def copy_results(self):
        if not self.last_results_text:
            messagebox.showinfo("Nothing to Copy", "Run a recommendation first.")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(self.last_results_text)
        messagebox.showinfo("Copied", "Results copied to clipboard.")


    # === Phase 6: Save Results to File ===
    def save_results(self):
        if not self.last_results_text:
            messagebox.showinfo("Nothing to Save", "Run a recommendation first.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")]
        )

        if not file_path:
            return

        with open(file_path, "w") as f:
            f.write(self.last_results_text)

        messagebox.showinfo("Saved", "Results saved successfully.")


    # === Phase 6: Save Hardware Info ===
    def save_hardware(self):
        if not self.last_hardware:
            messagebox.showinfo("Nothing to Save", "Run a recommendation first.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")]
        )

        if not file_path:
            return

        with open(file_path, "w") as f:
            for key, value in self.last_hardware.items():
                f.write(f"{key}: {value}\n")

        messagebox.showinfo("Saved", "Hardware info saved successfully.")


    # === Phase 8: More Info Popup ===
    def show_more_info(self):
        if not self.top_distro_id:
            messagebox.showinfo("No Data", "Run a recommendation first.")
            return

        profiles = load_profiles()

        key = self.top_distro_id

        if key not in profiles:
            messagebox.showinfo("No Profile", f"No profile found for {self.top_distro_name}.")
            return

        profile = profiles[key]

        # Create popup window
        win = Toplevel(self.root)
        win.title(f"{self.top_distro_name} — More Info")
        win.geometry("600x500")

        # Scrollable frame
        frame = ttk.Frame(win)
        frame.pack(fill="both", expand=True)

        text = tk.Text(frame, wrap="word", font=("Arial", 11))
        text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        scrollbar.pack(side="right", fill="y")
        text.configure(yscrollcommand=scrollbar.set)

        # Build profile text
        text.insert(tk.END, f"=== {self.top_distro_name} — Detailed Profile ===\n\n")

        if "pros" in profile:
            text.insert(tk.END, "Pros:\n")
            for p in profile["pros"]:
                text.insert(tk.END, f"- {p}\n")
            text.insert(tk.END, "\n")

        if "cons" in profile:
            text.insert(tk.END, "Cons:\n")
            for c in profile["cons"]:
                text.insert(tk.END, f"- {c}\n")
            text.insert(tk.END, "\n")

        if "best_for" in profile:
            text.insert(tk.END, f"Best for: {profile['best_for']}\n\n")

        if "avoid_if" in profile:
            text.insert(tk.END, f"Avoid if: {profile['avoid_if']}\n\n")

        if "package_manager" in profile:
            text.insert(tk.END, f"Package manager: {profile['package_manager']}\n")

        if "release_cycle" in profile:
            text.insert(tk.END, f"Release cycle: {profile['release_cycle']}\n")

        if "notes" in profile:
            text.insert(tk.END, f"\nNotes:\n{profile['notes']}\n")

        text.config(state="disabled")
