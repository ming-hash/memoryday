// utils/filter.js

/**
 * 菜品筛选工具类
 */
class DishFilter {
  /**
   * 根据条件筛选菜品
   * @param {Array} dishes 菜品列表
   * @param {Object} filters 筛选条件
   * @returns {Array} 筛选后的菜品列表
   */
  static filterDishes(dishes, filters = {}) {
    let filtered = [...dishes]

    // 关键词搜索
    if (filters.keyword) {
      filtered = this.filterByKeyword(filtered, filters.keyword)
    }

    // 用餐场景筛选
    if (filters.mealTime) {
      filtered = this.filterByMealTime(filtered, filters.mealTime)
    }

    // 烹饪时间筛选
    if (filters.cookingTime && filters.cookingTime.length > 0) {
      filtered = this.filterByCookingTime(filtered, filters.cookingTime)
    }

    // 难度筛选
    if (filters.difficulty && filters.difficulty.length > 0) {
      filtered = this.filterByDifficulty(filtered, filters.difficulty)
    }

    // 菜系筛选
    if (filters.cuisineType && filters.cuisineType.length > 0) {
      filtered = this.filterByCuisineType(filtered, filters.cuisineType)
    }

    // 食材筛选
    if (filters.ingredients && filters.ingredients.length > 0) {
      filtered = this.filterByIngredients(filtered, filters.ingredients)
    }

    // 星级筛选
    if (filters.minRating) {
      filtered = this.filterByRating(filtered, filters.minRating)
    }

    // 排序
    if (filters.sortBy) {
      filtered = this.sortDishes(filtered, filters.sortBy, filters.sortOrder)
    }

    return filtered
  }

  /**
   * 关键词搜索
   */
  static filterByKeyword(dishes, keyword) {
    const searchTerm = keyword.toLowerCase().trim()
    if (!searchTerm) return dishes

    return dishes.filter(dish => {
      // 搜索菜品名称
      if (dish.name.toLowerCase().includes(searchTerm)) {
        return true
      }

      // 搜索菜品描述
      if (dish.description && dish.description.toLowerCase().includes(searchTerm)) {
        return true
      }

      // 搜索食材
      if (dish.ingredients && dish.ingredients.some(ingredient => 
        ingredient.toLowerCase().includes(searchTerm)
      )) {
        return true
      }

      return false
    })
  }

  /**
   * 用餐场景筛选
   */
  static filterByMealTime(dishes, mealTime) {
    return dishes.filter(dish => 
      dish.mealTime && dish.mealTime.includes(mealTime)
    )
  }

  /**
   * 烹饪时间筛选
   */
  static filterByCookingTime(dishes, cookingTimes) {
    return dishes.filter(dish => 
      dish.cookingTime && cookingTimes.includes(dish.cookingTime)
    )
  }

  /**
   * 难度筛选
   */
  static filterByDifficulty(dishes, difficulties) {
    return dishes.filter(dish => 
      dish.difficulty && difficulties.includes(dish.difficulty)
    )
  }

  /**
   * 菜系筛选
   */
  static filterByCuisineType(dishes, cuisineTypes) {
    return dishes.filter(dish => 
      dish.cuisineType && cuisineTypes.includes(dish.cuisineType)
    )
  }

  /**
   * 食材筛选
   */
  static filterByIngredients(dishes, ingredients) {
    return dishes.filter(dish => 
      dish.ingredients && ingredients.every(ingredient => 
        dish.ingredients.includes(ingredient)
      )
    )
  }

  /**
   * 星级筛选
   */
  static filterByRating(dishes, minRating) {
    return dishes.filter(dish => 
      dish.starRating >= minRating
    )
  }

  /**
   * 菜品排序
   */
  static sortDishes(dishes, sortBy = 'createdAt', order = 'desc') {
    const sorted = [...dishes]
    
    sorted.sort((a, b) => {
      let valueA = a[sortBy]
      let valueB = b[sortBy]

      // 处理不同类型的排序
      if (typeof valueA === 'string') {
        valueA = valueA.toLowerCase()
        valueB = valueB.toLowerCase()
      }

      if (valueA < valueB) {
        return order === 'asc' ? -1 : 1
      }
      if (valueA > valueB) {
        return order === 'asc' ? 1 : -1
      }
      return 0
    })

    return sorted
  }

  /**
   * 随机选择菜品
   */
  static randomSelect(dishes, count = 1, weights = null) {
    if (dishes.length === 0) return []
    if (dishes.length <= count) return [...dishes]

    if (weights) {
      // 加权随机
      const totalWeight = weights.reduce((sum, weight) => sum + weight, 0)
      const selected = []

      while (selected.length < count && dishes.length > 0) {
        const randomNum = Math.random() * totalWeight
        let weightSum = 0

        for (let i = 0; i < dishes.length; i++) {
          weightSum += weights[i]
          if (randomNum <= weightSum) {
            selected.push(dishes[i])
            dishes.splice(i, 1)
            weights.splice(i, 1)
            break
          }
        }
      }

      return selected
    } else {
      // 完全随机
      const shuffled = [...dishes].sort(() => Math.random() - 0.5)
      return shuffled.slice(0, count)
    }
  }

  /**
   * 获取筛选条件摘要
   */
  static getFilterSummary(filters) {
    const summary = []

    if (filters.keyword) {
      summary.push(`关键词: ${filters.keyword}`)
    }

    if (filters.mealTime) {
      summary.push(`用餐: ${filters.mealTime}`)
    }

    if (filters.cookingTime && filters.cookingTime.length > 0) {
      summary.push(`时间: ${filters.cookingTime.join(',')}`)
    }

    if (filters.difficulty && filters.difficulty.length > 0) {
      summary.push(`难度: ${filters.difficulty.join(',')}`)
    }

    if (filters.cuisineType && filters.cuisineType.length > 0) {
      summary.push(`菜系: ${filters.cuisineType.join(',')}`)
    }

    if (filters.ingredients && filters.ingredients.length > 0) {
      summary.push(`食材: ${filters.ingredients.join(',')}`)
    }

    if (filters.minRating) {
      summary.push(`评分: ${filters.minRating}+星`)
    }

    return summary.length > 0 ? summary.join(' | ') : '全部菜品'
  }
}

module.exports = DishFilter