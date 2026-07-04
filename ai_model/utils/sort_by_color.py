import cv2
import os
import shutil

# Setup: Define your source and destination base paths
source_folder = r'C:\Users\kumac\OneDrive\Documents\Verte_2.0\AI_model\training\data\glass'
# Ensure these match the exact folder names you have in your dataset directory
target_base = r'C:\Users\kumac\OneDrive\Documents\Verte_2.0\AI_model\training\verte_dataset'

folders = {
    'c': os.path.join(target_base, 'white-glass'),
    'b': os.path.join(target_base, 'brown-glass'),
    'g': os.path.join(target_base, 'green-glass')
}

# Ensure folders exist
for path in folders.values():
    os.makedirs(path, exist_ok=True)

for img_name in os.listdir(source_folder):
    img_path = os.path.join(source_folder, img_name)
    
    # Skip if it's a directory or not an image file
    if not os.path.isfile(img_path):
        continue
        
    img = cv2.imread(img_path)
    
    # Check if image loaded correctly
    if img is None:
        print(f"Skipping unreadable file: {img_name}")
        continue

    cv2.imshow('Sort Glass: c=Clear, b=Brown, g=Green', img)
    
    key = cv2.waitKey(0) & 0xFF
    char_key = chr(key).lower()
    
    if char_key in folders:
        shutil.move(img_path, os.path.join(folders[char_key], img_name))
        print(f"Moved {img_name} to {folders[char_key]}")
    elif char_key == 'q': # Added a 'q' to quit early if needed
        print("Quitting...")
        break
        
    cv2.destroyAllWindows()