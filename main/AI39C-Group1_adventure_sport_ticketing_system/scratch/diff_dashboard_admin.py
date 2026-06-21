import difflib

path_a = r"C:\Users\ACER\OneDrive\Desktop\ThrillDash_AdminFix\ThrillDash_AdminFix\App\templates\dashboard_Admin.html"
path_b = r"C:\Users\ACER\OneDrive\Desktop\group project\group project\AI39C-Group1_adventure_sport_ticketing_system\AI39C-Group1_adventure_sport_ticketing_system\app\templates\dashboard_Admin.html"
report_path = r"C:\Users\ACER\OneDrive\Desktop\group project\group project\AI39C-Group1_adventure_sport_ticketing_system\AI39C-Group1_adventure_sport_ticketing_system\scratch\dashboard_admin_diff.txt"

with open(path_a, "r", encoding="utf-8", errors="ignore") as f:
    content_a = f.read()
with open(path_b, "r", encoding="utf-8", errors="ignore") as f:
    content_b = f.read()

diff = list(difflib.unified_diff(
    content_a.splitlines(),
    content_b.splitlines(),
    fromfile="A/dashboard_Admin.html",
    tofile="B/dashboard_Admin.html",
    n=5
))

with open(report_path, "w", encoding="utf-8") as out:
    for line in diff:
        out.write(line + "\n")

print("Diff report written to scratch/dashboard_admin_diff.txt")
