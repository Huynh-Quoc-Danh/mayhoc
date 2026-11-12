// Sinh Báo cáo tiến độ giữa kỳ (.docx) – Nhóm 06. Đọc số liệu từ ../results/report_data.json
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, AlignmentType, HeadingLevel,
  WidthType, BorderStyle, ShadingType, LevelFormat, PageBreak, TableOfContents, Footer, PageNumber,
  VerticalAlign, PageBorderDisplay, PageBorderOffsetFrom, PageBorderZOrder,
} = require("docx");

const ROOT = path.resolve(__dirname, "..");
const D = JSON.parse(fs.readFileSync(path.join(ROOT, "results/report_data.json"), "utf8"));
const TEXT = JSON.parse(fs.readFileSync(path.join(__dirname, "report_text.json"), "utf8"));
const FONT = "Times New Roman";
const W = 9360; // vùng nội dung (A4, lề trái 3cm, phải 2cm -> ~ 9.360 DXA) – dùng 9.000 cho bảng
const TW = 9000;

// ---------- helpers
const runs = (s, o = {}) => {
  // hỗ trợ **đậm** trong chuỗi
  const parts = String(s).split(/(\*\*[^*]+\*\*)/g).filter(Boolean);
  return parts.map((p) => p.startsWith("**") ? new TextRun({ text: p.slice(2, -2), bold: true, ...o }) : new TextRun({ text: p, ...o }));
};
const P = (s, o = {}) => new Paragraph({ children: runs(s, o.run || {}), alignment: o.align || AlignmentType.JUSTIFIED,
  spacing: { after: 100, line: 312 }, indent: o.noIndent ? undefined : { firstLine: 0 }, ...o.p });
const B = (s, lvl = 0) => new Paragraph({ children: runs(s), numbering: { reference: "bul", level: lvl },
  alignment: AlignmentType.JUSTIFIED, spacing: { after: 60, line: 300 } });
const H1 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(s)] });
const H2 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(s)] });
const H3 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(s)] });
let figNo = 0, tabNo = 0;
const caption = (s) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 200 },
  children: [new TextRun({ text: s, italics: true, size: 22 })] });
function FIG(file, title, widthPx = 600) {
  const buf = fs.readFileSync(path.join(ROOT, "figures", file));
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  const width = Math.min(widthPx, 600);
  figNo += 1;
  return [new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120 },
    children: [new ImageRun({ type: "png", data: buf, transformation: { width, height: Math.round(width * h / w) },
      altText: { title, description: title, name: file } })] }),
    caption(`Hình ${figNo}. ${title}`)];
}
const border = { style: BorderStyle.SINGLE, size: 4, color: "8EA9C1" };
const borders = { top: border, bottom: border, left: border, right: border };
function TABLE(header, rows, widths, opts = {}) {
  tabNo += 1;
  const total = widths.reduce((a, b) => a + b, 0);
  const cell = (t, i, isH, hl) => new TableCell({
    borders, width: { size: widths[i], type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
    shading: isH ? { fill: "1F4E79", type: ShadingType.CLEAR, color: "auto" } : (hl ? { fill: "E2EFDA", type: ShadingType.CLEAR, color: "auto" } : undefined),
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    children: [new Paragraph({ alignment: (isH || (opts.center || []).includes(i)) ? AlignmentType.CENTER : AlignmentType.LEFT,
      children: runs(t, { size: opts.size || 21, bold: isH, color: isH ? "FFFFFF" : undefined, font: FONT }) })],
  });
  const out = [new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 160, after: 80 },
    children: [new TextRun({ text: `Bảng ${tabNo}. ${opts.title}`, italics: true, bold: true, size: 22 })] }),
  new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, alignment: AlignmentType.CENTER,
    rows: [new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, i, true)) }),
      ...rows.map((r) => new TableRow({ cantSplit: true, children: r.map((t, i) => cell(t, i, false, opts.highlight && opts.highlight(r))) }))] }),
  new Paragraph({ spacing: { after: 120 }, children: [] })];
  return out;
}
const f4 = (x) => (x === null || x === undefined || Number.isNaN(x)) ? "–" : Number(x).toFixed(4);
const f1 = (x) => (x === null || x === undefined) ? "–" : Number(x).toFixed(1);
const pct = (x) => (x * 100).toFixed(2) + "%";
const vn = (n) => Number(n).toLocaleString("de-DE"); // 35.311

