# -*- coding: utf-8 -*-
"""TB05C

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1g9aFlcoAG1xE9Y_3FYgiamkn7TfMvx7b

# Tugas 5 Deep Learning

## Import Library dan Dataset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import torch
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
df_train = pd.read_csv('Train.csv')
df_test = pd.read_csv('test.csv')

df_train = pd.read_csv('Train.csv')
df_test = pd.read_csv('test.csv')

"""## Praproses Data

### Atribut Kategorikal
"""

def fill_missing_with_mode(df, columns):
    for col in columns:
        if col in df.columns:
            mode_value = df[col].mode()[0]  # Menentukan modus
            df[col] = df[col].fillna(mode_value)  # Mengisi missing values dengan modus
        else:
            print(f"Kolom {col} tidak ditemukan dalam DataFrame.")
    return df

# Mengisi null values pada kolom non numerik dengan value terbanyak dari masing masing atribut
columns_to_fill = ['Ever_Married', 'Graduated', 'Profession', 'Var_1']
df_train = fill_missing_with_mode(df_train, columns_to_fill)
df_test = fill_missing_with_mode(df_test, columns_to_fill)

"""###  Atribut Numerik

#### Periksa Karakteristik sebelum praproses
"""

def check_distribution(df, column):
    if column in df.columns:
        skewness = df[column].skew()  # Menghitung skewness
        print(f"Hasil: '{column}' = {skewness}")

        if skewness > 0:
            return f"Kolom '{column}' memiliki distribusi Right Skewed."
        elif skewness < 0:
            return f"Kolom '{column}' memiliki distribusi Left Skewed."
        else:
            return f"Kolom '{column}' memiliki distribusi normal."
    else:
        return f"Kolom '{column}' tidak ditemukan."

print(check_distribution(df_train, 'Age'))
print(check_distribution(df_train, 'Work_Experience'))
print(check_distribution(df_train, 'Family_Size'))
print(check_distribution(df_test, 'Age'))
print(check_distribution(df_test, 'Work_Experience'))
print(check_distribution(df_test, 'Family_Size'))

"""#### Praproses Atribut Numerik"""

def fill_with_median(df, columns):
    for col in columns:
        if col in df.columns:
            median_value = df[col].median()  # Mencari median
            df[col] = df[col].fillna(median_value)  # Mengisi missing values dengan median
        else:
            print(f"Kolom {col} tidak ditemukan dalam DataFrame.")
    return df

columns_to_fill = ['Age', 'Work_Experience', 'Family_Size']
df_train = fill_with_median(df_train, columns_to_fill)
df_test = fill_with_median(df_test, columns_to_fill)

"""#### Periksa Karakteristik Setelah Praproses"""

print(check_distribution(df_train, 'Age'))
print(check_distribution(df_train, 'Work_Experience'))
print(check_distribution(df_train, 'Family_Size'))
print(check_distribution(df_test, 'Age'))
print(check_distribution(df_test, 'Work_Experience'))
print(check_distribution(df_test, 'Family_Size'))

"""## Pengubahan Data menjadi Tensor"""

def map_categorical_columns(df):
  mappings = {}
  for col in df.columns:
    if df[col].dtypes == 'object':
      label_dict = {k: i for i, k in enumerate(df[col].unique(), 0)}
      mappings[col] = label_dict
  return mappings

