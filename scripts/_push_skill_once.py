"""一次性:把技能目录推到 GitHub Public 仓库(不含 .secrets)。
用法: py scripts/_push_skill_once.py [--repo george-ui-v3]
推完后本脚本可删除。令牌不打印、不写入 remote。
"""
from pathlib import Path
import argparse, json, os, re, subprocess, sys, time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
API = 'https://api.github.com'
UA = 'George-UI-V3-skill-push'


def redact(t):
    t = str(t)
    t = re.sub(r'x-access-token:[^@\s]+', 'x-access-token:***', t)
    t = re.sub(r'ghp_[A-Za-z0-9]+', 'ghp_***', t)
    t = re.sub(r'github_pat_[A-Za-z0-9_]+', 'github_pat_***', t)
    return t


def fail(msg, code=1):
    print(redact(msg), file=sys.stderr)
    raise SystemExit(code)


def load_token():
    token = (os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN') or '').strip()
    if token:
        return token
    for path in (ROOT / '.secrets' / 'github.token', Path.home() / '.george-ui' / 'github.token'):
        if path.is_file():
            token = path.read_text(encoding='utf-8').strip()
            if token:
                return token
    fail('未找到 GitHub 令牌(.secrets/github.token)')


def api(method, path, token, body=None):
    data = None if body is None else json.dumps(body).encode('utf-8')
    req = Request(
        API + path, data=data, method=method,
        headers={
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/vnd.github+json',
            'Content-Type': 'application/json',
            'User-Agent': UA,
            'X-GitHub-Api-Version': '2022-11-28',
        },
    )
    try:
        with urlopen(req, timeout=40) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw.decode('utf-8')) if raw else {}
    except HTTPError as exc:
        raw = exc.read().decode('utf-8', 'replace')
        try:
            payload = json.loads(raw) if raw else {}
        except ValueError:
            payload = {'message': raw[:300]}
        return exc.code, payload
    except URLError as exc:
        fail('无法连接 GitHub API: ' + str(exc.reason))


def run(cmd, cwd, env=None, check=True):
    r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, env=env)
    if check and r.returncode != 0:
        fail('命令失败: ' + ' '.join(cmd) + '\n' + (r.stderr or r.stdout or ''))
    return r


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo', default='george-ui-v3')
    p.add_argument('--private', action='store_true', help='建私有库(默认 Public)')
    a = p.parse_args()
    token = load_token()

    code, user = api('GET', '/user', token)
    if code != 200:
        fail('令牌无效: ' + str(user.get('message')))
    owner = user['login']
    repo = a.repo
    print(f'账号: {owner}')
    print(f'仓库: {owner}/{repo} ({"Private" if a.private else "Public"})')

    code, info = api('GET', f'/repos/{owner}/{repo}', token)
    if code == 404:
        code, info = api('POST', '/user/repos', token, {
            'name': repo,
            'description': 'George-UI-V3 Cursor Agent Skill — 建材企业静态 demo 生成技能 (v2.7.0)',
            'private': bool(a.private),
            'has_issues': True,
            'has_projects': False,
            'has_wiki': False,
            'auto_init': False,
        })
        if code not in (201, 200):
            fail('创建仓库失败: ' + json.dumps(info, ensure_ascii=False)[:400])
        print('仓库已创建')
        time.sleep(1)
    elif code == 200:
        print('仓库已存在,复用')
    else:
        fail('查询仓库失败: ' + str(info.get('message')))

    git_dir = ROOT / '.git'
    if not git_dir.exists():
        run(['git', 'init', '-b', 'main'], ROOT)
        print('已 git init')

    # 确保 .secrets 被忽略
    gi = ROOT / '.gitignore'
    if not gi.is_file() or '.secrets' not in gi.read_text(encoding='utf-8', errors='replace'):
        fail('.gitignore 缺少 .secrets/,拒绝推送以免泄露令牌')

    run(['git', 'add', '-A'], ROOT)
    # 双重确认: secrets 不在暂存区
    staged = run(['git', 'diff', '--cached', '--name-only'], ROOT).stdout or ''
    if '.secrets' in staged or staged.strip().endswith('.token') or '\n.secrets' in staged:
        fail('暂存区含密钥文件,已中止: ' + staged)

    st = run(['git', 'status', '--porcelain'], ROOT).stdout or ''
    if st.strip():
        msg = 'chore: release george-ui-v3 skill v2.7.0 (pitfalls + auto-deploy + sys pages)'
        run(['git', 'commit', '-m', msg], ROOT)
        print('已提交')
    else:
        print('工作区无新变更(可能已提交过)')

    clean = f'https://github.com/{owner}/{repo}.git'
    auth = f'https://x-access-token:{token}@github.com/{owner}/{repo}.git'
    run(['git', 'remote', 'remove', 'origin'], ROOT, check=False)
    run(['git', 'remote', 'add', 'origin', clean], ROOT)
    # 推送用一次性 auth URL,结束后保证 origin 干净
    env = os.environ.copy()
    env['GIT_TERMINAL_PROMPT'] = '0'
    r = subprocess.run(
        ['git', 'push', '-u', auth, 'main', '--force'],
        cwd=str(ROOT), capture_output=True, text=True, env=env,
    )
    run(['git', 'remote', 'set-url', 'origin', clean], ROOT)
    if r.returncode != 0:
        fail('推送失败:\n' + (r.stderr or r.stdout or ''))
    print('推送成功')
    print(f'仓库地址: https://github.com/{owner}/{repo}')
    print(f'克隆: git clone https://github.com/{owner}/{repo}.git')


if __name__ == '__main__':
    main()
