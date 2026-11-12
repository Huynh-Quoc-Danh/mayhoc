// Slide báo cáo giữa kỳ – Nhóm 06 (pptxgenjs). Số liệu đọc từ ../results/report_data.json
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const ROOT = path.resolve(__dirname, "..");
const D = JSON.parse(fs.readFileSync(path.join(ROOT, "results/report_data.json"), "utf8"));
const TX = JSON.parse(fs.readFileSync(path.join(__dirname, "slides_text.json"), "utf8"));
const FIG = (f) => path.join(ROOT, "figures", f);

const THEME = { name: "Nhom06 Retail", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: "1B2A3A", lt1: "FFFFFF", dk2: "16324F", lt2: "EEF3F8", accent1: "16324F", accent2: "E8833A",
    accent3: "3B6FB6", accent4: "5FA37B", accent5: "8FB3E0", accent6: "C0504D", hlink: "3B6FB6", folHlink: "6B5B95" } };
const HEX = THEME.colors;
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Nhóm 06 – Báo cáo giữa kỳ"; pres.author = "Nhóm 06";
const C = pres.SchemeColor;

pres.defineSlideMaster({ title: "N06_TITLE", background: { color: HEX.dk2 },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.2, w: 11.7, h: 1.6, fontSize: 40, bold: true, color: C.background1, valign: "bottom" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.95, w: 11.7, h: 1.6, fontSize: 18, color: C.background2, valign: "top" }, text: "" } }] });
pres.defineSlideMaster({ title: "N06_CONTENT", background: { color: HEX.lt1 },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.85, fontSize: 30, bold: true, color: C.text2, valign: "middle", margin: 0 }, text: "" } },
    { text: { text: "Nhóm 06 · Product Classification and Clustering · Báo cáo giữa kỳ", options: { x: 0.6, y: 7.0, w: 9, h: 0.3, fontSize: 10, color: "7A8794", margin: 0 } } }],
  slideNumber: { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: "7A8794", align: "right" } });

let sec = "";
const section = (t) => { pres.addSection({ title: t }); sec = t; };
const content = (title) => { const s = pres.addSlide({ masterName: "N06_CONTENT", sectionTitle: sec }); s.addText(title, { placeholder: "title" }); return s; };
const card = (s, x, y, w, h, fill = HEX.lt2) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { color: fill } });
const txt = (s, t, o) => s.addText(t, { isTextBox: true, fontSize: 15, color: C.text1, valign: "top", ...o });
const bullets = (arr, size = 15) => arr.map((t, i) => ({ text: t, options: { bullet: { indent: 16 }, breakLine: i < arr.length - 1, paraSpaceAfter: 6, fontSize: size } }));
const img = (s, f, x, y, w) => { const b = fs.readFileSync(FIG(f)); const iw = b.readUInt32BE(16), ih = b.readUInt32BE(20);
  s.addImage({ path: FIG(f), x, y, w, h: w * ih / iw, altText: f }); return w * ih / iw; };
const imgFit = (s, f, x, y, w, h) => { const b = fs.readFileSync(FIG(f)); const r = b.readUInt32BE(16) / b.readUInt32BE(20);
  let W = w, H = w / r; if (H > h) { H = h; W = h * r; } s.addImage({ path: FIG(f), x: x + (w - W) / 2, y, w: W, h: H, altText: f }); };
const f4 = (x) => Number(x).toFixed(4);
const vn = (n) => Number(n).toLocaleString("de-DE");
const best = D.cls_main.find((r) => r.exp_id === D.best_id);
const tbl = (rows, o) => ({ ...o, fontSize: o.fontSize || 12, fontFace: "Calibri", color: HEX.dk1, border: { type: "solid", pt: 0.75, color: "C9D6E3" }, valign: "middle" });
const hdr = (arr) => arr.map((t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: HEX.dk2 }, align: "center" } }));

// 1. Title
section("Mở đầu");
let s = pres.addSlide({ masterName: "N06_TITLE", sectionTitle: sec });
s.addText("Product Classification and Clustering", { placeholder: "title" });
s.addText([{ text: "Báo cáo tiến độ giữa kỳ – Môn Máy học", options: { bold: true, breakLine: true } },
  { text: "Nhóm 06 · Khoa Công nghệ Thông tin · Trường Đại học Sài Gòn", options: { breakLine: true } },
  { text: D.members.map((m) => m.name).join(" · "), options: { fontSize: 15 } }], { placeholder: "body" });
