<template>
    <div class="kg-container dark-theme">
        <!-- 操作栏 -->
        <div class="control-bar">
            <el-button type="primary" @click="showCreateDialog">
                <el-icon>
                    <CirclePlus />
                </el-icon>新增节点
            </el-button>
            <el-select v-model="filterType" placeholder="筛选类型">
                <el-option label="全部" value="all" />
                <el-option label="事故案例" value="accident" />
                <el-option label="施工标准" value="standard" />
                <el-option label="法律法规" value="law" />
            </el-select>
        </div>

        <!-- 主内容区 -->
        <div class="main-content">
            <!-- 图谱可视化区域 -->
            <div ref="networkContainer" class="network-container"></div>

            <!-- 侧边信息面板 -->
            <div class="side-panel">
                <div v-if="selectedNode" class="node-info">
                    <h3>节点详情</h3>
                    <el-form label-width="80px">
                        <el-form-item label="节点名称">
                            <el-input v-model="selectedNode.label" />
                        </el-form-item>
                        <el-form-item label="节点类型">
                            <el-select v-model="selectedNode.type">
                                <el-option v-for="type in nodeTypes" :key="type.value" :label="type.label" :value="type.value" />
                            </el-select>
                        </el-form-item>
                        <el-form-item label="描述">
                            <el-input v-model="selectedNode.properties.description" type="textarea" rows="3" />
                        </el-form-item>
                        <div class="action-buttons">
                            <el-button type="primary" @click="updateNode">更新</el-button>
                            <el-button type="danger" @click="deleteNode">删除</el-button>
                        </div>
                    </el-form>
                </div>

                <!-- 节点列表 -->
                <div class="node-list">
                    <h3>知识节点列表</h3>
                    <el-scrollbar>
                        <div v-for="node in filteredNodes" :key="node.id" class="list-item" @click="focusNode(node.id)">
                            <div class="node-type" :style="getTypeStyle(node.type)">{{ getTypeLabel(node.type) }}</div>
                            {{ node.label }}
                        </div>
                    </el-scrollbar>
                </div>
            </div>
        </div>

        <!-- 新增节点对话框 -->
        <el-dialog v-model="createDialogVisible" title="创建新节点">
            <el-form :model="newNode">
                <el-form-item label="节点名称" required>
                    <el-input v-model="newNode.label" />
                </el-form-item>
                <el-form-item label="节点类型">
                    <el-select v-model="newNode.type">
                        <el-option v-for="type in nodeTypes" :key="type.value" :label="type.label" :value="type.value" />
                    </el-select>
                </el-form-item>
                <el-form-item label="描述">
                    <el-input v-model="newNode.description" type="textarea" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="createDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="createNode">创建</el-button>
            </template>
        </el-dialog>
    </div>
</template>

  <script setup>
import { ref, onMounted, computed } from 'vue'
import { Network } from 'vis-network'
import { DataSet } from 'vis-data'
import { ElMessage } from 'element-plus'

// 模拟数据 - 虚构案例
const nodes = new DataSet([
    // 事故案例
    {
        id: 1,
        label: '2023杭城高速路桥坍塌',
        type: 'accident',
        properties: {
            date: '2023-05-12',
            location: '杭州东交通枢纽',
            casualties: 3,
            description: '浇筑施工时支架失稳导致整体坍塌',
        },
        title: makeTitle({
            date: '2023‑05‑12',
            location: '杭州东交通枢纽',
            casualties: 3,
            description: '浇筑施工时支架失稳导致整体坍塌',
        }),
    },

    // 施工标准
    {
        id: 2,
        label: '高空作业防坠落规范',
        type: 'standard',
        properties: {
            code: 'GB 50870-2023',
            scope: '建筑高度超过2m的临边作业',
            description: '要求设置双道安全绳和防坠网',
        },
    },

    // 法律法规
    {
        id: 3,
        label: '建设工程质量管理条例',
        type: 'law',
        properties: {
            promulgator: '国务院',
            effectiveDate: '2022-01-01',
            description: '明确施工各方质量责任和义务',
        },
    },
])

const edges = new DataSet([
    { from: 1, to: 2, label: '违反标准' },
    { from: 1, to: 3, label: '法律追责' },
    { from: 2, to: 3, label: '依据法规' },
])

