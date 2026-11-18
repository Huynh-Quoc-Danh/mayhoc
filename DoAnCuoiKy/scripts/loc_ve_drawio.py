"""Vẽ 5 hình Chương 2 (Lộc) thành file draw.io từ dữ liệu thật.

Chạy trong thư mục DoAnCuoiKy:
    python scripts/loc_ve_drawio.py
Kết quả: docs/hinh_ve_tay/loc_hinh_2_1.drawio ... loc_hinh_2_5.drawio
và in ra các con số dùng để viết nhận xét.
"""
import os
from html import escape

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import chi2

DATA = 'data/pricerunner_aggregate.csv'
OUT = 'docs/hinh_ve_tay'
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv(DATA)
df.columns = df.columns.str.strip()
df['title'] = df['Product Title'].astype(str).str.lower()
df['so_tu'] = df['title'].str.split().str.len()
NG = 'Category Label'
COLD = {'Fridge Freezers', 'Fridges', 'Freezers'}
N = len(df)


# ---------------------------------------------------------------- draw.io helpers
class Diagram:
    def __init__(self, title, w=900, h=600):
        self.cells, self.i, self.w, self.h = [], 2, w, h
        self.text(title, 20, 10, w - 40, 30, size=16, bold=True, align='left')

    def _add(self, xml):
        self.cells.append(xml)
        self.i += 1

    def box(self, x, y, w, h, fill='#FFFFFF', stroke='#555555', value='', size=11, bold=False):
        st = (f'rounded=0;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};'
              f'fontSize={size};fontStyle={1 if bold else 0};verticalAlign=middle;')
        self._add(f'<mxCell id="c{self.i}" value="{escape(value)}" style="{st}" vertex="1" parent="1">'
                  f'<mxGeometry x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" as="geometry"/></mxCell>')

    def text(self, value, x, y, w, h, size=11, bold=False, align='center', valign='middle', color='#000000', extra=''):
        st = (extra + f'text;html=1;whiteSpace=wrap;align={align};verticalAlign={valign};fontSize={size};'
              f'fontStyle={1 if bold else 0};fontColor={color};')
        self._add(f'<mxCell id="c{self.i}" value="{escape(value)}" style="{st}" vertex="1" parent="1">'
                  f'<mxGeometry x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" as="geometry"/></mxCell>')

    def line(self, x1, y1, x2, y2, color='#333333', width=1, dashed=False):
        st = f'endArrow=none;html=1;strokeColor={color};strokeWidth={width};' + ('dashed=1;' if dashed else '')
        self._add(f'<mxCell id="c{self.i}" value="" style="{st}" edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
                  f'<mxPoint x="{x1:.0f}" y="{y1:.0f}" as="sourcePoint"/><mxPoint x="{x2:.0f}" y="{y2:.0f}" as="targetPoint"/>'
                  f'</mxGeometry></mxCell>')

    def save(self, name):
        xml = (f'<mxfile><diagram name="{name}"><mxGraphModel grid="0" page="1" pageWidth="{self.w}" '
               f'pageHeight="{self.h}"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
               + ''.join(self.cells) + '</root></mxGraphModel></diagram></mxfile>')
        path = os.path.join(OUT, name + '.drawio')
        open(path, 'w', encoding='utf-8').write(xml)
        print('Đã lưu', path)


def vn(x, d=1):
    return f'{x:,.{d}f}'.replace(',', ' ').replace('.', ',').replace(' ', '.')


def blue(t):
    """t trong [0,1] -> màu từ trắng tới xanh đậm"""
    t = max(0.0, min(1.0, t))
    r = int(255 + (31 - 255) * t); g = int(255 + (78 - 255) * t); b = int(255 + (121 - 255) * t)
    return f'#{r:02X}{g:02X}{b:02X}'


# ---------------------------------------------------------------- Hình 2.1
dem = df[NG].value_counts()
d = Diagram(f'Hình 2.1 – Số tiêu đề theo ngành (tổng {vn(N, 0)})', 760, 510)
X0, S, Y, H, G = 170, 440 / dem.max(), 55, 26, 10
for k, (ng, c) in enumerate(dem.items()):
    y = Y + k * (H + G)
    d.text(ng, 10, y, X0 - 18, H, align='right', size=12)
    d.box(X0, y, c * S, H, fill='#F4B183' if ng in COLD else '#9DC3E6')
    d.text(f'{vn(c, 0)} ({vn(c / N * 100)}%)', X0 + c * S + 6, y, 120, H, align='left')
