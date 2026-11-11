# -*- coding: utf-8 -*-
"""Nội dung chữ của báo cáo (.docx) và slide (.pptx). Số liệu điền từ results/report_data.json."""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
D = json.load(open(R / "results/report_data.json", encoding="utf-8"))
E = D["eda"]
M = {r["exp_id"]: r for r in D["cls_main"]}
G = {g["exp_id"]: g for g in D["group"]}
C = {c["exp_id"]: c for c in D["clu"]}
A = D["ablation"]
B = D["best_id"]; BM = M[B]
f4 = lambda x: f"{x:.4f}".replace(".", ",")
p2 = lambda x: f"{x * 100:.2f}%".replace(".", ",")
n = lambda x: f"{int(x):,}".replace(",", ".")
nf = lambda x: str(x).replace(".", ",")
gb = M["E08"]["model"]
rank = sorted(D["cls_main"], key=lambda r: -r["test_f1_macro"])
cb = C[D["best_clu"]]
tc = D["top_conf"]
fr_set = {"Fridges", "Freezers", "Fridge Freezers"}
fr_err = sum(r[2] for r in tc if r[0] in fr_set and r[1] in fr_set)
best_err = A[-1]["total_err"] if B == "E06" else None
grp_drop = max(abs(g["f1_group"] - g["f1_strat"]) for g in D["group"]) * 100