// 可视化网络
function makeTitle(p) {
    // p 就是 node.properties
    const lines = []
    Object.entries(p).forEach(([k, v]) => {
        lines.push(`${k}：${v}`)
    })
    return lines.join('\n')
}
const networkInstance = ref(null) // 保存 vis Network 对象
const networkContainer = ref(null) // 保存 DOM 容器
// 节点配置
const options = {
    autoResize: true,
    nodes: { shape: 'box', borderWidth: 2, font: { size: 16 }, margin: 10 },
    edges: { arrows: 'to', smooth: { type: 'continuous' } },
    physics: {
        stabilization: false, // 直接让 barnesHut 计算实时布局
        barnesHut: {
            gravitationalConstant: -9000, // 斥力更大 → 节点更分散
            centralGravity: 0.1,
            springLength: 350,
        },
    },
}

// 节点类型配置
const nodeTypes = [
    { value: 'accident', label: '事故案例', color: '#ff4d4f' },
    { value: 'standard', label: '施工标准', color: '#00f3ff' },
    { value: 'law', label: '法律法规', color: '#52c41a' },
]

// 初始化网络
onMounted(() => {
    networkInstance.value = new Network(networkContainer.value, { nodes, edges }, options)

    /* ① 监听 stabilized 事件再 fit，可以避免动画过程中频繁缩放 */
    networkInstance.value.once('stabilized', () => {
        networkInstance.value.fit({ animation: { duration: 500 } })
    })

    /* ② 点击节点之后，同样先 focus 再微调 fit（可选）*/
    networkInstance.value.on('click', (params) => {
        if (params.nodes.length) {
            selectedNode.value = nodes.get(params.nodes[0])
            networkInstance.value.focus(params.nodes[0], {
                scale: 1.1,
                animation: { duration: 300 },
            })
        }
    })
})

// 过滤节点
const filterType = ref('all')
const filteredNodes = computed(() => {
    return nodes.get().filter((node) => filterType.value === 'all' || node.type === filterType.value)
})

// 节点操作
const selectedNode = ref(null)
const createDialogVisible = ref(false)
const newNode = ref({ type: 'accident' })

const getTypeStyle = (type) => {
    const typeConfig = nodeTypes.find((t) => t.value === type)
    return { backgroundColor: typeConfig?.color }
}

const getTypeLabel = (type) => {
    return nodeTypes.find((t) => t.value === type)?.label
}

const showCreateDialog = () => {
    createDialogVisible.value = true
    newNode.value = { type: 'accident' }
}

const createNode = () => {
    const id = Math.max(...nodes.get().map((n) => n.id)) + 1
    nodes.add({
        id,
        label: newNode.value.label || '新节点',
        type: newNode.value.type,
        // properties: {
        //     description: newNode.value.description || '',
        // },
        properties: props,
        title: makeTitle(props), // 关键行
    })
    createDialogVisible.value = false
    ElMessage.success('节点创建成功')
}

const updateNode = () => {
    nodes.update(selectedNode.value)
    ElMessage.success('节点更新成功')
}

const deleteNode = () => {
    nodes.remove(selectedNode.value.id)
    edges.remove(edges.get().filter((e) => e.from === selectedNode.value.id || e.to === selectedNode.value.id))
    selectedNode.value = null
    ElMessage.success('节点已删除')
}

const focusNode = (id) => {
    if (!networkInstance.value) return
    networkInstance.value.focus(id, {
        scale: 1,
        animation: { duration: 500, easingFunction: 'easeInOutQuad' },
    })
}
</script>

  <style scoped>
.dark-theme {
    background: #0a0e17;
    color: #fff;
    height: 100vh;
    padding: 20px;
}

.main-content {
    display: flex;
    height: calc(100vh - 100px);
}

.network-container {
    flex: 1 1 auto; /* 可伸缩 */
    min-width: 600px; /* 最小 600px 宽 */
    min-height: 500px; /* 最小 500px 高 */
    border: 1px solid #24324a;
    border-radius: 8px;
    background: #05090e;
}

.side-panel {
    width: 350px;
    margin-left: 20px;
    padding: 15px;
    background: rgba(16, 24, 40, 0.8);
    border-radius: 8px;
}

.node-info {
    padding: 15px;
    border: 1px solid #2d374d;
    border-radius: 6px;
    margin-bottom: 20px;
}

.node-list .list-item {
    padding: 10px;
    margin: 5px 0;
    cursor: pointer;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
    display: flex;
    align-items: center;
}

.node-type {
    width: 80px;
    padding: 2px 8px;
    border-radius: 3px;
    margin-right: 10px;
    text-align: center;
    font-size: 12px;
}

.control-bar {
    margin-bottom: 20px;
    display: flex;
    gap: 10px;
}

:deep(.vis-network) {
    outline: none;
}

:deep(.vis-tooltip) {
    padding: 6px 10px !important;
    border-radius: 4px !important;
    white-space: pre-line !important; /* 保留换行 */
}
</style>