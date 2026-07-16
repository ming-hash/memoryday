// pages/login/login.js
const StorageService = require('../../services/storage')
const app = getApp()

Page({
  data: {
    phone: '',
    code: '',
    isSendingCode: false,
    isLoggingIn: false,
    isLoading: false,
    codeCountdown: 0,
    agreed: false
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

  onPhoneInput(e) {
    this.setData({
      phone: e.detail.value.replace(/\D/g, '')
    })
  },

  onCodeInput(e) {
    this.setData({
      code: e.detail.value.replace(/\D/g, '')
    })
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

  async onSendCode() {
    if (this.data.isSendingCode || this.data.codeCountdown > 0) return

    const phone = this.data.phone.trim()
    if (!phone) {
      wx.showToast({ title: '请输入手机号', icon: 'none' })
      return
    }

    if (!/^1[3-9]\d{9}$/.test(phone)) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' })
      return
    }

    this.setData({ isSendingCode: true })

    try {
      // 调用后端发送验证码API（待实现短信服务，暂时模拟）
      await app.request('/auth/send-sms-code/', { phone }, 'POST')

      wx.showToast({ title: '验证码已发送', icon: 'success' })
      this.startCountdown()
    } catch (error) {
      console.error('发送验证码失败:', error)
      wx.showToast({ title: '发送失败，请重试', icon: 'none' })
    } finally {
      this.setData({ isSendingCode: false })
    }
  },

  startCountdown() {
    this.setData({ codeCountdown: 60 })

    const timer = setInterval(() => {
      if (this.data.codeCountdown <= 1) {
        clearInterval(timer)
        this.setData({ codeCountdown: 0 })
        return
      }
      this.setData({ codeCountdown: this.data.codeCountdown - 1 })
    }, 1000)
  },

  async onLogin() {
    if (!this.data.agreed) {
      wx.showToast({ title: '请先同意协议', icon: 'none' })
      return
    }

    const phone = this.data.phone.trim()
    const code = this.data.code.trim()

    if (!phone) {
      wx.showToast({ title: '请输入手机号', icon: 'none' })
      return
    }

    if (!code) {
      wx.showToast({ title: '请输入验证码', icon: 'none' })
      return
    }

    this.setData({ isLoggingIn: true })

    try {
      // 调用后端手机号+验证码登录
      const res = await app.request('/auth/login/', {
        username: phone,
        password: code  // 短信验证码作为临时密码
      }, 'POST')

      if (res && res.access) {
        // 存储JWT token和用户信息
        StorageService.setToken(res.access)
        StorageService.setUserInfo(res.user)
        app.globalData.userInfo = res.user

        wx.showToast({ title: '登录成功', icon: 'success' })

        setTimeout(() => {
          wx.switchTab({ url: '/pages/index/index' })
        }, 1000)
      } else {
        wx.showToast({ title: '登录失败', icon: 'none' })
      }
    } catch (error) {
      console.error('手机号登录失败:', error)
      wx.showToast({ title: '登录失败，请重试', icon: 'none' })
    } finally {
      this.setData({ isLoggingIn: false })
    }
  },

  async onWechatLogin() {
    if (!this.data.agreed) {
      wx.showToast({ title: '请先同意协议', icon: 'none' })
      return
    }

    this.setData({ isLoading: true })

    try {
      // 1. 调用wx.login获取code
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

      // 2. 将code发送到后端，换取JWT
      const res = await app.request('/auth/wechat-login/', {
        code: loginRes.code
      }, 'POST')

      if (res && res.access) {
        // 3. 存储JWT token和用户信息
        StorageService.setToken(res.access)
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
      this.setData({ isLoading: false })
    }
  }
})
