"""把已通过自测的 George-UI-V3 demo 部署到 GitHub Pages。

纯标准库:git + GitHub REST API,不依赖 gh,不需要 pip。
用法(在技能目录):
  py scripts/deploy.py <demo目录>
  py scripts/deploy.py <demo目录> --repo my-demo-name

令牌从 GH_TOKEN / GITHUB_TOKEN 或 %USERPROFILE%\\.george-ui\\github.token 读取。
令牌不会写入 demo、git config、deploy-report.json 或标准输出。
"""
from pathlib import Path
import argparse, hashlib, json, os, re, subprocess, sys, time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
import preflight

SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TOKEN_PATH = SKILL_ROOT / '.secrets' / 'github.token'   # 内置在技能内(默认 gitignore,不进 zip)
TOKEN_PATH = Path.home() / '.george-ui' / 'github.token'       # 本机用户目录
API = 'https://api.github.com'
UA = 'George-UI-V3-deploy'


def fail(message, code=1):
    print(redact(message), file=sys.stderr)
    raise SystemExit(code)


def redact(text):
    text = str(text)
    text = re.sub(r'x-access-token:[^@\s]+', 'x-access-token:***', text)
    text = re.sub(r'ghp_[A-Za-z0-9]+', 'ghp_***', text)
    text = re.sub(r'github_pat_[A-Za-z0-9_]+', 'github_pat_***', text)
    return text


