# 可执行交付契约(2.0.0,纯静态)

## 先建立"需求→代码"的对应
用户只说要演示什么。模糊、歧义、缺参数时先按 [requirements-guide.md](requirements-guide.md) 的**最高优先级规则**:AI 先补齐建议方案(页面、字段、默认值、假设)再请用户确认。确认后:
- `business-plan.md` 写原始需求、角色、本次范围、关键假设(哪些字段/规则是演示默认值)。
- `delivery-plan.json` 写机器可检查的对应关系。列表、卡片、详情、表单、抽屉、审批流都要登记;抽屉/审批面板作为所属页的 feature;不要为凑数量虚构无关页面。

`delivery-plan.json` 结构(可参照 `assets/static-kit` 生成后自建):
- `pages`:`id`(与导航 `data-page`/leaf 对应)、`contentSelector`(定位业务内容,不定位公共菜单)、文件路径。
- `features`:唯一 `id`、`pageId`、`description`、`implementation`(实际文件数组)、`steps`。
- `steps`:支持 `click` / `fill` / `expectText` / `expectCount` / `expectValue`。每个 feature 至少一个结果断言。
- 操作验收要验证**操作后的数据变化**(保存后列表值、详情同 ID、取消恢复原值、库存/流水变化),不能只断言标题或 toast。页内每个可用按钮都应有对应测试。

## 生成顺序(纯静态多页)
1. `py scripts/scaffold.py <目录>` 复制 `assets/static-kit`。
2. 先改 `assets/js/nav-config.js`(品牌+导航)与 `assets/js/data.js`(演示数据)。
3. 一次做完一页:组装 `assets/pages/*.html` → 本地打开核对 → 再做下一页。
4. 复用 `components.css` 的类与 `shell.js` 的能力(`Shell.openDrawer` 右侧抽屉、`Shell.openApproval` 审批流宽面板、`Shell.toast`)。**不手写新的通用控件/面板,不引入 Ant Design 蓝色主题,不加联网 CDN。**
5. `index.html` 及各页引用的每个 JS/CSS 必须是真实非空文件,全部相对路径;不交付省略号、TODO、空函数。
6. 无数据时显示带解释和可用动作的业务空状态,不以空状态掩盖未实现。

## 长任务、中断与跨 AI 兼容
按页连续增量完成,保留计划与完成状态。上下文不足时写 `checkpoint.md`(已生成文件、未完成项、最后失败信息、下一步),从检查结果恢复;不得删除未完成页或谎称全部完成。只能写文件的模型:先完整输出文件再给运行指导,不声称已打包或运行。

## 验证
在技能目录执行(路径含空格加引号):
```
python scripts/preflight.py <demo目录>
```
`preflight.py` 只用标准库,查:`.nojekyll`、入口依赖是否缺失/空文件、路径大小写/绝对路径、`delivery-plan.json` 结构、每个 feature 是否有关联实现与可观察断言;它不证明业务逻辑正确。

浏览器走查(必做,真实点击):首次打开 → 每个菜单与二级导航展开/收起 → 列表翻页与筛选 → 详情第二条记录 → 新增必填/成功 → 编辑保存/取消 → 抽屉/审批面板滚动与遮罩 → 窄窗口降级。失败必须改代码再跑,不改断言迁就错误结果。

## 完成标准
完整文件与依赖 + 所有需求对应项实现 + `preflight` 通过 + 浏览器走查通过。报告区分"通过/失败/未执行"并记录视口。不保证任意 AI 一次做到生产 1:1;本契约用可运行起点与门禁减少空白交付。