yb = Y + len(dem) * (H + G)
d.line(X0, Y - 6, X0, yb)
lanh = dem[list(COLD)].sum()
d.box(X0, yb + 12, 16, 16, fill='#F4B183')
d.text(f'Nhóm làm lạnh (3 ngành = {vn(lanh, 0)} tiêu đề, {vn(lanh / N * 100)}%)', X0 + 22, yb + 6, 420, 28, align='left')
d.box(X0, yb + 38, 16, 16, fill='#9DC3E6')
d.text('Các ngành khác', X0 + 22, yb + 32, 200, 28, align='left')
d.text('Nguồn: data/pricerunner_aggregate.csv (cột Category Label)', 20, yb + 64, 600, 20, size=10, align='left', color='#666666')
d.save('loc_hinh_2_1')
print('\n[2.1] Số tiêu đề theo ngành:\n', dem.to_string(), '\n  lệch lớn/nhỏ =', round(dem.max() / dem.min(), 2))

# ---------------------------------------------------------------- Hình 2.2
st = df.groupby(NG)['so_tu'].describe().sort_values('50%')
d = Diagram('Hình 2.2 – Độ dài tiêu đề (số từ) theo ngành', 860, 520)
X0, Y, H, G = 170, 70, 26, 10
vmax = 25  # trục 0–25 từ
S = 600 / vmax
for t in range(0, vmax + 1, 5):
    x = X0 + t * S
    d.line(x, Y - 10, x, Y + len(st) * (H + G), color='#DDDDDD', dashed=True)
    d.text(str(t), x - 15, Y - 30, 30, 18, size=10)
d.text('số từ', X0 + vmax * S + 5, Y - 30, 50, 18, size=10, align='left')
for k, (ng, r) in enumerate(st.iterrows()):
    y = Y + k * (H + G)
    d.text(ng, 10, y, X0 - 18, H, align='right', size=12)
    d.line(X0 + r['min'] * S, y + H / 2, X0 + min(r['max'], vmax) * S, y + H / 2, color='#888888')
    d.box(X0 + r['25%'] * S, y, (r['75%'] - r['25%']) * S, H, fill='#F4B183' if ng in COLD else '#9DC3E6')
    d.line(X0 + r['50%'] * S, y, X0 + r['50%'] * S, y + H, color='#C00000', width=3)
    d.text(f'TB {vn(r["mean"])}', X0 + vmax * S + 5, y, 70, H, size=10, align='left')
yb = Y + len(st) * (H + G)
d.text('Hộp: từ 25% đến 75% tiêu đề · vạch đỏ: trung vị · đường xám: ngắn nhất → dài nhất (cắt ở 25 từ) · TB: trung bình',
       20, yb + 8, 820, 20, size=10, align='left')
d.text(f'Toàn bộ dữ liệu: trung bình {vn(df.so_tu.mean(), 2)} từ, trung vị {df.so_tu.median():.0f}, '
       f'dài nhất {df.so_tu.max()} từ. Nguồn: data/pricerunner_aggregate.csv', 20, yb + 30, 820, 20,
       size=10, align='left', color='#666666')
d.save('loc_hinh_2_2')
print('\n[2.2] Độ dài tiêu đề theo ngành:\n', st[['mean', '25%', '50%', '75%', 'min', 'max']].round(1).to_string())

# ---------------------------------------------------------------- Hình 2.3
cv = CountVectorizer(ngram_range=(1, 2), min_df=5, binary=True, token_pattern=r'(?u)\b\w[\w.]*\b')
X = cv.fit_transform(df['title'])
ten = np.array(cv.get_feature_names_out())
nganh = list(dem.index)
top = {}
for ng in nganh:
    y = (df[NG] == ng).values
    s, _ = chi2(X, y)
    trong = np.asarray(X[y].mean(axis=0)).ravel()
    ngoai = np.asarray(X[~y].mean(axis=0)).ravel()
    s = np.where(trong > ngoai, s, 0)
    top[ng] = list(ten[np.argsort(s)[::-1][:5]])