s.addImage({ path: path.join(__dirname, "assets/sgu_logo.png"), x: 0.8, y: 0.6, w: 1.6, h: 1.2, altText: "Logo SGU" });
s.addNotes(TX.notes[0]);

// 2. Team & progress
s = content("Thành viên, phân công và tiến độ");
s.addTable([hdr(["Thành viên", "MSSV", "Nhiệm vụ giữa kỳ"]),
  ...D.members.map((m) => [{ text: m.name + (m.role === "Nhóm trưởng" ? " (NT)" : ""), options: { bold: true } }, { text: m.mssv, options: { align: "center" } }, m.task_mid])],
  tbl(null, { x: 0.6, y: 1.4, w: 7.4, colW: [1.9, 1.2, 4.3], fontSize: 11.5, rowH: 0.3 }));
card(s, 8.4, 1.4, 4.3, 5.3);
txt(s, "Tiến độ theo lộ trình 6 tuần", { x: 8.65, y: 1.55, w: 3.9, h: 0.4, bold: true, fontSize: 16, color: C.text2 });
D.timeline.forEach((t, i) => {
  const done = t.status.startsWith("Hoàn thành") && !t.status.includes("còn");
  const part = !done && !t.status.startsWith("Chưa");
  const col = done ? HEX.accent4 : part ? HEX.accent2 : "A9B4BF";
  const y = 2.1 + i * 0.75;
  s.addShape(pres.shapes.OVAL, { x: 8.7, y: y + 0.05, w: 0.42, h: 0.42, fill: { color: col }, line: { color: col } });
  txt(s, t.week, { x: 8.7, y: y + 0.05, w: 0.42, h: 0.42, align: "center", valign: "middle", bold: true, color: "FFFFFF", fontSize: 13, margin: 0 });
  txt(s, [{ text: t.task, options: { breakLine: true, fontSize: 11.5 } }, { text: t.status, options: { fontSize: 10.5, italic: true, color: col } }], { x: 9.25, y, w: 3.35, h: 0.7, margin: 0 });
});
s.addNotes(TX.notes[1]);

// 3. Problem
section("Bài toán & dữ liệu");
s = content("Bài toán: hai nhánh trên cùng một tiêu đề sản phẩm");
txt(s, TX.problem_lead, { x: 0.6, y: 1.35, w: 12.1, h: 0.8, fontSize: 16, italic: true, color: "44546A" });
[["Nhánh 1 · Phân loại đa lớp (có giám sát)", TX.branch1, HEX.accent3], ["Nhánh 2 · Phân cụm (không giám sát)", TX.branch2, HEX.accent2]].forEach(([h, b, col], i) => {
  const x = 0.6 + i * 6.2; card(s, x, 2.35, 5.9, 4.3);
  s.addShape(pres.shapes.OVAL, { x: x + 0.3, y: 2.6, w: 0.55, h: 0.55, fill: { color: col }, line: { color: col } });
  txt(s, String(i + 1), { x: x + 0.3, y: 2.6, w: 0.55, h: 0.55, align: "center", valign: "middle", color: "FFFFFF", bold: true, fontSize: 18, margin: 0 });
  txt(s, h, { x: x + 1.0, y: 2.6, w: 4.7, h: 0.55, bold: true, fontSize: 17, color: C.text2, valign: "middle" });
  txt(s, bullets(b, 17), { x: x + 0.3, y: 3.45, w: 5.4, h: 3.1 });
});
s.addNotes(TX.notes[2]);

// 4. Data
s = content("Dữ liệu PriceRunner (UCI #837)");
const stats = [[vn(D.eda.n_rows), "offer sản phẩm"], ["10", "ngành hàng (lớp)"], [String(D.eda.n_merchants), "merchant"], [vn(D.eda.n_clusters), "cụm thực thể"]];
stats.forEach(([n, l], i) => { const y = 1.4 + i * 1.3; card(s, 0.6, y, 3.4, 1.1);
  txt(s, n, { x: 0.8, y: y + 0.05, w: 3.0, h: 0.62, fontSize: 32, bold: true, color: C.accent1, fontFace: "Cambria", margin: 0 });
  txt(s, l, { x: 0.8, y: y + 0.65, w: 3.0, h: 0.35, fontSize: 13, color: "5A6B7C", margin: 0 }); });
