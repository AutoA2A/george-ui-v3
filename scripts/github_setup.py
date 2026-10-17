"""一次性保存 GitHub 经典 PAT,并在缺失时补 git 身份。

默认写入 %USERPROFILE%\\.george-ui\\github.token(技能目录之外,最安全)。
加 --in-skill 则写入技能内 .secrets/github.token(已 gitignore、默认不进 zip)。
用法:
  py scripts/github_setup.py             # 交互输入令牌(不回显),存到用户目录
  py scripts/github_setup.py --in-skill  # 内置到技能内 .secrets/github.token
  py scripts/github_setup.py --save-env  # 把已有的 GH_TOKEN/GITHUB_TOKEN 存起来
"""
from pathlib import Path
import argparse, getpass, json, os, subprocess, sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

SKILL_ROOT = Path(__file__).resolve().parents[1]
HOME_TOKEN_PATH = Path.home() / '.george-ui' / 'github.token'
SKILL_TOKEN_PATH = SKILL_ROOT / '.secrets' / 'github.token'
TOKEN_PATH = HOME_TOKEN_PATH  # 兼容旧引用,实际目标在 main 里按 --in-skill 决定


def ensure_secret_gitignore(folder):
    """确保 .secrets 目录永远不会被 git 提交。"""
    folder.mkdir(parents=True, exist_ok=True)
    (folder / '.gitignore').write_text('*\n!.gitignore\n', encoding='utf-8')


def load_env_token():
    return (os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN') or '').strip()


def api_user(token):
    req = Request(
        'https://api.github.com/user',
        headers={
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/vnd.github+json',
            'User-Agent': 'George-UI-V3-setup',
            'X-GitHub-Api-Version': '2022-11-28',
        },
    )
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except HTTPError as exc:
        detail = exc.read().decode('utf-8', 'replace')[:240]
        raise SystemExit('令牌校验失败 HTTP %s。请确认是勾了 repo 的经典 PAT。%s' % (exc.code, detail))
    except URLError as exc:
        raise SystemExit('无法连接 GitHub:' + str(exc.reason))


def restrict(path):
    if os.name != 'nt':
        os.chmod(path, 0o600)
        return
    user = os.environ.get('USERNAME') or ''
    if not user:
        return
    subprocess.run(
        ['icacls', str(path), '/inheritance:r', '/grant:r', '%s:(R,W)' % user],
        capture_output=True, text=True,
    )


def git_value(key):
    proc = subprocess.run(['git', 'config', '--global', key], capture_output=True, text=True)
    return (proc.stdout or '').strip()


def ensure_git_identity(login):
    name = git_value('user.name')
    email = git_value('user.email')
    if not name:
        subprocess.run(['git', 'config', '--global', 'user.name', login], check=True)
        name = login
    if not email:
        email = '%s@users.noreply.github.com' % login
        subprocess.run(['git', 'config', '--global', 'user.email', email], check=True)
    return name, email


def main():
    parser = argparse.ArgumentParser(description='保存 George-UI-V3 的 GitHub 部署令牌')
    parser.add_argument('--save-env', action='store_true', help='把 GH_TOKEN/GITHUB_TOKEN 写入密钥文件')
    parser.add_argument('--in-skill', action='store_true', help='内置到技能内 .secrets/github.token(默认 gitignore)')
    args = parser.parse_args()
    target = SKILL_TOKEN_PATH if args.in_skill else HOME_TOKEN_PATH

    if args.save_env:
        token = load_env_token()
        if not token:
            raise SystemExit('环境变量 GH_TOKEN / GITHUB_TOKEN 为空。')
    else:
        token = load_env_token()
        if token:
            print('检测到环境变量中的令牌,将校验并保存到密钥文件。')
        else:
            print('请粘贴 GitHub 经典 PAT(No expiration, scopes: repo + workflow)。输入不回显。')
            token = getpass.getpass('Token: ').strip()
    if not token or token.startswith('ghp_') is False and not token.startswith(('github_pat_', 'gho_')):
        if not token:
            raise SystemExit('没有读到令牌。')
        print('提示: 经典 PAT 一般以 ghp_ 开头。仍会向 GitHub 校验。')

    user = api_user(token)
    login = user.get('login') or ''
    if not login:
        raise SystemExit('GitHub 没有返回登录名,令牌不可用。')

    target.parent.mkdir(parents=True, exist_ok=True)
    if args.in_skill:
        ensure_secret_gitignore(target.parent)
    target.write_text(token + '\n', encoding='utf-8')
    restrict(target)
    name, email = ensure_git_identity(login)
    print('已校验 GitHub 用户: %s' % login)
    print('令牌已保存: %s' % target)
    if args.in_skill:
        print('该文件已 gitignore;打包技能时请勿包含 .secrets/,避免令牌外泄。')
    print('git 身份: %s <%s>' % (name, email))
    print('之后在技能目录执行: py scripts/deploy.py <demo目录>')


if __name__ == '__main__':
    main()