def explore_clean_tensor(df,is_training=True):
    mappings = map_categorical_columns(df)
    """
    CONTOH HASIL:
     mappings = {
         'Gender': {'Male': 0, 'Female': 1},
         'Ever_Married': {'No': 0, 'Yes': 1},
         'Graduated': {'No': 0, 'Yes': 1},
         'Profession': {
             'Healthcare': 0, 'Engineer': 1, 'Lawyer': 2, 'Entertainment': 3,
             'Artist': 4, 'Executive': 5, 'Doctor': 6, 'Homemaker': 7, 'Marketing': 8
         },
         'Spending_Score': {'Low': 0, 'Average': 1, 'High': 2},
         'Var_1': {
             'Cat_4': 0, 'Cat_6': 1, 'Cat_7': 2, 'Cat_3': 3,
             'Cat_1': 4, 'Cat_2': 5, 'Cat_5': 6
         },
         'Segmentation': {'D': 0, 'A': 1, 'B': 2, 'C': 3}
     }
    """
    data = df
       # map atribut kategorikal dengan mapping yang sudah dibuat
    for col, map_dict in mappings.items():
        if col in data.columns:
            print(f"Mapping column '{col}' with values: {map_dict}")
            data[col] = data[col].map(map_dict)

    # memastikan seluruh data pada setiap atribut adalah numeric
    for col in data.columns:
        try:
              pd.to_numeric(data[col])
        except ValueError:
            return f"Error: Column '{col}' contains non-numeric values."

    # memisahkan atribut yang digunakan untuk fitur dan target, dengan asumsi bahwa target selalu berada di kolom paling akhir
    if is_training:
        features = data.iloc[:, :-1]
        target = data.iloc[:,-1:]
    else:
        features = data.iloc[:, :-1]
        target = data.iloc[:, -1:]

    # normalisasi fitur
    scaler = StandardScaler()
    features = scaler.fit_transform(features)

    # mengubah ke tensor pytorch sehingga nanti siap diproses
    features_tensor = torch.tensor(features, dtype=torch.float32)
    target_tensor = (
        torch.tensor(target.values, dtype=torch.long) if target is not None else None
    )

    return features_tensor, target_tensor

train_features, train_target = explore_clean_tensor(
    df_train,is_training=True
)

test_features, test_target = explore_clean_tensor(
    df_test,is_training=False
)

"""## Pembuatan Model

Berikut ini adalah kode pembuatan model pada tugas lalu:
"""

from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

batch_size = 10

Xtrain = train_features
Ytrain = train_target

Xtest = test_features
Ytest = test_target

class MyDataset(Dataset):
    def __init__(self, X, Y):
        super().__init__()
        self.X = X
        self.Y = Y

    def __len__(self):
        return self.X.shape[0]

    def __getitem__(self, idx):
        return self.X[idx], self.Y[idx]

"""Merujuk pada rencana awal tugas besar, kami tidak memiliki dataset untuk validation. Oleh karena itu, kami akan membagi kembali data train dengan perbandingan 80% untuk train, dan 20% validation."""

from sklearn.model_selection import train_test_split

X_train, X_val, Y_train, Y_val = train_test_split(Xtrain, Ytrain, test_size=0.2, random_state=42)

trainset = MyDataset(X_train, Y_train)
valset = MyDataset(X_val, Y_val)
testset = MyDataset(Xtest, Ytest)

trainloader = DataLoader(trainset, batch_size, shuffle=True)
valloader = DataLoader(valset, batch_size)
testloader = DataLoader(testset, batch_size)

class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(10, 32)
        self.layer2 = nn.Linear(32, 64)
        self.layer3 = nn.Linear(64, 64)
        self.layer4 = nn.Linear(64, 64)
        self.layer5 = nn.Linear(64, 64)
        self.layer6 = nn.Linear(64, 64)
        self.layer7 = nn.Linear(64, 64)
        self.layer8 = nn.Linear(64, 64)
        self.layer9 = nn.Linear(64, 64)
        self.layer10 = nn.Linear(64, 64)
        self.layer11 = nn.Linear(64, 64)
        self.layer12 = nn.Linear(64, 64)
        self.layer13= nn.Linear(64, 32)
        self.layer14 = nn.Linear(32, 16)
        self.layer15 = nn.Linear(16, 4)  # Output layer for 4 classes

    # relu for hidden layers bc its simple (making the negative to 0) : sparsity, thurning off some neurons.
    # relu is gud bc can mitigate Vanishing Gradient Problem, where the gradient is too low.

    # sigmoid = 1/(1/+e^-x). transforms the raw output into a value between 0 and 1, so the res is probabilistic.
    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        x = F.relu(self.layer3(x))
        x = F.relu(self.layer4(x))
        x = F.relu(self.layer5(x))
        x = F.relu(self.layer6(x))
        x = F.relu(self.layer7(x))
        x = F.relu(self.layer8(x))
        x = F.relu(self.layer9(x))
        x = F.relu(self.layer10(x))
        x = F.relu(self.layer11(x))
        x = F.relu(self.layer12(x))
        x = F.relu(self.layer13(x))
        x = F.relu(self.layer14(x))
        return F.sigmoid(self.layer15(x))

