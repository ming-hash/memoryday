// config/env.js

/**
 * 获取应用版本号
 * @returns {string} 应用版本号
 */
const getAppVersion = () => {
  return '1.0.0'
}

/**
 * 获取构建时间
 * @returns {string} 构建时间
 */
const getBuildTime = () => {
  return '2024-01-01 00:00:00'
}

/**
 * 获取环境变量
 * @returns {Object} 环境变量
 */
const getEnvVars = () => {
  // 微信小程序无法使用 process.env，改用其他方式判断环境
  const isDev = isDevelopment()
  
  // 微信云托管配置（生产环境使用）
  const wxCloudConfig = {
    WX_CLOUD: isDev ? 'false' : 'true', // 生产环境启用云托管
    WX_CLOUD_ENV: isDev ? 'dev-test' : 'prod-memoryday', // 云托管环境ID
    WX_CLOUD_APPID: 'wxbe5cb0f551d030e5' // 小程序AppID
  }
  
  return {
    NODE_ENV: isDev ? 'development' : 'production',
    TARO_ENV: 'weapp',
    BUILD_TIME: getBuildTime(),
    VERSION: getAppVersion(),
    ...wxCloudConfig
  }
}

/**
 * 是否是开发环境
 * @returns {boolean} 是否是开发环境
 */
const isDevelopment = () => {
  // 通过微信小程序配置判断开发环境
  try {
    // 在微信开发者工具中，__wxConfig 可能不可用，使用更安全的方式
    if (typeof __wxConfig !== 'undefined' && __wxConfig.envVersion === 'develop') {
      return true
    }
    
    // 如果无法判断，默认返回开发环境（安全起见）
    return true
  } catch (error) {
    console.error('判断开发环境失败:', error)
    return true // 默认开发环境
  }
}

/**
 * 是否是生产环境
 * @returns {boolean} 是否是生产环境
 */
const isProduction = () => {
  // 通过微信小程序配置判断生产环境
  try {
    if (typeof __wxConfig !== 'undefined' && __wxConfig.envVersion === 'release') {
      return true
    }
    
    return false
  } catch (error) {
    console.error('判断生产环境失败:', error)
    return false
  }
}

/**
 * 获取平台信息
 * @returns {string} 平台信息
 */
const getPlatform = () => {
  try {
    const systemInfo = wx.getSystemInfoSync()
    return systemInfo.platform
  } catch (error) {
    return 'unknown'
  }
}

/**
 * 是否是微信小程序环境
 * @returns {boolean} 是否是微信小程序环境
 */
const isWechatMiniProgram = () => {
  return getPlatform() === 'devtools' || getPlatform() === 'ios' || getPlatform() === 'android'
}

module.exports = {
  getAppVersion,
  getBuildTime,
  getEnvVars,
  isDevelopment,
  isProduction,
  getPlatform,
  isWechatMiniProgram
}