# -*- coding: utf-8 -*-
"""[Velora] Capstone Project Dicoding.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1qSvdIG-jx0s1I2tGRMFKRAhD5M8MB2js

## Velora - Perhitungan Kalori dan Rekomendasi Makanan

3 Paper/studi terkait perhitungan kalori harian:
1. Persamaan Mifflin-St Jeor, [Paper Link](https://pmc.ncbi.nlm.nih.gov/articles/PMC7478086/)
2. Rekomendasi koreksi faktor klinis, [Paper Link](https://pmc.ncbi.nlm.nih.gov/articles/PMC6068274/)

#### Import Library
"""

# Install library/packages
!pip install tensorflow tensorflowjs pandas

# Import Library
import pandas as pd
import numpy as np
import seaborn as sns
import tensorflow as tf
from IPython.display import display, Markdown, HTML
import matplotlib.pyplot as plt
import random

"""#### Load Dataset"""

# url google sheets (dataset)
sheet_url = "https://docs.google.com/spreadsheets/d/1XsQ7G0yBhPkCHSMAziD8RWpr5IEcTquvDBMmjdT0ZtM/edit?usp=sharing"

# Load data
csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv")
data = pd.read_csv(csv_url)

display(data.head(15))

label_menu = ['breakfast', 'lunch', 'dinner', 'snack']

# Jumlah item per kategori
print("Jumlah Item per Kategori:")
for label in label_menu:
    count = data['label'].str.contains(label, na=False).sum()
    print(f"- {label.capitalize()}: {count} item")

label_menu = ['breakfast', 'lunch', 'dinner', 'snack']
label_counts = {}

# jumlah item per kategori pada label makanan
for label in label_menu:
    count = data['label'].str.contains(label, na=False).sum()

    # capitalized label sebagai key
    label_counts[label.capitalize()] = count

counts_series = pd.Series(label_counts)

plt.figure(figsize=(10, 5))
counts_series.plot(kind='barh', color=sns.palettes.mpl_palette('Dark2'))
plt.title('Jumlah menu per Kategori')
plt.xlabel('Jumlah menu')
plt.ylabel('Kategori/label')
plt.gca().spines[['top', 'right',]].set_visible(False)
plt.show()

# Data validation
data = data.dropna(subset=["calories", "proteins", "fat", "carbohydrate", "name", "label"])
data = data.reset_index(drop=True)

"""#### Hitung Kalori Harian (TDEE)"""

# Hitung REE dengan rumus Mifflin-St Jeor
def calc_ree(age, sex, height, weight):
    return (10 * weight + 6.25 * height - 5 * age + (5 if sex == "laki-laki" else -161))

# Get activity factor
def get_activity_factor(activity, exercise):
    levels = {
        "rendah": {"tidak pernah": 1.2, "jarang": 1.3},
        "sedang": {"jarang": 1.375, "sering": 1.45},
        "tinggi": {"jarang": 1.55, "sering": 1.6}
    }
    return levels.get(activity, {}).get(exercise, 1.2)

# Calculate TDEE
def calc_tdee(age, sex, height, weight, activity, exercise, goal, target_weight):
    ree = calc_ree(age, sex, height, weight)
    factor = get_activity_factor(activity, exercise)
    tdee = ree * factor
    if goal == "Menurunkan Berat Badan":
        tdee -= 500
    elif goal == "Meningkatkan Berat Badan":
        tdee += 500
    return max(int(tdee), 1000)   # agar tidak negatif

"""#### Split TDEE Menjadi 4 Kategori Makanan"""

# Split TDEE menjadi 4 Kategori Makanan
def split_tdee(tdee):
    return {
        "breakfast": int(tdee * 0.25),  # Breakfast (0.25)
        "lunch": int(tdee * 0.35),      # Lunch (0.35)
        "dinner": int(tdee * 0.30),     # Dinner (0.30)
        "snack": int(tdee * 0.10)       # Snack (0.10)
    }                                   # Total (1.00)

"""#### Rekomendasi Makanan"""

# Rekomendasi makanan ≤ slot kalori
# Max per menu yaitu 100-150 gram (diambil dari artikel hallosehat.com)
def recommend_menus(slot, max_calories, max_gram=150, retries=5, exclude_list=None):
    if exclude_list is None:
        exclude_list = []

    label_filter_original = data[data['label'].str.contains(slot)]
    label_filter_original = label_filter_original[label_filter_original['calories'] > 0].copy()

    # Filter menu
    label_filter_original = label_filter_original[~label_filter_original['name'].isin(exclude_list)].copy()


    for attempt in range(retries):
        label_filter = label_filter_original.copy()
        recommended = []
        total_cal = 0
        current_slot_recommended_names = []

        while not label_filter.empty:
            food = label_filter.sample(1).iloc[0]
            food_cal = food["calories"]

            gram_needed = (max_calories - total_cal) / food_cal * 100
            gram = min(gram_needed, max_gram)

            MIN_GRAM = 50
            gram = max(gram, MIN_GRAM)

            total_calories = (food["calories"] * gram) / 100

            # Jika melebihi batas, jangan tambahkan
            if total_cal + total_calories > max_calories:
                # Cek apakah ada sisa calories untuk menu lain
                label_filter = label_filter[label_filter["name"] != food["name"]]
                continue

            item = {
                "name": food["name"],
                "calories": food["calories"],
                "proteins": food["proteins"],
                "fat": food["fat"],
                "carbohydrate": food["carbohydrate"],
                "grams": gram,
                "total_calories": total_calories,
                "total_protein": (food["proteins"] * gram) / 100,
                "total_fat": (food["fat"] * gram) / 100,
                "total_carb": (food["carbohydrate"] * gram) / 100
            }

            total_cal += item["total_calories"]
            recommended.append(item)
            current_slot_recommended_names.append(food["name"]) # Add name to the list

            label_filter = label_filter[label_filter["name"] != food["name"]]

        if total_cal <= max_calories:
            return recommended

    raise ValueError(f"Tidak dapat menemukan kombinasi makanan untuk slot '{slot}' yang tidak melebihi {max_calories}.")