model = MyModel()
loss_fn = nn.CrossEntropyLoss()
epoch = 200

"""#### Parameter Early Stopping"""

patience = 100  # jumlah epoch yang diperbolehkan tanpa perbaikan loss validasi sebelum training diberhentikan.
best_val_loss = float('inf')  # Nilai awal loss validasi terbaik (tak hingga)
best_model_state = None  # Menyimpan model terbaik

"""## Model Sebelumnya: Early Stopping + Adam (weight decay)

Model ini sudah dicoba pada TB04C sebelumnya
"""

optimizer = optim.Adam(model.parameters(), lr=0.0001, weight_decay=0.0001)  # L2 Regularization dengan weight_decay
l1_lambda = 0.001  # Koefisien penalti L1

best_val_loss = float('inf')
counter = 0  # Jumlah epoch tanpa perbaikan
epoch = 100
for ei in range(epoch):
     # Training
    model.train()
    train_loss = 0.0

    for x, y in trainloader:
        y = y.long().squeeze()
        optimizer.zero_grad()
        output = model(x)
        loss = loss_fn(output, y)

        # Menambahkan penalti L1
        l1_norm = sum(p.abs().sum() for p in model.parameters())
        loss += l1_lambda * l1_norm

        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    train_loss /= len(trainloader)

    # Validasi
    model.eval()
    val_loss = 0.0
    with torch.no_grad():
        for x, y in valloader:
            y = y.long().squeeze()
            output = model(x)
            val_loss += loss_fn(output, y).item()
    avg_train_loss = train_loss
    avg_val_loss = val_loss / len(valloader)

    print(f"Epoch={ei + 1}, Avg Train Loss={avg_train_loss:.4f}, Avg Val Loss={avg_val_loss:.4f}")

    # Early stopping:
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        counter = 0
        best_model_state = model.state_dict()
    else:
        counter += 1
    if counter >= patience:
        print(f"Early stopping triggered pada epoch {ei + 1}")
        break

if best_model_state:
    model.load_state_dict(best_model_state)

# Evaluasi pada data test
model.eval()
with torch.no_grad():
    ncorrect = 0
    test_loss = 0.0
    for x, y in testloader:
        y = y.long().squeeze()
        yt = model(x)
        test_loss += loss_fn(yt, y).item()
        preds = torch.argmax(yt, dim=1)
        ncorrect += (preds == y).sum().item()

    avg_test_acc = ncorrect / len(test_features) * 100.0
    avg_test_loss = test_loss / len(testloader)

print("Final Test Results")
print(f'Avg Test Loss={avg_test_loss:.4f}')
print(f'Avg Test Acc={avg_test_acc:.2f}%')

"""## Alternatif 1: Early Stopping + RMS Prop

"""

best_val_loss = float('inf')
best_model_state = None
counter = 0  # Untuk early stopping

"""RMSprop adalah algoritma optimasi yang menjaga stabilitas pembaruan parameter dengan menormalisasi gradien menggunakan rata-rata eksponensial dari kuadrat gradien. Kode dibawah ini memiliki parameter alpha=0.99 menjaga agar rata-rata gradien kuadrat tetap stabil, eps=1e-8 mencegah error akibat pembagian nol, weight_decay=0.0001 menambahkan penalti pada bobot besar untuk mencegah overfitting, dan momentum=0.9 membantu model lebih cepat mencapai hasil optimal dengan mempertahankan arah pembaruan sebelumnya."""

optimizer = optim.RMSprop(model.parameters(), lr=0.0001, alpha=0.99, eps=1e-8, weight_decay=0.0001, momentum=0.9)
# momentum mempengaruhi influence nilai sebelumnya, mepeprcepat pelatihan... 0,9 = 90% gradien sebelumnya
# alpha  faktor peluruhan eksponensial

