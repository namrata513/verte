import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

# Define Paths
BASE_DIR = r'C:\Users\kumac\OneDrive\Documents\Verte_2.0\AI_model\training\split_dataset'
TRAIN_DIR = os.path.join(BASE_DIR, 'train')
VAL_DIR = os.path.join(BASE_DIR, 'val')
TEST_DIR = os.path.join(BASE_DIR, 'test')

def get_data_generators():
    # Training: Augmented
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True
    )

    # Evaluation: Only scaled
    eval_datagen = ImageDataGenerator(rescale=1./255)

    # Creating flows
    train_gen = train_datagen.flow_from_directory(
        TRAIN_DIR, target_size=(224, 224), batch_size=32, class_mode='categorical'
    )
    
    val_gen = eval_datagen.flow_from_directory(
        VAL_DIR, target_size=(224, 224), batch_size=32, class_mode='categorical'
    )
    
    test_gen = eval_datagen.flow_from_directory(
        TEST_DIR, target_size=(224, 224), batch_size=32, class_mode='categorical'
    )

    # Converting to tf.data.Dataset to enable prefetching for faster training
    def to_dataset(gen):
        ds = tf.data.Dataset.from_generator(
            lambda: gen,
            output_signature=(
                tf.TensorSpec(shape=(None, 224, 224, 3), dtype=tf.float32),
                tf.TensorSpec(shape=(None, gen.num_classes), dtype=tf.float32)
            )
        )
        return ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    print("preprocessing done (optimized with prefetch) 🐻🐻‍❄️🐼")
    
    return to_dataset(train_gen), to_dataset(val_gen), to_dataset(test_gen)