// ---------- Trang bìa
const logo = fs.readFileSync(path.join(ROOT, "report/assets/sgu_logo.png"));
const C = (s, size, bold = true, after = 120, extra = {}) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after },
  children: [new TextRun({ text: s, bold, size, font: FONT, ...extra })] });
const memberRows = D.members.map((m) => [m.name, m.mssv]);
const coverTableW = [4300, 3000];
const coverTable = new Table({ width: { size: 7300, type: WidthType.DXA }, columnWidths: coverTableW, alignment: AlignmentType.CENTER,
  rows: [["Tên sinh viên", "Mã số sinh viên"], ...memberRows].map((r, ri) => new TableRow({ children: r.map((t, i) => new TableCell({
    borders, width: { size: coverTableW[i], type: WidthType.DXA }, margins: { top: 60, bottom: 60, left: 120, right: 120 },
    shading: ri === 0 ? { fill: "DCE6F1", type: ShadingType.CLEAR, color: "auto" } : undefined,
    children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: t, bold: ri === 0, size: 26, font: FONT })] })] })) })) });

const cover = [
  C("TRƯỜNG ĐẠI HỌC SÀI GÒN", 30, true, 60),
  C("KHOA CÔNG NGHỆ THÔNG TIN", 30, true, 60),
  C("----□☯□----", 24, false, 300),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 300 }, children: [new ImageRun({ type: "png", data: logo,
    transformation: { width: 184, height: 138 }, altText: { title: "Logo SGU", description: "Logo Trường Đại học Sài Gòn", name: "logo" } })] }),
  C("BÁO CÁO TIẾN ĐỘ GIỮA KỲ", 40, true, 120, { color: "1F4E79" }),
  C("Học phần: Máy học", 28, false, 300),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: "Tên đề tài: ", bold: true, size: 28, font: FONT }),
    new TextRun({ text: "PRODUCT CLASSIFICATION AND CLUSTERING", bold: true, size: 28, font: FONT, color: "1F4E79" })] }),
  C("(Phân loại đa lớp và phân cụm sản phẩm thương mại điện tử dựa trên học máy)", 26, false, 300, { italics: true }),
  C("Nhóm 06 – Sinh viên thực hiện:", 26, true, 120),
  coverTable,
  new Paragraph({ spacing: { before: 900 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "TP. Hồ Chí Minh, tháng 11 năm 2026", size: 26, italics: true, font: FONT })] }),
];

// ---------- Nội dung
const T = TEXT;
const body = [];
const add = (...xs) => xs.flat().forEach((x) => body.push(x));
const para = (arr) => arr.map((s) => s.startsWith("- ") ? B(s.slice(2)) : (s.startsWith("  - ") ? B(s.slice(4), 1) : P(s)));

// Mục lục
add(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "MỤC LỤC", bold: true, size: 32 })] }),
  new TableOfContents("Mục lục", { hyperlink: true, headingStyleRange: "1-2" }),
  new Paragraph({ children: [new PageBreak()] }));

// 1
add(H1("1. THÔNG TIN ĐỀ TÀI"));
add(para(T.s1_intro));
add(TABLE(["STT", "Họ và tên", "MSSV", "Vai trò", "Nhiệm vụ giai đoạn giữa kỳ"],
  D.members.map((m, i) => [String(i + 1), m.name, m.mssv, m.role, m.task_mid]), [600, 1900, 1400, 1200, 3900],
  { title: "Thành viên và phân công nhiệm vụ", center: [0, 2, 3] }));
