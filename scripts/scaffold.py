"""George-UI-V3 脚手架:复制纯静态多页套件(index.html + assets/{css,js,pages,images})。
产物双击 index.html 即可离线打开,全部相对路径,无需任何服务器或构建。
用法:
  py scripts/scaffold.py <新目录>
目标目录必须不存在,不覆盖任何文件。
"""
from pathlib import Path
import argparse, shutil, json, hashlib

p = argparse.ArgumentParser(description='George-UI-V3 纯静态 demo 脚手架')
p.add_argument('destination', type=Path)
a = p.parse_args()
root = Path(__file__).resolve().parents[1]
dest = a.destination.resolve()
if dest.exists():
    p.error('目标目录已存在,请换一个新目录;未覆盖任何文件。')

shutil.copytree(root / 'assets/static-kit', dest)
files = {
    str(f.relative_to(dest)).replace('\\', '/'): hashlib.sha256(f.read_bytes()).hexdigest()
    for f in dest.rglob('*') if f.is_file()
}
(dest / 'design-lock.json').write_text(json.dumps({
    'skill': 'george-ui-v3',
    'mode': 'static-multipage',
    'figmaSpec': '2026-09-14 (R001~R175, seven-spec-rules.md)',
    'entry': 'index.html',
    'verifiedForCurrentRequest': False,
    'sha256': files
}, ensure_ascii=False, indent=2), encoding='utf-8')
print(dest / 'index.html')
print('纯静态套件已复制。下一步:改 assets/js/nav-config.js(品牌+导航)与 assets/js/data.js(演示数据),')
print('按需增删 assets/pages/*.html(含 todo.html 待办审批样例);所有路径保持相对;交付前双击 index.html 本地验证。')
