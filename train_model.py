# train_model.py - Fixed version with image loading
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.utils import to_categorical
import numpy as np
import os
import json
from sklearn.model_selection import train_test_split

print("🌿 TRAINING PLANT CARE MODEL")
print("=" * 50)

# ============================================
# LOAD IMAGES FROM FOLDER
# ============================================
def load_images_from_folder(folder, target_size=(224,224)):
    """Load images and labels from folder structure"""
    images = []
    labels = []
    class_names = []
    
    # Get all class folders
    classes = sorted([d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))])
    
    for class_idx, class_name in enumerate(classes):
        class_path = os.path.join(folder, class_name)
        class_names.append(class_name)
        
        print(f"   Loading {class_name}...")
        count = 0
        for img_name in os.listdir(class_path):
            if img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                img_path = os.path.join(class_path, img_name)
                try:
                    img = image.load_img(img_path, target_size=target_size)
                    img_array = image.img_to_array(img)
                    img_array = img_array / 255.0
                    images.append(img_array)
                    labels.append(class_idx)
                    count += 1
                except Exception as e:
                    print(f"      ⚠️ Error: {img_name}")
        print(f"      ✅ Loaded {count} images")
    
    return np.array(images), np.array(labels), class_names

# ============================================
# LOAD DATA
# ============================================
print("\n📂 Loading datasets...")

print("📁 Loading Rice...")
rice_images, rice_labels, rice_classes = load_images_from_folder('Crop_Disease/Rice/')
print(f"✅ Rice: {len(rice_images)} images, {len(rice_classes)} classes")

print("\n📁 Loading Potato...")
potato_images, potato_labels, potato_classes = load_images_from_folder('Crop_Disease/Potato/')
print(f"✅ Potato: {len(potato_images)} images, {len(potato_classes)} classes")

# Combine datasets
x = np.concatenate([rice_images, potato_images])
y = np.concatenate([rice_labels, potato_labels + len(rice_classes)])

# Get all class names
class_names = rice_classes + potato_classes
num_classes = len(class_names)

print(f"\n✅ Total: {len(x)} images, {num_classes} classes")
print("\n📊 Classes:")
for i, name in enumerate(class_names):
    count = np.sum(y == i)
    print(f"   {i+1}. {name} ({count} images)")

# Split into train/validation
x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)

print(f"\n✅ Training: {len(x_train)} images")
print(f"✅ Validation: {len(x_val)} images")

# Convert labels to one-hot
y_train_cat = to_categorical(y_train, num_classes)
y_val_cat = to_categorical(y_val, num_classes)

# Free up memory
del rice_images, rice_labels, potato_images, potato_labels
del x, y

# ============================================
# BUILD MODEL
# ============================================
print("\n🔨 Building model...")

base = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224,224,3))
base.trainable = False

x = base.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation='relu')(x)
x = Dropout(0.5)(x)
output = Dense(num_classes, activation='softmax')(x)

model = Model(inputs=base.input, outputs=output)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

print(f"✅ Model built! Parameters: {model.count_params():,}")

# ============================================
# TRAIN
# ============================================
print("\n🚀 Training...")
print("⏰ This will take 10-15 minutes...")

callbacks = [
    EarlyStopping(patience=5, restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(patience=3, factor=0.5, verbose=1)
]

history = model.fit(
    x_train, y_train_cat,
    validation_data=(x_val, y_val_cat),
    epochs=20,
    batch_size=32,
    callbacks=callbacks,
    verbose=1
)

# ============================================
# SAVE
# ============================================
print("\n💾 Saving...")
os.makedirs('model', exist_ok=True)
model.save('model/plant_care_model.h5')
print("✅ Model saved as 'model/plant_care_model.h5'")

with open('model/class_names.json', 'w') as f:
    json.dump(class_names, f)
print("✅ Class names saved")

print("\n" + "=" * 50)
print("🎉 TRAINING COMPLETE!")
print("📊 Model can detect:")
for i, name in enumerate(class_names):
    print(f"   {i+1}. {name}")
print("=" * 50)