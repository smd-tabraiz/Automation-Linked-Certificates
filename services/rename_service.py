import os
import csv
import shutil

def clean_name(name):
    return name.strip().replace(" ", "_")

def rename_certificates(
    csv_file,
    original_folder,
    renamed_folder
):
    os.makedirs(renamed_folder, exist_ok=True)

    # 🔒 SAFE CSV READ (BOM + header normalization)
    with open(csv_file, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]

        for index, row in enumerate(reader, start=1):
            name = clean_name(row["name"])
            filename_value = (row.get("filename") or "").strip()
            found = False

            # 1️⃣ filename provided
            if filename_value:
                # a) numeric filename → 3 → 3.png / 3.jpg / ...
                if filename_value.isdigit():
                    for ext in [".jpg", ".jpeg", ".png", ".pdf"]:
                        original_file = os.path.join(original_folder, f"{filename_value}{ext}")
                        if os.path.exists(original_file):
                            new_file = os.path.join(renamed_folder, f"{name}{ext}")
                            shutil.copy(original_file, new_file)
                            print(f"Renamed: {original_file} → {new_file}")
                            found = True
                            break
                # b) exact filename
                else:
                    original_file = os.path.join(original_folder, filename_value)
                    if os.path.exists(original_file):
                        _, ext = os.path.splitext(filename_value)
                        new_file = os.path.join(renamed_folder, f"{name}{ext}")
                        shutil.copy(original_file, new_file)
                        print(f"Renamed: {original_file} → {new_file}")
                        found = True

            # 2️⃣ fallback to index-based
            if not found:
                for ext in [".jpg", ".jpeg", ".png", ".pdf"]:
                    original_file = os.path.join(original_folder, f"{index}{ext}")
                    if os.path.exists(original_file):
                        new_file = os.path.join(renamed_folder, f"{name}{ext}")
                        shutil.copy(original_file, new_file)
                        print(f"Renamed: {original_file} → {new_file}")
                        found = True
                        break

            # 3️⃣ not found at all
            if not found:
                print(f"❌ Certificate missing for row {index} ({row.get('name')})")
