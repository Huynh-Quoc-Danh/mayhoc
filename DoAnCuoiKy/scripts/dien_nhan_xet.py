"""Điền / sửa cột nhan_xet, rut_ra trong nhật ký thí nghiệm mà KHÔNG cần Excel hay Google Sheets.

Script tự đặt ngoặc kép cho ô có dấu phẩy nên file CSV không bao giờ bị lệch cột.

    # 1. Xem các dòng (đánh dấu dòng còn trống nhận xét)
    python scripts/dien_nhan_xet.py thinh --file cluster_log.csv
    # 2. Điền / sửa nhận xét cho 1 dòng (chỉ cần 6 số cuối của run_id)
    python scripts/dien_nhan_xet.py thinh --file cluster_log.csv --dong 214111 --nx "câu nhận xét" --rr "câu rút ra"

Trong PowerShell: đặt mỗi câu trong ngoặc kép "...", bên trong câu KHÔNG dùng dấu ngoặc kép.
"""
import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("member", choices=["danh", "loc", "nhan", "thinh"])
    ap.add_argument("--file", default="experiment_log.csv", help="tên file nhật ký (mặc định experiment_log.csv)")
    ap.add_argument("--dong", help="run_id hoặc vài số cuối của run_id cần sửa")
    ap.add_argument("--nx", help="nội dung cột nhan_xet")
    ap.add_argument("--rr", help="nội dung cột rut_ra")
    a = ap.parse_args()

    path = ROOT / "experiments" / a.member / a.file
    with open(path, encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        header, rows = rd.fieldnames, [r for r in rd if any((v or "").strip() for v in r.values())]
    bad = [r["run_id"] for r in rows if None in r]
    if bad:
        raise SystemExit(f"File đang bị lệch cột ở {bad}. Chạy scripts/sua_nhat_ky.py trước.")

    if not a.dong:  # chế độ xem
        ten = "ten_thi_nghiem" if "ten_thi_nghiem" in header else "algo"
        so = "test_f1_macro" if "test_f1_macro" in header else "nmi"
        for r in rows:
            trong = "  <-- CHƯA CÓ NHẬN XÉT" if not (r.get("nhan_xet") or "").strip() else ""
            print(f"{r['run_id']:24s} {r.get(ten, ''):18s} {so}={r.get(so, '')}{trong}")
        return

    hit = [r for r in rows if r["run_id"].endswith(a.dong)]
    if len(hit) != 1:
        raise SystemExit(f"Tìm thấy {len(hit)} dòng khớp '{a.dong}'. Ghi thêm số cho đủ khác biệt.")
    r = hit[0]
    if a.nx is not None:
        r["nhan_xet"] = a.nx.strip()
    if a.rr is not None:
        r["rut_ra"] = a.rr.strip()
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)
    print(f"Đã ghi {r['run_id']}:\n  nhan_xet = {r['nhan_xet']}\n  rut_ra   = {r['rut_ra']}")


if __name__ == "__main__":
    main()
