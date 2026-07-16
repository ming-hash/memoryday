// pages/dish-edit/dish-edit.js
const app = getApp()
const getCosService = require('../../services/cosService')

// 难度映射：前端显示 <-> 后端API值
const DIFFICULTY_MAP = {
  '简单': 'easy',
  '中等': 'medium',
  '复杂': 'hard'
}
const DIFFICULTY_REVERSE_MAP = { easy: '简单', medium: '中等', hard: '复杂', expert: '复杂' }

// 菜系映射：前端显示 <-> 后端API值
const CUISINE_MAP = {
  '家常菜': 'chinese',
  '川菜': 'chinese',
  '粤菜': 'chinese',
  '西餐': 'western',
  '其他': 'other'
}
const CUISINE_REVERSE_MAP = { chinese: '家常菜', western: '西餐', japanese: '日式', korean: '韩式', thai: '泰式', indian: '印度', vietnamese: '越南', other: '其他' }

// 烹饪时间映射
const COOKING_TIME_MAP = {
  '5分钟内': 5,
  '10-20分钟': 15,
  '30分钟以上': 45
}
const COOKING_TIME_REVERSE_MAP = {}

// 根据后端cooking_time值反推前端显示
function cookingTimeToLabel(minutes) {
  if (!minutes) return ''
  if (minutes <= 5) return '5分钟内'
  if (minutes <= 20) return '10-20分钟'
  return '30分钟以上'
}