add(H2("1.1. Tiến độ thực hiện tổng quát"));
add(TABLE(["Tuần", "Nội dung theo kế hoạch", "Phụ trách", "Trạng thái"],
  D.timeline.map((t) => [t.week, t.task, t.who, t.status]), [900, 4300, 2000, 1800],
  { title: "Tiến độ so với lộ trình 06 tuần trong Proposal", center: [0, 3] }));
add(para(T.s1_progress));

// 2
add(H1("2. GIỚI THIỆU BÀI TOÁN"));
add(para(T.s2));
add(TABLE(["Nhánh", "Input", "Output", "Loại bài toán ML"], T.s2_io, [1700, 2900, 2300, 2100], { title: "Input/Output và loại bài toán" }));

// 3
add(H1("3. MÔ TẢ DỮ LIỆU"));
add(para(T.s3));
add(TABLE(["STT", "Thuộc tính", "Kiểu", "Vai trò", "Số giá trị khác nhau / ghi chú"], D.attributes.map((a, i) => [String(i + 1), ...a]),
  [600, 1700, 1300, 1900, 3500], { title: "Các thuộc tính của pricerunner_aggregate.csv (số liệu đo trực tiếp)", center: [0] }));
add(TABLE(["Chỉ số", "Giá trị"], D.data_stats, [5400, 3600], { title: "Thống kê tổng quan bộ dữ liệu", center: [1] }));
add(para(T.s3_after));

// 4 EDA
add(H1("4. KHÁM PHÁ VÀ TIỀN XỬ LÝ DỮ LIỆU"));
add(H2("4.1. Phân phối biến mục tiêu"));
add(FIG("eda_01_class_distribution.png", "Phân phối 10 ngành hàng", 520));
add(para(T.eda_class));
add(H2("4.2. Độ dài tiêu đề và mã chữ-số"));
add(FIG("eda_02_title_length_by_class.png", "Số từ và số token chữ-số (mã model) theo ngành", 600));
add(para(T.eda_len));
add(H2("4.3. Từ khóa đặc trưng và mức chồng lấn từ vựng"));
add(FIG("eda_04_top_ngrams_chi2.png", "Top-10 n-gram đặc trưng từng ngành theo Chi-square (one-vs-rest)", 600));
add(para(T.eda_chi2));
add(FIG("eda_05_vocab_overlap.png", "Độ chồng lấn từ vựng (Jaccard) giữa các ngành", 430));
add(para(T.eda_overlap));
add(H2("4.4. Nhà bán hàng (Merchant) và cụm thực thể (Cluster)"));
add(FIG("eda_06_merchant_category_heatmap.png", "Ma trận Merchant (top-30 theo số offer) × Ngành hàng", 470));
add(para(T.eda_merchant));
add(FIG("eda_08_cluster_size.png", "Phân phối kích thước cụm thực thể (Cluster ID)", 400));
add(para(T.eda_cluster));
add(H2("4.5. Tiền xử lý dữ liệu và xây dựng đặc trưng"));
add(para(T.prep));
add(TABLE(["Hạng mục", "Cách xử lý trong dự án", "Lý do"], T.prep_table, [1700, 4100, 3200], { title: "Tóm tắt các bước tiền xử lý" }));

// 5 Method
add(H1("5. PHƯƠNG PHÁP VÀ MÔ HÌNH"));
add(H2("5.1. Pipeline học máy"));
add(FIG("method_pipeline.png", "Pipeline học máy của nhóm (giai đoạn giữa kỳ)", 620));
add(para(T.method_pipe));
add(H2("5.2. Các thuật toán đã chọn"));
add(TABLE(["Mô hình", "Nguyên lý", "Lý do lựa chọn / vai trò"], T.models, [2000, 3500, 3500], { title: "Các mô hình baseline đã triển khai" }));
add(H2("5.3. Thiết kế thực nghiệm"));
add(para(T.design));

