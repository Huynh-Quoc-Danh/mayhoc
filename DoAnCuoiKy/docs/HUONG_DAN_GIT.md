# Hướng dẫn GitHub cho Nhóm 06

## Lần đầu (mỗi người)
```bash
git config --global user.name "Ho Ten That"
git config --global user.email "email-dang-ky-github@..."
git clone https://github.com/<nhom-truong>/Nhom06-Product-Classification-Clustering.git
cd Nhom06-Product-Classification-Clustering
pip install -r requirements.txt
git checkout -b <ten>          # danh / loc / nhan / thinh
```

## Mỗi ngày làm việc
```bash
git checkout <ten>
git pull origin main           # lấy phần mới của các bạn
# ... chạy thí nghiệm, điền nhan_xet / rut_ra, sửa code ...
git add experiments/<ten> notebooks/<notebook-cua-minh> src figures
git commit -m "exp(<ten>): <làm gì> – <kết quả chính>"
git push origin <ten>
```
Sau đó mở **Pull Request** `<ten> → main` trên GitHub, nhờ nhóm trưởng (hoặc 1 bạn) review rồi merge.

## Quy ước commit message
| Loại | Ví dụ |
|---|---|
| `exp(...)` thí nghiệm | `exp(nhan): XGBoost max_depth 3/6/9 – depth 6 tốt nhất F1=0.981` |
| `feat(...)` thêm tính năng | `feat(demo): trang Streamlit hiển thị top-3 ngành` |
| `fix(...)` sửa lỗi | `fix(common): giữ dấu chấm thập phân trong clean_title` |
| `docs(...)` tài liệu | `docs(loc): viết nháp chương 2 – mô tả dữ liệu` |
| `fig(...)` hình | `fig(thinh): t-SNE 6000 mẫu tô màu theo cụm HDBSCAN` |

## Quản lý công việc
- Mỗi việc trong `KE_HOACH_CUOI_KY.docx` là 1 **Issue**, gán người, gắn vào **Projects** (bảng Todo / Doing / Done).
- Commit có thể đóng issue: `exp(loc): quét alpha NB (closes #7)`.
- Cuối kỳ chụp **Insights → Contributors** đưa vào báo cáo làm minh chứng đóng góp.
