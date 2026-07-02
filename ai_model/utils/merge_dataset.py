import os
import shutil

def merge_to_training_dataset():
    # Define your base training directory
    base_training_dir = r'C:\Users\kumac\OneDrive\Documents\Verte_2.0\AI_model\training\verte_dataset'
    
    # Take input from the user
    folder1 = input("Enter path of the first source folder: ").strip()
    folder2 = input("Enter path of the second source folder: ").strip()
    category_name = input("Enter the category name (e.g., cardboard): ").strip()
    
    # Create the destination path for this specific category
    destination = os.path.join(base_training_dir, category_name)
    
    if not os.path.exists(destination):
        os.makedirs(destination)
    
    # Collect files
    all_files = []
    for f in os.listdir(folder1):
        if os.path.isfile(os.path.join(folder1, f)):
            all_files.append((folder1, f))
            
    for f in os.listdir(folder2):
        if os.path.isfile(os.path.join(folder2, f)):
            all_files.append((folder2, f))
    
    # Process files and rename sequentially
    count = 1
    for source_folder, filename in all_files:
        ext = os.path.splitext(filename)[1]
        new_name = f"item_{count:04d}{ext}"
        dest_path = os.path.join(destination, new_name)
        
        shutil.copy2(os.path.join(source_folder, filename), dest_path)
        print(f"Merged: {filename} -> {new_name}")
        count += 1
            
    print(f"\nSuccess! Merged {count-1} files into: {destination}")

if __name__ == "__main__":
    merge_to_training_dataset()