<template>
  <el-container class="dashboard-container">
    <!-- 左侧侧边栏（深色） -->
    <el-aside width="260px" class="sidebar">
      <div class="sidebar-header">
        <h2>🏥 仁爱医院</h2>
        <p>病历管理系统</p>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        background-color="#1e293b"
        text-color="#e2e8f0"
        active-text-color="#ffffff"
        @select="handleMenuSelect"
      >
        <!-- 仪表盘（所有用户都有） -->
        <el-menu-item index="dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        
        <!-- 病历管理（所有用户都有） -->
        <el-menu-item index="records">
          <el-icon><Document /></el-icon>
          <span>病历管理</span>
        </el-menu-item>

<!-- AI问诊（仅医生） -->
<el-menu-item index="ai-assistant" v-if="userInfo.role === 'doctor'">
  <el-icon><Service /></el-icon>
  <span>AI问诊</span>
</el-menu-item>
        
        <!-- 医生管理（仅管理员） -->
        <el-menu-item index="doctors" v-if="userInfo.role === 'admin'">
          <el-icon><UserFilled /></el-icon>
          <span>医生管理</span>
        </el-menu-item>
      </el-menu>
      
      <div class="sidebar-footer">
        <el-avatar :size="40" :icon="UserFilled" style="background-color: #2563eb;" />
        <div class="user-info">
          <div class="user-name">{{ userInfo.name }}</div>
          <div class="user-role">{{ userInfo.role === 'admin' ? '系统管理员' : '主治医师' }}</div>
          <div class="user-dept">{{ userInfo.department }}</div>
        </div>
        <el-button type="danger" size="small" @click="handleLogout" style="width: 100%">
          退出登录
        </el-button>
      </div>
    </el-aside>

    <!-- 右侧主内容区 -->
    <el-main class="main-content">
      <!-- 根据角色和菜单显示不同内容 -->
      <DoctorDashboard 
        v-if="userInfo.role === 'doctor'"
        :active-tab="activeMenu"
      />
      
      <AdminDashboard 
        v-else
        :active-tab="activeMenu"
        @menu-change="handleMenuSelect"
      />
    </el-main>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataBoard, Document, UserFilled, Service} from '@element-plus/icons-vue'
import DoctorDashboard from './DoctorDashboard.vue'
import AdminDashboard from './AdminDashboard.vue'
import axios from 'axios'

const router = useRouter()
const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))
const activeMenu = ref('dashboard')

const handleMenuSelect = (index) => {
  activeMenu.value = index
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    delete axios.defaults.headers.common['Authorization']
    ElMessage.success('已退出登录')
    router.replace('/login')
  }).catch(() => {})
}
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
  background-color: #f8fafc;
  display: flex;
}

.sidebar {
  background-color: #1e293b;
  display: flex;
  flex-direction: column;
  height: 100%;
  box-shadow: 2px 0 8px rgba(0,0,0,0.1);
  width: 260px;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 24px 20px;
  border-bottom: 1px solid #334155;
}
.sidebar-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: white;
}
.sidebar-header p {
  margin: 4px 0 0;
  font-size: 0.85rem;
  color: #94a3b8;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  background-color: #1e293b;
}
.sidebar-menu :deep(.el-menu-item) {
  color: #e2e8f0;
}
.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #2563eb;
  color: white;
}
.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: #334155;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid #334155;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.user-info {
  text-align: center;
  width: 100%;
}
.user-name {
  font-weight: 500;
  color: white;
  font-size: 14px;
}
.user-role {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 2px;
}
.user-dept {
  font-size: 0.7rem;
  color: #64748b;
  margin-top: 2px;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  background-color: #f8fafc;
  padding: 20px;
}
</style>