"""#### Model Inference/input

##### Data User/pengguna
"""

# Contoh data user
# Contoh 10 pertanyaan
user = {
    "age": 22,
    "sex": "laki-laki",
    "height": 160,
    "weight": 50,
    "target_weight": 60,
    "activity": "sedang",
    "exercise": "sering",
    "snack_habit": "sering",
    "sleep": 6,
    "goal": "Meningkatkan Berat Badan"
}

# Hitung TDEE dan slot
tdee = calc_tdee(user["age"], user["sex"], user["height"], user["weight"],
                 user["activity"], user["exercise"], user["goal"], user["target_weight"])
slots = split_tdee(tdee)

# TDEE
display(Markdown(f"Kalori Harian (TDEE): **{tdee} kcal**"))

# Inisialisasi
rekomendasi = {}
recommended_items_across_slots = []

for slot in ["breakfast", "lunch", "dinner", "snack"]:
    limit = slots[slot]

    menu_list = recommend_menus(slot, limit, exclude_list=recommended_items_across_slots)
    rekomendasi[slot] = menu_list

    # filter menu yang muncul
    for item in menu_list:
        recommended_items_across_slots.append(item["name"])

    display(Markdown(f"## {slot.capitalize()}"))
    slot_total = sum(item["total_calories"] for item in menu_list)

    html_content = '<div style="display: flex; flex-wrap: wrap; gap: 24px;">'

    for item in menu_list:
        html_content += f"""
        <div style="width: 220px; border-radius: 10px; border: 1px solid #ddd; padding: 10px;">
            <div style="padding-top: 8px; min-height: 120px;">
                <div><b>{item['name']}</b></div>
                <div>porsi: {item['grams']:.0f} gram</div>
                <div>kalori: {item['total_calories']:.1f} kcal</div>
                <div>protein: {item['total_protein']:.1f} g</div>
                <div>lemak: {item['total_fat']:.1f} g</div>
                <div>karbo: {item['total_carb']:.1f} g</div>
            </div>
        </div>
        """

    html_content += '</div>'
    display(HTML(html_content))
    display(Markdown(f"**Total Kalori untuk {slot.capitalize()}:** {slot_total:.1f} kcal"))

"""#### Konversi ke TF.js Model"""

x_dummy = []
y_dummy = []

# Mapping (one-hot encoding)
slot_to_onehot = {
    "breakfast": [1, 0, 0, 0],
    "lunch":     [0, 1, 0, 0],
    "dinner":    [0, 0, 1, 0],
    "snack":     [0, 0, 0, 1]
}

for slot, items in rekomendasi.items():
    for item in items:
        # fitur (kalori, protein, lemak, karbohidrat)
        x_dummy.append([item["calories"], item["proteins"], item["fat"], item["carbohydrate"]])
        y_dummy.append(slot_to_onehot[slot])

x_dummy = np.array(x_dummy, dtype=np.float32)
y_dummy = np.array(y_dummy, dtype=np.float32)

# Model rekomendasi
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(4,)),              # input layer (kalori, protein, lemak, karbo)
    tf.keras.layers.Dense(8, activation='relu'),    # 8 unit hidden layer dan aktivasi ReLU
    tf.keras.layers.Dense(4, activation='softmax')  # 4 output: breakfast, lunch, dinner, snack
])

model.compile(optimizer='adam', loss='categorical_crossentropy')

# Train dummy (agar bisa disimpan)
model.fit(x_dummy, y_dummy, epochs=3)

# Simpan ke .h5
model.save("rekomendasi_makan.h5")

# Konversi ke tfjs
!pip install tensorflowjs
!tensorflowjs_converter --input_format keras rekomendasi_makan.h5 model_tfjs/

# zip model
!zip -r model_tfjs.zip model_tfjs/

!ls

"""#### Evaluasi Precision"""

# Evaluasi dengan precision
# Apakah makanan sesuai label slot?
def evaluasi(result):
    correct = 0
    total = 0
    for slot, items in result.items():
        for item in items:
            if slot in data[data["name"] == item["name"]]["label"].values[0]:
                correct += 1
            total += 1
    precision = correct / total if total else 0
    return precision

precision = evaluasi(rekomendasi)
display(Markdown(f"Evaluasi (Precision): **{precision:.2f}**"))