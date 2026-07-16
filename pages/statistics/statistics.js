// pages/statistics/statistics.js
const app = getApp()
const imageUtils = require('../../utils/imageUtils')

Page({
  data: {
    stats: {
      totalDishes: 0,
      weeklyRecords: 0,
      newThisMonth: 0,
      topDishes: [],
      cuisineDistribution: [],
      mealTimeDistribution: [],
      difficultyDistribution: [],
      updateTime: ''
    },
    loading: false,
    needLogin: false
  },

  onLoad() {
    this.loadStatistics()
  },

  onShow() {
    this.loadStatistics()
  },

  // 加载统计数据 - 调用后端API
  async loadStatistics() {
    if (this.data.loading) return
    this.setData({ loading: true, needLogin: false })

    try {
      wx.showLoading({ title: '加载中...' })

      // 调用后端统计API
      const res = await app.request('/stats/dashboard/', {}, 'GET')

      const stats = res || {}

      // 获取热门菜品（按烹饪次数排序）
      let topDishes = []
      try {
        const dishesRes = await app.request('/dishes/my-dishes/', {}, 'GET')
        const dishes = dishesRes.results || dishesRes || []
        topDishes = dishes
          .sort((a, b) => (b.cooked_count || 0) - (a.cooked_count || 0))
          .slice(0, 5)
          .map(dish => ({
            id: dish.id,
            name: dish.name,
            image: imageUtils.getOptimizedUrl(dish.main_image || '', 'thumbnail'),
            count: dish.cooked_count || 0
          }))
      } catch (e) {
        console.warn('获取热门菜品失败:', e)
      }

      // 处理分类统计
      const cuisineColors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#F9C80E', '#999']
      const cuisineDistribution = (stats.category_stats || []).map((item, index) => ({
        type: item.category || '未分类',
        count: item.count || 0,
        percentage: stats.total_dishes ? Math.round((item.count / stats.total_dishes) * 100) : 0,
        color: cuisineColors[index % cuisineColors.length]
      }))

      // 处理难度统计
      const difficultyMap = { easy: '简单', medium: '中等', hard: '困难', expert: '专家' }
      const difficultyColors = ['#2EC4B6', '#FF9F1C', '#E71D36', '#9B59B6']
      const difficultyDistribution = (stats.difficulty_stats || []).map((item, index) => ({
        type: difficultyMap[item.difficulty] || item.difficulty || '未知',
        count: item.count || 0,
        percentage: stats.total_dishes ? Math.round((item.count / stats.total_dishes) * 100) : 0,
        color: difficultyColors[index % difficultyColors.length]
      }))

      // 用餐场景分布（基于标签）
      const mealTimeLabels = { breakfast: '早餐', lunch: '午餐', dinner: '晚餐', snack: '加餐' }
      const mealTimeColors = ['#FF9F1C', '#2EC4B6', '#E71D36', '#F9C80E']
      const mealTimeDistribution = Object.keys(mealTimeLabels).map((key, index) => ({
        time: mealTimeLabels[key],
        count: 0,
        percentage: 0,
        color: mealTimeColors[index]
      }))

      this.setData({
        stats: {
          totalDishes: stats.total_dishes || 0,
          weeklyRecords: stats.recent_activity || 0,
          newThisMonth: stats.recent_activity || 0,
          topDishes: topDishes,
          cuisineDistribution: cuisineDistribution,
          difficultyDistribution: difficultyDistribution,
          mealTimeDistribution: mealTimeDistribution,
          updateTime: this.formatTime(new Date())
        }
      })

    } catch (error) {
      console.error('加载统计数据失败:', error)
      if (error.message === 'AUTH_REQUIRED') {
        // 未登录，提示用户登录
        this.setData({ needLogin: true })
      } else {
        app.showErrorToast('加载失败')
      }
    } finally {
      wx.hideLoading()
      this.setData({ loading: false })
    }
  },

  // 跳转登录页
  goToLogin() {
    wx.navigateTo({
      url: '/pages/login/login'
    })
  },

  // 格式化时间
  formatTime(date) {
    const year = date.getFullYear()
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    const hours = date.getHours().toString().padStart(2, '0')
    const minutes = date.getMinutes().toString().padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}`
  },

  // 刷新数据
  refreshData() {
    this.loadStatistics()
  },

  // 分享功能
  onShareAppMessage() {
    return {
      title: '我的饮食统计',
      path: '/pages/statistics/statistics'
    }
  }
})
