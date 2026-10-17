/* 演示数据(全部虚构,仅用于原型演示) */
(function () {
  var raw = [
    { id: 'P001', seq: 167195, uid: '1120990000000021', code: 'XF-5721', name: '岩板·卡拉拉白 750x1500', en: 'Carrara White Slab', parent: 'GC-3147', cat: '岩板', brand: '乔治建材', spec: '750×1500mm', price: 268.0, stock: 1240, status: '在售', urgency: '普通', region: '华东', updated: '2026-10-10', supplier: '意利佳', desc: '通体大理石纹岩板,适用于墙面与台面,防污耐磨。' },
    { id: 'P002', seq: 167194, uid: '1120990000000020', code: 'XF-5722', name: '通体砖·深空灰 600x600', en: 'Deep Grey Tile', parent: 'ZD-1214', cat: '瓷砖', brand: '乔治建材', spec: '600×600mm', price: 89.5, stock: 320, status: '在售', urgency: '紧急', region: '华南', updated: '2026-10-09', supplier: '东鹏', desc: '哑光防滑通体砖,适合商业空间地面铺贴。' },
    { id: 'P003', seq: 167192, uid: '1120990000000019', code: 'XF-5730', name: '实木复合地板·橡木原色', en: 'Oak Engineered Floor', parent: 'PE-3588', cat: '地板', brand: 'Nature', spec: '910×125mm', price: 420.0, stock: 56, status: '预售', urgency: '加急', region: '华北', updated: '2026-10-08', supplier: '大自然', desc: '多层实木结构,环保 E0 级,适合地暖环境。' },
    { id: 'P004', seq: 167188, uid: '1120990000000018', code: 'XF-5741', name: '墙板·胡桃木纹 2440x1220', en: 'Walnut Wall Panel', parent: 'FK-3889', cat: '墙板', brand: '乔治建材', spec: '2440×1220mm', price: 356.0, stock: 0, status: '缺货', urgency: '普通', region: '西南', updated: '2026-10-05', supplier: '兔宝宝', desc: '竹木纤维集成墙板,免漆安装快。' },
    { id: 'P005', seq: 167186, uid: '1120990000000017', code: 'XF-5755', name: '台面石英石·雪花白', en: 'Snow White Quartz', parent: 'DYX-2585', cat: '石材', brand: 'Caesar', spec: '3200×1600mm', price: 880.0, stock: 18, status: '在售', urgency: '普通', region: '华东', updated: '2026-10-03', supplier: '赛凯隆', desc: '高硬度石英石台面,耐高温抗渗透。' },
    { id: 'P006', seq: 167183, uid: '1120990000000016', code: 'XF-5760', name: '微水泥·灰调套装', en: 'Microcement Grey Set', parent: 'XHX-1454', cat: '涂料', brand: 'Topciment', spec: '20kg/套', price: 1260.0, stock: 44, status: '在售', urgency: '普通', region: '华南', updated: '2026-10-01', supplier: '拓新', desc: '意大利微水泥,无缝连续面层,工业风首选。' },
    { id: 'P007', seq: 167179, uid: '1120990000000015', code: 'XF-5768', name: '岩板·安德拉灰 900x1800', en: 'Andra Grey Slab', parent: 'PVC-5458', cat: '岩板', brand: '乔治建材', spec: '900×1800mm', price: 398.0, stock: 210, status: '在售', urgency: '普通', region: '华中', updated: '2026-09-28', supplier: '意利佳', desc: '大规格岩板,背景墙整体性强。' },
    { id: 'P008', seq: 167176, uid: '1120990000000014', code: 'XF-5779', name: '仿古砖·砖红 300x600', en: 'Vintage Red Brick', parent: 'DN25wt', cat: '瓷砖', brand: '马可波罗', spec: '300×600mm', price: 46.0, stock: 980, status: '在售', urgency: '普通', region: '华北', updated: '2026-09-25', supplier: '马可波罗', desc: '复古砖面,适合阳台与庭院。' },
    { id: 'P009', seq: 167170, uid: '1120990000000013', code: 'XF-5790', name: 'SPC 锁扣地板·浅灰', en: 'SPC Click Floor', parent: 'SPC-220', cat: '地板', brand: 'Nature', spec: '1220×180mm', price: 158.0, stock: 134, status: '预售', urgency: '紧急', region: '华东', updated: '2026-09-22', supplier: '大自然', desc: '石塑锁扣地板,防水免胶,适合出租房快装。' },
    { id: 'P010', seq: 167165, uid: '1120990000000012', code: 'XF-5801', name: '艺术玻璃·长虹纹', en: 'Changhong Glass', parent: 'XY-884', cat: '玻璃', brand: '信义', spec: '2440×1220mm', price: 230.0, stock: 67, status: '在售', urgency: '普通', region: '华南', updated: '2026-09-20', supplier: '信义玻璃', desc: '长虹压花玻璃,隔断与柜门通透不透视。' },
    { id: 'P011', seq: 167158, uid: '1120990000000011', code: 'XF-5812', name: '不锈钢收边条·钛金', en: 'Titanium Trim', parent: 'FS-050', cat: '辅材', brand: '通用', spec: '2.4m/根', price: 28.0, stock: 2300, status: '在售', urgency: '普通', region: '全国', updated: '2026-09-18', supplier: '佛山五金', desc: '岩板与墙板收口专用,钛金拉丝面。' },
    { id: 'P012', seq: 167150, uid: '1120990000000010', code: 'XF-5820', name: '岩板胶·专用 AB', en: 'Slab Adhesive AB', parent: 'HG-15', cat: '辅材', brand: '汉高', spec: '1.5kg/组', price: 55.0, stock: 760, status: '在售', urgency: '普通', region: '全国', updated: '2026-09-15', supplier: '汉高', desc: '岩板背胶与收口 AB 胶,快干高强度。' }
  ];
  // 缩略图占位(内联 SVG data URI,离线可用,无需外链图片)
  var colors = ['#dfe9d2', '#dde6f5', '#f5e7d6', '#e7e3f5', '#eef6e0', '#eceef0'];
  raw.forEach(function (p, i) {
    var c = colors[i % colors.length];
    p.thumb = 'data:image/svg+xml,' + encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" width="96" height="68"><rect width="96" height="68" fill="' + c + '"/><text x="48" y="38" font-size="12" fill="#8a8a8a" text-anchor="middle" font-family="sans-serif">' + p.cat + '</text></svg>');
  });
  /* ---------------- 待办 / 审批流 演示数据 ---------------- */
  // 每条待办含:基础信息 + 分组详情(sections)+ 审批节点(nodes,流程记录时间线)。
  // nodes[].status: done=已通过 / skipped=已跳过 / current=待我审批 / pending=未开始
  var todos = [
    {
      id: 'DO20260814000001', seq: 16402, title: '补充/修正信息(协调员/负责人)',
      bizType: '家装', source: '手动录入', status: '进行中', urgency: '正常',
      applicant: '陈潮汉', dept: '设计部', submitTime: '2026-08-14 18:25', currentNode: '平面设计师上传完成任务',
      sections: [
        { title: '基础信息', cols: 4, items: [
          ['文本', 'DO20260814000001'], ['来源', '手动录入'], ['来源类型', '手动录入'], ['状态', '进行中']
        ] },
        { title: '项目信息', cols: 3, items: [
          ['期望完成时间', '2026-09-01'], ['紧急程度', '正常'], ['设计面积(m²)', ''],
          ['风格备注/设计方向', ''], ['项目类型', '家装'], ['客户等级', 'E类客户']
        ] },
        { title: '详细信息 · 项目', cols: 3, items: [
          ['项目名称', ''], ['项目详细地址', ''], ['CRM项目', ''],
          ['回款', ''], ['负责部门', '1268'], ['项目负责人', '加磊'],
          ['设计区域附件', ''], ['期望完成时间', '2026-09-01'], ['设计面积(m²)', ''],
          ['水单截图', ''], ['建筑图纸', ''], ['紧急度', '正常']
        ] },
        { title: '客户与预算', cols: 3, items: [
          ['客户名称', ''], ['客户等级', 'E类客户'], ['最低预算', ''],
          ['最高预算', ''], ['设计费预算', ''], ['最终抵扣方案', ''],
          ['风格备注/设计方向', '', true]
        ] },
        { title: '对接与协作', cols: 3, items: [
          ['PM', ''], ['是否需要协编设计', '需要'], ['协调员', ''],
          ['平面设计师', ''], ['3D设计师', '']
        ] }
      ],
      nodes: [
        { name: '①平面设计师上传完成任务', time: '2026-09-17 14:42', actor: '朱大威', role: '平面设计师', duration: '25天21小时27分49秒', status: 'current', note: '等待平面方案上传与确认。', action: true },
        { name: '请接受平面设计师邀请', time: '2026-08-14 18:25', actor: '罗元霆', role: '平面设计师', duration: '0秒', status: 'skipped' },
        { name: '②分配平面设计师(助理+部门负责人)', time: '2026-08-14 18:25', actor: '陈潮汉', role: '部门负责人', duration: '0秒', status: 'skipped' },
        { name: '①协调员:需求收集 & 文档', time: '2026-08-14 18:25', actor: '陈潮汉', role: '协调员', duration: '43秒', status: 'done' },
        { name: 'CRM 立项改状态(有据跟踪/无需跟踪)', time: '2026-08-14 16:24', actor: '陈潮汉', role: '协调员', duration: '45分46秒', status: 'done' },
        { name: '请接受协调员邀请', time: '2026-08-14 16:20', actor: '陈潮汉', role: '协调员', duration: '12秒', status: 'done' }
      ]
    },
    {
      id: 'DO20260903000017', seq: 16411, title: '采购申请审批(岩板补货)',
      bizType: '采购', source: '采购系统', status: '待审批', urgency: '紧急',
      applicant: 'Lucy', dept: '运营部', submitTime: '2026-09-03 09:40', currentNode: '采购经理审批',
      sections: [
        { title: '基础信息', cols: 4, items: [
          ['单据编号', 'DO20260903000017'], ['来源', '采购系统'], ['单据类型', '采购申请'], ['状态', '待审批']
        ] },
        { title: '采购信息', cols: 3, items: [
          ['物料名称', '岩板·卡拉拉白 750x1500'], ['申请数量', '400 片'], ['预计单价(元)', '248.0'],
          ['预计金额(元)', '99,200.0'], ['需求日期', '2026-09-20'], ['供应商', '意利佳']
        ] },
        { title: '申请说明', cols: 1, items: [
          ['申请原因', '华东仓库存低于安全阈值,大客户样板间订单需提前备货。', true]
        ] }
      ],
      nodes: [
        { name: '采购经理审批', time: '2026-09-03 10:02', actor: '张明', role: '采购经理', duration: '待处理', status: 'current', note: '核对数量与预算后审批。', action: true },
        { name: '运营主管复核', time: '2026-09-03 09:55', actor: '周琳', role: '运营主管', duration: '15分', status: 'done' },
        { name: '发起采购申请', time: '2026-09-03 09:40', actor: 'Lucy', role: '运营专员', duration: '-', status: 'done' }
      ]
    },
    {
      id: 'DO20260910000042', seq: 16420, title: '报价单审批(E类客户整装)',
      bizType: '销售', source: 'CRM', status: '待审批', urgency: '加急',
      applicant: '王恒', dept: '销售部', submitTime: '2026-09-10 15:12', currentNode: '销售总监审批',
      sections: [
        { title: '基础信息', cols: 4, items: [
          ['单据编号', 'DO20260910000042'], ['来源', 'CRM'], ['单据类型', '报价审批'], ['状态', '待审批']
        ] },
        { title: '报价信息', cols: 3, items: [
          ['客户名称', '敬城·翰林苑样板间'], ['客户等级', 'E类客户'], ['报价总额(元)', '186,400.0'],
          ['折扣率', '92%'], ['有效期', '2026-09-30'], ['负责销售', '王恒']
        ] }
      ],
      nodes: [
        { name: '销售总监审批', time: '2026-09-10 15:30', actor: '李强', role: '销售总监', duration: '待处理', status: 'current', note: '折扣超出常规,需总监复核。', action: true },
        { name: '区域经理初审', time: '2026-09-10 15:20', actor: '赵敏', role: '区域经理', duration: '8分', status: 'done' },
        { name: '发起报价单', time: '2026-09-10 15:12', actor: '王恒', role: '销售专员', duration: '-', status: 'done' }
      ]
    }
  ];

  window.DEMO_DATA = {
    products: raw,
    todos: todos,
    statusTag: { '在售': 'success', '预售': 'info', '缺货': 'error', '停售': 'neutral', '进行中': 'info', '待审批': 'warning', '已通过': 'success', '已驳回': 'error' },
    urgencyTag: { '普通': 'neutral', '正常': 'neutral', '紧急': 'error', '加急': 'warning' }
  };
})();