Page({
  data: {
    mode: 'add', // 'add' 或 'edit'
    dishId: null, // 编辑模式下的菜品ID
    dish: {
      id: '',
      name: '',
      images: [], // COS图片URL
      description: '',
      cookingTime: '',
      difficulty: '',
      cuisineType: '',
      mealTime: [],
      ingredients: [],
      starRating: 0
    },
    newIngredient: '',
    showDeleteDialog: false,
    isUploading: false,
    isSaving: false,
    
    // 选择器选项
    cookingTimeOptions: ['5分钟内', '10-20分钟', '30分钟以上'],
    cookingTimeIndex: -1,
    
    difficultyOptions: ['简单', '中等', '复杂'],
    difficultyIndex: -1,
    
    cuisineTypeOptions: ['家常菜', '川菜', '粤菜', '西餐', '其他'],
    cuisineTypeIndex: -1,
    
    mealTimeOptions: [
      { label: '早餐', value: 'breakfast' },
      { label: '午餐', value: 'lunch' },
      { label: '晚餐', value: 'dinner' },
      { label: '加餐', value: 'snack' }
    ]
  },

  onLoad(options) {
    const mode = options.mode || 'add'
    const dishId = options.id || null
    
    this.setData({ mode, dishId })
    
    if (mode === 'edit' && dishId) {
      this.loadDishForEdit(dishId)
    }

    // 设置导航栏标题
    wx.setNavigationBarTitle({
      title: mode === 'edit' ? '编辑菜品' : '添加菜品'
    })
  },

  // 加载要编辑的菜品 - 调用后端API
  async loadDishForEdit(dishId) {
    wx.showLoading({ title: '加载中...' })
    
    try {
      const res = await app.request(`/dishes/${dishId}/`, {}, 'GET')
      
      const dish = res
      const cookingTimeLabel = cookingTimeToLabel(dish.cooking_time)
      const difficultyLabel = DIFFICULTY_REVERSE_MAP[dish.difficulty] || ''
      const cuisineTypeLabel = CUISINE_REVERSE_MAP[dish.cuisine_type] || ''
      
      // 构造前端数据结构
      const frontendDish = {
        id: dish.id,
        name: dish.name || '',
        images: dish.images || (dish.main_image ? [dish.main_image] : []),
        description: dish.description || '',
        cookingTime: cookingTimeLabel,
        difficulty: difficultyLabel,
        cuisineType: cuisineTypeLabel,
        mealTime: dish.tags ? dish.tags.map(t => t.name) : [],
        ingredients: Array.isArray(dish.ingredients) ? dish.ingredients : [],
        starRating: dish.rating || 0
      }
      
      // 设置选择器索引
      const cookingTimeIndex = this.data.cookingTimeOptions.indexOf(cookingTimeLabel)
      const difficultyIndex = this.data.difficultyOptions.indexOf(difficultyLabel)
      const cuisineTypeIndex = this.data.cuisineTypeOptions.indexOf(cuisineTypeLabel)
      
      this.setData({
        dish: frontendDish,
        cookingTimeIndex: cookingTimeIndex,
        difficultyIndex: difficultyIndex,
        cuisineTypeIndex: cuisineTypeIndex
      })
      
    } catch (error) {
      console.error('加载菜品失败:', error)
      app.showErrorToast('加载菜品失败')
      setTimeout(() => wx.navigateBack(), 1500)
    } finally {
      wx.hideLoading()
    }
  },

  // 选择图片
  async chooseImage() {
    if (this.data.isUploading) {
      app.showErrorToast('正在上传中，请稍候')
      return
    }
    
    try {
      wx.chooseImage({
        count: 3 - this.data.dish.images.length,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: async (res) => {
          await this.uploadImagesToCos(res.tempFilePaths)
        },
        fail: (err) => {
          console.error('选择图片失败:', err)
          app.showErrorToast('选择图片失败，请重试')
        }
      })
    } catch (error) {
      console.error('选择图片异常:', error)
      app.showErrorToast('选择图片异常')
    }
  },

  // 上传图片到腾讯云COS
  async uploadImagesToCos(tempFilePaths) {
    if (this.data.isUploading) return
    
    this.setData({ isUploading: true })
    
    try {
      const cosService = getCosService()
      
      if (!cosService.config) {
        throw new Error('COS服务未正确初始化')
      }
      
      wx.showLoading({ title: '上传中...', mask: true })
      
      const uploadResults = []
      
      for (const filePath of tempFilePaths) {
        try {
          const sizeValidation = await cosService.validateFileSize(filePath)
          if (!sizeValidation.valid) {
            throw new Error(sizeValidation.error)
          }
          
          if (!cosService.validateFileType(filePath)) {
            throw new Error('不支持的文件格式')
          }
          
          const result = await cosService.uploadImage(filePath, null, 'dish_images')
          uploadResults.push(result)
        } catch (error) {
          console.error('单张图片上传失败:', error)
          app.showErrorToast(`图片上传失败: ${error.message}`)
          continue
        }
      }
      
      if (uploadResults.length > 0) {
        const cosUrls = uploadResults.map(result => result.url)
        const newImages = [...this.data.dish.images, ...cosUrls]
        
        this.setData({
          'dish.images': newImages.slice(0, 3),
          'dish.tempImages': []
        })
        
        app.showSuccessToast(`成功上传${uploadResults.length}张图片`)
      }
      
    } catch (error) {
      console.error('上传图片到COS失败:', error)
      app.showErrorToast(`上传失败: ${error.message}`)
    } finally {
      this.setData({ isUploading: false })
      wx.hideLoading()
    }
  },

  // 移除图片
  async removeImage(e) {
    const index = e.currentTarget.dataset.index
    const images = [...this.data.dish.images]
    const removedImage = images[index]
    
    images.splice(index, 1)
    this.setData({ 'dish.images': images })
    
    if (removedImage && removedImage.includes('cos.myqcloud.com')) {
      try {
        await this.deleteImageFromCos(removedImage)
      } catch (error) {
        console.warn('从COS删除图片失败（不影响界面）:', error)
      }
    }
  },

  // 从COS删除图片
  async deleteImageFromCos(imageUrl) {
    try {
      const cosService = getCosService()
      const urlParts = imageUrl.split('/')
      const fileName = urlParts[urlParts.length - 1]
      const fileKey = `dish_images/${fileName}`
      await cosService.deleteFile(fileKey)
    } catch (error) {
      console.error('从COS删除图片失败:', error)
      throw error
    }
  },

  // 烹饪时间选择
  onCookingTimeChange(e) {
    const index = e.detail.value
    this.setData({
      cookingTimeIndex: index,
      'dish.cookingTime': this.data.cookingTimeOptions[index]
    })
  },

  // 难度选择
  onDifficultyChange(e) {
    const index = e.detail.value
    this.setData({
      difficultyIndex: index,
      'dish.difficulty': this.data.difficultyOptions[index]
    })
  },

  // 菜系选择
  onCuisineTypeChange(e) {
    const index = e.detail.value
    this.setData({
      cuisineTypeIndex: index,
      'dish.cuisineType': this.data.cuisineTypeOptions[index]
    })
  },

  // 切换用餐场景
  toggleMealTime(e) {
    const value = e.currentTarget.dataset.value
    const mealTime = [...this.data.dish.mealTime]
    const index = mealTime.indexOf(value)
    
    if (index > -1) {
      mealTime.splice(index, 1)
    } else {
      mealTime.push(value)
    }
    
    this.setData({ 'dish.mealTime': mealTime })
  },

  // 食材输入
  onIngredientInput(e) {
    this.setData({ newIngredient: e.detail.value })
  },

  // 添加食材
  addIngredient() {
    const ingredient = this.data.newIngredient.trim()
    if (!ingredient) return
    
    const ingredients = [...this.data.dish.ingredients]
    if (!ingredients.includes(ingredient)) {
      ingredients.push(ingredient)
      this.setData({
        'dish.ingredients': ingredients,
        newIngredient: ''
      })
    }
  },

  // 移除食材
  removeIngredient(e) {
    const index = e.currentTarget.dataset.index
    const ingredients = [...this.data.dish.ingredients]
    ingredients.splice(index, 1)
    this.setData({ 'dish.ingredients': ingredients })
  },

  // 设置星级评分
  setStarRating(e) {
    const rating = e.currentTarget.dataset.rating
    this.setData({ 'dish.starRating': rating })
  },

  // 表单提交
  submitForm(e) {
    const formData = e.detail.value
    const { dish } = this.data
    
    if (!dish.name.trim() && !formData.name?.trim()) {
      app.showErrorToast('请输入菜品名称')
      return
    }
    
    const finalDish = {
      ...dish,
      name: formData.name || dish.name,
      description: formData.description || dish.description
    }
    
    this.saveDish(finalDish)
  },

  // 保存菜品 - 调用后端API
  async saveDish(dish) {
    if (this.data.isSaving) return
    this.setData({ isSaving: true })
    
    wx.showLoading({ title: this.data.mode === 'add' ? '添加中...' : '保存中...' })
    
    try {
      // 处理未上传的临时文件
      const tempImages = dish.images.filter(image => !image.includes('cos.myqcloud.com') && !image.startsWith('http'))
      if (tempImages.length > 0) {
        await this.uploadImagesToCos(tempImages)
        // 重新获取最新图片列表
        dish.images = this.data.dish.images
      }
      
      // 构造后端API所需数据格式
      const apiData = {
        name: dish.name,
        description: dish.description || '',
        cooking_time: COOKING_TIME_MAP[dish.cookingTime] || 15,
        difficulty: DIFFICULTY_MAP[dish.difficulty] || 'easy',
        cuisine_type: CUISINE_MAP[dish.cuisineType] || 'chinese',
        ingredients: dish.ingredients || [],
        main_image: dish.images[0] || '',
        images: dish.images || [],
        tags: dish.mealTime || [],
        rating: dish.starRating || 0
      }
      
      let res
      if (this.data.mode === 'edit' && this.data.dishId) {
        // 编辑模式：PUT请求
        res = await app.request(`/dishes/${this.data.dishId}/`, apiData, 'PUT')
      } else {
        // 新增模式：POST请求
        res = await app.request('/dishes/', apiData, 'POST')
      }
      
      wx.hideLoading()
      app.showSuccessToast(this.data.mode === 'add' ? '添加成功' : '保存成功')
      
      // 通知上一页刷新数据
      const pages = getCurrentPages()
      if (pages.length > 1) {
        const prevPage = pages[pages.length - 2]
        if (prevPage.route === 'pages/index/index' && typeof prevPage.loadDishes === 'function') {
          prevPage.loadDishes()
        }
      }
      
      setTimeout(() => wx.navigateBack(), 500)
      
    } catch (error) {
      wx.hideLoading()
      console.error('保存菜品失败:', error)
      app.showErrorToast('保存失败，请重试')
    } finally {
      this.setData({ isSaving: false })
    }
  },

  // 显示删除确认
  showDeleteConfirm() {
    this.setData({ showDeleteDialog: true })
  },

  // 隐藏删除确认
  hideDeleteDialog() {
    this.setData({ showDeleteDialog: false })
  },

  // 确认删除 - 调用后端API
  async confirmDelete() {
    const { dishId } = this.data
    
    if (!dishId) {
      app.showErrorToast('菜品ID无效')
      return
    }
    
    wx.showLoading({ title: '删除中...' })
    
    try {
      await app.request(`/dishes/${dishId}/`, {}, 'DELETE')
      
      wx.hideLoading()
      app.showSuccessToast('删除成功')
      
      // 通知上一页刷新数据
      const pages = getCurrentPages()
      if (pages.length > 1) {
        const prevPage = pages[pages.length - 2]
        if (prevPage.route === 'pages/index/index' && typeof prevPage.loadDishes === 'function') {
          prevPage.loadDishes()
        }
      }
      
      setTimeout(() => wx.navigateBack(), 500)
      
    } catch (error) {
      wx.hideLoading()
      console.error('删除菜品失败:', error)
      app.showErrorToast('删除失败，请重试')
    }
  }
})
