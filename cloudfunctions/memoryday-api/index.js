const cloud = require('wx-server-sdk')
cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
})

// 简单的菜品数据（生产环境应该连接数据库）
const dishes = [
  { id: 1, name: "红烧肉", category: "家常菜", difficulty: "中等", cookingTime: "60分钟", image: "https://example.com/hongshaorou.jpg" },
  { id: 2, name: "西红柿炒鸡蛋", category: "家常菜", difficulty: "简单", cookingTime: "15分钟", image: "https://example.com/xihongshi.jpg" },
  { id: 3, name: "麻婆豆腐", category: "川菜", difficulty: "中等", cookingTime: "30分钟", image: "https://example.com/mapodoufu.jpg" },
  { id: 4, name: "清蒸鲈鱼", category: "粤菜", difficulty: "困难", cookingTime: "25分钟", image: "https://example.com/qingzhengluyu.jpg" },
  { id: 5, name: "宫保鸡丁", category: "川菜", difficulty: "中等", cookingTime: "20分钟", image: "https://example.com/gongbaojiding.jpg" }
]

// 主函数入口
exports.main = async (event, context) => {
  const { action, data } = event
  
  try {
    switch (action) {
      case 'getDishes':
        return await getDishes(data)
      case 'getRandomDish':
        return await getRandomDish(data)
      case 'getDishDetail':
        return await getDishDetail(data)
      case 'healthCheck':
        return { status: 'ok', timestamp: new Date().toISOString() }
      default:
        return { error: 'Unknown action', action }
    }
  } catch (error) {
    console.error('API Error:', error)
    return { error: error.message }
  }
}

// 获取菜品列表
async function getDishes(data) {
  const { category, difficulty, page = 1, limit = 10 } = data || {}
  
  let filteredDishes = [...dishes]
  
  if (category) {
    filteredDishes = filteredDishes.filter(dish => dish.category === category)
  }
  
  if (difficulty) {
    filteredDishes = filteredDishes.filter(dish => dish.difficulty === difficulty)
  }
  
  const startIndex = (page - 1) * limit
  const endIndex = startIndex + limit
  const paginatedDishes = filteredDishes.slice(startIndex, endIndex)
  
  return {
    dishes: paginatedDishes,
    total: filteredDishes.length,
    page,
    limit,
    hasMore: endIndex < filteredDishes.length
  }
}

// 随机选择菜品
async function getRandomDish(data) {
  const { category, difficulty } = data || {}
  
  let filteredDishes = [...dishes]
  
  if (category) {
    filteredDishes = filteredDishes.filter(dish => dish.category === category)
  }
  
  if (difficulty) {
    filteredDishes = filteredDishes.filter(dish => dish.difficulty === difficulty)
  }
  
  if (filteredDishes.length === 0) {
    return { error: 'No dishes found with the specified filters' }
  }
  
  const randomIndex = Math.floor(Math.random() * filteredDishes.length)
  const randomDish = filteredDishes[randomIndex]
  
  return {
    dish: randomDish,
    timestamp: new Date().toISOString(),
    totalOptions: filteredDishes.length
  }
}

// 获取菜品详情
async function getDishDetail(data) {
  const { id } = data || {}
  
  if (!id) {
    return { error: 'Dish ID is required' }
  }
  
  const dish = dishes.find(d => d.id === parseInt(id))
  
  if (!dish) {
    return { error: 'Dish not found' }
  }
  
  return {
    dish: {
      ...dish,
      ingredients: ["主料", "辅料", "调料"],
      steps: ["步骤1", "步骤2", "步骤3"],
      tips: "烹饪小贴士"
    }
  }
}