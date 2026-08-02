// utils/ingredientIcons.js
// 食材图标映射（图床方案：jsDelivr 代理 GitHub）
// 图标源文件位于仓库 images/ingredients/ 目录下，通过 jsDelivr CDN 引用
// 使用固定 tag (v1.0.0) 锁定版本，避免 jsDelivr 分支缓存导致的更新不及时问题
//
// 并在小程序后台「开发管理 → 服务器域名 → downloadFile 合法域名」加入：cdn.jsdelivr.net

const CDN_BASE = 'https://cdn.jsdelivr.net/gh/ming-hash/memoryday@v1.0.0/images/ingredients/'

// 图标文件名（BaseName）-> 标准食材名 的映射
// 注意：文件名含中文与括号，URL 拼接时统一 encodeURIComponent
const ICON_FILE_MAP = {
  '上海青': '上海青',
  '全脂牛奶': '全脂牛奶',
  '内酯豆腐': '内酯豆腐',
  '冬瓜': '冬瓜',
  '千张': '千张',
  '南瓜': '南瓜',
  '卷心菜': '卷心菜',
  '圣女果': '圣女果',
  '培根': '培根',
  '基围虾': '基围虾',
  '夏威夷果': '夏威夷果',
  '大头菜': '大头菜',
  '奶酪': '奶酪',
  '娃娃菜': '娃娃菜',
  '小番茄': '小番茄',
  '小白菜': '小白菜',
  '山药': '山药',
  '排骨': '排骨',
  '杏仁': '杏仁',
  '柿子': '柿子',
  '核桃肉': '核桃肉',
  '橄榄油': '橄榄油',
  '毛豆': '毛豆',
  '油豆腐': '油豆腐',
  '洋葱': '洋葱',
  '海带': '海带',
  '火腿': '火腿',
  '熟西兰花': '熟西兰花',
  '牛奶': '牛奶',
  '牛排': '牛排',
  '牛油果': '牛油果',
  '牛肉': '牛肉',
  '猪肉（肥廋）': '猪肉（肥廋）',
  '瓜子': '瓜子',
  '生三文鱼': '生三文鱼',
  '生胡萝卜': '生胡萝卜',
  '生菜': '生菜',
  '番茄': '番茄',
  '白玉米': '白玉米',
  '白糖': '白糖',
  '白菜': '白菜',
  '白萝卜': '白萝卜',
  '紫薯': '紫薯',
  '红枣': '红枣',
  '红薯': '红薯',
  '红豆': '红豆',
  '胡萝卜': '胡萝卜',
  '腐竹': '腐竹',
  '芝麻酱': '芝麻酱',
  '花卷': '花卷',
  '花生': '花生',
  '花菜': '花菜',
  '菜心': '菜心',
  '菠菜': '菠菜',
  '萝卜': '萝卜',
  '蘑菇': '蘑菇',
  '虾仁': '虾仁',
  '蜂蜜': '蜂蜜',
  '西兰花': '西兰花',
  '豆皮': '豆皮',
  '豆腐': '豆腐',
  '豆芽': '豆芽',
  '豌豆': '豌豆',
  '贝贝南瓜': '贝贝南瓜',
  '金针菇': '金针菇',
  '青椒': '青椒',
  '青菜': '青菜',
  '鲑鱼(三文鱼)': '鲑鱼(三文鱼)',
  '鲜玉米': '鲜玉米',
  '鸡肉': '鸡肉',
  '鸡胸肉': '鸡胸肉',
  '鸡蛋': '鸡蛋',
  '鸡蛋白': '鸡蛋白',
  '黄油': '黄油',
  '黄玉米': '黄玉米',
  '黄瓜': '黄瓜',
  '黄豆': '黄豆',
  '黑芝麻': '黑芝麻',
  '黑芝麻糊粉': '黑芝麻糊粉',
  '黑豆': '黑豆'
}

// 别名归一：用户输入的常见写法 -> 图标文件名（BaseName）
const ALIAS_MAP = {
  '三文鱼': '鲑鱼(三文鱼)',
  '鲑鱼': '鲑鱼(三文鱼)',
  '肥猪肉': '猪肉（肥廋）',
  '瘦猪肉': '猪肉（肥廋）',
  '猪肉': '猪肉（肥廋）',
  '小葱': '葱',
  '香葱': '葱',
  '土豆': '土豆',
  '洋芋': '土豆',
  '马铃薯': '土豆',
  '玉米': '鲜玉米',
  '西蓝花': '西兰花',
  '西兰花菜': '西兰花',
  '番茄酱': '番茄',
  '西红柿': '番茄',
  '青菜': '青菜',
  '小青菜': '青菜',
  '大白菜': '白菜',
  '白芝麻': '黑芝麻',
  '虾肉': '虾仁',
  '鲜虾': '虾仁',
  '鸡腿肉': '鸡肉',
  '鸡丁': '鸡肉',
  '豆浆': '黄豆',
  '毛豆仁': '毛豆'
}

// 将食材名归一为图标文件名（BaseName），找不到返回 null
function resolveIconFile(name) {
  if (!name) return null
  const trimmed = String(name).trim()
  if (!trimmed) return null

  // 1. 直接命中文件名
  if (ICON_FILE_MAP[trimmed]) return trimmed

  // 2. 别名命中
  if (ALIAS_MAP[trimmed]) return ALIAS_MAP[trimmed]

  // 3. 包含匹配：如「西红柿鸡蛋」这种复合不会被处理；只做前缀包含
  const matchedByPrefix = Object.keys(ICON_FILE_MAP).find(
    file => trimmed.indexOf(file) > -1 || file.indexOf(trimmed) > -1
  )
  if (matchedByPrefix) return matchedByPrefix

  return null
}

// 获取食材图标的完整 CDN URL；找不到返回空字符串
function getIngredientIcon(name) {
  const file = resolveIconFile(name)
  if (!file) return ''
  return CDN_BASE + encodeURIComponent(file) + '.png'
}

module.exports = {
  CDN_BASE,
  ICON_FILE_MAP,
  ALIAS_MAP,
  resolveIconFile,
  getIngredientIcon
}
