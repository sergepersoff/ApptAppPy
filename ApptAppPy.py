import os
import pandas as pd
from datetime import datetime
import subprocess

# ✅ Shared folder path for both public CSV and backups
shared_folder = r"C:\Users\serge\Desktop\EDIFY\Python"
private_csv_path = os.path.join(shared_folder, "appointments_final.csv")
public_csv_name = "appointments_public.csv"
log_file_name = "public_export_log.txt"

def create_public_csv(log_versions=True):
    """Generate a de-identified public CSV from appointments_final.csv."""
    if not os.path.exists(private_csv_path):
        print("❌ appointments_final.csv not found.")
        return

    try:
        df = pd.read_csv(private_csv_path)

        # Drop PHI
        if "Patient Name" in df.columns:
            df.drop(columns=["Patient Name"], inplace=True)
            print("🧼 Removed 'Patient Name' column.")
        else:
            print("ℹ️ No 'Patient Name' column found — already clean.")

        # Always write standard public CSV
        public_path = os.path.join(shared_folder, public_csv_name)
        df.to_csv(public_path, index=False)
        print(f"✅ Public CSV written to: {public_path}")

        files_to_commit = [public_csv_name]

        # Optionally create timestamped version
        if log_versions:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            versioned_name = f"appointments_public_{timestamp}.csv"
            versioned_path = os.path.join(shared_folder, versioned_name)
            df.to_csv(versioned_path, index=False)
            print(f"📁 Versioned public CSV written to: {versioned_path}")

            # Log the export
            log_path = os.path.join(shared_folder, log_file_name)
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"{timestamp} | Exported {len(df)} rows → {versioned_path}\n")

            files_to_commit.append(versioned_name)

        # ✅ Push to GitHub
        push_to_github(files_to_commit)

    except Exception as e:
        print("❌ Failed to create public CSV.")
        print(e)

def push_to_github(files_to_commit):
    """Automatically add, commit, and push the selected files to GitHub."""
    try:
        for file in files_to_commit:
            subprocess.run(["git", "add", file], cwd=shared_folder, check=True)

        subprocess.run(["git", "commit", "-m", "Update public CSV"], cwd=shared_folder, check=True)
        subprocess.run(["git", "push"], cwd=shared_folder, check=True)
        print("🚀 Public CSV pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print("⚠️ Git push failed.")
        print(e)

if __name__ == "__main__":
    create_public_csv(log_versions=True)
