"""Sửa file nhật ký thí nghiệm bị hỏng sau khi đi qua Excel / Google Sheets.

Hai lỗi thường gặp:
  1. Google Sheets để định dạng Việt Nam đọc dấu chấm thập phân thành dấu ngăn hàng nghìn:
     0.9679 -> 967.909, 14.71 -> 14.715.635; mã commit 7290... -> 7.29E+09; ngày đổi kiểu 11/12/2026.
  2. File tải về không có dòng trống cuối -> lần chạy sau ghi dính vào dòng cuối (một dòng có 51 cột).

Cách sửa: mọi số liệu gốc vẫn còn trong experiments/<ten>/runs/<run_id>.json (ghi tự động lúc chạy).
Script đọc lại các JSON đó và GHI ĐÈ các cột số liệu, ngày giờ, mã commit; GIỮ NGUYÊN cột nhan_xet, rut_ra
(phần người chạy tự viết). Dòng nào không có JSON thì giữ nguyên và báo ra màn hình.

    python scripts/sua_nhat_ky.py danh            # xem trước, không ghi
    python scripts/sua_nhat_ky.py danh --ghi      # ghi file đã sửa (bản cũ lưu thành experiment_log.bak.csv)
"""
import argparse
import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_COLS = ("nhan_xet", "rut_ra")


def doc_csv(path):
    """Đọc CSV, tách các dòng bị dính (một dòng có số cột gấp đôi)."""
    raw = list(csv.reader(open(path, encoding="utf-8-sig", newline="")))
    header, rows = raw[0], []
    n = len(header)
    for r in raw[1:]:
        if not any(c.strip() for c in r):
            continue
        while len(r) > n:  # dòng dính: cột cuối của dòng trước nối liền run_id của dòng sau
            first, rest = r[:n], r[n:]
            last = first[-1]
            # run_id có dạng <member>_YYYYmmdd_HHMMSS; tách theo vị trí của nó trong ô cuối
            member = path.parent.name
            pos = last.rfind(member + "_20")
            if pos < 0:
                break
            first[-1], next_id = last[:pos], last[pos:]
            rows.append(dict(zip(header, first)))
            r = [next_id] + rest
        rows.append(dict(zip(header, r + [""] * (n - len(r)))))
    return header, rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("member", choices=["danh", "loc", "nhan", "thinh"])
    ap.add_argument("--file", default="experiment_log.csv", help="tên file nhật ký (mặc định experiment_log.csv)")
    ap.add_argument("--ghi", action="store_true", help="ghi đè file sau khi sửa")
    a = ap.parse_args()

    folder = ROOT / "experiments" / a.member
    path = folder / a.file
    header, rows = doc_csv(path)
    sua, thieu = 0, []
    for row in rows:
        js = folder / "runs" / f"{row.get('run_id', '').strip()}.json"
        if not js.exists():
            thieu.append(row.get("run_id"))
            continue
        d = json.load(open(js, encoding="utf-8"))
        goc = {}
        if "config" in d:  # JSON của run_experiment.py
            goc.update({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v)
                        for k, v in d["config"].items()})
            goc.update({k: round(v, 6) for k, v in d["results"].items()})
            goc["thoi_diem_chay"] = d["time"]
        else:  # JSON của log_generic (phân cụm)
            goc.update(d)
        for k, v in goc.items():
            if k in header and k not in TEXT_COLS and k != "run_id":
                row[k] = "" if v is None else v
        sua += 1
    print(f"{path.name}: {len(rows)} dòng; khôi phục số liệu {sua} dòng từ JSON; không có JSON: {thieu or 'không'}")
    for r in rows:
        print(f"  {r['run_id']:24s} {str(r.get('ten_thi_nghiem', r.get('algo', ''))):14s} "
              f"F1/NMI={r.get('test_f1_macro') or r.get('nmi')}  nhan_xet={'có' if r.get('nhan_xet', '').strip() else 'TRỐNG'}")
    if a.ghi:
        shutil.copy(path, path.with_suffix(".bak.csv"))
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=header, lineterminator="\r\n")
            w.writeheader()
            w.writerows(rows)
        print(f"Đã ghi {path} (bản cũ: {path.with_suffix('.bak.csv').name})")
    else:
        print("Chưa ghi gì. Thêm --ghi để lưu.")


if __name__ == "__main__":
    main()
