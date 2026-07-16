// pages/settings/settings.js
const StorageService = require('../../services/storage')
const { getAppVersion } = require('../../config/env')

Page({
  data: {
    userInfo: {},
    settings: {
      notifications: true,
      darkMode: false,
      autoBackup: false,
      dataSync: true
    },
    cacheSize: '0KB',
    appVersion: '1.0.0'
  },

  onLoad() {
    this.loadUserInfo()
    this.loadSettings()
    this.calculateCacheSize()
    this.setData({
      appVersion: getAppVersion()
    })
  },

  onShow() {
    this.loadUserInfo()
  },

  loadUserInfo() {
    const userInfo = StorageService.getUserInfo()
    if (userInfo) {
      this.setData({ userInfo })
    }
  },

  loadSettings() {
    const settings = StorageService.getSettings()
    if (settings) {
      this.setData({ settings: { ...this.data.settings, ...settings } })
    }
  },

  async calculateCacheSize() {
    try {
      const info = StorageService.info()
      const size = (info.currentSize / 1024).toFixed(1)
      this.setData({ cacheSize: size + 'KB' })
    } catch (error) {
      console.error('计算缓存大小失败:', error)
    }
  },

  onEditProfile() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
  },

  onChangePassword() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
  },

  onNotificationsChange(e) {
    const notifications = e.detail.value
    this.setData({
      'settings.notifications': notifications
    })
    StorageService.updateSettings({ notifications })
    
    wx.showToast({
      title: notifications ? '通知已开启' : '通知已关闭',
      icon: 'none'
    })
  },

  onDarkModeChange(e) {
    const darkMode = e.detail.value
    this.setData({
      'settings.darkMode': darkMode
    })
    StorageService.updateSettings({ darkMode })
    
    wx.showToast({
      title: darkMode ? '深色模式已开启' : '深色模式已关闭',
      icon: 'none'
    })
  },

  onClearCache() {
    wx.showModal({
      title: '清理缓存',
      content: '确定要清理所有缓存数据吗？',
      confirmText: '清理',
      confirmColor: '#ff4d4f',
      success: (res) => {
        if (res.confirm) {
          this.clearCache()
        }
      }
    })
  },

  async clearCache() {
    wx.showLoading({ title: '清理中...' })
    
    try {
      // 清除缓存但保留用户信息和设置
      const userInfo = StorageService.getUserInfo()
      const settings = StorageService.getSettings()
      const token = StorageService.getToken()
      
      StorageService.clear()
      
      // 恢复必要的数据
      if (userInfo) StorageService.setUserInfo(userInfo)
      if (settings) StorageService.setSettings(settings)
      if (token) StorageService.setToken(token)
      
      await this.calculateCacheSize()
      
      wx.showToast({
        title: '清理完成',
        icon: 'success'
      })
    } catch (error) {
      wx.showToast({
        title: '清理失败',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
    }
  },

  onExportData() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
  },

  onImportData() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
  },

  onBackupData() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
  },

  onAboutApp() {
    wx.showModal({
      title: '关于今日吃啥',
      content: '版本: v' + this.data.appVersion + '\n\n一个帮助你记录和管理菜谱的小程序，让每天的饮食选择更加简单有趣。',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  onFeedback() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
  },

  onCheckUpdate() {
    wx.showToast({
      title: '已是最新版本',
      icon: 'none'
    })
  },

  onLogout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      confirmText: '退出',
      confirmColor: '#ff4d4f',
      success: (res) => {
        if (res.confirm) {
          this.logout()
        }
      }
    })
  },

  logout() {
    // 清除用户相关数据
    StorageService.removeUserInfo()
    StorageService.removeToken()
    
    wx.showToast({
      title: '已退出登录',
      icon: 'success'
    })
    
    // 跳转到登录页
    setTimeout(() => {
      wx.reLaunch({
        url: '/pages/login/login'
      })
    }, 1000)
  }
})