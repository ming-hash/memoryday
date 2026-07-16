# 存储桶配置使用指南

## 配置说明

### 存储桶后缀变量

项目现在统一使用 `STORAGE_SUFFIX` 变量来管理存储桶名称中的动态部分：

- **前端配置** (`config/cos.js`):
  ```javascript
  const STORAGE_SUFFIX = '1259810697' // 存储桶后缀，统一配置
  const BUCKET_NAME = `memoryday-${STORAGE_SUFFIX}` // 完整的存储桶名称
  ```

- **后端配置** (`.env`):
  ```bash
  COS_STORAGE_SUFFIX=1259810697  # 存储桶后缀，统一配置
  COS_BUCKET=memoryday-1259810697  # 自动生成：memoryday-${COS_STORAGE_SUFFIX}
  ```

### 私有读写存储桶支持

存储桶权限设置为**私有读写**时，所有文件访问都需要签名URL：

- **启用签名URL**: `COS_USE_SIGNED_URL=True`
- **默认签名有效期**: `COS_DEFAULT_EXPIRES=3600` (1小时)

## 使用方式

### 1. 前端使用

#### 获取图片URL
```javascript
const cosService = getCosService()

// 获取单个图片的签名URL
const imageUrl = await cosService.getImageUrl('images/avatar.jpg', {
  thumbnail: true // 可选：生成缩略图
})

// 批量获取签名URL
const urls = await cosService.getSignedUrls(['image1.jpg', 'image2.jpg'], {
  style: 'thumbnail' // 可选：缩略图
})
```

#### 上传图片
```javascript
const result = await cosService.uploadImage(filePath, fileName, folder)
console.log(result.url) // 自动返回签名URL
```

### 2. 后端API接口

#### 获取签名URL
```bash
POST /cos/signed-url/

{
  "file_key": "images/avatar.jpg",
  "expires": 3600,
  "style": "thumbnail" // 可选：original, thumbnail, preview, detail
}
```

#### 批量获取签名URL
```bash
POST /cos/batch-signed-urls/

{
  "file_keys": ["image1.jpg", "image2.jpg"],
  "expires": 3600,
  "style": "thumbnail"
}
```

### 3. 图片处理样式

- **缩略图**: `thumbnail` - 200x200像素
- **预览图**: `preview` - 质量80%
- **详情图**: `detail` - 质量90%
- **原图**: `original` - 无处理

## 配置修改

### 修改存储桶后缀

如果需要更换存储桶，只需修改以下配置：

1. **前端** (`config/cos.js`):
   ```javascript
   const STORAGE_SUFFIX = '新的后缀值'
   ```

2. **后端** (`.env`):
   ```bash
   COS_STORAGE_SUFFIX=新的后缀值
   ```

### 禁用签名URL

如果存储桶改为"公有读私有写"，可以禁用签名URL：

```bash
COS_USE_SIGNED_URL=False
```

## 注意事项

1. **签名有效期**: 签名URL有有效期限制，过期后需要重新获取
2. **性能考虑**: 频繁获取签名URL会增加后端负载
3. **缓存策略**: 建议在前端缓存签名URL，避免重复请求
4. **降级处理**: 如果签名URL获取失败，会返回无签名URL（显示403错误）

## 错误处理

### 常见错误

- **403 Forbidden**: 无签名URL或签名过期
- **404 Not Found**: 文件不存在
- **500 Internal Error**: 后端服务异常

### 降级方案

系统会自动降级到无签名URL，确保基本功能可用：

```javascript
// 如果签名URL获取失败，返回无签名URL
// 用户会看到403错误，但不会导致应用崩溃
```

## 测试建议

1. 上传图片并验证签名URL生成
2. 测试图片加载和显示
3. 验证签名过期后的重新获取机制
4. 测试批量获取签名URL功能