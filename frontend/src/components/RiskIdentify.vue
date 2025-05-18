<template>
    <div class="risk-container dark-theme">
        <!-- 标题 -->
        <div class="tech-header">
            <h1>智慧施工风险识别系统</h1>
            <div class="glow-bar"></div>
        </div>
        <!-- 大模型选择组件 -->
        <div class="model-selector">
            <el-form :inline="true">
                <el-form-item label="选择大模型">
                    <el-select v-model="selectedModel" placeholder="请选择大模型" style="width: 220px">
                        <el-option label="Qwen2.5-VL-MAX " value="qwen-vl-max" />
                        <el-option label="Qwen2.5-VL-3B (Ollama)" value="qwen-vl-3b" />
                        <el-option label="Qwen2.5-VL-3B Finetune (Ollama)" value="qwen-vl-s" />
                    </el-select>
                </el-form-item>
            </el-form>
            <!-- 添加重新识别按钮 -->
            <el-button type="primary" @click="handleSuccess" style="margin-left: 2rem">
                <el-icon>
                    <UploadFilled />
                </el-icon>重新识别
            </el-button>
            <!-- 初始提示 -->
        </div>
        <div class="empty-tip">
            <p>上传施工现场图片开始安全分析</p>
        </div>
        <!-- 主内容区 -->
        <div class="main-content">
            <!-- 左侧上传区 -->
            <div class="upload-section">
                <!-- 上传区域 -->
                <el-upload class="tech-upload tiny" drag action="/api/upload_and_detect/" :show-file-list="false" :on-success="handleSuccess" :before-upload="beforeUpload" accept="image/*">
                    <div class="upload-area">
                        <div class="holographic-effect"></div>
                        <el-icon class="upload-icon">
                            <UploadFilled />
                        </el-icon>
                        <div class="upload-text">
                            <p class="tip-text">点击或拖拽上传施工图片到此区域</p>
                            <p class="support-text">支持 JPG/PNG 格式，大小不超过 10MB</p>
                        </div>
                    </div>
                </el-upload>

                <!-- 结果图片 -->
                <div class="image-display">
                    <img :src="imageUrl || defaultImg" class="display-image" :class="{ placeholder: !imageUrl }" />
                </div>
            </div>

            <!-- 右侧结果区 -->
            <div class="result-section">
                <!-- 加载状态 -->
                <div v-if="loading" class="loading-box">
                    <div class="radar-scan"></div>
                    <p>AI风险分析中...</p>
                </div>

                <!-- 分析结果 -->
                <div v-else-if="resultData" class="result-content">
                    <!-- 风险描述 -->
                    <div class="result-card danger">
                        <div class="card-header">
                            <el-icon class="card-icon">
                                <WarningFilled />
                            </el-icon>
                            <h3>识别到的风险</h3>
                        </div>
                        <div class="card-content">{{ resultData.riskDescription }}</div>
                    </div>

                    <!-- 法规依据 -->
                    <div class="result-card law">
                        <div class="card-header">
                            <el-icon class="card-icon">
                                <Document />
                            </el-icon>
                            <h3>相关法规依据</h3>
                        </div>
                        <div class="regulation-list">
                            <div v-for="(item, index) in resultData.regulations" :key="index" class="regulation-item">
                                <div class="law-title">《{{ item.title }}》</div>
                                <div class="law-content">{{ item.content }}</div>
                                <div class="law-code">标准号：{{ item.code }}</div>
                            </div>
                        </div>
                    </div>

                    <!-- 风险隐患提交按钮 -->
                    <el-button type="primary" class="submit-button" @click="submitHazard">提交所识别的风险隐患</el-button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { UploadFilled, WarningFilled, Document, Picture } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 模拟数据
const resultData = ref(null)
const imageUrl = ref('')
const loading = ref(false)
const defaultImg =
    'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjIwIiBoZWlnaHQ9IjIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjIwIiBoZWlnaHQ9IjIyMCIgZmlsbD0iI2ZmZiIgZmlsbC1vcGFjaXR5PSIwLjA1Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNnB4IiBmaWxsPSIjY2NjIj5ObyBJbWFnZTwvdGV4dD48L3N2Zz4='
const beforeUpload = (file) => {
    console.log('file', file)
    imageUrl.value = URL.createObjectURL(file)
    if (file.size > 10 * 1024 * 1024) {
        ElMessage.error('图片大小不能超过10MB')
        return false
    }

    loading.value = false

    return true
}
const selectedModel = ref('')

