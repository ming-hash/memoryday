// pages/user/user.js
const app = getApp()

Page({
  data: {
    userInfo: {},
    userStats: {
      favoriteDishes: 0,
      totalRecords: 0,
      totalDishes: 0,
      recentActivity: 0
    },
    version: '1.0.0',
    hasUpdate: false
  },

  onLoad() {
    this.loadUserInfo()
    this.loadUserStats()
    this.checkVersion()
  },

  onShow() {
    this.loadUserStats()
  },

  // 加载用户信息
  loadUserInfo() {
    const userInfo = app.globalData.userInfo
    if (userInfo && userInfo.nickname) {
      this.setData({ userInfo })
    } else {
      // 从本地存储获取
      try {
        const storedInfo = wx.getStorageSync('userInfo')
        if (storedInfo) {
          this.setData({ userInfo: storedInfo })
        }
      } catch (e) {
        console.warn('获取本地用户信息失败:', e)
      }
    }
  },

  // 加载用户统计 - 调用后端API
  async loadUserStats() {
    try {
      const res = await app.request('/stats/dashboard/', {}, 'GET')

      const stats = res || {}
      this.setData({
        userStats: {
          totalDishes: stats.total_dishes || 0,
          recentActivity: stats.recent_activity || 0,
          favoriteDishes: stats.recommended_dishes || 0,
          totalRecords: stats.total_dishes || 0
        }
      })
    } catch (error) {
      console.error('加载用户统计失败:', error)
      // 降级：使用本地数据
      this.setData({
        userStats: {
          favoriteDishes: 0,
          totalRecords: 0,
          totalDishes: 0,
          recentActivity: 0
        }
      })
    }
  },

  // 检查版本更新
  checkVersion() {
    const updateManager = wx.getUpdateManager?.()
    
    if (updateManager) {
      updateManager.onCheckForUpdate((res) => {
        this.setData({ hasUpdate: res.hasUpdate })
      })
    }
  },

  // 导航到页面
  navigateTo(e) {
    const url = e.currentTarget.dataset.url
    // tabBar 页面需用 switchTab 打开，navigateTo 对其无效且无报错
    const tabBarPages = [
      '/pages/index/index',
      '/pages/statistics/statistics',
      '/pages/user/user'
    ]
    if (tabBarPages.indexOf(url) !== -1) {
      wx.switchTab({ url })
    } else {
      wx.navigateTo({ url })
    }
  },

  // 清除缓存
  clearCache() {
    wx.showModal({
      title: '清除缓存',
      content: '确定要清除所有缓存数据吗？（不会清除登录状态）',
      success: (res) => {
        if (res.confirm) {
          wx.clearStorage({
            success: () => {
              // 重新保存登录信息
              if (app.globalData.token) {
                wx.setStorageSync('token', app.globalData.token)
                wx.setStorageSync('userInfo', app.globalData.userInfo)
              }
              app.showSuccessToast('缓存已清除')
              this.loadUserStats()
            }
          })
        }
      }
    })
  },

  // 联系支持
  contactSupport() {
    wx.showModal({
      title: '联系支持',
      content: '如有问题请联系：support@example.com',
      showCancel: false
    })
  },

  // 分享小程序
  shareApp() {
    wx.showShareMenu({
      withShareTicket: true
    })
  },

  // 检查更新
  checkUpdate() {
    const updateManager = wx.getUpdateManager?.()
    
    if (updateManager) {
      updateManager.onUpdateReady(() => {
        wx.showModal({
          title: '更新提示',
          content: '新版本已经准备好，是否重启应用？',
          success: (res) => {
            if (res.confirm) {
              updateManager.applyUpdate()
            }
          }
        })
      })
    }
  },

  // 分享功能
  onShareAppMessage() {
    return {
      title: '今日吃啥 - 让饮食更简单',
      path: '/pages/index/index',
      imageUrl: '/images/share-cover.jpg'
    }
  }
})
