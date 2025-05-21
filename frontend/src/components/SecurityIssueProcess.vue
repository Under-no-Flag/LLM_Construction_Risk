<template>
    <div class="hazard-container dark-theme">
        <!-- ================= 页面标题 ================= -->
        <div class="tech-header">
            <el-icon>
                <Collection />
            </el-icon>
            <h1>风险管控与隐患治理台账</h1>
            <div class="glow-bar"></div>
        </div>

        <!-- ================= 搜索折叠面板 ================= -->
        <el-collapse v-model="searchCollapse" class="filter-panel">
            <el-collapse-item name="1">
                <template #title>
                    <el-icon>
                        <Search />
                    </el-icon>搜索 / 过滤
                </template>
                <el-form :inline="true" class="filter-form">
                    <el-form-item label="标题">
                        <el-input v-model="searchTitle" placeholder="标题关键词" clearable style="width: 240px" />
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
                    </el-form-item>
                </el-form>
            </el-collapse-item>
        </el-collapse>

        <!-- ================= 工具栏 ================= -->
        <div class="table-toolbar">
            <el-button type="primary" :icon="Plus" @click="addHazard">添加风险隐患</el-button>
        </div>

        <!-- ================= 隐患列表 ================= -->
        <el-table :data="filteredList" stripe highlight-current-row class="hazard-table">
            <el-table-column type="index" label="#" width="60" />

            <el-table-column prop="title" label="标题" min-width="80">
                <template #default="scope">
                    <el-icon>
                        <Warning />
                    </el-icon>
                    <span>{{ scope.row.title }}</span>
                </template>
            </el-table-column>
            <el-table-column prop="description" label="隐患描述" min-width="250">
                <template #default="scope">
                    <span>{{ scope.row.description }}</span>
                </template>
            </el-table-column>

            <el-table-column prop="uploader" label="上传人" width="140">
                <template #default="scope">
                    <el-icon>
                        <User />
                    </el-icon>
                    {{ scope.row.uploader }}
                </template>
            </el-table-column>

            <el-table-column prop="status" label="处理状态" width="140">
                <template #default="scope">
                    <el-tag :type="statusTypeMap[scope.row.status]" effect="dark">{{ scope.row.status }}</el-tag>
                </template>
            </el-table-column>

            <el-table-column prop="updatedAt" label="更新时间" width="180" />

            <el-table-column label="操作" width="300">
                <template #default="scope">
                    <el-button size="small" link type="primary" :icon="View" @click="goDetail(scope.row)">详细</el-button>
                    <el-button size="small" link type="success" :icon="Paperclip" @click="downloadAttachment(scope.row)">附件</el-button>
                    <el-button size="small" link type="warning" :icon="Edit" @click="editHazard(scope.row)">编辑</el-button>
                    <el-popconfirm title="确认删除该隐患?" confirm-button-text="删除" cancel-button-text="取消" @confirm="deleteHazard(scope.row)">
                        <template #reference>
                            <el-button size="small" link type="danger" :icon="Delete">删除</el-button>
                        </template>
                    </el-popconfirm>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Search, Plus, View, Paperclip, Edit, Delete, Warning, User, Collection } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// -------------------- 数据 --------------------
// const hazardList = ref<HazardItem[]>([
//   {
//     id: 1,
//     title: '脚手架搭设不规范',
//     uploader: '张三',
//     status: '待处理',
//     updatedAt: '2025-05-18 09:30',
//   },
//   {
//     id: 2,
//     title: '配电箱门未关闭',
//     uploader: '李四',
//     status: '整改中',
//     updatedAt: '2025-05-17 15:20',
//   },
//   {
//     id: 3,
//     title: '裸露钢筋未做防护',
//     uploader: '王五',
//     status: '已完成',
//     updatedAt: '2025-05-16 11:00',
//   },
// ])

interface HazardItem {
    id: number
    title: string
    description: string
    uploader: string
    status: '待处理' | '整改中' | '已完成'
    updatedAt: string
}
const hazardList = ref<HazardItem[]>([])

// -------------------- 过滤 --------------------
const searchCollapse = ref<string[]>(['1'])
const searchTitle = ref('')
const filteredList = computed(() => {
    const key = searchTitle.value.trim()
    return key ? hazardList.value.filter((i) => i.title.includes(key)) : hazardList.value
})

// -------------------- 映射 --------------------
const statusTypeMap: Record<string, 'info' | 'warning' | 'success'> = {
    待处理: 'info',
    整改中: 'warning',
    已完成: 'success',
}

// -------------------- 事件 --------------------
const router = useRouter()
function handleSearch() {
    ElMessage.success('筛选已应用')
}
function addHazard() {
    ElMessage.info('添加风险隐患功能待实现')
}
function goDetail(row: HazardItem) {
    router.push({ name: 'hazard-process', params: { id: row.id } })
}
function downloadAttachment(row: HazardItem) {
    // 如果后端有附件下载 URL，可以直接 window.open
    window.open(`/api/hazard/${row.id}/attachments/`)
}
function editHazard(row: HazardItem) {
    router.push({ name: 'hazard-process', params: { id: row.id } })
}
function deleteHazard(row: HazardItem) {
    axios
        .delete(`/api/hazard/${row.id}/`)
        .then(() => {
            hazardList.value = hazardList.value.filter((i) => i.id !== row.id)
            ElMessage.success('删除成功')
        })
        .catch(() => ElMessage.error('删除失败'))
}

// —— 页面挂载后从后端拉列表 ——
onMounted(async () => {
    try {
        const resp = await axios.get('/api/hazards/')
        hazardList.value = resp.data.data
    } catch (e) {
        console.error(e)
        ElMessage.error('加载隐患列表失败')
    }
})
</script>

<style scoped>
.hazard-container {
    padding: 2rem;
    min-height: 100vh;
}

.tech-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1rem;
}
.tech-header h1 {
    margin: 0;
}

/* 折叠面板 */
.filter-panel {
    margin-bottom: 1rem;
    --el-color-primary: #00f3ff;
}
.filter-form {
    padding: 0.8rem 0 0.2rem 0.2rem;
}

/* 工具栏 */
.table-toolbar {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 0.6rem;
}

/* 表格行 hover */
.hazard-table ::v-deep .el-table__row {
    transition: background-color 0.15s ease;
}
.hazard-table ::v-deep .el-table__row:hover {
    background: rgba(0, 243, 255, 0.05);
}

/* 按钮色彩 */
.el-button.is-link {
    color: #0b1010;
}
</style>