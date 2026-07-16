// pages/index/index.js
const app = getApp()

Page({
  data: {
    dishes: [],
    randomDish: null,
    loading: false,
    showRandom: false
  },

  onLoad() {
    this.loadDishes()
  },

  // 加载菜品列表
  async loadDishes() {
    this.setData({ loading: true })
    
    try {
      let result;
      
      if (app.globalData.devMode) {
        // 开发模式：直接调用本地 Django API
        const baseUrl = app.globalData.baseUrl;
        result = await this.requestWithAuth('GET', `${baseUrl}/dishes/`);
        result = { dishes: result.results || [], total: result.count || 0 };
      } else {
        // 生产模式：使用云函数
        result = await wx.cloud.callFunction({
          name: 'memoryday-api',
          data: { action: 'getDishes' }
        });
        result = result.result;
      }
      
      this.setData({
        dishes: result.dishes || [],
        loading: false
      })
    } catch (error) {
      console.error('加载菜品失败:', error)
      this.setData({ loading: false })
      wx.showToast({
        title: '加载失败: ' + (error.message || error.errMsg || '未知错误'),
        icon: 'none'
      })
    }
  },

  // 随机选择菜品
  async chooseRandomDish() {
    this.setData({ 
      loading: true,
      showRandom: false 
    })
    
    try {
      let result;
      
      if (app.globalData.devMode) {
        // 开发模式：直接调用本地 API
        const baseUrl = app.globalData.baseUrl;
        result = await this.requestWithAuth('GET', `${baseUrl}/dishes/random/`);
      } else {
        // 生产模式：使用云函数
        result = await wx.cloud.callFunction({
          name: 'memoryday-api',
          data: { action: 'getRandomDish' }
        });
        result = result.result;
      }
      
      if (result.error) {
        wx.showToast({
          title: result.error,
          icon: 'none'
        })
      } else {
        this.setData({
          randomDish: result,
          showRandom: true,
          loading: false
        })
      }
    } catch (error) {
      console.error('随机选择失败:', error)
      this.setData({ loading: false })
      wx.showToast({
        title: '选择失败',
        icon: 'none'
      })
    }
  },

  // 封装请求方法（带 Token）
  requestWithAuth(method, url, data) {
    return new Promise((resolve, reject) => {
      const token = wx.getStorageSync('access_token');
      const header = {
        'Content-Type': 'application/json'
      };
      if (token) {
        header['Authorization'] = `Bearer ${token}`;
      }
      
      wx.request({
        url,
        method,
        data,
        header,
        success: (res) => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(res.data);
          } else {
            reject(new Error(res.data?.error || `请求失败: ${res.statusCode}`));
          }
        },
        fail: (err) => {
          reject(new Error(err.errMsg || '网络请求失败'));
        }
      });
    });
  },

  // 查看菜品详情
  viewDishDetail(e) {
    const dishId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/dish-detail/dish-detail?id=${dishId}`
    })
  },

  // 添加新菜品
  addDish() {
    wx.navigateTo({
      url: '/pages/dish-edit/dish-edit'
    })
  }
})