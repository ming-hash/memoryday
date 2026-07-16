// config/config.js

// 开发环境配置
const devConfig = {
  baseUrl: 'http://localhost:8000/api',
  debug: true,
  uploadUrl: 'http://localhost:8000/api/upload',
  imageBaseUrl: 'http://localhost:8000/media'
}

// 生产环境配置
const prodConfig = {
  baseUrl: 'https://api.yourdomain.com/api',
  debug: false,
  uploadUrl: 'https://api.yourdomain.com/api/upload',
  imageBaseUrl: 'https://api.yourdomain.com/media'
}

// 根据环境选择配置
console.log('CODEBUDDY_DEBUG config.js: 尝试获取环境变量')
console.log('CODEBUDDY_DEBUG config.js: process对象是否存在 =', typeof process !== 'undefined')

// 修复：微信小程序无法使用process.env，改用env.js中的方法
const { isDevelopment } = require('./env')
const config = isDevelopment() ? devConfig : prodConfig
console.log('CODEBUDDY_DEBUG config.js: isDevelopment() =', isDevelopment())
console.log('CODEBUDDY_DEBUG config.js: 最终选择的配置 =', config)

// 常量配置
const constants = {
  // 菜品相关
  DISH_CATEGORIES: [
    { value: 'breakfast', label: '早餐', icon: '🍳' },
    { value: 'lunch', label: '午餐', icon: '🍲' },
    { value: 'dinner', label: '晚餐', icon: '🍽️' },
    { value: 'snack', label: '小吃', icon: '🍕' },
    { value: 'dessert', label: '甜点', icon: '🍰' }
  ],

  // 烹饪时间
  COOKING_TIMES: [
    { value: 'quick', label: '快速（15分钟内）', max: 15 },
    { value: 'medium', label: '中等（15-30分钟）', min: 15, max: 30 },
    { value: 'long', label: '较慢（30-60分钟）', min: 30, max: 60 },
    { value: 'very_long', label: '慢炖（60分钟以上）', min: 60 }
  ],

  // 难度级别
  DIFFICULTY_LEVELS: [
    { value: 'easy', label: '简单', level: 1 },
    { value: 'medium', label: '中等', level: 2 },
    { value: 'hard', label: '困难', level: 3 },
    { value: 'expert', label: '专家', level: 4 }
  ],

  // 菜系类型
  CUISINE_TYPES: [
    { value: 'chinese', label: '中餐' },
    { value: 'western', label: '西餐' },
    { value: 'japanese', label: '日料' },
    { value: 'korean', label: '韩餐' },
    { value: 'thai', label: '泰餐' },
    { value: 'indian', label: '印度菜' },
    { value: 'mexican', label: '墨西哥菜' },
    { value: 'italian', label: '意大利菜' },
    { value: 'french', label: '法国菜' },
    { value: 'other', label: '其他' }
  ],

  // 常用食材
  COMMON_INGREDIENTS: [
    '米饭', '面条', '鸡蛋', '鸡肉', '猪肉', '牛肉', '鱼肉', '虾',
    '蔬菜', '土豆', '番茄', '洋葱', '大蒜', '青椒', '胡萝卜', '豆腐',
    '酱油', '醋', '盐', '糖', '油', '辣椒', '姜', '葱'
  ],

  // 页面路由
  ROUTES: {
    HOME: '/pages/index/index',
    DISH_DETAIL: '/pages/dish-detail/dish-detail',
    DISH_EDIT: '/pages/dish-edit/dish-edit',
    STATISTICS: '/pages/statistics/statistics',
    USER: '/pages/user/user',
    SETTINGS: '/pages/settings/settings'
  },

  // 存储键名
  STORAGE_KEYS: {
    TOKEN: 'token',
    USER_INFO: 'user_info',
    DISH_LIST: 'dish_list',
    SEARCH_HISTORY: 'search_history',
    SETTINGS: 'app_settings'
  },

  // API端点
  API_ENDPOINTS: {
    // 认证相关
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH_TOKEN: '/auth/refresh',

    // 用户相关
    USER_PROFILE: '/user/profile',
    USER_UPDATE: '/user/update',
    USER_STATS: '/user/stats',

    // 菜品相关
    DISH_LIST: '/dishes',
    DISH_DETAIL: '/dishes/:id',
    DISH_CREATE: '/dishes/create',
    DISH_UPDATE: '/dishes/:id/update',
    DISH_DELETE: '/dishes/:id/delete',
    DISH_RANDOM: '/dishes/random',
    DISH_SEARCH: '/dishes/search',

    // 标签相关
    TAGS: '/tags',
    TAGS_CREATE: '/tags/create',
    TAGS_SEARCH: '/tags/search',

    // 统计相关
    STATS_OVERVIEW: '/stats/overview',
    STATS_WEEKLY: '/stats/weekly',
    STATS_MONTHLY: '/stats/monthly',
    STATS_DISTRIBUTION: '/stats/distribution',

    // 上传相关
    UPLOAD_IMAGE: '/upload/image',
    UPLOAD_FILE: '/upload/file'
  },

  // 错误代码
  ERROR_CODES: {
    SUCCESS: 0,
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    INTERNAL_ERROR: 500,
    VALIDATION_ERROR: 422,
    NETWORK_ERROR: -1
  },

  // 分页设置
  PAGINATION: {
    DEFAULT_PAGE: 1,
    DEFAULT_PAGE_SIZE: 20,
    MAX_PAGE_SIZE: 100
  },

  // 上传限制
  UPLOAD_LIMITS: {
    MAX_IMAGE_SIZE: 5 * 1024 * 1024, // 5MB
    MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
    ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    ALLOWED_FILE_TYPES: ['image/*', 'application/pdf', 'text/plain']
  },

  // 缓存时间（毫秒）
  CACHE_TIMES: {
    SHORT: 5 * 60 * 1000, // 5分钟
    MEDIUM: 30 * 60 * 1000, // 30分钟
    LONG: 2 * 60 * 60 * 1000, // 2小时
    VERY_LONG: 24 * 60 * 60 * 1000 // 24小时
  }
}

module.exports = {
  ...config,
  ...constants
}