onMounted(() => {
    // 组件加载时的初始化操作
    // 例如：获取默认图片或其他数据
    // resultData.value = {
    //     riskDescription:
    //         '图片中可以看到仅有 1 人戴安全帽，其余人员未佩戴;作业面在夜间、临边无任何防护栏杆或安全网;	未见系挂式安全带或水平生命线',
    //     regulations: [
    //         {
    //             title: '建筑施工安全检查标准',
    //             code: 'JGJ59—2011',
    //             content: '第3.13.3 (1) 条：进入施工现场的人员必须正确佩戴安全帽',
    //         },
    //         {
    //             title: '建筑施工高处作业安全技术规范',
    //             code: ' JGJ 80-2016',
    //             content:
    //                 '第4.1.3条： 建筑物外围边沿处，对没有设置外脚手架的工程，应设置防护栏杆；对有外脚手架的工程，应采用密目式安全立网全封闭。密目式安全立网应设置在脚手架外侧立杆上，并应与脚手杆紧密连接。',
    //         },
    //         {
    //             title: '建设工程施工现场供用电安全规范',
    //             code: 'JGJ59—2011',
    //             content: '第3.13.3 (3) 条：高处作业人员应按规定系挂安全带。',
    //         },
    //     ],
    // }
    // imageUrl.value = '/src/statics/demo_images/1.png'
})

const handleSuccess = (response) => {
    // 模拟API响应

    // setTimeout(() => {
    //     resultData.value = {
    //         riskDescription: response.riskList, // 已经是数组
    //         regulations: response.regulations, // 同样是数组
    //     }
    //     loading.value = false
    // }, 10000)

    resultData.value = {
        riskDescription:
            '图片中可以看到工人们都佩戴了安全帽，但没有看到其他防护装备如手套、护目镜等;工人在搬运重物时没有使用适当的工具或设备，增加了受伤的风险;施工现场显得非常混乱，材料堆放杂乱，通道不清晰，增加了安全隐患',
        regulations: [
            {
                title: '中华人民共和国安全生产法',
                code: 'JGJ 80-2016',
                content:
                    '第42条：生产经营单位必须为从业人员提供符合国家标准或者行业标准的劳动防护用品，并监督、教育从业人员按照使用规则佩戴、使用',
            },
            {
                title: '建筑施工高处作业安全技术规范',
                code: 'GB 50870-2013',
                content: '第3.0.1条：施工现场应设置明显的安全标志和必要的安全防护设施',
            },
            {
                title: '建筑施工安全检查标准',
                code: 'JGJ59-2011',
                content: '第3.18.3条：施工现场应保持整洁，材料堆放整齐，通道畅通',
            },
        ],
    }
}
</script>

  <style scoped>
.dark-theme {
    background: #0a0e17;
    color: #fff;
    min-height: 100vh;
    padding: 2rem;
}

.tech-header {
    text-align: center;
    margin-bottom: 3rem;
    position: relative;
}

