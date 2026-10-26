// Public-facing draft grounded in the user-supplied résumé. No personal phone number.
export const ITEMS = [
  {id:'about', n:'01', label:'先认识我', object:'笔记本电脑', kicker:'HELLO, I’M MIRA', title:'Hi, I’m Mira.', sub:'门月淇 · 产品经理、海外创业者、AI 内容创作者'},
  {id:'resume', n:'02', label:'履历与作品', object:'大显示器', kicker:'WORK & EXPLORATION', title:'我是谁', sub:'从复杂业务中的产品建设，到自己的生意与新探索。'},
  {id:'awards', n:'03', label:'项目荣誉', object:'奖杯', kicker:'MILESTONES', title:'一些被认可的努力', sub:'奖杯背后，是具体的人、问题与项目。'},
  {id:'photos', n:'04', label:'我的摄影', object:'相机', kicker:'THROUGH MY LENS', title:'用我的眼睛看世界', sub:'喜欢拍照片，也喜欢为别人留下照片。'},
  {id:'life', n:'05', label:'生活片段', object:'旋转木马', kicker:'LITTLE MOMENTS', title:'把日子转成回忆', sub:'一座亲手 3D 打印的照片旋转木马，留住我们的生活片段。'},
  {id:'travel', n:'06', label:'旅行足迹', object:'钱包', kicker:'PLACES & MEMORIES', title:'带回来一点世界', sub:'从钱包里的纸币，到记忆里的地方。'},
  {id:'cat', n:'07', label:'和猫打招呼', object:'小猫', kicker:'MY LITTLE COMPANION', title:'这里还有一位主人', sub:'已经陪伴我们很久的小猫。'},
  {id:'notebook', n:'08', label:'AI 随手记', object:'手写笔记本', kicker:'LEARNING BY MAKING', title:'AI 随手记', sub:'正在做的事，和还想试试的事。'},
];
export const NOTEBOOK_PAGES = [
 {id:'doing',label:'正在做',title:'正在用 AI 做什么',entries:[{title:'把我的工位，做成一个网站',body:'从梳理桌上的物件，到尝试不同布局、制作模型和打通交互，我正在用 AI 一点点搭起这个属于自己的小空间。',note:'眼前的这张书桌，就是正在进行中的一个尝试。'}],blank:'新的实践、遇到的问题和小发现，慢慢记在这里。'},
 {id:'ideas',label:'想试试',title:'想用 AI 做什么',entries:[],blank:'这一页先留白，等下一个想法。',prompts:['想解决的一个小问题','想做出来的一个小作品','想试试的一种新方法']},
];
export const EXPERIENCE = [
  {id:'workfx', group:'venture', date:'2025.12 — 2026.10', title:'WorkfxAI', role:'Co-founder · 悉尼', summary:'围绕海外品牌在 AI 问答场景中的可见度与营销效果，建设订阅型 AI 产品，交付企业级 AI 增长方案。', metrics:[['2,000+','累计注册用户'],['100+','付费用户']], points:['设计并搭建 Multi-Agent 系统，串联意图分析、内容生成与分发、效果归因。','面向有出海需求的国内企业及澳大利亚品牌，深入业务场景，结合知识库、定制 Agent、Workflow 与营销服务交付方案。'], link:{text:'WorkfxAI 官网 ↗',url:'https://www.workfx.ai/'}},
  {id:'independent',group:'venture',date:'2023.12 — 2025.10',title:'跨境电商与知识付费',role:'个人创业 · 悉尼',summary:'从选品、供应链和履约到内容与商业化，亲自跑通一门生意。',metrics:[['1,000+','累计付费学员'],['3','电商平台实践']],points:['经营 TikTok Shop 美区本土店、Temu 全托管与 Etsy 店铺，覆盖搭建、选品、达人合作、内容和订单履约。','参与品牌东南亚出海营销，统筹短视频、本土直播与广告投放。','将 TikTok Shop、Temu 的实操经验整理为课程，并参与线下授课及出海主题分享。']},
  {id:'bytedance',group:'career',date:'2019.10 — 2023.10',title:'字节跳动 · TikTok',role:'Trust & Safety 产品经理 · 北京',summary:'从数据资产与人审策略中台，到海外审核模式升级，让复杂系统更有效地运转。',metrics:[['20%','人审审出产能提升'],['7.28%','平均处理时长下降']],points:['带领 5 人团队，推进“内容池＋智能审核”架构，统筹排队调度、智能策略与运营工具。','建设国内与海外人审策略中台，支持 TikTok、抖音等产品的 20 余个核心场景接入。','梳理审核平台数据资产、指标与生产链路，将核心小时级表产出延时由 3 小时缩短至 1.5 小时。','架构升级项目获公司级优秀项目奖；具体奖项名称后续补充。']},
  {id:'qunar',group:'career',date:'2017.07 — 2019.10',title:'去哪儿网',role:'机票事业部产品经理 · 北京',summary:'围绕用户增长、国际机票售后与辅营收益，持续改进服务体验和业务结果。',metrics:[['10.8%','辅营单票收益提升'],['0 → 1','小驼里程积分体系']],points:['国际辅营：通过调价实验和转化链路优化，搭售比例由 4.9% 提升至 6.0%。','国际售后：优化自助退改流程，退票平均处理时长由 81.9 小时降至 51.7 小时，改签由 34.3 小时降至 22.1 小时。','从零搭建“小驼里程”，覆盖国内及国际机票、火车票业务，以积分促进用户复购。']},
];
export const LIFE = [
  {src:'assets/carousel-reference.jpg',title:'我的照片旋转木马',caption:'Mira 提供的实物参考照片。珍珠白的 3D 打印照片架，装着生活里的小片段。'},
  {src:'assets/desk-reference.jpg',title:'真实的窗边工位',caption:'Mira 提供的真实桌面参考。这一版网站从这张书桌出发。'},
];
export const AWARDS = [
  {title:'内容审核架构升级',org:'字节跳动',note:'简历记载：公司级优秀项目奖。正式名称、获奖时间与证书待补充。',experience:'bytedance'},
  {title:'国际退改服务质量提升',org:'去哪儿网',note:'简历记载：国际退款、改签服务质量提升项目获部门项目奖。具体奖项待补充。',experience:'qunar'},
];
export const PLACES = [
  {id:'cn',name:'中国',tag:'北京 · 大连',currency:'CNY',title:'从学习到职业起点',body:'在大连理工大学学习软件工程，之后在北京先后进入去哪儿与字节跳动，做用户增长、机票业务、内容安全与平台产品。',status:'简历中确认的学习与工作坐标'},
  {id:'au',name:'澳大利亚',tag:'悉尼',currency:'AUD',title:'开始自己的探索',body:'以悉尼为海外创业的起点，尝试跨境电商、内容与知识付费，之后参与 WorkfxAI，探索 AI 产品与企业服务。',status:'简历中确认的创业坐标'},
];
