# 自动部署到 GitHub Pages

每个 demo 在本地自测通过后，必须用 `scripts/deploy.py` 发布成公开静态站，并把本地目录和线上地址一起交给用户。地址形态与 `https://agentopen.github.io/yundesign-web` 相同：`https://<GitHub登录名>.github.io/<仓库名>/`。每个 demo 一个 Public 仓库。

官方说明：<https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site>

## 一次性：经典 PAT（长期有效）

1. 打开 <https://github.com/settings/tokens> ，选 **Generate new token (classic)**。
2. Note 写 `george-ui-v3 deploy`。Expiration 选 **No expiration**（永不过期）。
3. 勾选 scopes：**`repo`**、**`workflow`**。`repo` 覆盖建公开仓库、推送代码、启用 Pages。
4. 生成后只复制一次。不要贴进聊天、技能文件、demo 或 git 提交。
5. 保存到本机（技能目录之外）：

```
py scripts/github_setup.py
```

按提示粘贴令牌。脚本会 `GET /user` 校验，写入 `%USERPROFILE%\.george-ui\github.token`（单行），并用 icacls 收成仅当前用户可读写。也可先设环境变量 `GH_TOKEN` 再执行 `py scripts/github_setup.py --save-env`。

读取顺序：环境变量 `GH_TOKEN` 或 `GITHUB_TOKEN` → 技能内 `.secrets/github.token` → `%USERPROFILE%\.george-ui\github.token`。部署脚本自动 `GET /user` 得到登录名，不用手填用户名。

## 创建经典 PAT 教程（图文步骤）

1. 浏览器登录 GitHub，访问 <https://github.com/settings/tokens>（也可从右上角头像 → Settings → Developer settings → Personal access tokens → Tokens (classic)）。
2. 点 **Generate new token** → **Generate new token (classic)**。可能要求输入账号密码/2FA 验证。
3. **Note**：填 `george-ui-v3 deploy`，方便日后识别。
4. **Expiration**：下拉选 **No expiration**（永不过期）。GitHub 会弹风险提示，确认即可。
5. **Select scopes**：勾选
   - `repo`（整组勾上，用于建公开仓库、推送、开 Pages）
   - `workflow`（为将来可能用到的 Actions 预留）
   其余不用勾。
6. 拉到底点 **Generate token**。
7. 页面只显示一次令牌（形如 `ghp_` 开头的一长串）。**立刻复制**，离开页面就看不到了。
8. 不要把它贴进聊天、代码或截图。按下面"内置到技能"或存到用户目录。

## 内置到技能（让技能自带令牌、一键部署）

想要"技能自带 key、换台机器/交给别的 AI 也能直接自动部署"，就把令牌放进技能内：

```
py scripts/github_setup.py --in-skill
```

按提示粘贴令牌（输入不回显），它会写入 `.secrets/github.token` 并校验账号。之后任何 demo 只需 `py scripts/deploy.py <demo目录>` 即自动部署，无需每次配置。

安全须知（内置令牌务必知道）：

- `.secrets/` 已被 `.gitignore`，正常 `git` 操作不会提交它。
- **打包/分享技能 zip 时必须排除 `.secrets/` 目录**。经典 PAT 永不过期且有 `repo` 权限，谁拿到它就能完全控制你的所有仓库。
- 不要把令牌写进 `SKILL.md`、任何 `.py`/`.md`、demo 或提交。只放在 `.secrets/github.token`。
- 怀疑泄露：到 <https://github.com/settings/tokens> 点该令牌 **Delete/Revoke**，再重建并重新 `--in-skill`。

> 更安全的替代：不加 `--in-skill`，令牌存到技能目录之外的 `%USERPROFILE%\.george-ui\github.token`，这样即使误把技能打包也不会带出令牌。按你的需求二选一。

## 安全红线

- 令牌只存在本机密钥文件或环境变量。禁止写入 `SKILL.md`、脚本、demo、`deploy-report.json`、提交信息、日志。
- 推送使用一次性地址 `https://x-access-token:<token>@github.com/<owner>/<repo>.git`，推完立刻确认 `origin` 仍是不含令牌的 `https://github.com/<owner>/<repo>.git`。不把令牌写进 demo 的 git config，也不启用会记住该地址的 credential helper。
- 永不过期令牌泄露后可长期建库、改库。文件已限权；怀疑泄露就到 GitHub 撤销并换新令牌。
- 仓库是 **Public**。只放虚构演示数据。

## 每次发布（硬性）

在技能目录执行（路径含空格要加引号）：

```
py scripts/deploy.py <demo目录>
py scripts/deploy.py <demo目录> --repo my-demo-name
```

脚本顺序固定，失败即停，不报告成功：

1. 跑 `preflight.py`：`index.html`、`.nojekyll`、相对路径、无远程 CDN、`delivery-plan.json` 结构合法。不过就中止。
2. 读令牌，`GET /user` 取 owner。
3. 仓库名来自 `--repo`，否则用目录名（小写连字符）。中文目录名会变成 `george-demo-` + 短哈希。
4. 仓库不存在则 `POST /user/repos`（`private: false`，不自动初始化）。已存在且属于同一 owner 则复用。
5. 在 **demo 目录**（不是技能目录）`git init -b main`、提交、推送到 `main`。
6. `POST /repos/{owner}/{repo}/pages`，源为 `main` 的 `/`。已启用则更新，不重复报错。
7. 轮询 `https://{owner}.github.io/{repo}/` 直到 HTTP 200，并再请求 `assets/css/tokens.css`。超时约 150 秒仍失败则退出码 1，并附上 Pages 状态。首次构建常见 1–2 分钟。
8. 写 `<demo>/deploy-report.json`（owner、repo、url、commit、校验结果、时间，**不含令牌**），打印本地路径和公开 URL。

同一仓库再次执行是更新：有新提交就推送，Pages 会重新构建。

## 为什么这样能在子路径打开

项目站挂在 `/<仓库名>/` 下，不是域名根。因此：

- 入口、CSS、JS、页面跳转全部用相对路径。`/assets/...` 或 `file:///D:/...` 在线上会 404。
- 根目录的空文件 `.nojekyll` 关掉 Jekyll，`assets/` 会原样发布。脚手架已带这个文件。
- `index.html` 用相对跳转到 `assets/pages/` 下的业务页，在 `file://` 和 `https://<user>.github.io/<repo>/` 都能进。

## 排错

| 现象 | 处理 |
|---|---|
| 提示未找到令牌 | 先跑 `github_setup.py`，或设置 `GH_TOKEN` |
| `GET /user` 401 | 令牌无效或已撤销，重新生成经典 PAT |
| 建库 403 | 令牌缺 `repo` scope，或账号无权建公开仓库 |
| 仓库名已属于别人 | 换 `--repo` |
| 推送被拒绝 | 确认令牌有 `repo`，且没有把含令牌的地址写进 `origin` |
| 线上一直 404 | 等构建；看报错里的 Pages 状态。私有仓库的免费账号不能开 Pages，本流程只建 Public |
| 页面能开但 CSS/JS 404 | 几乎都是绝对路径。改回相对路径后重新 `deploy.py` |
| `preflight` 失败 | 先补 `.nojekyll`、`delivery-plan.json` 和缺失文件，不要带错部署 |
