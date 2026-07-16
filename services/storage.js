// services/storage.js
const { STORAGE_KEYS } = require('../config/config')

/**
 * 本地存储服务
 */
class StorageService {
  /**
   * 设置存储数据
   * @param {string} key 键名
   * @param {any} data 数据
   * @param {number} expire 过期时间（毫秒）
   */
  static set(key, data, expire = null) {
    try {
      const storageData = {
        data: data,
        expire: expire ? Date.now() + expire : null,
        timestamp: Date.now()
      }
      wx.setStorageSync(key, storageData)
      return true
    } catch (error) {
      console.error('Storage set error:', error)
      return false
    }
  }

  /**
   * 获取存储数据
   * @param {string} key 键名
   * @returns {any} 数据
   */
  static get(key) {
    try {
      const storageData = wx.getStorageSync(key)
      if (!storageData) return null

      // 检查是否过期
      if (storageData.expire && Date.now() > storageData.expire) {
        this.remove(key)
        return null
      }

      return storageData.data
    } catch (error) {
      console.error('Storage get error:', error)
      return null
    }
  }

  /**
   * 移除存储数据
   * @param {string} key 键名
   */
  static remove(key) {
    try {
      wx.removeStorageSync(key)
      return true
    } catch (error) {
      console.error('Storage remove error:', error)
      return false
    }
  }

  /**
   * 清空所有存储
   */
  static clear() {
    try {
      wx.clearStorageSync()
      return true
    } catch (error) {
      console.error('Storage clear error:', error)
      return false
    }
  }

  /**
   * 获取所有键名
   * @returns {Array} 键名列表
   */
  static keys() {
    try {
      const { keys } = wx.getStorageInfoSync()
      return keys
    } catch (error) {
      console.error('Storage keys error:', error)
      return []
    }
  }

  /**
   * 获取存储信息
   * @returns {Object} 存储信息
   */
  static info() {
    try {
      return wx.getStorageInfoSync()
    } catch (error) {
      console.error('Storage info error:', error)
      return { keys: [], currentSize: 0, limitSize: 1024 * 1024 * 10 }
    }
  }

  // 用户相关存储方法
  static setUserInfo(userInfo) {
    return this.set(STORAGE_KEYS.USER_INFO, userInfo, 7 * 24 * 60 * 60 * 1000) // 7天
  }

  static getUserInfo() {
    return this.get(STORAGE_KEYS.USER_INFO)
  }

  static removeUserInfo() {
    return this.remove(STORAGE_KEYS.USER_INFO)
  }

  // Token相关存储方法
  static setToken(token) {
    return this.set(STORAGE_KEYS.TOKEN, token, 2 * 60 * 60 * 1000) // 2小时
  }

  static getToken() {
    return this.get(STORAGE_KEYS.TOKEN)
  }

  static removeToken() {
    return this.remove(STORAGE_KEYS.TOKEN)
  }

  // 菜品列表缓存
  static setDishList(dishes) {
    return this.set(STORAGE_KEYS.DISH_LIST, dishes, 30 * 60 * 1000) // 30分钟
  }

  static getDishList() {
    return this.get(STORAGE_KEYS.DISH_LIST)
  }

  static removeDishList() {
    return this.remove(STORAGE_KEYS.DISH_LIST)
  }

  // 搜索历史
  static setSearchHistory(history) {
    return this.set(STORAGE_KEYS.SEARCH_HISTORY, history, 30 * 24 * 60 * 60 * 1000) // 30天
  }

  static getSearchHistory() {
    return this.get(STORAGE_KEYS.SEARCH_HISTORY) || []
  }

  static addSearchHistory(keyword) {
    const history = this.getSearchHistory()
    // 去重
    const filtered = history.filter(item => item !== keyword)
    // 添加到开头
    filtered.unshift(keyword)
    // 限制长度
    const limited = filtered.slice(0, 10)
    return this.setSearchHistory(limited)
  }

  static clearSearchHistory() {
    return this.remove(STORAGE_KEYS.SEARCH_HISTORY)
  }

  // 应用设置
  static setSettings(settings) {
    return this.set(STORAGE_KEYS.SETTINGS, settings)
  }

  static getSettings() {
    return this.get(STORAGE_KEYS.SETTINGS) || {}
  }

  static updateSettings(newSettings) {
    const current = this.getSettings()
    return this.setSettings({ ...current, ...newSettings })
  }
}

module.exports = StorageService