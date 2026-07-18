// pages/login/login.js
const StorageService = require('../../services/storage')
const app = getApp()

Page({
  data: {
    isLoading: false,
    agreed: false,
    isLoggingIn: false
  },

  onLoad() {
    // 检查是否已登录
    const token = StorageService.getToken()
    if (token) {
      wx.switchTab({
        url: '/pages/index/index'
      })
    }
  },

  onAgreementChange() {
    this.setData({
      agreed: !this.data.agreed
    })
  },

  onShowAgreement() {
    wx.showModal({
      title: '用户协议',
      content: '请阅读并同意用户协议',
      showCancel: false
    })
  },

  onShowPrivacy() {
    wx.showModal({
      title: '隐私政策',
      content: '请阅读并同意隐私政策',
      showCancel: false
    })
  },

  async onWechatLogin() {
    if (!this.data.agreed) {
      wx.showToast({ title: '请先同意协议', icon: 'none' })
      return
    }

    this.setData({ isLoggingIn: true, isLoading: true })

    try {
      // 1. 调用 wx.login 获取临时 code
      const loginRes = await new Promise((resolve, reject) => {
        wx.login({
          success: resolve,
          fail: reject
        })
      })

      if (!loginRes.code) {
        wx.showToast({ title: '微信登录失败', icon: 'none' })
        return
      }

      // 2. 将 code 发送到后端，换取 JWT
      const res = await app.request('/auth/wechat-login/', {
        code: loginRes.code
      }, 'POST')

      if (res && res.access) {
        // 3. 存储 JWT token 和用户信息
        StorageService.setToken(res.access)
        if (res.refresh) {
          StorageService.set('refresh_token', res.refresh)
        }
        StorageService.setUserInfo(res.user)
        app.globalData.userInfo = res.user

        wx.showToast({ title: '登录成功', icon: 'success' })

        setTimeout(() => {
          wx.switchTab({ url: '/pages/index/index' })
        }, 1000)
      } else {
        wx.showToast({ title: '微信登录失败', icon: 'none' })
      }
    } catch (error) {
      console.error('微信登录失败:', error)
      wx.showToast({ title: '微信登录失败，请重试', icon: 'none' })
    } finally {
      this.setData({ isLoggingIn: false, isLoading: false })
    }
  }
})