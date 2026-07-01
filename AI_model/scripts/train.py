import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt
from preprocess import get_data_generators
from tensorflow.keras import mixed_precision
#It tells TensorFlow to use lower-precision math (16-bit instead of 32-bit), which is faster and uses less memory.
policy = mixed_precision.Policy('mixed_float16')
mixed_precision.set_global_policy(policy)

# 1. Initialize data pipelines from your preprocess.py
print("Initializing data pipelines...")
train_gen, val_gen, test_gen = get_data_generators()

# 2. Build the MobileNetV2 architecture
print("Building MobileNetV2 architecture...")
# We use 'imagenet' weights because the model already understands shapes/textures
base_model = MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
base_model.trainable = False  # Freeze pre-trained layers to keep "learned" knowledge

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.2), # Prevent overfitting
    layers.Dense(128, activation='relu'),
    layers.Dense(train_gen.num_classes, activation='softmax') # Dynamic output for your waste types
])

# 3. Compile the model
model.compile(
    optimizer='adam', 
    loss='categorical_crossentropy', 
    metrics=['accuracy']
)

# 4. Train the model
print("Starting training...🕔")
history = model.fit(
    train_gen, 
    validation_data=val_gen, 
    epochs=10
)

# 5. Save the model and visualize performance
model.save('verte_model.keras')
print("Model saved as 'verte_model.keras'🐼🐻‍❄️🐻")

# Plotting the Training History
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Val Accuracy')
plt.title('Accuracy over Epochs')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Val Loss')
plt.title('Loss over Epochs')
plt.legend()

plt.savefig('training_results.png')
print("Performance charts saved as 'training_results.png'")