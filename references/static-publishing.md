# 静态HTML与GitHub Pages

交付目录的index.html可打开，所有运行资源随包提供：HTML/CSS/JS、图片、字体、本地组件依赖。默认不需要Node构建、不需要后端或联网CDN。业务数据用本地模拟数据；明示刷新是否恢复。源码不能依赖开发者电脑绝对路径、127.0.0.1、根路径/assets或临时Figma资源链接。

路径区分大小写，使用相对路径。页面切换使用当前HTML内状态或hash；不要采用需要服务器rewrite的history路径。CSS的url相对CSS文件位置，JS资源按自身位置解析。中文文件名可用但发布资源建议简单稳定名称。

发布源根目录（index.html旁）必须包含空文件.nojekyll，避免GitHub默认Jekyll处理影响assets等资源。此包脚手架自动生成。官方说明：https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site

给业务用户的发布方法：把完整demo目录内容放进要发布的仓库根目录或docs目录；仓库Settings → Pages选择从分支发布，选择相应分支及目录并保存。之后用GitHub给出的地址查看。只准备发布文件不等于已经替用户公开发布；用户要求实际发布时再按指定仓库执行。

本地验收同时测试file://双击打开与HTTP子目录（如/project-demo/）访问。在HTTP模式下检查404、大小写、相对路径、菜单切换、打开抽屉/审批面板及刷新。可用 `py -m http.server` 起一个本地静态服务做HTTP预演；它不连接或更改GitHub账号。

共享演示仅放虚构业务数据。静态demo的角色切换用于演示，不是服务器权限控制。

## 自动部署（默认，硬性）

自测通过后不要停在“目录已备好、请用户自己发布”。在技能目录执行：

```
py scripts/deploy.py <demo目录>
```

脚本使用本机经典 PAT（`GH_TOKEN` 或 `%USERPROFILE%\.george-ui\github.token`），创建或更新一个 Public 仓库，推送 `main`，打开 GitHub Pages，并轮询到公开地址返回 200。成功后同时保留本地目录，并给出 `https://<登录名>.github.io/<仓库名>/`。

首次使用先 `py scripts/github_setup.py` 保存令牌。令牌不进入 demo。步骤、安全要求和排错见 [github-deploy.md](github-deploy.md)。上面的手动 Settings → Pages 只作为脚本不可用时的备用，不能代替自动部署。
