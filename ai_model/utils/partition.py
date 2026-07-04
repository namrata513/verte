import splitfolders

# The folder containing your labeled categories
input_folder = r'C:\Users\kumac\OneDrive\Documents\Verte_2.0\AI_model\training\verte_dataset'

# The folder where you want the split data to be saved
output_folder = r'C:\Users\kumac\OneDrive\Documents\Verte_2.0\AI_model\training\split_dataset'

# Perform the split: 80% Training, 10% Validation, 10% Testing
splitfolders.ratio(input_folder, output=output_folder, seed=42, ratio=(0.8, 0.1, 0.1))

print("Partitioning complete! Check your 'split_dataset' folder.")