const cd = D.class_dist;
s.addChart(pres.charts.BAR, [{ name: "Số mẫu", labels: cd.map((r) => r[0]), values: cd.map((r) => r[1]) }], {
  x: 4.3, y: 1.3, w: 5.2, h: 5.4, barDir: "bar", chartColors: [HEX.accent3], showValue: true, dataLabelPosition: "outEnd",
  dataLabelFontSize: 10, dataLabelColor: "44546A", catAxisLabelFontSize: 11, valAxisHidden: true, catAxisOrientation: "maxMin",
  valGridLine: { style: "none" }, catGridLine: { style: "none" }, showLegend: false, showTitle: true, title: "Phân phối 10 ngành hàng",
  titleFontSize: 13, titleColor: "44546A", catAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt", titleFontFace: "+mn-lt", catAxisLabelColor: "44546A" });
card(s, 9.8, 1.4, 2.9, 5.3);
txt(s, "Điểm đáng chú ý", { x: 10.0, y: 1.55, w: 2.5, h: 0.4, bold: true, fontSize: 15, color: C.text2 });
txt(s, bullets(TX.data_notes, 12.5), { x: 10.0, y: 2.0, w: 2.6, h: 4.6 });
s.addNotes(TX.notes[3]);

// 5. EDA length
section("EDA & tiền xử lý");
s = content("EDA: tiêu đề ngắn, giàu mã model chữ-số");
imgFit(s, "eda_02_title_length_by_class.png", 0.5, 1.35, 8.2, 4.0);
card(s, 8.95, 1.4, 3.75, 5.3);
txt(s, bullets(TX.eda_len, 13.5), { x: 9.15, y: 1.6, w: 3.4, h: 5.0 });
txt(s, TX.eda_len_caption, { x: 0.6, y: 5.6, w: 8.0, h: 1.1, fontSize: 13, italic: true, color: "5A6B7C" });
s.addNotes(TX.notes[4]);

// 6. EDA chi2/overlap
s = content("EDA: từ khóa đặc trưng và vùng chồng lấn");
imgFit(s, "eda_04_top_ngrams_chi2.png", 0.5, 1.3, 8.6, 3.7);
imgFit(s, "eda_05_vocab_overlap.png", 9.3, 1.3, 3.5, 3.0);
txt(s, bullets(TX.eda_chi2, 13.5), { x: 0.6, y: 5.15, w: 12.1, h: 1.6 });
s.addNotes(TX.notes[5]);

// 7. Preprocessing
s = content("Tiền xử lý và xây dựng đặc trưng");
TX.prep_steps.forEach(([h, b], i) => { const x = 0.6 + i * 3.1; card(s, x, 1.5, 2.85, 4.0);
  s.addShape(pres.shapes.OVAL, { x: x + 0.2, y: 1.7, w: 0.55, h: 0.55, fill: { color: HEX.accent2 }, line: { color: HEX.accent2 } });
  txt(s, String(i + 1), { x: x + 0.2, y: 1.7, w: 0.55, h: 0.55, align: "center", valign: "middle", color: "FFFFFF", bold: true, fontSize: 18, margin: 0 });
  txt(s, h, { x: x + 0.2, y: 2.4, w: 2.5, h: 0.6, bold: true, fontSize: 15.5, color: C.text2, margin: 0 });
  txt(s, b, { x: x + 0.2, y: 3.05, w: 2.5, h: 2.4, fontSize: 15, margin: 0 }); });
txt(s, TX.prep_foot, { x: 0.6, y: 5.75, w: 12.1, h: 0.9, fontSize: 14, italic: true, color: "44546A" });
s.addNotes(TX.notes[6]);

// 8. Pipeline
section("Phương pháp");
s = content("Pipeline học máy và thiết kế thực nghiệm");
imgFit(s, "method_pipeline.png", 0.5, 1.3, 8.4, 3.9);
card(s, 9.1, 1.4, 3.6, 5.3);
txt(s, "Thiết kế thực nghiệm", { x: 9.3, y: 1.55, w: 3.2, h: 0.4, bold: true, fontSize: 15, color: C.text2 });
txt(s, bullets(TX.design, 12.5), { x: 9.3, y: 2.0, w: 3.3, h: 4.6 });
txt(s, bullets(TX.models_short, 13), { x: 0.6, y: 5.3, w: 8.3, h: 1.5 });
s.addNotes(TX.notes[7]);

// 9. Results table + chart
section("Kết quả");
s = content("Kết quả phân loại: 9 cấu hình baseline");
const M = D.cls_main;
s.addChart(pres.charts.BAR, [{ name: "Test Macro-F1", labels: M.map((r) => r.exp_id), values: M.map((r) => +r.test_f1_macro.toFixed(4)) }], {
  x: 0.5, y: 1.3, w: 5.6, h: 5.4, barDir: "col", chartColors: M.map((r) => r.exp_id === D.best_id ? HEX.accent2 : HEX.accent3),
  valAxisMinVal: 0.9, valAxisMaxVal: 1.0, valAxisMajorUnit: 0.02, showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.000",
  dataLabelFontSize: 9, dataLabelColor: "44546A", catAxisLabelFontSize: 11, valAxisLabelFontSize: 10, valAxisLabelColor: "7A8794", catAxisLabelColor: "44546A",
  valGridLine: { color: "E1E8EF", size: 0.5 }, catGridLine: { style: "none" }, showLegend: false, showTitle: true, title: "Macro-F1 trên tập Test (trục từ 0,90)",
  titleFontSize: 12, titleColor: "44546A", catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt", titleFontFace: "+mn-lt" });
s.addTable([hdr(["Mã", "Mô hình", "Đặc trưng", "CV F1", "Test Acc", "Test F1"]),
  ...M.map((r) => { const hl = r.exp_id === D.best_id ? { fill: { color: "FBE3CF" }, bold: true } : {};
    return [{ text: r.exp_id, options: { align: "center", ...hl } }, { text: r.model.replace(" (thay XGBoost)", "*"), options: hl }, { text: r.features_short, options: hl },
      { text: f4(r.cv_f1_macro_mean), options: { align: "center", ...hl } }, { text: f4(r.test_accuracy), options: { align: "center", ...hl } }, { text: f4(r.test_f1_macro), options: { align: "center", ...hl } }]; })],
  tbl(null, { x: 6.3, y: 1.35, w: 6.4, colW: [0.5, 1.75, 2.0, 0.7, 0.75, 0.7], fontSize: 10, rowH: 0.42 }));
txt(s, TX.res_note, { x: 6.3, y: 5.75, w: 6.4, h: 1.0, fontSize: 11.5, italic: true, color: "5A6B7C" });
s.addNotes(TX.notes[8]);

// 10. Ablation
s = content("RQ1: n-gram ký tự là đòn bẩy lớn nhất");
D.ablation.forEach((a, i) => { const x = 0.6 + i * 4.1; card(s, x, 1.5, 3.8, 2.6, i === 1 ? "FBE3CF" : HEX.lt2);
  txt(s, a.name, { x: x + 0.25, y: 1.65, w: 3.3, h: 0.5, fontSize: 14, bold: true, color: C.text2, margin: 0 });
  txt(s, f4(a.f1), { x: x + 0.25, y: 2.2, w: 3.3, h: 0.9, fontSize: 40, bold: true, color: i === 1 ? C.accent2 : C.accent1, fontFace: "Cambria", margin: 0 });
  txt(s, `Macro-F1 · ${a.delta === "–" ? "mốc so sánh" : a.delta} · ${a.total_err} lỗi / ${vn(D.n_test)}`, { x: x + 0.25, y: 3.2, w: 3.3, h: 0.7, fontSize: 12.5, color: "5A6B7C", margin: 0 }); });
txt(s, bullets(TX.ablation, 15), { x: 0.6, y: 4.4, w: 12.1, h: 2.3 });
s.addNotes(TX.notes[9]);

// 11. Error analysis
s = content(`Phân tích lỗi mô hình tốt nhất (${D.best_id})`);
imgFit(s, "res_02_confusion_matrix_best.png", 0.5, 1.3, 6.4, 5.5);
s.addTable([hdr(["Thực tế", "Dự đoán thành", "Số mẫu"]), ...D.top_conf.slice(0, 6).map((r) => [r[0], r[1], { text: String(r[2]), options: { align: "center" } }])],
  tbl(null, { x: 7.2, y: 1.4, w: 5.5, colW: [2.1, 2.3, 1.1], fontSize: 11.5, rowH: 0.32 }));
txt(s, bullets(TX.errors, 13.5), { x: 7.2, y: 4.0, w: 5.5, h: 2.8 });
s.addNotes(TX.notes[10]);

// 12. Group split + time
s = content("Kiểm chứng: chia theo sản phẩm và chi phí tính toán");
s.addTable([hdr(["Mô hình", "F1 Stratified", "F1 Group", "Chênh lệch"]),
  ...D.group.map((g) => [g.exp_id + " · " + g.model.replace(" (thay XGBoost)", "*"), { text: f4(g.f1_strat), options: { align: "center" } }, { text: f4(g.f1_group), options: { align: "center" } }, { text: g.delta, options: { align: "center" } }])],
  tbl(null, { x: 0.6, y: 1.4, w: 6.3, colW: [2.9, 1.2, 1.1, 1.1], fontSize: 11.5, rowH: 0.4 }));
txt(s, bullets(TX.group, 13.5), { x: 0.6, y: 3.7, w: 6.3, h: 3.0 });
imgFit(s, "res_04_f1_vs_time.png", 7.2, 1.35, 5.5, 4.0);
txt(s, TX.time, { x: 7.2, y: 5.5, w: 5.5, h: 1.2, fontSize: 12.5, italic: true, color: "5A6B7C" });
s.addNotes(TX.notes[11]);

// 13. Clustering
s = content("Baseline phân cụm: K-Means (K = 10) trên LSA");
imgFit(s, "clu_01_contingency.png", 0.5, 1.3, 6.6, 4.5);
s.addTable([hdr(["Mã", "Không gian", "Silh.", "ARI", "NMI"]), ...D.clu.map((c) => { const hl = c.exp_id === D.best_clu ? { bold: true, fill: { color: "FBE3CF" } } : {};
  return [{ text: c.exp_id, options: { align: "center", ...hl } }, { text: (c.model === "MiniBatchKMeans" ? "MiniBatch · " : "") + c.space, options: hl },
    { text: Number(c.silhouette_cosine).toFixed(3), options: { align: "center", ...hl } }, { text: Number(c.ari_vs_category).toFixed(3), options: { align: "center", ...hl } }, { text: Number(c.nmi_vs_category).toFixed(3), options: { align: "center", ...hl } }]; })],
  tbl(null, { x: 7.3, y: 1.4, w: 5.4, colW: [0.6, 2.4, 0.8, 0.8, 0.8], fontSize: 11, rowH: 0.36 }));
txt(s, bullets(TX.cluster, 13.5), { x: 7.3, y: 3.5, w: 5.4, h: 3.3 });
txt(s, TX.cluster_caption, { x: 0.6, y: 5.95, w: 6.5, h: 0.8, fontSize: 12, italic: true, color: "5A6B7C" });
s.addNotes(TX.notes[12]);

// 14. Progress
section("Tiến độ & kế hoạch");
s = content("Đánh giá tiến độ");
[["Đã hoàn thành", TX.done_s, HEX.accent4], ["Khó khăn / hạn chế", TX.issues_s, HEX.accent6], ["Còn lại đến cuối kỳ", TX.next_s, HEX.accent2]].forEach(([h, b, col], i) => {
  const x = 0.6 + i * 4.1; card(s, x, 1.45, 3.8, 5.3);
  s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: 1.65, w: 0.36, h: 0.36, fill: { color: col }, line: { color: col } });
  txt(s, h, { x: x + 0.75, y: 1.6, w: 2.9, h: 0.45, bold: true, fontSize: 17, color: C.text2, valign: "middle", margin: 0 });
  txt(s, bullets(b, 15.5), { x: x + 0.2, y: 2.3, w: 3.45, h: 4.35 }); });
s.addNotes(TX.notes[13]);

// 15. Contribution
s = content("Phân công và đóng góp");
s.addTable([hdr(["Thành viên", "Công việc đã thực hiện", "Sản phẩm", "Đóng góp"]),
  ...D.members.map((m) => [{ text: m.name, options: { bold: true } }, m.done, m.files, { text: m.share, options: { align: "center", bold: true } }])],
  tbl(null, { x: 0.6, y: 1.4, w: 12.1, colW: [2.0, 6.0, 3.1, 1.0], fontSize: 12, rowH: 0.9 }));
s.addNotes(TX.notes[14]);

// 16. Close
s = pres.addSlide({ masterName: "N06_TITLE", sectionTitle: sec });
s.addText("Cảm ơn thầy/cô và các bạn đã lắng nghe", { placeholder: "title" });
s.addText([{ text: TX.closing, options: { breakLine: true } }, { text: "Mã nguồn · experiment log · hình gốc: kèm trong file nộp Nhom06_…_GiuaKy.zip", options: { fontSize: 14 } }], { placeholder: "body" });
s.addNotes(TX.notes[15]);

(async () => { const out = path.join(__dirname, "Nhom06_Slide_GiuaKy.pptx");
  await pres.writeFile({ fileName: out }); await applyTheme(out, THEME); console.log("wrote", out); })();
