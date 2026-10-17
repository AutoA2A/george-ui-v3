/* 导航与品牌配置 —— 生成新 demo 时主要改这里 + data.js
 * 每个 leaf 的 page 指向 assets/pages/ 下的 html 文件(同目录,写文件名即可)。 */
window.GUI_NAV = {
  brand: 'George Design',   // 默认品牌:不知道具体系统名时统一显示 George / George Design,改成本次系统名即可
  logoText: 'G',
  tenant: 'George',
  theme: '', // 可选 purple / blue / orange
  identities: [
    { id: 'admin', name: '张明', dept: '产品部', role: '管理员' },
    { id: 'editor', name: 'Lucy', dept: '运营部', role: '编辑' },
    { id: 'viewer', name: '访客', dept: '-', role: '只读' }
  ],
  primary: [
    {
      id: 'work', label: '工作台', icon: 'detail',
      children: [
        { id: 'todo-mine', label: '我的待办', page: 'todo.html' },
        { id: 'todo-task', label: '我的任务', page: 'todo.html' }
      ]
    },
    {
      id: 'prod', label: '产品库', icon: 'box',
      children: [
        { id: 'prod-list', label: '产品列表', page: 'list.html' },
        { id: 'prod-cards', label: '产品图册', page: 'cards.html' },
        { id: 'prod-cat', label: '产品分类', page: 'list.html' },
        { id: 'prod-spec', label: '产品规格', page: 'list.html' },
        { id: 'prod-img', label: '产品图片', page: 'cards.html' },
        { id: 'prod-new', label: '新建产品', page: 'form.html' }
      ]
    },
    { id: 'tag', label: '标签管理', icon: 'list', children: [{ id: 'tag-list', label: '标签列表', page: 'list.html' }] },
    { id: 'board', label: '数据看板', icon: 'card', home: 'cards.html' },
    { id: 'order', label: '外采系统', icon: 'detail', children: [{ id: 'order-list', label: '采购订单', page: 'list.html' }] }
    // 注意:不要在这里自定义 id:'sys' 的「系统管理」。shell.js 会自动注入固定三页
    //(角色管理 sys-roles / 用户管理 sys-users / 菜单管理 sys-menus),自定义会覆盖掉真实三页。
  ]
};
