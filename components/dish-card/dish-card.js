// components/dish-card/dish-card.js
Component({
  properties: {
    dish: {
      type: Object,
      value: {}
    }
  },

  data: {
    // 组件内部数据
  },

  methods: {
    onCardTap() {
      const dishId = this.properties.dish.id
      if (dishId) {
        wx.navigateTo({
          url: `/pages/dish-detail/dish-detail?id=${dishId}`
        })
      }
    }
  }
})