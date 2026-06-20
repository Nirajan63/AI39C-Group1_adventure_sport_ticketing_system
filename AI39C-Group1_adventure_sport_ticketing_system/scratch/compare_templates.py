import os
import difflib

dir_a = r"C:\Users\ACER\OneDrive\Desktop\ThrillDash_AdminFix\ThrillDash_AdminFix\App\templates"
dir_b = r"C:\Users\ACER\OneDrive\Desktop\group project\group project\AI39C-Group1_adventure_sport_ticketing_system\AI39C-Group1_adventure_sport_ticketing_system\app\templates"
report_path = r"C:\Users\ACER\OneDrive\Desktop\group project\group project\AI39C-Group1_adventure_sport_ticketing_system\AI39C-Group1_adventure_sport_ticketing_system\scratch\templates_diff_report.txt"

templates_to_compare = [
    ("Base.html", "base.html"),
    ("change_password_Admin.html", "change_password_Admin.html"),
    ("Dashboard.html", "Dashboard.html"),
    ("dashboard_Admin.html", "dashboard_Admin.html"),
    ("Login.html", "login.html"),
    ("login_Admin.html", "login_Admin.html"),
    ("Register.html", "register.html"),
]

with open(report_path, "w", encoding="utf-8") as out:
    for file_a_name, file_b_rel in templates_to_compare:
        path_a = os.path.join(dir_a, file_a_name)
        path_b = os.path.join(dir_b, file_b_rel)
        
        if not os.path.exists(path_a):
            out.write(f"File A does not exist: {path_a}\n")
            continue
        if not os.path.exists(path_b):
            out.write(f"File B does not exist: {path_b}\n")
            continue
            
        with open(path_a, "r", encoding="utf-8", errors="ignore") as f:
            content_a = f.read()
        with open(path_b, "r", encoding="utf-8", errors="ignore") as f:
            content_b = f.read()
            
        if content_a.strip() == content_b.strip():
            out.write(f"Identical: {file_a_name} <-> {file_b_rel}\n")
        else:
            diff = list(difflib.unified_diff(
                content_a.splitlines(),
                content_b.splitlines(),
                fromfile=f"A/{file_a_name}",
                tofile=f"B/{file_b_rel}",
                n=2
            ))
            out.write(f"DIFFERENT: {file_a_name} <-> {file_b_rel} (diff lines: {len(diff)})\n")
            for line in diff[:30]:
                out.write(f"   {line}\n")
            out.write("-" * 50 + "\n")

print("Comparison completed. Report written to scratch/templates_diff_report.txt")
