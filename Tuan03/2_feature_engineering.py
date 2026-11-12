import pandas as pd
import numpy as np
import sys

# Ép Python sử dụng bảng mã UTF-8 để in tiếng Việt ra màn hình
sys.stdout.reconfigure(encoding='utf-8')

print("--- BẮT ĐẦU BƯỚC 2: KỸ NGHỆ ĐẶC TRƯNG ---")

# 1. Đọc dữ liệu đã làm sạch
df = pd.read_csv('train_cleaned.csv')

# 2. Sáng tạo đặc trưng mới
df['TotalSqFeet'] = df['TotalBsmtSF'] + df['1stFlrSF'] + df['2ndFlrSF']
df['TotalBaths'] = df['FullBath'] + (0.5 * df['HalfBath']) + df['BsmtFullBath'] + (0.5 * df['BsmtHalfBath'])
df['HouseAge'] = df['YrSold'] - df['YearBuilt']
df['IsRemodeled'] = (df['YearRemodAdd'] != df['YearBuilt']).astype(int)

df['HasPool'] = (df['PoolArea'] > 0).astype(int)
df['HasGarage'] = (df['GarageArea'] > 0).astype(int)
df['HasBsmt'] = (df['TotalBsmtSF'] > 0).astype(int)
df['HasFireplace'] = (df['Fireplaces'] > 0).astype(int)

# 3. Ép kiểu các biến giả dạng số về chuỗi
df['MSSubClass'] = df['MSSubClass'].astype(str)
df['YrSold'] = df['YrSold'].astype(str)
df['MoSold'] = df['MoSold'].astype(str)

# 4. Mã hóa thứ bậc (Ordinal Encoding)
quality_map = {'None': 0, 'Po': 1, 'Fa': 2, 'TA': 3, 'Gd': 4, 'Ex': 5}
qual_cols = ['ExterQual', 'ExterCond', 'BsmtQual', 'BsmtCond', 
             'HeatingQC', 'KitchenQual', 'FireplaceQu', 
             'GarageQual', 'GarageCond', 'PoolQC']

for col in qual_cols:
    df[col] = df[col].map(quality_map).fillna(0)

exposure_map = {'None': 0, 'No': 1, 'Mn': 2, 'Av': 3, 'Gd': 4}
df['BsmtExposure'] = df['BsmtExposure'].map(exposure_map).fillna(0)

# 5. Biến đổi Logarit cho biến mục tiêu 
df['SalePrice_Log'] = np.log1p(df['SalePrice'])
df = df.drop(['SalePrice', 'Id'], axis=1)

# 6. Mã hóa One-Hot Encoding
df_final = pd.get_dummies(df)
print(f"Kích thước ma trận sau mã hóa: {df_final.shape}")

# 7. Lưu kết quả ra file
df_final.to_csv('train_engineered.csv', index=False)
print("=> Đã lưu dữ liệu mã hóa vào 'train_engineered.csv'\n")