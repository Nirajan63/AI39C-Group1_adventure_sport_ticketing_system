import os
import difflib

dir_a = r"C:\Users\ACER\OneDrive\Desktop\ThrillDash_AdminFix\ThrillDash_AdminFix\App\Static"
dir_b = r"C:\Users\ACER\OneDrive\Desktop\group project\group project\AI39C-Group1_adventure_sport_ticketing_system\AI39C-Group1_adventure_sport_ticketing_system\app\static"
report_path = r"C:\Users\ACER\OneDrive\Desktop\group project\group project\AI39C-Group1_adventure_sport_ticketing_system\AI39C-Group1_adventure_sport_ticketing_system\scratch\static_diff_report.txt"

files_to_compare = [
    ("calendar.css", "css/calendar.css"),
    ("calendar.js", "js/calendar.js"),
    ("dashboard.css", "css/dashboard.css"),
    ("dashboard.js", "js/dashboard.js"),
    ("dashboard_Admin.css", "css/dashboard_Admin.css"),
    ("dashboard_Admin.js", "js/dashboard_Admin.js"),
    ("payment-assets.js", "js/payment-assets.js"),
    ("payment.css", "css/payment.css"),
    ("payment.js", "js/payment.js"),
]

with open(report_path, "w", encoding="utf-8") as out:
    for file_a_name, file_b_rel in files_to_compare:
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
                n=1
            ))
            out.write(f"DIFFERENT: {file_a_name} <-> {file_b_rel} (diff lines: {len(diff)})\n")
            for line in diff[:20]:
                out.write(f"   {line}\n")
            out.write("-" * 50 + "\n")

print("Comparison completed. Report written to scratch/static_diff_report.txt")