.glow-bar {
    width: 200px;
    height: 4px;
    background: linear-gradient(90deg, transparent, #00f3ff, transparent);
    margin: 1rem auto;
    border-radius: 2px;
    filter: blur(1px);
}

.main-content {
    display: flex; /* 横向排列 */
    align-items: flex-start; /* 顶端对齐，避免垂直错位 */
    gap: 2rem; /* 左右间距 */
    flex-wrap: wrap; /* 小屏幕可自动换行 */
}

.tech-upload {
    border: 2px dashed rgba(0, 163, 255, 0.3);
    border-radius: 12px;
    background: rgba(16, 24, 40, 0.8);
    transition: all 0.3s;
}

.tech-upload:hover {
    border-color: #00a3ff;
    box-shadow: 0 0 20px rgba(0, 163, 255, 0.2);
}

.upload-area {
    padding: 3rem;
    position: relative;
    overflow: hidden;
}

.holographic-effect {
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: conic-gradient(from 0deg at 50% 50%, #00f3ff22 0%, #0066ff44 25%, #00f3ff22 50%, #0066ff44 75%, #00f3ff22 100%);
    animation: rotate 10s linear infinite;
    opacity: 0.3;
}

@keyframes rotate {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

.upload-icon {
    font-size: 4rem;
    color: #00f3ff;
    margin-bottom: 1rem;
    filter: drop-shadow(0 0 8px #00a3ff66);
}

.image-preview {
    margin-top: 2rem;
    border-radius: 8px;
    overflow: hidden;
    position: relative;
}

.preview-image {
    width: 100%;
    border-radius: 8px;
    display: block;
}

.scanning-effect {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(to bottom, transparent 49%, #00f3ff33 50%, transparent 51%);
    animation: scan 3s linear infinite;
}

@keyframes scan {
    0% {
        transform: translateY(-100%);
    }
    100% {
        transform: translateY(100%);
    }
}

.result-card {
    background: rgba(16, 24, 40, 0.8);
    border: 1px solid #2d374d;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
}

.card-header {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
}

.card-icon {
    font-size: 1.5rem;
    margin-right: 0.8rem;
}

.danger .card-icon {
    color: #ff4d4f;
}

.law .card-icon {
    color: #00f3ff;
}

.regulation-item {
    background: rgba(255, 255, 255, 0.05);
    border-left: 3px solid #00f3ff;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 6px;
}

.law-title {
    color: #00f3ff;
    font-weight: bold;
    margin-bottom: 0.5rem;
}

.law-code {
    font-size: 0.9rem;
    color: #888;
    margin-top: 0.5rem;
}

.loading-box {
    text-align: center;
    padding: 3rem;
}

.radar-scan {
    width: 60px;
    height: 60px;
    margin: 0 auto 1rem;
    border: 3px solid #00f3ff;
    border-radius: 50%;
    position: relative;
}

.radar-scan::before {
    content: '';
    position: absolute;
    width: 80%;
    height: 80%;
    border: 2px solid #00f3ff;
    border-radius: 50%;
    top: 10%;
    left: 10%;
    animation: pulse 1.5s ease-out infinite;
}

.upload-section {
    width: 100%;
    max-width: 880px; /* 适当限制最大宽度，居中更好看 */
    margin-inline: auto;
    display: flex;
    flex-direction: column; /* 默认竖排 */
    gap: 1.5rem; /* 上下间距 */
    padding: 0 1rem; /* 侧边留白，避免贴边 */
}
.tech-upload.tiny {
    flex: 0 0 auto; /* 不被压缩 */
    width: 100%;

    aspect-ratio: 4 / 3; /* 高度随宽自动算；失效时 fallback 到… */
    max-height: 220px; /* …不超过 220px */
    border-radius: 8px;
    overflow: hidden;
}
.tech-upload.tiny .upload-area {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 0.5rem;
}
.display-image {
    flex: 1 1 auto; /* 可以被拉伸，占剩余空间 */
    width: 100%;
}
.image-display {
    width: 100%;
    height: auto;
    border-radius: 4px;
    object-fit: cover;
    border: 3px solid #00f3ff;
}

.result-section {
    flex: 1 1 300px;
    min-width: 0;
}
/* 占位图淡一点 */
.display-image.placeholder {
    filter: grayscale(1) opacity(0.4);
}

@keyframes pulse {
    0% {
        transform: scale(0.8);
        opacity: 1;
    }
    100% {
        transform: scale(2);
        opacity: 0;
    }
}

.upload-text {
    text-align: center;
    padding: 20px;
    margin: 15px 0;
    border: 2px dashed #d9d9d9;
    border-radius: 8px;
    color: #131212;
    transition: border-color 0.3s ease;
}

.model-selector {
    margin: 1.2rem 0 0.8rem;
    display: flex;
    justify-content: center;
}

/* 覆盖 Element Plus 组件内部文本颜色 */
.model-selector ::v-deep .el-form-item__label,
.model-selector ::v-deep .el-input__inner,
.model-selector ::v-deep .el-select-dropdown__item {
    color: #00f3ff;
}

/* 覆盖 Element Plus 主题主色及悬停边框色 */
.model-selector ::v-deep .el-select {
    --el-color-primary: #00f3ff;
    --el-border-color-hover: #00f3ff;
}

.empty-tip {
    margin-left: 15cm;
    color: #00f3ff;
    justify-content: center;
    text-align: center;
}

/* 提交按钮样式 */
.submit-button {
  margin-top: 1.5rem;
  background-color: #00f3ff;
  border-color: #00d4ff;
  color: #0a0e17;
  font-weight: 600;

}
.submit-button:hover {
  filter: brightness(1.1);
  text-align: center;
}
</style>