T = {}
T["s1_intro"] = [
    "**Tên đề tài (tiếng Anh):** Product Classification and Clustering.",
    "**Tên đề tài (tiếng Việt):** Phân loại danh mục và phân cụm thực thể sản phẩm thương mại điện tử dựa trên các thuật toán học máy có giám sát và không giám sát.",
    "**Nhóm thực hiện:** Nhóm 06 – học phần Máy học, Khoa Công nghệ Thông tin, Trường Đại học Sài Gòn. Bảng 1 trình bày thành viên và nhiệm vụ trong giai đoạn giữa kỳ; Bảng 2 đối chiếu tiến độ thực tế với lộ trình 06 tuần đã nêu trong Proposal.",
]
T["s1_progress"] = [
    f"Tính đến thời điểm báo cáo, nhóm đã hoàn thành phần EDA, pipeline tiền xử lý – trích xuất đặc trưng có chống rò rỉ dữ liệu, {len(D['cls_main'])} cấu hình thực nghiệm phân loại (6 thuật toán khác nhau) kèm 5-Fold Cross Validation, {len(D['group'])} thực nghiệm kiểm chứng theo Group split và {len(D['clu'])} thực nghiệm baseline phân cụm. Phần còn lại tập trung vào tinh chỉnh siêu tham số, hai thuật toán phân cụm còn thiếu (Agglomerative, DBSCAN/HDBSCAN), trực quan hóa t-SNE/UMAP và Web Demo (mục 7).",
]
T["s2"] = [
    "**Bối cảnh.** Trên các nền tảng so sánh giá và sàn thương mại điện tử (PriceRunner, Google Shopping, Shopee, Lazada…), mỗi ngày có hàng chục nghìn chào bán (offer) mới từ hàng trăm nhà bán lẻ. Mỗi nhà bán đặt tiêu đề theo quy ước riêng – thứ tự từ khóa, viết tắt, ngôn ngữ (Anh/Đức) và mã model khác nhau – cho cùng một sản phẩm thực, ví dụ “apple iphone 8 plus 64gb silver” và “apple iphone 8 plus 64 gb spacegrau”.",
    "**Mục tiêu.** (1) Tự động gán mỗi offer vào đúng 1 trong 10 ngành hàng chuẩn chỉ từ tiêu đề và mã nhà bán (phân loại đa lớp); (2) gom các offer tương đồng thành cụm mà không dùng nhãn (phân cụm), làm nền cho so khớp sản phẩm giữa các cửa hàng.",
    "**Ý nghĩa.** Giảm chi phí gán danh mục thủ công, cải thiện bộ lọc tìm kiếm và hỗ trợ so sánh giá tự động, chống trùng lặp danh mục. Về mặt học thuật, bài toán là trường hợp điển hình của phân loại văn bản rất ngắn, nhiều nhiễu và nhiều mã kỹ thuật.",
    "**Câu hỏi nghiên cứu (giữ nguyên từ Proposal).** RQ1 – Đặc trưng n-gram ký tự và đặc trưng hình thái/merchant cải thiện phân loại các lớp dễ nhầm (Fridges/Freezers/Fridge Freezers) đến mức nào? RQ2 – Mô hình nào tối ưu nhất về Macro-F1 và tốc độ? RQ3 – Phân cụm không giám sát tái tạo được cấu trúc ngành hàng ở mức nào (Silhouette, ARI, NMI)?",
]
T["s2_io"] = [
    ["Phân loại", "Tiêu đề sản phẩm (văn bản ngắn) + Merchant ID → vector TF-IDF word/char + 5 đặc trưng hình thái + 10 đặc trưng P(ngành | merchant)", "Nhãn ngành hàng y ∈ {10 lớp}", "Học có giám sát – phân loại đa lớp (multi-class classification)"],
    ["Phân cụm", "Vector LSA z ∈ R^m (TF-IDF → TruncatedSVD, m = 50/100/150) chuẩn hóa L2", "Nhãn cụm c ∈ {1..K}", "Học không giám sát – phân cụm (clustering)"],
]
T["s3"] = [
    "**Nguồn dữ liệu.** Bộ “Product Classification and Clustering” (file pricerunner_aggregate.csv) do L. Akritidis và cộng sự công bố trên UCI Machine Learning Repository (ID 837, DOI 10.24432/C5M91Z), thu thập từ nền tảng so sánh giá PriceRunner. Đường dẫn: https://archive.ics.uci.edu/dataset/837/product+classification+and+clustering.",
    f"**Quy mô.** {n(E['n_rows'])} mẫu × 7 cột; {E['n_merchants']} nhà bán; 10 ngành hàng; {n(E['n_clusters'])} cụm thực thể. Biến mục tiêu của nhánh phân loại là **Category Label**; Cluster ID/Cluster Label chỉ dùng để đánh giá phân cụm và để chia dữ liệu theo nhóm, không đưa vào mô hình.",
]
T["s3_after"] = [
    f"**Đặc điểm và chất lượng dữ liệu.** Dữ liệu không có giá trị khuyết. Có {n(E['dup_titles'])} tiêu đề trùng sau khi chuyển chữ thường (nhiều nhà bán đăng cùng tiêu đề) và chỉ {E['titles_with_conflicting_labels']} tiêu đề trùng nhưng mang nhãn ngành khác nhau – mức nhiễu nhãn không đáng kể. Phân phối lớp mất cân bằng nhẹ (tỷ lệ lớn nhất/nhỏ nhất {nf(E['imbalance_ratio'])}). Tiêu đề rất ngắn (trung bình {nf(E['words_mean'])} từ, {nf(E['chars_mean'])} ký tự) và {nf(E['pct_titles_with_alnum'])}% tiêu đề chứa ít nhất một mã chữ-số (ví dụ lwf28441w, kif52af30). Dữ liệu trộn tiếng Anh và tiếng Đức, trong đó ký tự có dấu đã bị lược bỏ ngay trong file gốc (“kühlschrank” → “k hlschrank”).",
    f"**Ghi chú so với Proposal.** Số cụm thực thể đo trực tiếp từ file là {n(E['n_clusters'])} (Proposal ghi 13.237 theo mô tả trên UCI); báo cáo này dùng số đo thực tế.",
]
cd = {r[0]: r for r in D["class_dist"]}
T["eda_class"] = [
    f"Lớp lớn nhất là Fridge Freezers ({n(cd['Fridge Freezers'][1])} mẫu, {nf(cd['Fridge Freezers'][2])}%), nhỏ nhất là Freezers ({n(cd['Freezers'][1])} mẫu, {nf(cd['Freezers'][2])}%). Mức mất cân bằng này không cần oversampling nhưng là lý do nhóm chọn **Macro-F1** làm độ đo chính và dùng Stratified split/Stratified K-Fold để giữ tỷ lệ lớp ở mọi tập con.",
]
T["eda_len"] = [
    f"Phần lớn tiêu đề dài 5–10 từ (trung vị {E['words_median']:.0f} từ; dài nhất {E['words_max']} từ). CPUs có tiêu đề dài nhất và nhiều mã chữ-số nhất (tên dòng chip, xung nhịp, cache, socket); Dishwashers, Freezers, Fridges ngắn nhất. Các tiêu đề dài bất thường (outlier về độ dài) là mô tả đầy đủ thông số chứ không phải lỗi, nên nhóm **giữ lại** thay vì loại bỏ.",
    f"Khoảng {nf(E['pct_titles_without_category_keyword'])}% tiêu đề không chứa từ khóa hiển nhiên của ngành (chỉ gồm hãng + mã model, hoặc viết bằng tiếng Đức) – cao nhất ở Digital Cameras và Mobile Phones (ví dụ “bosch kif52af30”, “siemens ks36fpi3p”). Với các mẫu này, mô hình chỉ có thể dựa vào **mẫu ký tự của mã model** (tiền tố hãng/dòng sản phẩm) – đây là căn cứ để thử nghiệm TF-IDF n-gram ký tự (RQ1).",
]
T["eda_chi2"] = [
    "Kiểm định Chi-square (one-vs-rest) trên unigram/bigram cho thấy mỗi ngành có các từ khóa rất mạnh: “tv, led, 4k” (TVs), “intel, processor, xeon” (CPUs), “washing machine, 1400rpm” (Washing Machines), “sim free, smartphone” (Mobile Phones). Đáng chú ý, các từ tiếng Đức như “geschirrsp ler”, “k hlschrank”, “gefrierschrank” xuất hiện trong top đặc trưng – chứng tỏ cần giữ nguyên các mảnh từ này thay vì lọc theo từ điển tiếng Anh.",
]
T["eda_overlap"] = [
    "Độ chồng lấn từ vựng (Jaccard trên các từ xuất hiện ≥ 5 lần) cao nhất nằm ở cụm ba lớp tủ lạnh/tủ đông: Fridges–Freezers 0,27; Fridges–Fridge Freezers 0,23; Freezers–Fridge Freezers 0,21. Các lớp điện tử (CPUs, Mobile Phones, TVs, Digital Cameras) gần như tách biệt (Jaccard ≤ 0,11). Dự đoán ban đầu: phần lớn lỗi phân loại sẽ tập trung ở ba lớp này – điều được xác nhận ở mục 6.3.",
]
T["eda_merchant"] = [
    f"Phân bố offer giữa các nhà bán rất lệch: trung vị {E['merchant_offers_median']:.0f} offer/merchant, merchant lớn nhất có {n(E['merchant_offers_max'])} offer, 20 merchant lớn nhất chiếm {nf(E['top20_merchant_share_pct'])}% dữ liệu. {E['merchants_single_category']}/{E['n_merchants']} merchant chỉ bán một ngành hàng (cửa hàng chuyên doanh), nên Merchant ID mang thông tin tiên nghiệm về ngành. Tuy vậy, tính theo số offer, ngành phổ biến nhất của mỗi merchant chỉ chiếm trung bình {nf(round(E['merchant_purity_weighted'] * 100, 1))}% – các merchant lớn là siêu thị điện máy bán nhiều ngành, nên merchant chỉ là đặc trưng phụ.",
]
T["eda_cluster"] = [
    f"Cụm thực thể rất nhỏ: trung bình {nf(E['cluster_size_mean'])} offer/cụm, trung vị {E['cluster_size_median']:.0f}, lớn nhất {E['cluster_size_max']}; {n(E['singleton_clusters'])} cụm chỉ có một offer. Hệ quả: (1) phân cụm vi mô ở mức sản phẩm (entity matching) với hơn 13 nghìn cụm là bài toán khó, phù hợp thuật toán mật độ (DBSCAN/HDBSCAN) ở giai đoạn cuối kỳ; (2) khi chia ngẫu nhiên, các offer của cùng một sản phẩm có thể nằm ở cả Train lẫn Test – nhóm bổ sung kịch bản **Group split theo Cluster ID** để kiểm tra rủi ro “học thuộc sản phẩm” (mục 6.4).",
]
T["prep"] = [
    "Toàn bộ tiền xử lý được cài đặt trong src/common.py và đóng gói vào sklearn Pipeline/ColumnTransformer, nên mọi tham số học từ dữ liệu (từ điển TF-IDF, IDF, ma trận SVD, trung bình/độ lệch chuẩn, bảng P(ngành|merchant)) chỉ được fit trên tập Train hoặc trên fold huấn luyện của Cross Validation.",
]
T["prep_table"] = [
    ["Tên cột", "Chuẩn hóa khoảng trắng đầu tên cột trong CSV gốc (“ Merchant ID” → merchant_id)", "File gốc có khoảng trắng thừa"],
    ["Dữ liệu thiếu", "Không có giá trị khuyết – không cần điền", "Kiểm tra: 0 ô trống"],
    ["Trùng lặp / nhiễu nhãn", f"Giữ nguyên {n(E['dup_titles'])} tiêu đề trùng; chỉ {E['titles_with_conflicting_labels']} tiêu đề có nhãn mâu thuẫn – giữ lại", "Trùng lặp phản ánh thực tế nhiều nhà bán cùng đăng; loại bỏ sẽ làm lệch phân phối"],
    ["Ngoại lệ", "Giữ tiêu đề dài bất thường; đặc trưng độ dài được chuẩn hóa z-score", "Tiêu đề dài là mô tả hợp lệ, không phải lỗi"],
    ["Làm sạch văn bản", "Chữ thường; ghép số với đơn vị (“64 gb” → “64gb”, “55 inch” → “55inch”); bỏ ký tự đặc biệt nhưng giữ . - + và toàn bộ số, mã chữ-số; không lọc stop-word", "Mã model và thông số là tín hiệu phân loại mạnh"],
    ["Encoding", "Văn bản: TF-IDF word (1,2) + char_wb (3,5), sublinear_tf; Merchant ID: target encoding P(ngành|merchant) làm trơn Laplace, merchant mới → phân phối chung", "One-hot 306 merchant quá thưa; target encoding gọn hơn"],
    ["Scaling", "5 đặc trưng hình thái chuẩn hóa z-score (fit trên Train); TF-IDF chuẩn hóa L2; vector LSA chuẩn hóa L2 cho phân cụm", "Đưa các nhóm đặc trưng về cùng thang đo"],
    ["Feature engineering", "Số ký tự, số từ, số token số, số token chữ-số, độ dài từ trung bình; SVD-150 (LSA) cho mô hình cây", "Theo Proposal; cây không xử lý tốt ma trận thưa hàng trăm nghìn chiều"],
]
T["method_pipe"] = [
    "Pipeline gồm 3 khối: (1) đọc dữ liệu và làm sạch tiêu đề; (2) chia dữ liệu; (3) hai nhánh song song. Nhánh phân loại dùng hai dạng biểu diễn: ma trận thưa TF-IDF (cho Naive Bayes, Logistic Regression, LinearSVC, Decision Tree) và ma trận đặc SVD-150 + đặc trưng hình thái + merchant (cho Decision Tree, Gradient Boosting, Random Forest). Nhánh phân cụm dùng TF-IDF → TruncatedSVD → chuẩn hóa L2 → K-Means (tương đương Spherical K-Means với độ đo cosine).",
]
T["models"] = [
    ["Multinomial Naive Bayes (E01)", "Mô hình xác suất, giả định độc lập giữa các từ; α = 0,1", "Baseline tham chiếu theo Proposal; huấn luyện < 1 giây"],
    ["Decision Tree (E02, E07)", "Chia không gian đặc trưng theo Gini, không giới hạn độ sâu", "Baseline cây đơn theo yêu cầu đề; dễ giải thích; dùng làm mốc cho ensemble"],
    ["Logistic Regression (E03)", "Softmax đa lớp, phạt L2 (C = 10), lbfgs", "Cho xác suất hậu nghiệm, giải thích được trọng số từ khóa"],
    ["LinearSVC – SVM tuyến tính (E04–E06)", "Siêu phẳng lề cực đại, one-vs-rest, squared hinge (C = 1)", "Rất mạnh với văn bản thưa nhiều chiều; mô hình SVM theo yêu cầu đề"],
    [f"{gb} (E08)", "Gradient boosting trên cây, histogram binning; 300 vòng, learning rate 0,1, 31 lá", "Đại diện họ XGBoost/LightGBM (Proposal); code tự dùng XGBoost khi thư viện có sẵn"],
    ["Random Forest (E09)", "Bagging 300 cây quyết định, chọn ngẫu nhiên đặc trưng", "Ensemble đối chứng với boosting"],
    ["K-Means / MiniBatch K-Means (C01–C04)", "Gom cụm theo tâm, K = 10, n_init = 10 trên LSA chuẩn hóa L2", "Baseline phân cụm theo Proposal"],
]
T["design"] = [
    f"- **Chia dữ liệu:** Stratified 80/20 theo Category Label, random_state = 42 → {n(D['n_train'])} mẫu Train, {n(D['n_test'])} mẫu Test. Tập Test chỉ dùng một lần để báo cáo.",
    "- **Đánh giá trên Train:** 5-Fold Stratified Cross Validation (shuffle, random_state = 42); toàn bộ pipeline được fit lại trong từng fold.",
    "- **Kiểm chứng rò rỉ:** GroupShuffleSplit 80/20 theo Cluster ID – mọi offer của cùng một sản phẩm thực chỉ nằm ở Train hoặc Test.",
    "- **Độ đo phân loại:** Accuracy, Macro Precision/Recall/F1 (độ đo chính), Weighted F1, Confusion Matrix 10×10, F1 từng lớp, thời gian huấn luyện và suy luận.",
    "- **Độ đo phân cụm:** Silhouette (cosine, mẫu ngẫu nhiên 10.000 điểm), Davies-Bouldin; ARI, NMI, V-measure khi đối chiếu với nhãn ngành.",
    "- **Ghi nhận:** mỗi lần chạy được ghi vào Experiment Log (results/experiment_log.xlsx) gồm mô hình, đặc trưng, tham số, cách chia, độ đo, thời gian và nhận xét. Siêu tham số giữa kỳ dùng giá trị mặc định/hợp lý; GridSearchCV để giai đoạn cuối kỳ.",
    "- **Môi trường:** Python 3.13, scikit-learn 1.9.1, máy 2 nhân CPU. Do môi trường chạy không cài được thư viện xgboost, thí nghiệm E08 dùng HistGradientBoostingClassifier (cùng thuật toán gradient boosting dựa trên histogram như XGBoost/LightGBM); mã nguồn tự chuyển sang XGBoost khi thư viện có sẵn.",
]
T["res_intro"] = [
    f"Bảng 8 tổng hợp {len(D['cls_main'])} cấu hình trên cùng một lần chia Stratified 80/20. Hàng tô xanh là mô hình tốt nhất theo Macro-F1 trên Test ({B}). Cột CV là trung bình ± độ lệch chuẩn Macro-F1 qua 5 fold trên tập Train.",
]
T["res_compare"] = [
    f"- **Nhóm dẫn đầu:** LinearSVC với Hybrid TF-IDF ({'E06' if M['E06']['test_f1_macro'] >= M['E05']['test_f1_macro'] else 'E05'}) đạt Macro-F1 ≈ {f4(max(M['E05']['test_f1_macro'], M['E06']['test_f1_macro']))} và Accuracy ≈ {p2(max(M['E05']['test_accuracy'], M['E06']['test_accuracy']))} – đã vượt mục tiêu trong Proposal (Accuracy ≥ 95%, Macro-F1 ≥ 0,94).",
    f"- **Baseline văn bản thuần (chỉ word TF-IDF):** Naive Bayes {f4(M['E01']['test_f1_macro'])}, Logistic Regression {f4(M['E03']['test_f1_macro'])}, LinearSVC {f4(M['E04']['test_f1_macro'])} – ba mô hình tuyến tính cho kết quả gần nhau (chênh ≤ {nf(round((max(M[k]['test_f1_macro'] for k in ['E01','E03','E04']) - min(M[k]['test_f1_macro'] for k in ['E01','E03','E04'])) * 100, 2))} điểm %), cho thấy biểu diễn đặc trưng quan trọng hơn lựa chọn bộ phân loại tuyến tính.",
    f"- **Mô hình cây:** Decision Tree thấp nhất ({f4(M['E02']['test_f1_macro'])} trên TF-IDF, {f4(M['E07']['test_f1_macro'])} trên SVD-150) do cây đơn dễ quá khớp trên văn bản thưa. Ensemble cải thiện rõ: {gb} {f4(M['E08']['test_f1_macro'])}, Random Forest {f4(M['E09']['test_f1_macro'])} – nhưng vẫn thấp hơn LinearSVC vì SVD-150 làm mất bớt thông tin chi tiết của n-gram ký tự (mã model).",
    "- **Độ ổn định:** CV Macro-F1 trên Train và Macro-F1 trên Test chênh nhau rất ít và độ lệch chuẩn giữa các fold nhỏ (Bảng 8), nghĩa là kết quả không phụ thuộc vào một lần chia may mắn.",
]
T["res_ablation"] = [
    f"Kết quả trả lời RQ1: thêm TF-IDF **n-gram ký tự (char_wb 3–5)** là bước cải thiện lớn nhất ({A[1]['delta']} Macro-F1, số lỗi trên tập Test giảm từ {A[0]['total_err']} xuống {A[1]['total_err']}; riêng lỗi nhầm lẫn giữa ba lớp tủ lạnh/tủ đông giảm từ {A[0]['fridge_err']} xuống {A[1]['fridge_err']}). N-gram ký tự nắm được tiền tố mã model (ví dụ “kif…”, “ks…” của Bosch/Siemens là tủ lạnh) và mảnh từ tiếng Đức bị vỡ dấu – đúng những trường hợp mà word n-gram bỏ sót (mục 4.2). Bổ sung đặc trưng hình thái và merchant prior chỉ tăng thêm {nf(round((A[2]['f1'] - A[1]['f1']) * 100, 2))} điểm % so với cấu hình chỉ có Hybrid TF-IDF (giảm {A[1]['total_err'] - A[2]['total_err']} lỗi), nhỏ hơn độ lệch chuẩn giữa các fold – chưa thể kết luận là cải thiện thật, cần kiểm định thêm ở giai đoạn cuối kỳ.",
]
T["res_error"] = [
    f"Ma trận nhầm lẫn của {B} gần như chéo hoàn toàn: các lớp CPUs, Mobile Phones, TVs, Digital Cameras có F1 gần 1. {fr_err} trong tổng số {sum(r[2] for r in tc)} lỗi thuộc các cặp nhầm lẫn ở Bảng 10 nằm trong nhóm Fridges / Freezers / Fridge Freezers, khớp với dự đoán từ phân tích chồng lấn từ vựng. Xem các mẫu sai (results/misclassified_{B}.csv) cho thấy nguyên nhân chính: tiêu đề chỉ có hãng + mã model, sản phẩm lai (tủ lạnh có ngăn đông nhỏ – “fridge with ice box”, “mit gefrierfach”) và tiêu đề tiếng Đức bị mất dấu.",
    "Biểu đồ F1 từng lớp (Hình 10) cho thấy Freezers và Fridges là hai lớp yếu nhất ở mọi mô hình; khoảng cách giữa các mô hình cũng lớn nhất ở hai lớp này. Đây là trọng tâm cải tiến ở giai đoạn cuối kỳ (class_weight, đặc trưng từ khóa phủ định, tinh chỉnh C).",
]
T["res_group"] = [
    "Khi buộc mọi offer của cùng một sản phẩm thực (Cluster ID) nằm hoàn toàn ở Train hoặc Test, Macro-F1 giảm ở cả bốn mô hình: " + "; ".join(f"{g['exp_id']} {g['delta']}" for g in D["group"]) + ". Điều này cho thấy chia ngẫu nhiên đánh giá **hơi lạc quan**, vì một phần offer trên Test có “anh em” cùng sản phẩm (thường có tiêu đề gần giống) trong Train.",
    f"Mức giảm khác nhau rõ rệt: các mô hình chỉ dùng word n-gram (Naive Bayes, LinearSVC word) giảm nhiều nhất do dựa nhiều vào trùng lặp tiêu đề; cấu hình {B} chỉ giảm {G[B + '-G']['delta']} và vẫn đạt Macro-F1 {f4(G[B + '-G']['f1_group'])} trên sản phẩm hoàn toàn mới. N-gram ký tự giúp mô hình học dấu hiệu tổng quát của ngành hàng (tiền tố mã model, đơn vị đo) thay vì ghi nhớ sản phẩm. Từ giai đoạn cuối kỳ, nhóm sẽ báo cáo song song cả hai cách chia và dùng GroupKFold khi tinh chỉnh siêu tham số.",
]
fast = sorted(D["cls_main"], key=lambda r: r["train_time_s"])
T["res_time"] = [
    f"Mô hình tuyến tính trên TF-IDF huấn luyện trong vài giây ({nf(round(M['E04']['train_time_s'], 1))} s với LinearSVC word; {nf(round(M['E06']['train_time_s'], 1))} s với cấu hình đầy đủ) và suy luận khoảng {round(M['E06']['infer_ms_per_1k'])} ms cho 1.000 tiêu đề (E06), trong khi {gb} mất {nf(round(M['E08']['train_time_s'], 1))} s và Random Forest {nf(round(M['E09']['train_time_s'], 1))} s nhưng cho Macro-F1 thấp hơn. Về RQ2, LinearSVC đang là lựa chọn tốt nhất cả về chất lượng lẫn tốc độ, phù hợp để triển khai Web Demo.",
]
T["res_cluster"] = [
    f"K-Means K = 10 trên SVD-50 ({D['best_clu']}) đạt kết quả tốt nhất: NMI {f4(cb['nmi_vs_category'])}, ARI {f4(cb['ari_vs_category'])}, Silhouette {f4(cb['silhouette_cosine'])}. Tăng số chiều SVD lên 100/150 làm cả ba chỉ số giảm – không gian nhiều chiều hơn chứa nhiều nhiễu hơn và khoảng cách cosine kém phân biệt hơn. MiniBatch K-Means nhanh hơn với chất lượng tương đương K-Means đầy đủ ở cùng số chiều.",
    "Bảng đối chiếu (Hình 12) cho thấy các ngành có từ vựng riêng (CPUs, Digital Cameras, Mobile Phones, TVs, Microwaves) gần như trùng với một cụm. Ngược lại Fridges, Freezers, Fridge Freezers bị trộn lẫn và một cụm “tạp” gom các tiêu đề chung chung (màu sắc, “freestanding”, “integrated”) của nhiều ngành gia dụng. Đường Elbow không có điểm gãy rõ và Silhouette tăng dần theo K, gợi ý cấu trúc tự nhiên của dữ liệu mịn hơn 10 ngành – phù hợp với hướng phân cụm vi mô ở cuối kỳ.",
]
T["res_summary"] = [
    f"- Mô hình tốt nhất giữa kỳ: **{B} – {BM['model']} + {BM['features']}**, Accuracy {p2(BM['test_accuracy'])}, Macro-F1 {f4(BM['test_f1_macro'])} trên {n(D['n_test'])} mẫu Test.",
    "- Đặc trưng quan trọng hơn thuật toán: n-gram ký tự đóng góp phần lớn cải thiện; các bộ phân loại tuyến tính cho kết quả gần nhau khi dùng chung biểu diễn.",
    "- Lỗi còn lại tập trung ở ba lớp tủ lạnh/tủ đông – đúng như EDA dự báo.",
    f"- Kết quả ổn định qua 5 fold; với sản phẩm hoàn toàn mới (Group split) {B} vẫn đạt Macro-F1 {f4(G[B + '-G']['f1_group'])}, trong khi mô hình chỉ dùng word n-gram giảm 1–2,5 điểm %.",
    "- Phân cụm K-Means tái tạo khá tốt các ngành có từ vựng riêng (NMI ≈ 0,73) nhưng chưa tách được nhóm tủ lạnh/tủ đông.",
]
T["done"] = [
    "- Tải, kiểm tra chất lượng dữ liệu; EDA đầy đủ với 8 biểu đồ và các bảng thống kê (results/eda_*.csv).",
    "- Xây dựng module tiền xử lý và đặc trưng có chống rò rỉ (src/common.py): làm sạch tiêu đề, 5 đặc trưng hình thái, target encoding merchant.",
    f"- Huấn luyện và đánh giá {len(D['cls_main'])} cấu hình phân loại với 6 thuật toán (Naive Bayes, Decision Tree, Logistic Regression, LinearSVC, Gradient Boosting, Random Forest) + {len(D['group'])} thí nghiệm Group split; phân tích lỗi.",
    f"- Baseline phân cụm K-Means/MiniBatch K-Means ({len(D['clu'])} cấu hình) + khảo sát K bằng Elbow/Silhouette.",
    "- Experiment log Excel, notebook, README, mô hình tốt nhất (.joblib) – tất cả tái lập được bằng random_state = 42.",
]
T["issues"] = [
    "- **Thiếu thư viện XGBoost/LightGBM trong môi trường chạy:** tạm thay bằng HistGradientBoosting (cùng họ thuật toán). Cần chạy lại E08 bằng XGBoost thật trên máy cá nhân để so sánh đúng như Proposal.",
    "- **Chi phí tính toán:** 5-Fold CV cho các mô hình trên SVD-150 (Random Forest, Gradient Boosting) mất nhiều thời gian trên máy 2 nhân; GridSearch ở cuối kỳ cần thu hẹp lưới tham số hoặc dùng RandomizedSearchCV.",
    "- **Hiệu năng đã rất cao (> 99%):** khoảng cách giữa các cấu hình tốt nhất nhỏ hơn dao động giữa các fold, cần kiểm định thống kê (ví dụ McNemar hoặc nhiều seed) trước khi kết luận mô hình nào tốt hơn.",
    "- **Target encoding merchant** được fit và áp dụng trên cùng tập Train nên có thể hơi lạc quan; cuối kỳ sẽ chuyển sang out-of-fold encoding.",
    "- **Phân cụm vi mô** (13 nghìn cụm, đa số chỉ 1–2 offer) khó đánh giá và tốn bộ nhớ với Agglomerative trên toàn bộ dữ liệu – cần lấy mẫu hoặc dùng HDBSCAN.",
]
T["plan"] = [
    ["Tuần 5", "Tinh chỉnh siêu tham số (GridSearchCV/RandomizedSearchCV theo f1_macro) cho LinearSVC, Logistic, XGBoost; chạy XGBoost/LightGBM thật; out-of-fold merchant encoding", "Danh, Nhân", "Bảng so sánh sau tinh chỉnh"],
    ["Tuần 5", "Agglomerative Clustering, DBSCAN/HDBSCAN; phân cụm vi mô đối chiếu Cluster ID; t-SNE/UMAP", "Thịnh, Lộc", "Notebook phân cụm, hình t-SNE"],
    ["Tuần 6", "Phân tích lỗi sâu cho 3 lớp tủ lạnh/tủ đông; kiểm định McNemar giữa các mô hình tốt nhất", "Nhân, Lộc", "Mục Error Analysis"],
    ["Tuần 6", "Web Demo Streamlit: phân loại tức thời + gợi ý sản phẩm tương đồng", "Thịnh, Danh", "App Streamlit"],
    ["Tuần 6", "Viết báo cáo cuối kỳ, slide, cập nhật GitHub và experiment log", "Cả nhóm", "Báo cáo, slide, source code"],
]
T["contrib_intro"] = ["Bảng 14 ghi nhận công việc cụ thể từng thành viên đã thực hiện trong giai đoạn giữa kỳ và các file tương ứng trong bài nộp."]
T["refs"] = [
    "[1] Akritidis, L. (2020). Product Classification and Clustering [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5M91Z.",
    "[2] Akritidis, L., Fevgas, A., Bozanis, P., & Makris, C. (2020). A self-verifying clustering approach to unsupervised matching of product titles. Artificial Intelligence Review, 53, 4777–4820.",
    "[3] Akritidis, L., Fevgas, A., & Bozanis, P. (2018). Effective product categorization with importance scores and morphological analysis of the titles. Proc. 30th IEEE ICTAI, 213–220.",
    "[4] Akritidis, L., & Bozanis, P. (2018). Effective unsupervised matching of product titles with k-combinations and permutations. Proc. 14th IEEE INISTA, 1–10.",
    "[5] Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825–2830.",
    "[6] Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. Proc. 22nd ACM SIGKDD, 785–794.",
    "[7] Géron, A. (2022). Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow (3rd ed.). O'Reilly Media.",
]
T["appendix"] = [
    ["report/", "Báo cáo giữa kỳ (.docx), slide (.pptx), script sinh báo cáo/slide"],
    ["src/common.py", "Đọc dữ liệu, làm sạch tiêu đề, MorphFeatures, MerchantPrior"],
    ["src/eda.py", "EDA – sinh figures/eda_*.png và results/eda_*.csv"],
    ["src/train_baselines.py", "9 thí nghiệm phân loại + 4 thí nghiệm Group split, phân tích lỗi"],
    ["src/cluster_baseline.py", "4 thí nghiệm phân cụm K-Means, Elbow/Silhouette"],
    ["src/draw_pipeline.py, build_experiment_log.py, make_*.py", "Vẽ sơ đồ pipeline, tạo experiment log, notebook, dữ liệu báo cáo"],
    ["notebooks/01_EDA, 02_Classification_Baselines, 03_Clustering_Baseline", "Notebook kèm output của lần chạy thực tế"],
    ["results/experiment_log.xlsx (.csv)", "Nhật ký thực nghiệm (Experiment Log)"],
    ["results/*.csv, *.json, *_stdout.log", "Bảng kết quả chi tiết, báo cáo phân loại, mẫu dự đoán sai, log chạy"],
    ["figures/", "Toàn bộ hình gốc: EDA, pipeline, kết quả, phân cụm"],
    ["models/best_*.joblib", "Pipeline tốt nhất đã huấn luyện"],
    ["data/pricerunner_aggregate.csv, LINK.txt", "Dataset và đường dẫn nguồn"],
    ["README.md, requirements.txt", "Hướng dẫn cài đặt và chạy lại"],
]
json.dump(T, open(R / "report/report_text.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------------- Slide
S = {}
S["problem_lead"] = "Cùng một sản phẩm, mỗi nhà bán đặt tiêu đề một kiểu: “apple iphone 8 plus 64gb silver” và “apple iphone 8 plus 64 gb spacegrau”. Nhóm muốn tự động gán ngành hàng và gom nhóm các offer chỉ từ tiêu đề."
S["branch1"] = ["Input: tiêu đề (≈ 9 từ) + Merchant ID", "Output: 1 trong 10 ngành hàng", "Độ đo chính: Macro-F1 (lớp mất cân bằng nhẹ)", "Mục tiêu Proposal: Acc ≥ 95%, Macro-F1 ≥ 0,94"]
S["branch2"] = ["Input: vector LSA (TF-IDF → SVD) chuẩn hóa L2", "Output: nhãn cụm, không dùng nhãn khi học", "Đánh giá: Silhouette, Davies-Bouldin, ARI, NMI", "Giữa kỳ: K-Means K = 10 (cấp ngành hàng)"]
S["data_notes"] = [f"0 giá trị khuyết; chỉ {E['titles_with_conflicting_labels']} tiêu đề có nhãn mâu thuẫn", f"Mất cân bằng nhẹ: tỷ lệ {nf(E['imbalance_ratio'])} lần", f"{nf(E['pct_titles_with_alnum'])}% tiêu đề có mã model chữ-số", "Trộn tiếng Anh và tiếng Đức (mất dấu)", f"Cụm thực thể nhỏ: trung vị {E['cluster_size_median']:.0f} offer/cụm"]
S["eda_len"] = [f"Trung bình {nf(E['words_mean'])} từ/tiêu đề; CPUs dài nhất, nhiều mã nhất", f"{nf(E['pct_titles_without_category_keyword'])}% tiêu đề không có từ khóa ngành, chỉ hãng + mã model", "Tiêu đề dài bất thường là mô tả hợp lệ → giữ lại", "→ Cần đặc trưng ở mức ký tự để đọc mã model"]
S["eda_len_caption"] = "Ví dụ khó: “bosch kif52af30”, “siemens ks36fpi3p” (Fridges), “indesit dif04b1/dif04b1” (Dishwashers)."
S["eda_chi2"] = ["Mỗi ngành có từ khóa mạnh: “tv, 4k” · “intel, xeon” · “washing machine, 1400rpm” · “sim free”", "Từ tiếng Đức mất dấu (“k hlschrank”, “geschirrsp ler”) nằm trong top đặc trưng → không lọc theo từ điển tiếng Anh", "Chồng lấn từ vựng cao nhất: Fridges–Freezers 0,27 · Fridges–Fridge Freezers 0,23 → dự báo vùng lỗi chính"]
S["prep_steps"] = [["Làm sạch", "Chữ thường; ghép số + đơn vị (64 gb → 64gb); giữ số và mã chữ-số; không lọc stop-word"],
                   ["Văn bản → vector", "TF-IDF word (1,2) + char_wb (3,5), sublinear tf"],
                   ["Đặc trưng thêm", "5 đặc trưng hình thái (z-score) + P(ngành | merchant) làm trơn Laplace"],
                   ["Giảm chiều", "TruncatedSVD-150 cho mô hình cây; SVD 50–150 + L2 cho phân cụm"]]
S["prep_foot"] = "Mọi bước có tham số đều nằm trong sklearn Pipeline nên chỉ fit trên Train hoặc trên fold huấn luyện, tránh rò rỉ dữ liệu. Không có dữ liệu thiếu; trùng lặp và ngoại lệ được giữ lại có chủ đích."
S["design"] = [f"Stratified 80/20: {n(D['n_train'])} Train / {n(D['n_test'])} Test", "5-Fold Stratified CV trên Train", "Kiểm chứng thêm: Group split theo Cluster ID", "random_state = 42, mọi lần chạy ghi vào Experiment Log", f"E08: {gb} thay XGBoost (môi trường thiếu thư viện)"]
S["models_short"] = ["Mô hình trên TF-IDF thưa: Naive Bayes · Logistic · LinearSVC (SVM) · Decision Tree", f"Mô hình trên SVD-150 + đặc trưng: Decision Tree · {gb} · Random Forest"]
S["res_note"] = f"* {gb} dùng thay XGBoost. Hàng tô cam là mô hình tốt nhất ({B}). Mọi mô hình tuyến tính có n-gram ký tự đều vượt mục tiêu Proposal."
S["ablation"] = ["Thêm n-gram ký tự đóng góp phần lớn cải thiện, nhờ đọc được tiền tố mã model và từ tiếng Đức bị mất dấu", f"Lỗi nhầm trong nhóm tủ lạnh/tủ đông: {A[0]['fridge_err']} → {A[1]['fridge_err']} → {A[2]['fridge_err']}", "Thêm đặc trưng hình thái + merchant chỉ tăng rất ít, nằm trong biên dao động giữa các fold"]
S["errors"] = ["Lỗi tập trung ở Fridges / Freezers / Fridge Freezers", "Nguyên nhân: tiêu đề chỉ có mã model, sản phẩm lai (“fridge with ice box”), tiếng Đức", "Cuối kỳ: class_weight, tinh chỉnh C, đặc trưng từ khóa riêng"]
S["group"] = ["Tách hẳn sản phẩm giữa Train/Test → mọi mô hình đều giảm: chia ngẫu nhiên hơi lạc quan", f"Mô hình chỉ có word n-gram giảm mạnh nhất; {B} chỉ giảm {G[B + '-G']['delta']}", "Cuối kỳ: báo cáo cả hai cách chia, tuning bằng GroupKFold"]
S["time"] = f"LinearSVC huấn luyện vài giây và vẫn tốt nhất; {gb} và Random Forest chậm hơn mà Macro-F1 thấp hơn (RQ2)."
S["cluster"] = [f"Tốt nhất: SVD-50 – NMI {nf(round(cb['nmi_vs_category'], 3))}, ARI {nf(round(cb['ari_vs_category'], 3))}", "Tăng số chiều SVD làm chất lượng cụm giảm", "Ngành có từ vựng riêng ≈ 1 cụm; nhóm tủ lạnh/tủ đông bị trộn", "Silhouette tăng theo K → cấu trúc mịn hơn 10 ngành"]
S["cluster_caption"] = "Mỗi hàng là một ngành thực tế, mỗi cột là một cụm K-Means; màu đậm = tỷ lệ cao."
S["done_s"] = ["EDA đầy đủ (8 biểu đồ)", "Pipeline chống rò rỉ dữ liệu", f"{len(D['cls_main'])} cấu hình phân loại, 6 thuật toán, 5-fold CV", f"{len(D['group'])} thí nghiệm Group split", f"{len(D['clu'])} baseline phân cụm", "Experiment log, notebook, README"]
S["issues_s"] = ["Thiếu xgboost trong môi trường chạy → tạm dùng HistGB", "5-fold CV cho ensemble trên SVD-150 tốn thời gian", "Chênh lệch giữa các mô hình top nhỏ hơn dao động giữa các fold", "Target encoding merchant cần chuyển sang out-of-fold"]
S["next_s"] = ["Tuning (GridSearch, RandomizedSearch) + XGBoost/LightGBM thật", "Agglomerative, DBSCAN/HDBSCAN, t-SNE/UMAP", "Kiểm định McNemar, phân tích lỗi sâu", "Web Demo Streamlit, báo cáo và slide cuối kỳ"]
S["closing"] = f"Kết quả giữa kỳ: {B} đạt Macro-F1 {f4(BM['test_f1_macro'])} · K-Means NMI {nf(round(cb['nmi_vs_category'], 2))}"
S["notes"] = [
    "Giới thiệu nhóm 06 và đề tài: phân loại và phân cụm sản phẩm thương mại điện tử trên dữ liệu PriceRunner.",
    "Trình bày phân công. Tuần 1–4 đã xong phần baseline; tuần 5–6 còn tinh chỉnh, phân cụm nâng cao và demo.",
    "Hai nhánh dùng chung dữ liệu tiêu đề. Nhánh phân loại có giám sát, nhánh phân cụm không dùng nhãn.",
    "Dữ liệu sạch, không khuyết, mất cân bằng nhẹ; nhấn mạnh mã model và tiếng Đức là thách thức.",
    "Gần một phần năm tiêu đề không có từ khóa ngành, nên mô hình phải đọc mã model; đây là lý do thử n-gram ký tự.",
    "Chi-square cho thấy từ khóa mạnh từng ngành; ma trận Jaccard chỉ ra vùng nhầm lẫn Fridges/Freezers/Fridge Freezers.",
    "Các bước tiền xử lý; nhấn mạnh tất cả nằm trong Pipeline để tránh rò rỉ dữ liệu.",
    "Pipeline hai nhánh, cách chia dữ liệu và các độ đo; nêu rõ E08 dùng HistGradientBoosting thay XGBoost.",
    "So sánh 9 cấu hình: mô hình tuyến tính với n-gram ký tự dẫn đầu, mô hình cây yếu hơn.",
    "Ablation trả lời RQ1: n-gram ký tự là đòn bẩy chính.",
    "Lỗi còn lại tập trung ở ba lớp tủ lạnh/tủ đông, khớp dự báo từ EDA.",
    "Group split chứng minh mô hình tổng quát hóa sang sản phẩm mới; LinearSVC vừa nhanh vừa tốt.",
    "K-Means tái tạo tốt các ngành điện tử, chưa tách được nhóm tủ lạnh; hướng tiếp theo là phân cụm mật độ.",
    "Tổng kết tiến độ, khó khăn và kế hoạch hai tuần cuối.",
    "Đóng góp từng thành viên.",
    "Cảm ơn, mời đặt câu hỏi.",
]
json.dump(S, open(R / "report/slides_text.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("text ok")
