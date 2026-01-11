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

    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for index, row in enumerate(reader, start=1):
            name = clean_name(row['name'])
            found = False

            for ext in ['.jpg', '.jpeg', '.png', '.pdf']:
                original_file = os.path.join(original_folder, f"{index}{ext}")
                if os.path.exists(original_file):
                    new_file = os.path.join(renamed_folder, f"{name}{ext}")
                    shutil.copy(original_file, new_file)
                    print(f"Renamed: {original_file} → {new_file}")
                    found = True
                    break

            if not found:
                print(f"❌ Certificate missing for row {index}")