def load_token():
    token = (os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN') or '').strip()
    if token:
        return token
    for path in (SKILL_TOKEN_PATH, TOKEN_PATH):   # 先技能内置,再本机用户目录
        if path.is_file():
            token = path.read_text(encoding='utf-8').strip()
            if token:
                return token
    fail(
        '未找到 GitHub 令牌。请先创建经典 PAT(No expiration, scopes: repo + workflow),再任选其一:\n'
        '  py scripts/github_setup.py --in-skill   # 内置到技能内 .secrets/github.token\n'
        '  py scripts/github_setup.py              # 存到本机用户目录\n'
        '  或设置环境变量 GH_TOKEN。说明见 references/github-deploy.md'
    )


def slugify(raw):
    text = (raw or '').strip().lower()
    slug = re.sub(r'[^a-z0-9]+', '-', text).strip('-')[:80].strip('-')
    if slug and re.match(r'^[a-z0-9]', slug):
        return slug
    digest = hashlib.sha1(text.encode('utf-8')).hexdigest()[:6]
    return 'george-demo-' + digest


def api(method, path, token, body=None, retries=3):
    data = None if body is None else json.dumps(body).encode('utf-8')
    last = None
    for attempt in range(retries):
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
            if exc.code in (502, 503, 504) and attempt + 1 < retries:
                time.sleep(2 + attempt)
                last = payload
                continue
            return exc.code, payload
        except URLError as exc:
            last = {'message': str(exc.reason)}
            if attempt + 1 < retries:
                time.sleep(2 + attempt)
                continue
    fail('无法连接 GitHub API: ' + str((last or {}).get('message')))


def git(args, cwd, check=True, extra_config=None):
    cmd = ['git']
    for item in extra_config or []:
        cmd.extend(['-c', item])
    cmd.extend(args)
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if check and proc.returncode != 0:
        detail = redact((proc.stderr or proc.stdout or '').strip())
        fail('git %s 失败:\n%s' % (args[0], detail))
    return proc


def identity_config():
    name = subprocess.run(['git', 'config', '--global', 'user.name'], capture_output=True, text=True)
    email = subprocess.run(['git', 'config', '--global', 'user.email'], capture_output=True, text=True)
    cfg = []
    if not (name.stdout or '').strip():
        cfg.append('user.name=George UI Deploy')
    if not (email.stdout or '').strip():
        cfg.append('user.email=george-ui-deploy@users.noreply.github.com')
    return cfg


def ensure_repo(token, owner, repo):
    status, payload = api('GET', '/repos/%s/%s' % (owner, repo), token)
    if status == 200:
        if (payload.get('owner') or {}).get('login', '').lower() != owner.lower():
            fail('仓库 %s/%s 不属于当前令牌用户。请换 --repo。' % (owner, repo))
        if payload.get('private'):
            fail('仓库 %s/%s 是私有的。本流程只发布 Public 仓库(免费 Pages)。请换一个仓库名。' % (owner, repo))
        return False
    if status != 404:
        fail('查询仓库失败 HTTP %s: %s' % (status, payload.get('message')))
    status, payload = api('POST', '/user/repos', token, {
        'name': repo,
        'private': False,
        'description': 'George-UI-V3 demo',
        'auto_init': False,
        'has_issues': False,
        'has_wiki': False,
        'has_projects': False,
    })
    if status not in (201, 200):
        fail('创建公开仓库失败 HTTP %s: %s' % (status, payload.get('message')))
    return True


def commit_demo(demo, cfg):
    git(['init', '-b', 'main'], demo, extra_config=cfg)
    git(['add', '-A'], demo, extra_config=cfg)
    status = git(['status', '--porcelain'], demo, extra_config=cfg)
    if not (status.stdout or '').strip():
        rev = git(['rev-parse', 'HEAD'], demo, check=False, extra_config=cfg)
        if rev.returncode != 0:
            fail('demo 目录没有可提交的文件。')
        return rev.stdout.strip(), False
    git(['commit', '-m', 'Publish George UI demo'], demo, extra_config=cfg)
    rev = git(['rev-parse', 'HEAD'], demo, extra_config=cfg)
    return rev.stdout.strip(), True


def push_demo(demo, owner, repo, token, cfg):
    clean = 'https://github.com/%s/%s.git' % (owner, repo)
    auth = 'https://x-access-token:%s@github.com/%s/%s.git' % (token, owner, repo)
    existing = git(['remote'], demo, check=False, extra_config=cfg)
    if 'origin' in (existing.stdout or '').split():
        git(['remote', 'set-url', 'origin', clean], demo, extra_config=cfg)
    else:
        git(['remote', 'add', 'origin', clean], demo, extra_config=cfg)
    pushed = git(
        ['-c', 'credential.helper=', 'push', auth, 'HEAD:main'],
        demo, check=False, extra_config=cfg,
    )
    git(['remote', 'set-url', 'origin', clean], demo, extra_config=cfg)
    verify = git(['remote', 'get-url', 'origin'], demo, extra_config=cfg)
    if 'x-access-token' in (verify.stdout or '') or token in (verify.stdout or ''):
        git(['remote', 'set-url', 'origin', clean], demo, extra_config=cfg)
        fail('origin 含令牌,已改回公开地址,但请检查 demo 的 .git/config。')
    if pushed.returncode != 0:
        fail('推送失败:\n' + redact((pushed.stderr or pushed.stdout or '').strip()))


def enable_pages(token, owner, repo):
    body = {'build_type': 'legacy', 'source': {'branch': 'main', 'path': '/'}}
    for _ in range(5):
        status, payload = api('POST', '/repos/%s/%s/pages' % (owner, repo), token, body)
        if status in (201, 204):
            return payload.get('html_url') or ('https://%s.github.io/%s/' % (owner, repo))
        message = (payload.get('message') or '').lower()
        if status == 409 or 'already exists' in message or 'already enabled' in message:
            status, payload = api('PUT', '/repos/%s/%s/pages' % (owner, repo), token, body)
            if status in (200, 204):
                return payload.get('html_url') or ('https://%s.github.io/%s/' % (owner, repo))
            get_status, got = api('GET', '/repos/%s/%s/pages' % (owner, repo), token)
            if get_status == 200:
                return got.get('html_url') or ('https://%s.github.io/%s/' % (owner, repo))
        if status in (404, 422):
            time.sleep(3)
            continue
        fail('启用 GitHub Pages 失败 HTTP %s: %s' % (status, payload.get('message')))
    fail('仓库已推送,但 GitHub Pages 仍未启用。请到仓库 Settings → Pages 查看。')


def http_get(url, limit=65536):
    req = Request(url, headers={'User-Agent': UA, 'Cache-Control': 'no-cache'})
    try:
        with urlopen(req, timeout=25) as resp:
            return resp.status, resp.read(limit)
    except HTTPError as exc:
        return exc.code, exc.read(limit)
    except URLError:
        return 0, b''


def pages_status(token, owner, repo):
    status, payload = api('GET', '/repos/%s/%s/pages' % (owner, repo), token)
    if status != 200:
        return 'pages HTTP %s %s' % (status, payload.get('message'))
    return 'status=%s html_url=%s' % (payload.get('status'), payload.get('html_url'))


def wait_until_live(token, owner, repo, page_url):
    asset = page_url.rstrip('/') + '/assets/css/tokens.css'
    deadline = time.time() + 150
    delay = 5
    last = ''
    while time.time() < deadline:
        code, body = http_get(page_url)
        asset_code, asset_body = http_get(asset) if code == 200 else (0, b'')
        last = 'index=%s asset=%s' % (code, asset_code)
        if code == 200 and b'assets/pages/' in body and asset_code == 200 and b'--g-' in asset_body:
            return [page_url, asset]
        time.sleep(delay)
        delay = min(delay + 3, 15)
    fail('线上地址在超时内未通过校验(%s)。Pages: %s\n地址: %s' % (last, pages_status(token, owner, repo), page_url))


def write_report(demo, owner, repo, url, commit, checked):
    report = {
        'skill': 'george-ui-v3',
        'owner': owner,
        'repo': repo,
        'url': url,
        'commit': commit,
        'verified': True,
        'checked': checked,
        'time': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    }
    (demo / 'deploy-report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )


def main():
    parser = argparse.ArgumentParser(description='部署 George-UI-V3 demo 到 GitHub Pages')
    parser.add_argument('demo', type=Path)
    parser.add_argument('--repo', help='仓库名(小写连字符)。默认取目录名')
    args = parser.parse_args()
    demo = args.demo.resolve()
    if not demo.is_dir():
        fail('目录不存在: ' + str(demo))
    if not (demo / 'index.html').is_file():
        fail('缺少 index.html,这不是可部署的 demo 目录。')

    errors = preflight.check(demo)
    if errors:
        fail('preflight 未通过,已中止部署:\n- ' + '\n- '.join(errors))

    token = load_token()
    status, user = api('GET', '/user', token)
    if status != 200 or not user.get('login'):
        fail('令牌无效 HTTP %s。请重新执行 py scripts/github_setup.py' % status)
    owner = user['login']
    repo = slugify(args.repo or demo.name)
    print('部署目标: %s/%s (Public)' % (owner, repo))

    created = ensure_repo(token, owner, repo)
    print('仓库%s。' % ('已创建' if created else '已存在,将更新'))
    cfg = identity_config()
    commit, _changed = commit_demo(demo, cfg)
    push_demo(demo, owner, repo, token, cfg)
    page_url = enable_pages(token, owner, repo)
    if not page_url.endswith('/'):
        page_url += '/'
    print('正在等待 Pages 生效: ' + page_url)
    checked = wait_until_live(token, owner, repo, page_url)
    write_report(demo, owner, repo, page_url, commit, checked)
    # 报告本身再推一次,失败不影响已经验过的地址
    try:
        commit_demo(demo, cfg)
        push_demo(demo, owner, repo, token, cfg)
    except SystemExit:
        print('线上已可访问。deploy-report.json 留在本地,补推失败不影响地址。')
    print('本地目录: ' + str(demo))
    print('公开地址: ' + page_url)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        fail('部署中断: ' + redact(exc))
