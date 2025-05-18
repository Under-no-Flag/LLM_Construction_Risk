<template>
  <div class="history-container dark-theme">
    <!-- ================= 页面标题 ================= -->
    <div class="tech-header">
      <el-icon><Clock /></el-icon>
      <h1>历史溯源与反馈</h1>
      <div class="glow-bar"></div>
    </div>

    <!-- ================= 查询区 ================= -->
    <el-card shadow="hover" class="filter-card">
      <template #header>
        <el-icon><Search /></el-icon>
        <span>条件筛选</span>
      </template>
      <el-form :inline="true" class="filter-form" @submit.prevent>
        <el-form-item label="隐患标题">
          <el-input v-model="query.title" placeholder="关键词" clearable />
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="query.dateRange"
            type="daterange"
            range-separator="-"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item label="处理状态">
          <el-select v-model="query.status" placeholder="全部" clearable style="width: 140px">
            <el-option label="待处理" value="待处理" />
            <el-option label="整改中" value="整改中" />
            <el-option label="已完成" value="已完成" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="search">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- ================= 左右布局 ================= -->
    <div class="main-layout">
      <!-- ========= 左侧：时间轴 ========= -->
      <el-card shadow="hover" class="timeline-card">
        <template #header>
          <el-icon><Tickets /></el-icon>
          <span>隐患处理全流程</span>
        </template>
        <el-timeline reverse>
          <el-timeline-item
            v-for="item in filteredLogs"
            :key="item.id"
            :timestamp="item.time"
            :icon="statusIcon(item.type)"
            :color="statusColor(item.type)"
            @click="selectLog(item)"
          >
            <b>{{ item.type }}</b> - {{ item.title }}
            <span class="clickable-detail">(查看)</span>
          </el-timeline-item>
        </el-timeline>
      </el-card>

      <!-- ========= 右侧：详情 + 反馈表单 ========= -->
      <div class="detail-pane">
        <el-card v-if="selectedLog" shadow="always" class="detail-card">
          <template #header>
            <el-icon><Document /></el-icon>
            <span>处理详情</span>
          </template>
          <p><strong>标题：</strong>{{ selectedLog.title }}</p>
          <p><strong>处理阶段：</strong>{{ selectedLog.type }}</p>
          <p><strong>责任人：</strong>{{ selectedLog.actor }}</p>
          <p><strong>内容：</strong>{{ selectedLog.content }}</p>
          <p><strong>时间：</strong>{{ selectedLog.time }}</p>
          <!-- 附件列表 -->
          <el-divider>附件</el-divider>
          <el-link
            v-for="file in selectedLog.files"
            :key="file.name"
            :href="file.url"
            target="_blank"
            type="primary"
            style="margin-right: 12px;"
            >{{ file.name}}</el-link>
        </el-card>

        <!-- 反馈表单 -->
        <el-card shadow="always" class="feedback-card">
          <template #header>
            <el-icon><ChatLineSquare /></el-icon>
            <span>反馈 / 复核意见</span>
          </template>
          <el-form @submit.prevent>
            <el-form-item label="反馈人">
              <el-input v-model="feedbackForm.author" placeholder="您的姓名" />
            </el-form-item>
            <el-form-item label="意见描述">
              <el-input
                v-model="feedbackForm.comment"
                type="textarea"
                :rows="4"
                placeholder="请输入复核意见或补充说明"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :icon="Position" @click="submitFeedback"
                >提交反馈</el-button
              >
            </el-form-item>
          </el-form>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Search,
  Clock,
  Tickets,
  Document,
  ChatLineSquare,
  Position,
  Warning,
  Check,
  View,
  Edit,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

interface LogItem {
  id: number
  title: string
  type: '发现' | '整改' | '复核' | '关闭'
  actor: string
  time: string
  content: string
  files: { name: string; url: string }[]
}

// ---------- 模拟日志 ----------
const logs = ref<LogItem[]>([
  {
    id: 1,
    title: '施工点A存在施工安全隐患',
    type: '发现',
    actor: 'AI识别',
    time: '2025-05-18 08:20',
    content: '仅有 1 人戴安全帽，其余人员未佩戴;作业面在夜间、临边无任何防护栏杆或安全网;	未见系挂式安全带或水平生命线。',
    files: [],
  },
  {
    id: 2,
    title: '施工点A存在施工安全隐患',
    type: '整改',
    actor: '施工班组',
    time: '2025-05-18 11:00',
    content: '立即停止未佩戴安全帽人员的作业，全员配发合格安全帽；在作业面临边处设置高度≥1.2m的钢制防护栏杆（上中下三道横杆）。栏杆底部设18cm高挡脚板，防止工具坠落；通道设置LED警示灯带',
    files: [
      { name: '整改照片1.jpg', url: '#' },
      { name: '整改照片2.jpg', url: '#' },
      { name: '整改照片3.jpg', url: '#' },
    ],
  },
  {
    id: 3,
    title: '施工点A存在施工安全隐患',
    type: '复核',
    actor: '安全员李四',
    time: '2025-05-18 15:30',
    content: '现场复查合格，已签字确认。',
    files: [
        { name: '签字扫描件.pdf', url: '#' },
    ],
  },
  {
    id: 4,
    title: '施工点A存在施工安全隐患',
    type: '关闭',
    actor: '项目经理王五',
    time: '2025-05-19 09:00',
    content: '隐患已关闭并归档。',
    files: [],
  },
])

// ---------- 查询条件 ----------
const query = ref<{ title: string; dateRange: string[] | null; status: string | null }>(
  { title: '', dateRange: null, status: null }
)

function search() {
  ElMessage.success('查询已应用')
}

const filteredLogs = computed(() => {
  return logs.value.filter((l) => {
    const matchTitle = query.value.title
      ? l.title.includes(query.value.title)
      : true
    const matchStatus = query.value.status ? l.type === query.value.status : true
    // 日期范围可以进一步实现
    return matchTitle && matchStatus
  })
})

// ---------- 详情 & 反馈 ----------
const selectedLog = ref<LogItem | null>(null)
function selectLog(item: LogItem) {
  selectedLog.value = item
}

const feedbackForm = ref({ author: '', comment: '' })
function submitFeedback() {
  if (!selectedLog.value) {
    ElMessage.warning('请先选择一条日志进行反馈')
    return
  }
  ElMessage.success('反馈已提交')
  feedbackForm.value = { author: '', comment: '' }
}

// icon / color helper
function statusIcon(type: LogItem['type']) {
  switch (type) {
    case '发现':
      return Warning
    case '整改':
      return Edit
    case '复核':
      return View
    case '关闭':
      return Check
    default:
      return Document
  }
}
function statusColor(type: LogItem['type']) {
  switch (type) {
    case '发现':
      return '#ff4d4f'
    case '整改':
      return '#faad14'
    case '复核':
      return '#1890ff'
    case '关闭':
      return '#52c41a'
    default:
      return '#ccc'
  }
}
</script>

<style scoped>
.history-container {
  padding: 2rem;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.tech-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.tech-header h1 {
  margin: 0;
}
.filter-card {
  --el-color-primary: #00f3ff;
}
.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
}
.main-layout {
  display: flex;
  gap: 1rem;
}
.timeline-card {
  flex: 1 0 40%;
  max-width: 420px;
  overflow-y: auto;
  height: calc(100vh - 320px);
}
.detail-pane {
  flex: 1 0 60%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.cy-wrapper {
  width: 100%;
  height: 300px;
}
.clickable-detail {
  cursor: pointer;
  color: #00f3ff;
}
</style>