epoch = 100
for ei in range(epoch):
    # Training
    model.train()
    sum_loss = 0.0
    for x, y in trainloader:
        y = y.long().squeeze()
        optimizer.zero_grad()
        yt = model(x)
        loss = loss_fn(yt, y)
        sum_loss += loss.item()
        loss.backward()
        optimizer.step()
    avg_train_loss = sum_loss / len(trainloader)

    # Validation
    model.eval()
    val_loss = 0.0
    with torch.no_grad():
        for x, y in valloader:
            y = y.long().squeeze()
            yt = model(x)
            val_loss += loss_fn(yt, y).item()
    avg_val_loss = val_loss / len(valloader)

    print(f"Epoch={ei + 1}, Avg Train Loss={avg_train_loss:.4f}, Avg Val Loss={avg_val_loss:.4f}")

    # Early stopping:
    if avg_val_loss < best_val_loss:
        best_val_loss = avg_val_loss
        counter = 0
        best_model_state = model.state_dict()
    else:
        counter += 1
    if counter >= patience:
        print(f"Early stopping triggered pada epoch {ei + 1}")
        break

if best_model_state:
    model.load_state_dict(best_model_state)

# Evaluasi pada data test
model.eval()
with torch.no_grad():
    ncorrect = 0
    test_loss = 0.0
    for x, y in testloader:
        y = y.long().squeeze()
        yt = model(x)
        test_loss += loss_fn(yt, y).item()
        preds = torch.argmax(yt, dim=1)
        ncorrect += (preds == y).sum().item()

    avg_test_acc = ncorrect / len(test_features) * 100.0
    avg_test_loss = test_loss / len(testloader)

print("Final Test Results")
print(f'Avg Test Loss={avg_test_loss:.4f}')
print(f'Avg Test Acc={avg_test_acc:.2f}%')

"""## Alternatif 2: Early Stopping + SGD momentum


"""

best_val_loss = float('inf')
best_model_state = None
counter = 0  # Untuk early stopping

"""Kode di bawah ini menggunakan algoritma Stochastic Gradient Descent (SGD) untuk model, dengan parameter learning rate 0.0001, momentum 0.9, dan weight decay (regularisasi) 0.0001. Optimizer ini digunakan untuk memperbarui bobot model selama proses pelatihan dengan memperhitungkan gradien dan parameter lainnya."""

optimizer = optim.SGD(model.parameters(), lr=0.0001, momentum=0.9, weight_decay=0.0001)

epoch = 100
for ei in range(epoch):
    # Training
    model.train()
    sum_loss = 0.0
    for x, y in trainloader:
        y = y.long().squeeze()
        optimizer.zero_grad()
        yt = model(x)
        loss = loss_fn(yt, y)
        sum_loss += loss.item()
        loss.backward()
        optimizer.step()
    avg_train_loss = sum_loss / len(trainloader)

    # Validation
    model.eval()
    val_loss = 0.0
    with torch.no_grad():
        for x, y in valloader:
            y = y.long().squeeze()
            yt = model(x)
            val_loss += loss_fn(yt, y).item()
    avg_val_loss = val_loss / len(valloader)

    print(f"Epoch={ei + 1}, Avg Train Loss={avg_train_loss:.4f}, Avg Val Loss={avg_val_loss:.4f}")

    # Early stopping:
    if avg_val_loss < best_val_loss:
        best_val_loss = avg_val_loss
        counter = 0
        best_model_state = model.state_dict()
    else:
        counter += 1
    if counter >= patience:
        print(f"Early stopping triggered pada epoch {ei + 1}")
        break

if best_model_state:
    model.load_state_dict(best_model_state)

# Evaluasi pada data test
model.eval()
with torch.no_grad():
    ncorrect = 0
    test_loss = 0.0
    for x, y in testloader:
        y = y.long().squeeze()
        yt = model(x)
        test_loss += loss_fn(yt, y).item()
        preds = torch.argmax(yt, dim=1)
        ncorrect += (preds == y).sum().item()

    avg_test_acc = ncorrect / len(test_features) * 100.0
    avg_test_loss = test_loss / len(testloader)

print("Final Test Results")
print(f'Avg Test Loss={avg_test_loss:.4f}')
print(f'Avg Test Acc={avg_test_acc:.2f}%')