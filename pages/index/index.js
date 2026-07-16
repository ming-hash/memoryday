// pages/index/index.js
const app = getApp()
const imageUtils = require('../../utils/imageUtils')

// 后端Dish字段 -> 前端展示格式映射
const DIFFICULTY_MAP = { easy: '简单', medium: '中等', hard: '困难', expert: '专家' }
const CUISINE_MAP = {
  chinese: '中式', western: '西式', japanese: '日式', korean: '韩式',
  thai: '泰式', indian: '印度', vietnamese: '越南', other: '其他'
}

function transformDish(backendDish) {
  if (!backendDish) return null
  return {
    id: backendDish.id,
    name: backendDish.name || '',
    images: backendDish.images || (backendDish.main_image ? [backendDish.main_image] : []),
    mainImage: backendDish.main_image || '',
    cookingTime: backendDish.cooking_time ? `${backendDish.cooking_time}分钟` : '',
    cookingTimeMinutes: backendDish.cooking_time || 0,
    difficulty: DIFFICULTY_MAP[backendDish.difficulty] || backendDish.difficulty || '',
    difficultyCode: backendDish.difficulty || '',
    cuisineType: CUISINE_MAP[backendDish.cuisine_type] || backendDish.cuisine_type || '',
    cuisineTypeCode: backendDish.cuisine_type || '',
    mealTime: backendDish.meal_time || [],
    ingredients: backendDish.ingredients || [],
    starRating: backendDish.rating || 0,
    description: backendDish.description || '',
    story: backendDish.story || '',
    steps: backendDish.steps || [],
    tags: backendDish.tags || [],
    author: backendDish.author || '',
    userNickname: backendDish.user_nickname || '',
    cookedCount: backendDish.cooked_count || 0,
    createdAt: backendDish.created_at || ''
  }
}

Page({
  data: {
    dishes: [],
    filteredDishes: [],
    searchKeyword: '',
    activeFilter: 'all',
    isLoading: true,
    isSpinning: false,
  },

  onLoad() {
    this.loadDishes()
  },

  onPullDownRefresh() {
    this.loadDishes().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  // 加载菜品数据 - 从后端API获取
  async loadDishes() {
    try {
      this.setData({ isLoading: true })

      const res = await app.request('/dishes/', {}, 'GET')

      // res可能是数组或{results: [...]}分页格式
      let dishList = []
      if (Array.isArray(res)) {
        dishList = res
      } else if (res && res.results) {
        dishList = res.results
      }

      // 转换后端字段为前端格式
      const dishes = dishList.map(transformDish).filter(Boolean)

      // 处理图片URL，适配COS
      dishes.forEach(dish => {
        if (dish.images && Array.isArray(dish.images)) {
          dish.images = imageUtils.getOptimizedUrls(dish.images, 'thumbnail')
        }
      })

      // 存储到全局数据
      app.globalData.dishes = dishes

      this.setData({
        dishes: dishes,
        filteredDishes: dishes,
        isLoading: false
      })
    } catch (error) {
      console.error('加载菜品失败:', error)
      app.showErrorToast('加载失败，请重试')
      this.setData({ isLoading: false })
    }
  },

  onSearchInput(e) {
    const keyword = e.detail.value
    this.setData({ searchKeyword: keyword })
    this.filterDishes()
  },

  clearSearch() {
    this.setData({ searchKeyword: '' })
    this.filterDishes()
  },

  setFilter(e) {
    const filter = e.currentTarget.dataset.filter
    this.setData({ activeFilter: filter })
    this.filterDishes()
  },

  filterDishes() {
    const { dishes, searchKeyword, activeFilter } = this.data
    let filtered = dishes

    if (searchKeyword) {
      filtered = filtered.filter(dish =>
        dish.name.toLowerCase().includes(searchKeyword.toLowerCase())
      )
    }

    if (activeFilter !== 'all') {
      if (activeFilter === 'favorite') {
        filtered = filtered.filter(dish => dish.starRating >= 4)
      } else {
        filtered = filtered.filter(dish => dish.mealTime.includes(activeFilter))
      }
    }

    this.setData({ filteredDishes: filtered })
  },

  viewDishDetail(e) {
    const dish = e.currentTarget.dataset.dish
    wx.navigateTo({
      url: `/pages/dish-detail/dish-detail?id=${dish.id}`
    })
  },

  addDish() {
    wx.navigateTo({
      url: '/pages/dish-edit/dish-edit?mode=add'
    })
  },

  // 随机选择菜品 - 带动画效果
  async randomDish() {
    const { filteredDishes } = this.data

    if (filteredDishes.length === 0) {
      app.showErrorToast('暂无菜品可随机选择')
      return
    }

    // 触发旋转动画状态
    this.setData({ isSpinning: true })

    // 先尝试调用后端随机API
    try {
      const res = await app.request('/dishes/random/', {}, 'GET')
      if (res && res.id) {
        const randomDish = transformDish(res)
        setTimeout(() => {
          this.setData({ isSpinning: false })
          this.showRandomResult(randomDish)
        }, 500)
        return
      }
    } catch (error) {
      console.log('后端随机API不可用，使用本地随机')
    }

    // 降级为本地随机
    const randomIndex = Math.floor(Math.random() * filteredDishes.length)
    const randomDish = filteredDishes[randomIndex]
    setTimeout(() => {
      this.setData({ isSpinning: false })
      this.showRandomResult(randomDish)
    }, 400)
  },

  showRandomResult(randomDish) {
    wx.showModal({
      title: '今日推荐',
      content: `今天吃：${randomDish.name}`,
      confirmText: '查看详情',
      cancelText: '换一个',
      success: (res) => {
        if (res.confirm) {
          wx.navigateTo({
            url: `/pages/dish-detail/dish-detail?id=${randomDish.id}`
          })
        } else if (res.cancel) {
          this.randomDish()
        }
      }
    })

    // 记录随机选择历史
    this.recordRandomHistory(randomDish.id)
  },

  async recordRandomHistory(dishId) {
    try {
      await app.request('/dishes/' + dishId + '/cook/', {}, 'POST')
    } catch (error) {
      console.log('记录随机选择失败:', error)
    }
  }
})
