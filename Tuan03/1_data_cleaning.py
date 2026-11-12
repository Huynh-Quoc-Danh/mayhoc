import pandas as pd
import numpy as np
import sys

# Ép Python sử dụng bảng mã UTF-8 để in tiếng Việt ra màn hình
sys.stdout.reconfigure(encoding='utf-8')

print("--- BẮT ĐẦU BƯỚC 1: LÀM SẠCH DỮ LIỆU ---")

# 1. Tải dữ liệu
df = pd.read_csv('train.csv')
print(f"Kích thước ban đầu: {df.shape}")

# 2. Xử lý "Thiếu mang ý nghĩa" - Điền chuỗi "None"
cols_none = ['PoolQC', 'MiscFeature', 'Alley', 'Fence', 'FireplaceQu', 
             'GarageType', 'GarageFinish', 'GarageQual', 'GarageCond',
             'BsmtQual', 'BsmtCond', 'BsmtExposure', 'BsmtFinType1', 'BsmtFinType2']
for col in cols_none:
    df[col] = df[col].fillna("None")

# 3. Xử lý thiếu diện tích mặt tiền theo trung vị khu vực
df['LotFrontage'] = df.groupby('Neighborhood')['LotFrontage'].transform(
    lambda x: x.fillna(x.median()))

# 4. Điền giá trị 0 cho các số đo của hạng mục không tồn tại
cols_zero = ['GarageYrBlt', 'GarageArea', 'GarageCars', 
             'BsmtFinSF1', 'BsmtFinSF2', 'BsmtUnfSF','TotalBsmtSF', 
             'BsmtFullBath', 'BsmtHalfBath', 'MasVnrArea']
for col in cols_zero:
    df[col] = df[col].fillna(0)

# 5. Xóa ngoại lệ (Diện tích lớn > 4000 nhưng giá rẻ < 300k)
df = df.drop(df[(df['GrLivArea'] > 4000) & (df['SalePrice'] < 300000)].index)
print(f"Kích thước sau khi xóa ngoại lệ: {df.shape}")

# 6. Lưu kết quả ra file tạm
df.to_csv('train_cleaned.csv', index=False)
print("=> Đã lưu dữ liệu làm sạch vào 'train_cleaned.csv'\n")