d = Diagram('Hình 2.3 – 5 từ / cụm từ đặc trưng nhất của mỗi ngành (theo chi²)', 900, 420)
W, Hh = 165, 150
for k, ng in enumerate(nganh):
    x, y = 20 + (k % 5) * (W + 7), 55 + (k // 5) * (Hh + 15)
    d.box(x, y, W, 28, fill='#F4B183' if ng in COLD else '#9DC3E6', value=ng, bold=True)
    d.box(x, y + 28, W, Hh - 28, fill='#FFFFFF', value='<br>'.join(f'{j + 1}. {t}' for j, t in enumerate(top[ng])))
d.text('Chi² đo mức một từ gắn với một ngành so với các ngành còn lại (từ và cặp từ, xuất hiện ≥ 5 lần). '
       'Nguồn: data/pricerunner_aggregate.csv, script scripts/loc_ve_drawio.py', 20, 390, 860, 20, size=10,
       align='left', color='#666666')
d.save('loc_hinh_2_3')
print('\n[2.3] Top 5 chi²:')
for ng in nganh:
    print(f'  {ng}: {", ".join(top[ng])}')

# ---------------------------------------------------------------- Hình 2.4
TOPN = 200
tu = {}
for ng in nganh:
    words = df.loc[df[NG] == ng, 'title'].str.split().explode()
    words = words[words.str.isalpha() & (words.str.len() > 1)]
    tu[ng] = set(words.value_counts().index[:TOPN])
M = pd.DataFrame(0.0, index=nganh, columns=nganh)
for a in nganh:
    for b in nganh:
        M.loc[a, b] = len(tu[a] & tu[b]) / TOPN
d = Diagram(f'Hình 2.4 – Tỉ lệ từ chung trong {TOPN} từ phổ biến nhất giữa các ngành', 900, 760)
C, X0, Y0 = 52, 170, 170
off = M.where(~np.eye(len(nganh), dtype=bool))
mx = off.max().max()
for j, b in enumerate(nganh):
    d.text(b, X0 + j * C, Y0 - 115, C, 110, size=10, align='left', extra='horizontal=0;')
for i_, a in enumerate(nganh):
    d.text(a, 10, Y0 + i_ * C, X0 - 18, C, align='right', size=11)
    for j, b in enumerate(nganh):
        v = M.loc[a, b]
        if a == b:
            d.box(X0 + j * C, Y0 + i_ * C, C, C, fill='#EEEEEE', value='–')
        else:
            t = v / mx
            d.box(X0 + j * C, Y0 + i_ * C, C, C, fill=blue(t), value=f'{v * 100:.0f}%', size=10)
            if t > 0.55:
                d.cells[-1] = d.cells[-1].replace('fontSize=10;', 'fontSize=10;fontColor=#FFFFFF;')
d.text(f'Ô càng đậm: hai ngành dùng chung càng nhiều từ. Chỉ tính từ chữ cái (bỏ số, mã model). '
       f'Nguồn: data/pricerunner_aggregate.csv, script scripts/loc_ve_drawio.py', 20, Y0 + 10 * C + 15, 860, 30,
       size=10, align='left', color='#666666')
d.save('loc_hinh_2_4')
cap = off.stack().sort_values(ascending=False)
cap = cap[[a < b for a, b in cap.index]]
print('\n[2.4] 5 cặp ngành chung từ nhiều nhất:')
for (a, b), v in cap.head(5).items():
    print(f'  {a} – {b}: {v * 100:.0f}%')

# ---------------------------------------------------------------- Hình 2.5
mid = 'Merchant ID'
top_m = df[mid].value_counts().index[:15]
B = pd.crosstab(df.loc[df[mid].isin(top_m), mid], df.loc[df[mid].isin(top_m), NG]).reindex(index=top_m, columns=nganh, fill_value=0)
d = Diagram('Hình 2.5 – 15 cửa hàng đăng nhiều tin nhất và số tin theo từng ngành', 900, 760)
C, Hc, X0, Y0 = 60, 34, 150, 170
mx = B.values.max()
for j, b in enumerate(nganh):
    d.text(b, X0 + j * C, Y0 - 115, C, 110, size=10, align='left', extra='horizontal=0;')
d.text('Tổng', X0 + len(nganh) * C, Y0 - 30, 70, 25, size=10, bold=True)
for i_, m in enumerate(top_m):
    y = Y0 + i_ * Hc
    d.text(f'Cửa hàng {m}', 10, y, X0 - 18, Hc, align='right', size=11)
    for j, b in enumerate(nganh):
        v = int(B.loc[m, b])
        t = (v / mx) ** 0.5 if v else 0
        d.box(X0 + j * C, y, C, Hc, fill=blue(t) if v else '#FFFFFF', value=str(v) if v else '', size=10)
        if t > 0.55:
            d.cells[-1] = d.cells[-1].replace('fontSize=10;', 'fontSize=10;fontColor=#FFFFFF;')
    d.text(vn(B.loc[m].sum(), 0), X0 + len(nganh) * C, y, 70, Hc, size=10)
yb = Y0 + len(top_m) * Hc
nm = df[mid].nunique()
mot = (df.groupby(mid)[NG].nunique() == 1).sum()
d.text(f'Ô trống: cửa hàng không bán ngành đó. Toàn bộ có {nm} cửa hàng, trong đó {mot} cửa hàng chỉ bán 1 ngành; '
       f'15 cửa hàng trên chiếm {vn(B.values.sum() / N * 100)}% số tin. Nguồn: data/pricerunner_aggregate.csv',
       20, yb + 12, 860, 40, size=10, align='left', color='#666666')
d.save('loc_hinh_2_5')
print('\n[2.5] 15 cửa hàng lớn nhất chiếm', round(B.values.sum() / N * 100, 1), '% số tin;',
      mot, '/', nm, 'cửa hàng chỉ bán 1 ngành;',
      'số ngành của 15 cửa hàng lớn:', (B > 0).sum(axis=1).tolist())
print('  Cluster ID:', df['Cluster ID'].nunique(), 'cụm; trung bình',
      round(df.groupby('Cluster ID').size().mean(), 2), 'tin/cụm; cụm lớn nhất',
      df.groupby('Cluster ID').size().max(), 'tin; số cửa hàng trung bình mỗi cụm',
      round(df.groupby('Cluster ID')[mid].nunique().mean(), 2))
