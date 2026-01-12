import csv
import matplotlib.pyplot as plt
import os
import glob

# Search for all results.csv files
runs = glob.glob(r'c:\Users\suman\Desktop\yoloMajor\runs\detect\*\results.csv')
if not runs:
    print("Error: No results.csv files found.")
    exit(1)

best_map = -1
best_run = None
best_data = None

# Find the run with the highest performance (using mAP as the selector still, but we will plot accuracy)
for run_path in runs:
    with open(run_path, mode='r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not rows: continue
        
        try:
            current_max = max(float(row.get('metrics/mAP50(B)', 0).strip()) for row in rows)
            if current_max > best_map:
                best_map = current_max
                best_run = run_path
                best_data = rows
        except:
            continue

if not best_run:
    print("Error: Could not determine the best run.")
    exit(1)

print(f"Generating Classification Accuracy for: {best_run}")

# Extract data
epochs = []
precision = []
recall = []
cls_loss = []

for row in best_data:
    row = {k.strip(): v.strip() for k, v in row.items()}
    try:
        epochs.append(int(row['epoch']))
        precision.append(float(row['metrics/precision(B)']))
        recall.append(float(row['metrics/recall(B)']))
        cls_loss.append(float(row['train/cls_loss']))
    except:
        continue

# Plotting Accuracy (Classification Focus)
plt.figure(figsize=(12, 8))
plt.style.use('seaborn-v0_8-darkgrid')

# Subplot 1: Classification Precision & Recall
plt.subplot(2, 1, 1)
plt.plot(epochs, precision, label='Classification Precision', marker='o', color='#1f77b4', linewidth=3)
plt.plot(epochs, recall, label='Classification Recall', marker='s', color='#ff7f0e', linewidth=3)
plt.title(f'Classification Accuracy Metrics (Run: {os.path.basename(os.path.dirname(best_run))})', fontsize=16, fontweight='bold')
plt.ylabel('Score (0.0 - 1.0)', fontsize=12)
plt.legend(loc='lower right')
plt.grid(True, linestyle='--', alpha=0.6)

# Subplot 2: Classification Loss
plt.subplot(2, 1, 2)
plt.plot(epochs, cls_loss, label='Classification Loss (Train)', marker='o', color='#d62728', linewidth=2)
plt.xlabel('Epoch', fontsize=12)
plt.ylabel('CLS Loss', fontsize=12)
plt.legend(loc='upper right')
plt.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
output_path = r'c:\Users\suman\Desktop\yoloMajor\classification_accuracy_graph.png'
plt.savefig(output_path, dpi=300)
print(f"Success! Classification accuracy graph saved to: {output_path}")
