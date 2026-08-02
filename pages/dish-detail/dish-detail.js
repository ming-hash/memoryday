// pages/dish-detail/dish-detail.js
const app = getApp()
const imageUtils = require('../../utils/imageUtils')
const { getIngredientIcon } = require('../../utils/ingredientIcons')

// 为食材数组附加图标 URL（图床），无图标则留空字符串
function buildIngredientsWithIcon(ingredients) {
  if (!Array.isArray(ingredients)) return []
  return ingredients.map(name => ({
    name: name,
    icon: getIngredientIcon(name)
  }))
}

// 字段映射（与index.js保持一致）
const DIFFICULTY_MAP = { easy: '简单', medium: '中等', hard: '困难', expert: '专家' }
const CUISINE_MAP = {
  chinese: '中式', western: '西式', japanese: '日式', korean: '韩式',
  thai: '泰式', indian: '印度', vietnamese: '越南', other: '其他'
}
const MEAL_TIME_MAP = { breakfast: '早餐', lunch: '午餐', dinner: '晚餐', snack: '加餐' }

Page({
  data: {
    dish: {
      id: '',
      name: '',
      images: [],
      description: '',
      cookingTime: '',
      difficulty: '',
      cuisineType: '',
      mealTime: [],
      ingredients: [],
      starRating: 0
    },
    mealTimeLabels: '',
    showDeleteDialog: false
  },

  onLoad(options) {
    const dishId = options.id
    if (dishId) {
      this.loadDishDetail(dishId)
    }
  },

  // 加载菜品详情 - 从后端API获取
  async loadDishDetail(dishId) {
    try {
      wx.showLoading({ title: '加载中...' })

      const res = await app.request('/dishes/' + dishId + '/', {}, 'GET')

      if (!res) {
        app.showErrorToast('菜品不存在')
        wx.navigateBack()
        return
      }

      // 转换后端字段为前端格式
      const dish = {
        id: res.id,
        name: res.name || '',
        images: res.images || (res.main_image ? [res.main_image] : []),
        mainImage: res.main_image || '',
        cookingTime: res.cooking_time ? `${res.cooking_time}分钟` : '',
        cookingTimeMinutes: res.cooking_time || 0,
        difficulty: DIFFICULTY_MAP[res.difficulty] || res.difficulty || '',
        cuisineType: CUISINE_MAP[res.cuisine_type] || res.cuisine_type || '',
        mealTime: res.meal_time || [],
        ingredients: res.ingredients || [],
        seasonings: res.seasonings || [],
        starRating: res.rating || 0,
        description: res.description || '',
        story: res.story || '',
        steps: res.steps || [],
        tips: res.tips || '',
        tags: res.tags || [],
        author: res.author || '',
        userNickname: res.user_nickname || '',
        cookedCount: res.cooked_count || 0,
        calories: res.calories || null
      }

      // 处理图片URL，适配COS
      if (dish.images && Array.isArray(dish.images)) {
        dish.images = dish.images.map(image => {
          if (imageUtils.canOptimizeImage(image)) {
            return imageUtils.getPreviewUrl(image, 600, 400)
          }
          return image
        })
      }

      // 转换用餐场景标签
      const mealTimeLabels = dish.mealTime.map(time => MEAL_TIME_MAP[time] || time).join('、')

      this.setData({
        dish: dish,
        mealTimeLabels: mealTimeLabels,
        ingredientsWithIcon: buildIngredientsWithIcon(dish.ingredients)
      })
    } catch (error) {
      console.error('加载菜品详情失败:', error)
      app.showErrorToast('加载失败')
    } finally {
      wx.hideLoading()
    }
  },

  editDish() {
    const { dish } = this.data
    wx.navigateTo({
      url: `/pages/dish-edit/dish-edit?mode=edit&id=${dish.id}`
    })
  },

  async randomThisType() {
    const { dish } = this.data
    wx.showToast({ title: '正在寻找同类菜品...', icon: 'loading' })

    try {
      // 调用后端搜索API，按菜系查找
      const res = await app.request('/dishes/search/', {
        q: '',
        cuisine_type: dish.cuisineTypeCode || ''
      }, 'GET')

      let dishList = Array.isArray(res) ? res : (res && res.results ? res.results : [])

      // 过滤掉当前菜品
      const similarDishes = dishList.filter(d => d.id !== dish.id)

      if (similarDishes.length > 0) {
        const randomIndex = Math.floor(Math.random() * similarDishes.length)
        const randomDish = similarDishes[randomIndex]
        wx.navigateTo({
          url: `/pages/dish-detail/dish-detail?id=${randomDish.id}`
        })
      } else {
        app.showErrorToast('暂无同类菜品')
      }
    } catch (error) {
      console.error('随机查找失败:', error)
      app.showErrorToast('查找失败')
    }
  },

  showDeleteDialog() {
    this.setData({ showDeleteDialog: true })
  },

  hideDeleteDialog() {
    this.setData({ showDeleteDialog: false })
  },

  async confirmDelete() {
    const { dish } = this.data

    try {
      await app.request('/dishes/' + dish.id + '/', {}, 'DELETE')

      wx.showToast({
        title: '删除成功',
        icon: 'success',
        duration: 1500,
        complete: () => {
          wx.navigateBack()
        }
      })
    } catch (error) {
      console.error('删除菜品失败:', error)
      wx.showToast({ title: '删除失败', icon: 'none' })
    }
  },

  onShareAppMessage() {
    const { dish } = this.data
    return {
      title: `推荐菜品：${dish.name}`,
      path: `/pages/dish-detail/dish-detail?id=${dish.id}`,
      imageUrl: dish.images[0] || ''
    }
  },

  onShareTimeline() {
    const { dish } = this.data
    return {
      title: dish.name,
      imageUrl: dish.images[0] || ''
    }
  }
})