// 6 Results
add(H1("6. KẾT QUẢ THỰC NGHIỆM BƯỚC ĐẦU"));
add(H2("6.1. Kết quả các mô hình phân loại"));
add(para(T.res_intro));
add(TABLE(["Mã", "Mô hình", "Đặc trưng", "CV Macro-F1 (±std)", "Test Acc", "Test Macro-F1", "Train (s)"],
  D.cls_main.map((r) => [r.exp_id, r.model, r.features_short, `${f4(r.cv_f1_macro_mean)} ± ${f4(r.cv_f1_macro_std)}`, f4(r.test_accuracy), f4(r.test_f1_macro), f1(r.train_time_s)]),
  [650, 1650, 2300, 1500, 950, 1050, 900], { title: "Kết quả phân loại – Stratified 80/20, 5-Fold CV trên Train (n_test = " + vn(D.n_test) + ")",
    center: [0, 3, 4, 5, 6], size: 19, highlight: (r) => r[0] === D.best_id }));
add(FIG("res_01_model_comparison.png", "So sánh Accuracy và Macro-F1 trên tập Test", 610));
add(para(T.res_compare));
add(H2("6.2. Ảnh hưởng của đặc trưng (RQ1)"));
add(TABLE(["Cấu hình (LinearSVC, C=1)", "Test Macro-F1", "Δ so với Word TF-IDF", "Lỗi trên 3 lớp tủ lạnh/tủ đông"], D.ablation.map((a) => [a.name, f4(a.f1), a.delta, String(a.fridge_err)]),
  [3600, 1600, 1800, 2000], { title: "Ablation đặc trưng trên LinearSVC", center: [1, 2, 3] }));
add(para(T.res_ablation));
add(H2("6.3. Phân tích lỗi của mô hình tốt nhất"));
add(FIG("res_02_confusion_matrix_best.png", `Ma trận nhầm lẫn của mô hình tốt nhất (${D.best_id}) trên tập Test`, 470));
add(TABLE(["Lớp thực tế", "Bị dự đoán thành", "Số mẫu"], D.top_conf.map((r) => [r[0], r[1], String(r[2])]), [3200, 3200, 1400],
  { title: `Các cặp nhầm lẫn nhiều nhất (${D.best_id})`, center: [2] }));
add(FIG("res_03_per_class_f1.png", "F1 theo từng ngành hàng của các mô hình", 600));
add(para(T.res_error));
add(H2("6.4. Kiểm tra rò rỉ theo sản phẩm (Group split theo Cluster ID)"));
add(TABLE(["Mã", "Mô hình", "Macro-F1 Stratified", "Macro-F1 Group split", "Chênh lệch"], D.group.map((g) => [g.exp_id, g.model, f4(g.f1_strat), f4(g.f1_group), g.delta]),
  [900, 3000, 1700, 1700, 1700], { title: "So sánh hai cách chia dữ liệu", center: [0, 2, 3, 4] }));
add(para(T.res_group));
add(H2("6.5. Hiệu năng – thời gian"));
add(FIG("res_04_f1_vs_time.png", "Đánh đổi Macro-F1 và thời gian huấn luyện", 470));
add(para(T.res_time));
add(H2("6.6. Baseline nhánh phân cụm"));
add(TABLE(["Mã", "Thuật toán", "Không gian", "Silhouette", "Davies-Bouldin", "ARI", "NMI"],
  D.clu.map((c) => [c.exp_id, c.model, c.space, f4(c.silhouette_cosine), f4(c.davies_bouldin), f4(c.ari_vs_category), f4(c.nmi_vs_category)]),
  [700, 1900, 2200, 1100, 1300, 900, 900], { title: "Kết quả phân cụm K = 10 (đối chiếu với nhãn ngành hàng)", center: [0, 3, 4, 5, 6], size: 19 }));
add(FIG("clu_01_contingency.png", `Đối chiếu ngành thực tế với cụm K-Means (${D.best_clu})`, 520));
add(FIG("clu_02_elbow_silhouette.png", "Elbow và Silhouette theo số cụm K", 440));
add(para(T.res_cluster));
add(H2("6.7. Nhận xét ban đầu"));
add(para(T.res_summary));

