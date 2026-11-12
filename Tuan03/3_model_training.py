import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import sys

# Ép Python sử dụng bảng mã UTF-8 để in tiếng Việt ra màn hình
sys.stdout.reconfigure(encoding='utf-8')

print("--- BẮT ĐẦU BƯỚC 3: HUẤN LUYỆN VÀ ĐÁNH GIÁ MÔ HÌNH ---")

# 1. Đọc dữ liệu đã xử lý
df = pd.read_csv('train_engineered.csv')

# 2. Tách biến độc lập (X) và biến mục tiêu (y)
y = df['SalePrice_Log']
X = df.drop('SalePrice_Log', axis=1)

# 3. Chia tập Train/Test nội bộ (Tỷ lệ 80/20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Số lượng mẫu huấn luyện (Train): {X_train.shape[0]}")
print(f"Số lượng mẫu kiểm thử (Test): {X_test.shape[0]}")

# 4. Khởi tạo và Huấn luyện mô hình XGBoost
print("\nĐang huấn luyện mô hình XGBoost...")
xgb_model = xgb.XGBRegressor(
    n_estimators=1000,
    learning_rate=0.05,
    max_depth=4,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    objective='reg:squarederror'
)

xgb_model.fit(X_train, y_train)

# 5. Dự đoán và Đánh giá (RMSE trên thang đo Logarit)
predictions = xgb_model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
print(f"\n=> KẾT QUẢ ĐÁNH GIÁ NỘI BỘ (RMSE): {rmse:.5f}")

# 6. Trực quan hóa Top 10 Đặc trưng quan trọng nhất
feature_importances = xgb_model.feature_importances_
features = X.columns
importance_df = pd.DataFrame({'Feature': features, 'Importance': feature_importances})
importance_df = importance_df.sort_values(by='Importance', ascending=False).head(10)

plt.figure(figsize=(10, 6))
plt.barh(importance_df['Feature'], importance_df['Importance'], color='coral')
plt.gca().invert_yaxis()
plt.title('Top 10 Đặc trưng quan trọng nhất ảnh hưởng đến Giá nhà (XGBoost)')
plt.xlabel('Độ quan trọng')
plt.tight_layout()
plt.show()