// 7 Progress
add(H1("7. ĐÁNH GIÁ TIẾN ĐỘ"));
add(H2("7.1. Công việc đã hoàn thành"));
add(para(T.done));
add(H2("7.2. Khó khăn và hạn chế"));
add(para(T.issues));
add(H2("7.3. Công việc còn lại và kế hoạch hoàn thành"));
add(TABLE(["Thời gian", "Công việc", "Phụ trách", "Sản phẩm đầu ra"], T.plan, [1300, 3900, 1800, 2000], { title: "Kế hoạch giai đoạn cuối kỳ" }));

// 8 Contribution
add(H1("8. PHÂN CÔNG VÀ ĐÓNG GÓP"));
add(para(T.contrib_intro));
add(TABLE(["Thành viên", "Công việc đã thực hiện (giữa kỳ)", "Sản phẩm / file liên quan", "Mức đóng góp"],
  D.members.map((m) => [`${m.name}\n`.trim(), m.done, m.files, m.share]), [1800, 3800, 2400, 1000],
  { title: "Đóng góp của từng thành viên", center: [3] }));

// 9 Ref
add(H1("9. TÀI LIỆU THAM KHẢO"));
T.refs.forEach((r) => add(new Paragraph({ children: runs(r), spacing: { after: 100 }, indent: { left: 500, hanging: 500 }, alignment: AlignmentType.JUSTIFIED })));

// Phụ lục
add(H1("PHỤ LỤC. DANH MỤC SẢN PHẨM NỘP"));
add(TABLE(["Đường dẫn", "Nội dung"], T.appendix, [3800, 5200], { title: "Cấu trúc thư mục bài nộp" }));

const doc = new Document({
  creator: "Nhóm 06", title: "Báo cáo tiến độ giữa kỳ – Product Classification and Clustering",
  styles: {
    default: { document: { run: { font: FONT, size: 26 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 30, bold: true, color: "1F4E79" }, paragraph: { spacing: { before: 360, after: 160 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 27, bold: true, color: "2E5C8A" }, paragraph: { spacing: { before: 240, after: 120 }, keepNext: true, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 26, bold: true, italics: true }, paragraph: { spacing: { before: 160, after: 80 }, keepNext: true, outlineLevel: 2 } },
    ],
  },
  numbering: { config: [{ reference: "bul", levels: [
    { level: 0, format: LevelFormat.BULLET, text: "●", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 560, hanging: 280 } }, run: { size: 18 } } },
    { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1000, hanging: 280 } } } },
  ] }] },
  features: { updateFields: true },
  sections: [
    { properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1418, right: 1134 },
        borders: { pageBorderTop: { style: BorderStyle.THICK_THIN_SMALL_GAP, size: 24, color: "1F4E79", space: 20 },
          pageBorderBottom: { style: BorderStyle.THIN_THICK_SMALL_GAP, size: 24, color: "1F4E79", space: 20 },
          pageBorderLeft: { style: BorderStyle.THICK_THIN_SMALL_GAP, size: 24, color: "1F4E79", space: 20 },
          pageBorderRight: { style: BorderStyle.THIN_THICK_SMALL_GAP, size: 24, color: "1F4E79", space: 20 },
          pageBorders: { display: PageBorderDisplay.ALL_PAGES, offsetFrom: PageBorderOffsetFrom.TEXT, zOrder: PageBorderZOrder.FRONT } } } },
      children: cover },
    { properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1701, right: 1134 }, pageNumbers: { start: 1 } } },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 22 })] })] }) },
      children: body },
  ],
});
Packer.toBuffer(doc).then((b) => { const out = path.join(__dirname, "Nhom06_BaoCaoGiuaKy_ProductClassificationClustering.docx"); fs.writeFileSync(out, b); console.log("wrote", out); });
