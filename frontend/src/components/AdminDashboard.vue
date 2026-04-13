<template>
  <div class="admin-dashboard">
    
    <!-- ========== 运营看板（所有子视图） ========== -->
    <template v-if="activeTab === 'dashboard' || activeTab === 'dashboard-dept' || activeTab === 'dashboard-trend'">
      
      <!-- 欢迎语（只保留一个） -->
      <div class="welcome-banner">
        <h2>欢迎回来，{{ userInfo.name }}管理员！</h2>
        <p v-if="activeTab === 'dashboard'">实时监控 - 全院运营数据</p>
        <p v-if="activeTab === 'dashboard-dept'">科室运营 - 各科室病历分布与医生配置</p>
        <p v-if="activeTab === 'dashboard-trend'">趋势分析 - 全院病历变化趋势</p>
        <p>今天是 {{ currentDate }}，系统运行正常</p>
      </div>

      <!-- 统计卡片（仅实时监控显示） -->
      <el-row v-if="activeTab === 'dashboard'" :gutter="16" class="stats-row">
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-label">总病历数</div>
            <div class="stat-value">{{ overallStats.total_records || 0 }}</div>
            <div class="stat-trend" :class="getTrendClass(overallStats.total_trend)">
              {{ overallStats.total_trend > 0 ? '↑' : overallStats.total_trend < 0 ? '↓' : '→' }}
              {{ Math.abs(overallStats.total_trend || 0) }}%
              <span class="trend-compare">较上月</span>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-label">医生总数</div>
            <div class="stat-value">{{ overallStats.doctor_count || 0 }}</div>
            <div class="stat-trend" :class="getTrendClass(overallStats.doctor_trend)">
              {{ overallStats.doctor_trend > 0 ? '↑' : overallStats.doctor_trend < 0 ? '↓' : '→' }}
              {{ Math.abs(overallStats.doctor_trend || 0) }}%
              <span class="trend-compare">较上月</span>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-label">今日新增</div>
            <div class="stat-value">{{ overallStats.today_new || 0 }}</div>
            <div class="stat-trend" :class="getTrendClass(overallStats.today_trend)">
              {{ overallStats.today_trend > 0 ? '↑' : overallStats.today_trend < 0 ? '↓' : '→' }}
              {{ Math.abs(overallStats.today_trend || 0) }}%
              <span class="trend-compare">较昨日</span>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-label">本月新增</div>
            <div class="stat-value">{{ overallStats.month_new || 0 }}</div>
            <div class="stat-trend" :class="getTrendClass(overallStats.month_trend)">
              {{ overallStats.month_trend > 0 ? '↑' : overallStats.month_trend < 0 ? '↓' : '→' }}
              {{ Math.abs(overallStats.month_trend || 0) }}%
              <span class="trend-compare">较上月</span>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- ========== 实时监控视图 ========== -->
      <template v-if="activeTab === 'dashboard'">
        <!-- 近期病历列表（显示20条） -->
        <el-card shadow="hover" class="table-card">
          <template #header>
            <div class="table-header">
              <span style="font-weight: 600;">近期病历列表</span>
              <el-button type="primary" link @click="goToRecords">查看更多 >></el-button>
            </div>
          </template>
          <el-table :data="recentRecords" stripe v-loading="loading">
            <el-table-column prop="record_id" label="病历号" width="150" />
            <el-table-column prop="name" label="患者姓名" width="100" />
            <el-table-column prop="gender" label="性别" width="60" :formatter="(r) => r.gender === 'M' ? '男' : '女'" />
            <el-table-column prop="age" label="年龄" width="60" />
            <el-table-column prop="department" label="科室" width="100" />
            <el-table-column prop="admission_date" label="入院日期" width="120" />
            <el-table-column prop="diagnosis" label="诊断" show-overflow-tooltip />
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click.stop="viewRecord(row)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </template>

<!-- ========== 科室运营视图 ========== -->
<template v-if="activeTab === 'dashboard-dept'">
  
  <!-- 科室筛选 + 统计卡片 -->
  <el-card shadow="hover" class="stat-card" style="margin-bottom: 20px;">
    <template #header>
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-weight: 600;">科室统计</span>
        <el-select 
          v-model="selectedDeptForStats" 
          placeholder="选择科室" 
          clearable 
          style="width: 150px;"
          @change="loadDeptStatsData"
        >
          <el-option v-for="dept in departments" :key="dept" :label="dept" :value="dept" />
        </el-select>
      </div>
    </template>
    
    <el-row :gutter="16">
      <el-col :span="6">
        <div class="stat-label">科室病历总数</div>
        <div class="stat-value">{{ deptStatsData.total || 0 }}</div>
        <div class="stat-trend" :class="getTrendClass(deptStatsData.totalTrend)">
          {{ deptStatsData.totalTrend > 0 ? '↑' : deptStatsData.totalTrend < 0 ? '↓' : '→' }}
          {{ Math.abs(deptStatsData.totalTrend || 0) }}%
          <span class="trend-compare">较上月</span>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-label">科室医生数</div>
        <div class="stat-value">{{ deptStatsData.doctor_count || 0 }}</div>
        <div class="stat-trend" :class="getTrendClass(deptStatsData.doctor_trend)">
          {{ deptStatsData.doctor_trend > 0 ? '↑' : deptStatsData.doctor_trend < 0 ? '↓' : '→' }}
          {{ Math.abs(deptStatsData.doctor_trend || 0) }}%
          <span class="trend-compare">较上月</span>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-label">今日新增</div>
        <div class="stat-value">{{ deptStatsData.today_new || 0 }}</div>
        <div class="stat-trend" :class="getTrendClass(deptStatsData.today_trend)">
          {{ deptStatsData.today_trend > 0 ? '↑' : deptStatsData.today_trend < 0 ? '↓' : '→' }}
          {{ Math.abs(deptStatsData.today_trend || 0) }}%
          <span class="trend-compare">较昨日</span>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-label">本月新增</div>
        <div class="stat-value">{{ deptStatsData.month_new || 0 }}</div>
        <div class="stat-trend" :class="getTrendClass(deptStatsData.month_trend)">
          {{ deptStatsData.month_trend > 0 ? '↑' : deptStatsData.month_trend < 0 ? '↓' : '→' }}
          {{ Math.abs(deptStatsData.month_trend || 0) }}%
          <span class="trend-compare">较上月</span>
        </div>
      </el-col>
    </el-row>
  </el-card>

  <!-- 科室图表 -->
  <el-row :gutter="16">
    <el-col :span="12">
      <el-card shadow="hover" class="chart-card">
        <template #header>
          <span style="font-weight: 600;">各科室病历分布</span>
        </template>
        <div ref="barChart" class="chart" v-loading="chartLoading"></div>
      </el-card>
    </el-col>

    <el-col :span="12">
      <el-card shadow="hover" class="chart-card">
        <template #header>
          <span style="font-weight: 600;">各科室医生数量分布</span>
        </template>
        <div ref="doctorPieChart" class="chart" v-loading="doctorChartLoading"></div>
      </el-card>
    </el-col>
  </el-row>

  <!-- 科室同比变化 -->
  <el-row :gutter="16" style="margin-top: 16px;">
    <el-col :span="24">
      <el-card shadow="hover" class="chart-card">
        <template #header>
          <div style="display: flex; justify-content: space-between;">
            <span style="font-weight: 600;">各科室病历同比变化</span>
            <el-select v-model="yoyYear" size="small" style="width: 100px;" @change="loadYoYComparison">
              <el-option v-for="y in availableYears" :key="y" :label="y" :value="y" />
            </el-select>
          </div>
        </template>
        <div ref="yoyChart" class="chart" v-loading="yoyLoading"></div>
      </el-card>
    </el-col>
  </el-row>
</template>

      <!-- ========== 趋势分析视图 ========== -->
      <template v-if="activeTab === 'dashboard-trend'">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div style="display: flex; justify-content: space-between;">
              <span style="font-weight: 600;">全院病历趋势</span>
              <div>
                <el-radio-group v-model="trendTimeUnit" size="small" @change="onTimeUnitChange">
                  <el-radio-button value="day">日</el-radio-button>
                  <el-radio-button value="week">周</el-radio-button>
                  <el-radio-button value="month">月</el-radio-button>
                  <el-radio-button value="year">年</el-radio-button>
                </el-radio-group>
                <el-date-picker v-model="trendDateRange" type="daterange" size="small" style="width: 260px; margin-left: 12px;" @change="onDateRangeChange" />
              </div>
            </div>
          </template>
          <div ref="trendChart" class="chart" v-loading="trendLoading"></div>
        </el-card>
      </template>

    </template>

    <!-- ========== 病历管理（所有子视图） ========== -->
    <template v-if="activeTab === 'records' || activeTab === 'records-stats'">
      
      <!-- 病历检索视图 -->
      <template v-if="activeTab === 'records'">
        <div class="welcome-banner-mini">
          <h3>病历管理 - 全部科室</h3>
        </div>

        <el-card shadow="hover" class="table-card">
          <template #header>
            <div class="table-header">
              <span style="font-weight: 600;">全部病历列表</span>
              <div class="filter-group">
                <el-select 
                  v-model="selectedDept" 
                  placeholder="筛选科室" 
                  clearable 
                  style="width: 140px; margin-right: 12px"
                  @change="loadRecords"
                >
                  <el-option v-for="dept in departments" :key="dept" :label="dept" :value="dept" />
                </el-select>
                <el-input 
                  v-model="searchKeyword" 
                  placeholder="搜索病历号/患者..." 
                  prefix-icon="Search" 
                  style="width: 240px" 
                  clearable
                  @input="searchRecords"
                />
              </div>
            </div>
          </template>
          <el-table :data="records" stripe v-loading="loading">
            <el-table-column prop="record_id" label="病历号" width="150" />
            <el-table-column prop="name" label="患者姓名" width="100" />
            <el-table-column prop="gender" label="性别" width="60" :formatter="(r) => r.gender === 'M' ? '男' : '女'" />
            <el-table-column prop="age" label="年龄" width="60" />
            <el-table-column prop="department" label="科室" width="100" />
            <el-table-column prop="admission_date" label="入院日期" width="120" />
            <el-table-column prop="diagnosis" label="诊断" show-overflow-tooltip />
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click.stop="viewRecord(row)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :total="total"
              layout="prev, pager, next, total"
              background
              @current-change="loadRecords"
            />
          </div>
        </el-card>
      </template>

      <!-- 病历统计视图 -->
      <template v-if="activeTab === 'records-stats'">
        <div class="welcome-banner-mini">
          <h3>病历统计 - 疾病排行与药品分析</h3>
        </div>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>疾病排行榜 TOP10</template>
              <div ref="diseaseChart" style="height: 300px;"></div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>药品使用排行 TOP10</template>
              <div ref="drugChart" style="height: 300px;"></div>
            </el-card>
          </el-col>
        </el-row>
      </template>

    </template>

    <!-- ========== 医生管理（所有子视图） ========== -->
    <template v-if="activeTab === 'doctors' || activeTab === 'doctors-workload'">
      
      <!-- 医生列表视图 -->
      <template v-if="activeTab === 'doctors'">
        <div class="welcome-banner-mini">
          <h3>医生账号管理</h3>
        </div>

        <el-card shadow="hover" class="table-card">
          <template #header>
            <div class="table-header">
              <span style="font-weight: 600;">医生账号列表</span>
              <el-button type="primary" size="small" @click="showCreateDoctor = true">
                + 新增医生
              </el-button>
            </div>
          </template>
          <el-table :data="doctors" stripe v-loading="doctorLoading">
            <el-table-column prop="username" label="账号" width="150" />
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="department" label="科室" width="120" />
            <el-table-column prop="role" label="角色" width="100" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="danger" link @click="deleteDoctor(row)">删除</el-button>
                <el-button type="primary" link @click="resetPassword(row)">重置密码</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </template>

      <!-- 医生绩效视图 -->
      <template v-if="activeTab === 'doctors-workload'">
        <div class="welcome-banner-mini">
          <h3>医生绩效分析</h3>
          <p>医生接诊量排行与绩效统计</p>
        </div>

        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
              <span style="font-weight: 600;">医生接诊量排行</span>
              <div style="display: flex; gap: 8px;">
                <el-select v-model="workloadDeptFilter" placeholder="全部科室" clearable size="small" style="width: 110px;" @change="loadWorkloadRanking">
                  <el-option v-for="dept in departments" :key="dept" :label="dept" :value="dept" />
                </el-select>
                <el-input v-model="workloadDoctorSearch" placeholder="搜索医生姓名" size="small" style="width: 130px;" clearable @input="filterWorkloadData" />
                <el-date-picker v-model="workloadDateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" size="small" style="width: 220px;" :clearable="false" />
                <el-button type="primary" size="small" @click="handleQuery" :loading="workloadLoading">查询</el-button>
              </div>
            </div>
          </template>
          
          <div style="margin-bottom: 12px;">
            <el-radio-group v-model="workloadViewType" size="small" @change="onWorkloadViewChange">
              <el-radio-button value="chart">柱状图</el-radio-button>
              <el-radio-button value="table">表格</el-radio-button>
            </el-radio-group>
          </div>
          
          <div v-if="workloadViewType === 'chart'">
            <div ref="workloadChart" class="chart workload-chart" v-loading="workloadLoading"></div>
          </div>
          
          <div v-else>
            <el-table :data="filteredWorkloadData" stripe size="small" max-height="400">
              <el-table-column prop="rank" label="排名" width="60" align="center">
                <template #default="{ $index }">{{ $index + 1 }}</template>
              </el-table-column>
              <el-table-column prop="name" label="医生姓名" width="100" />
              <el-table-column prop="department" label="科室" width="100" />
              <el-table-column prop="count" label="接诊量" width="80" sortable>
                <template #default="{ row }">
                  <span style="font-weight: bold; color: #2563eb;">{{ row.count }}</span>
                </template>
              </el-table-column>
              <el-table-column label="占比" width="100">
                <template #default="{ row }">
                  <el-progress :percentage="getPercentage(row.count)" :stroke-width="8" :show-text="false" color="#2563eb" />
                  <span style="font-size: 12px;">{{ getPercentage(row.count) }}%</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="viewDoctorDetail(row)">详情</el-button>
                </template>
              </el-table-column>
            </el-table>
            <div style="margin-top: 12px; text-align: right;">
              共 {{ filteredWorkloadData.length }} 位医生，总接诊 {{ totalWorkload }} 人次
            </div>
          </div>

          <!-- 医生详情抽屉 -->
      <el-drawer v-model="showDoctorDetail" :title="`${selectedDoctor?.name} 医生接诊详情`" size="40%">
        <div v-if="selectedDoctor">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="医生姓名">{{ selectedDoctor.name }}</el-descriptions-item>
            <el-descriptions-item label="所属科室">{{ selectedDoctor.department }}</el-descriptions-item>
            <el-descriptions-item label="总接诊量">{{ selectedDoctor.count }} 人次</el-descriptions-item>
          </el-descriptions>
          <el-divider />
          <h4>近期接诊记录</h4>
<el-table :data="doctorRecentRecords" size="small" max-height="300" stripe>
  <el-table-column prop="admission_date" label="接诊日期" width="100" />
  <el-table-column prop="patient_name" label="患者姓名" width="100" />
  <el-table-column prop="diagnosis" label="诊断" show-overflow-tooltip />
</el-table>
        </div>
      </el-drawer>

        </el-card>
      </template>

    </template>

    <!-- 创建医生对话框 -->
    <el-dialog v-model="showCreateDoctor" title="新增医生账号" width="500px">
      <el-form :model="newDoctor" :rules="doctorRules" ref="doctorFormRef">
        <el-form-item label="账号" prop="username">
          <el-input v-model="newDoctor.username" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="newDoctor.name" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="newDoctor.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="科室" prop="department">
          <el-select v-model="newDoctor.department" style="width: 100%">
            <el-option v-for="dept in departments" :key="dept" :label="dept" :value="dept" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDoctor = false">取消</el-button>
        <el-button type="primary" @click="createDoctor" :loading="createLoading">创建</el-button>
      </template>
    </el-dialog>

    <!-- 病历详情抽屉 -->
    <el-drawer v-model="showDetail" title="病历详情" size="50%">
      <div v-loading="detailLoading" class="drawer-content">
        <div v-if="currentDetail">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="病历号">{{ currentDetail.record_id }}</el-descriptions-item>
            <el-descriptions-item label="姓名">{{ currentDetail.name }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ currentDetail.gender === 'M' ? '男' : '女' }}</el-descriptions-item>
            <el-descriptions-item label="年龄">{{ currentDetail.age }}</el-descriptions-item>
            <el-descriptions-item label="身份证">{{ currentDetail.id_card }}</el-descriptions-item>
            <el-descriptions-item label="入院日期">{{ currentDetail.admission_date }}</el-descriptions-item>
            <el-descriptions-item label="出院日期">{{ currentDetail.discharge_date }}</el-descriptions-item>
            <el-descriptions-item label="科室">{{ currentDetail.department }}</el-descriptions-item>
            <el-descriptions-item label="主治医生">{{ currentDetail.doctor_id }}</el-descriptions-item>
          </el-descriptions>

          <el-divider />
          <h4>诊断</h4>
          <p>{{ currentDetail.diagnosis }}</p>

          <h4>治疗项目</h4>
          <ul>
            <li v-for="item in currentDetail.treatments" :key="item">{{ item }}</li>
          </ul>

          <h4>处方</h4>
          <el-table :data="currentDetail.prescriptions" size="small">
            <el-table-column prop="drug" label="药品" />
          </el-table>

          <h4>检验结果</h4>
          <pre>{{ currentDetail.lab_results }}</pre>

          <h4>影像报告</h4>
          <p>{{ currentDetail.imaging_reports }}</p>

          <h4>备注</h4>
          <p>{{ currentDetail.notes }}</p>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, computed, watch } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  activeTab: {
    type: String,
    default: 'dashboard'
  }
})

const emit = defineEmits(['menu-change'])

const BASE_URL = 'http://127.0.0.1:8000/api'
const token = localStorage.getItem('token')
const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))

axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

// 当前日期
const currentDate = ref(new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }))

// 科室列表
const departments = ['心内科', '呼吸内科', '神经内科', '骨科', '普外科', '消化内科', '内分泌科']

// 总体统计
const overallStats = ref({
  total_records: 0,
  doctor_count: 0,
  today_new: 0,
  month_new: 0
})

// 科室统计
const deptStats = ref([])
const chartLoading = ref(false)

// 病历列表
const records = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const selectedDept = ref('')
const searchKeyword = ref('')
const loading = ref(false)

// 近期病历（最近5条）
const recentRecords = computed(() => records.value.slice(0, 5))

// 医生列表
const doctors = ref([])
const doctorLoading = ref(false)

// 创建医生
const showCreateDoctor = ref(false)
const createLoading = ref(false)
const doctorFormRef = ref(null)
const newDoctor = reactive({
  username: '',
  name: '',
  password: '',
  department: ''
})
const doctorRules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码至少6位', trigger: 'blur' }],
  department: [{ required: true, message: '请选择科室', trigger: 'change' }]
}

// 图表
const barChart = ref(null)
let barInstance = null

// 详情
const showDetail = ref(false)
const detailLoading = ref(false)
const currentDetail = ref(null)
let pianoClient = null

// 跳转到病历管理
const goToRecords = () => {
  emit('menu-change', 'records')
}

// 加载总体统计
// async function loadOverallStats() {
//   try {
//     const res = await axios.get(`${BASE_URL}/stats/overall`)
//     const current = res.data
    
//     // 获取上月数据
//     const lastMonthRes = await axios.get(`${BASE_URL}/stats/overall/lastmonth`)
//     const lastMonth = lastMonthRes.data
    
//     // 获取昨日数据
//     const yesterdayRes = await axios.get(`${BASE_URL}/stats/overall/yesterday`)
//     const yesterday = yesterdayRes.data
    
//     overallStats.value = {
//       ...current,
//       total_trend: lastMonth.total_records ? ((current.total_records - lastMonth.total_records) / lastMonth.total_records * 100).toFixed(1) : 0,
//       doctor_trend: lastMonth.doctor_count ? ((current.doctor_count - lastMonth.doctor_count) / lastMonth.doctor_count * 100).toFixed(1) : 0,
//       today_trend: yesterday.today_new ? ((current.today_new - yesterday.today_new) / yesterday.today_new * 100).toFixed(1) : 0,
//       month_trend: lastMonth.month_new ? ((current.month_new - lastMonth.month_new) / lastMonth.month_new * 100).toFixed(1) : 0
//     }
//   } catch (err) {
//     console.error('加载统计失败:', err)
//   }
// }
async function loadOverallStats() {
  try {
    const [res, lastMonthRes, yesterdayRes] = await Promise.all([
      axios.get(`${BASE_URL}/stats/overall`),
      axios.get(`${BASE_URL}/stats/overall/lastmonth`),
      axios.get(`${BASE_URL}/stats/overall/yesterday`)
    ])
    
    const current = res.data
    const lastMonth = lastMonthRes.data
    const yesterday = yesterdayRes.data
    
    overallStats.value = {
      total_records: current.total_records,
      doctor_count: current.doctor_count,
      month_new: current.month_new,
      today_new: yesterday.today_new,  // ← 关键修复
      total_trend: lastMonth.total_records ? ((current.total_records - lastMonth.total_records) / lastMonth.total_records * 100).toFixed(1) : 0,
      doctor_trend: lastMonth.doctor_count ? ((current.doctor_count - lastMonth.doctor_count) / lastMonth.doctor_count * 100).toFixed(1) : 0,
      today_trend: yesterday.today_new ? ((yesterday.today_new - yesterday.today_new) / yesterday.today_new * 100).toFixed(1) : 0,
      month_trend: lastMonth.month_new ? ((current.month_new - lastMonth.month_new) / lastMonth.month_new * 100).toFixed(1) : 0
    }
  } catch (err) {
    console.error('加载统计失败:', err)
  }
}

// 加载科室统计和图表
async function loadDeptStats() {
  chartLoading.value = true
  try {
    const res = await axios.get(`${BASE_URL}/stats/department`)
    deptStats.value = res.data.stats
    initChart()
    loadDeptStatsData()
  } catch (err) {
    console.error('加载科室统计失败:', err)
  } finally {
    chartLoading.value = false
  }
}

async function loadRecords() {
  loading.value = true
  try {
    const params = {
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value,
      department: userInfo.value.role === 'doctor' ? userInfo.value.department : selectedDept.value
    }
    
    // 添加搜索关键词
    if (searchKeyword.value && searchKeyword.value.trim()) {
      params.search = searchKeyword.value.trim()
    }
    
    const res = await axios.get(`${BASE_URL}/records/list`, { params })
    records.value = res.data.records
    total.value = res.data.total
  } catch (err) {
    console.error('加载病历列表失败:', err)
    ElMessage.error('加载病历列表失败')
  } finally {
    loading.value = false
  }
}

// 加载医生列表
async function loadDoctors() {
  doctorLoading.value = true
  try {
    const res = await axios.get(`${BASE_URL}/users/list`)
    doctors.value = res.data.users
  } catch (err) {
    console.error('加载医生列表失败:', err)
  } finally {
    doctorLoading.value = false
  }
}

// 创建医生
async function createDoctor() {
  if (!doctorFormRef.value) return
  
  await doctorFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    createLoading.value = true
    try {
      await axios.post(`${BASE_URL}/admin/create-user`, {
        username: newDoctor.username,
        password: newDoctor.password,
        name: newDoctor.name,
        department: newDoctor.department
      })
      ElMessage.success('医生账号创建成功')
      showCreateDoctor.value = false
      loadDoctors()
      loadOverallStats()
      Object.assign(newDoctor, { username: '', name: '', password: '', department: '' })
    } catch (err) {
      ElMessage.error(err.response?.data?.detail || '创建失败')
    } finally {
      createLoading.value = false
    }
  })
}

// 删除医生
async function deleteDoctor(row) {
  ElMessageBox.confirm(`确定要删除医生 ${row.name} 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await axios.delete(`${BASE_URL}/admin/delete-user/${row.id}`)
      ElMessage.success('删除成功')
      loadDoctors()
      loadOverallStats()
    } catch (err) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

// 重置密码
async function resetPassword(row) {
  ElMessageBox.prompt('请输入新密码', '重置密码', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputType: 'password',
    inputPattern: /^.{6,}$/,
    inputErrorMessage: '密码至少6位'
  }).then(async ({ value }) => {
    try {
      await axios.post(`${BASE_URL}/admin/reset-password/${row.id}`, { password: value })
      ElMessage.success('密码重置成功')
    } catch (err) {
      ElMessage.error('重置失败')
    }
  }).catch(() => {})
}

// 搜索
function searchRecords() {
  currentPage.value = 1
  loadRecords()
}

//各科室病历趋势
function initChart() {
  nextTick(() => {
    if (!barChart.value) return
    if (barInstance) barInstance.dispose()
    
    barInstance = echarts.init(barChart.value)
    
    const departmentNames = deptStats.value.map(s => s.department)
    const counts = deptStats.value.map(s => s.total)
    
    // 按数量排序（从高到低）
    const sorted = departmentNames.map((name, i) => ({ name, count: counts[i] }))
      .sort((a, b) => b.count - a.count)
    
    const sortedNames = sorted.map(s => s.name)
    const sortedCounts = sorted.map(s => s.count)
    
    // 定义每个科室的颜色（五颜六色）
    const colorPalette = [
      '#3b82f6', // 蓝色
      '#10b981', // 绿色
      '#f59e0b', // 橙色
      '#ef4444', // 红色
      '#8b5cf6', // 紫色
      '#ec489a', // 粉色
      '#06b6d4', // 青色
      '#84cc16', // 黄绿色
      '#f97316', // 橘色
      '#d946ef', // 紫罗兰
      '#14b8a6', // 蓝绿色
      '#f43f5e', // 玫瑰红
      '#6366f1', // 靛蓝
      '#a855f7', // 紫色
      '#eab308'  // 金色
    ]
    
    // 为每个科室分配颜色
    const colors = sortedNames.map((name, index) => {
      return colorPalette[index % colorPalette.length]
    })
    
    barInstance.setOption({
      tooltip: { 
        trigger: 'axis', 
        axisPointer: { type: 'shadow' },
        formatter: '{b}<br/>病历数: {c} 例'
      },
      grid: {
        top: 30,
        bottom: 30,
        left: 100,
        right: 30,
        containLabel: true
      },
      xAxis: { 
        type: 'value', 
        name: '病历数 (例)', 
        nameLocation: 'middle', 
        nameGap: 35,
        axisLabel: { fontSize: 11 },
        splitLine: { lineStyle: { color: '#e2e8f0', type: 'dashed' } }
      },
      yAxis: { 
        type: 'category', 
        data: sortedNames,
        axisLabel: { 
          fontSize: 12,
          fontWeight: 500,
          color: '#1e293b'
        },
        axisLine: { show: false },
        axisTick: { show: false }
      },
      series: [{
        data: sortedCounts,
        type: 'bar',
        orientation: 'horizontal',
        itemStyle: {
          color: function(params) {
            // 根据数据索引返回对应颜色
            return colors[params.dataIndex]
          },
          borderRadius: [0, 8, 8, 0],
          shadowColor: 'rgba(0, 0, 0, 0.1)',
          shadowBlur: 4
        },
        barWidth: '60%',
        label: {
          show: true,
          position: 'right',
          formatter: '{c}',
          fontSize: 12,
          fontWeight: 'bold',
          color: '#1e293b'
        }
      }]
    })
  })
}

//查看病历详情
async function viewRecord(row) {
  console.log('=== [PIR模式] 开始查询病历详情 ===', row)
  showDetail.value = true
  detailLoading.value = true
  currentDetail.value = null

  try {
    const token = localStorage.getItem('token')
    
    // 1. 获取元数据
    const metaRes = await axios.get(`${BASE_URL}/meta`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const blockSize = metaRes.data.block_size
    
    // 2. 获取当前总记录数
    const totalRes = await axios.get(`${BASE_URL}/stats/total`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const totalSize = totalRes.data.total_records
    
    // 3. 加载预处理表（每次查询都重新获取，确保最新）
    let pianoTables = null
    try {
      const tablesRes = await axios.get(`${BASE_URL}/piano/tables`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      pianoTables = tablesRes.data
      console.log('[PIR] 加载预处理表成功，主表大小:', pianoTables.primary_table?.length)
    } catch (err) {
      console.warn('[PIR] 加载预处理表失败:', err)
    }
    
    // 4. 初始化或更新 PianoClient
    if (!pianoClient) {
      const { PianoClient } = await import('../utils/piano.js')
      pianoClient = new PianoClient(totalSize, blockSize, pianoTables)
    } else {
      pianoClient.updateCurrentSize(totalSize)
    }
    
    // 5. 生成查询
    const query = pianoClient.generateQuery(row.index)
    console.log('[PIR] 查询大小:', query.byteLength)
    
    // 6. 发送查询
    const response = await fetch(`${BASE_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/octet-stream',
        'Authorization': `Bearer ${token}`
      },
      body: query
    })
    
    if (!response.ok) throw new Error(`查询失败: ${response.status}`)
    
    const encryptedData = await response.arrayBuffer()
    console.log('[PIR] 收到加密响应，大小:', encryptedData.byteLength)
    
    // 7. 解密
    const plainData = pianoClient.decryptResponse(encryptedData)
    
    // 8. 解码 JSON
    let decodedText = new TextDecoder('utf-8').decode(new Uint8Array(plainData))
    decodedText = decodedText.replace(/\0/g, '').trim()
    
    // 提取 JSON
    const jsonMatch = decodedText.match(/\{[\s\S]*\}/)
    if (!jsonMatch) {
      throw new Error('无法提取 JSON 数据')
    }
    
    let cleanedText = jsonMatch[0]
    const lastBrace = cleanedText.lastIndexOf('}')
    if (lastBrace !== -1) {
      cleanedText = cleanedText.substring(0, lastBrace + 1)
    }
    
    console.log('[PIR] 解析后的 JSON:', cleanedText.substring(0, 200))
    
    const decoded = JSON.parse(cleanedText)
    
    // 9. 组装详情
    currentDetail.value = {
      record_id: decoded.record_id || row.record_id,
      name: decoded.name || row.name,
      gender: decoded.gender || row.gender,
      age: decoded.age || row.age,
      id_card: decoded.id_card || '未知',
      admission_date: decoded.admission_date || row.admission_date,
      discharge_date: decoded.discharge_date || '未出院',
      department: decoded.department || row.department,
      doctor_id: decoded.doctor_id || row.doctor_id,
      doctor_name: decoded.doctor_name || row.doctor_name,
      diagnosis: decoded.diagnosis || row.diagnosis || '暂无诊断',
      treatments: Array.isArray(decoded.treatments) ? decoded.treatments : (decoded.treatments ? [decoded.treatments] : []),
      prescriptions: Array.isArray(decoded.prescriptions) ? decoded.prescriptions : (decoded.prescriptions ? [{ drug: decoded.prescriptions }] : []),
      lab_results: decoded.lab_results || '暂无检验结果',
      imaging_reports: decoded.imaging_reports || '暂无影像报告',
      notes: decoded.notes || '暂无备注'
    }
    
    console.log('✅ [PIR] 数据加载成功')
    
  } catch (err) {
    console.error('❌ [PIR] 获取详情失败:', err)
    ElMessage.error('获取病历详情失败：' + err.message)
    currentDetail.value = { ...row, treatments: [], prescriptions: [], notes: '加载失败' }
  } finally {
    detailLoading.value = false
  }
}

onMounted(() => {
  loadOverallStats()
  loadDeptStats()
  loadRecords()
  loadDoctors()
  initDateRange()
  loadTrendData()
  initWorkloadDateRange()
  loadYoYComparison()
  initAvailableYears()
  window.addEventListener('resize', () => {
    trendInstance?.resize()
    doctorPieInstance?.resize()
    workloadInstance?.resize()
    yoyInstance?.resize()
  })
  
  // 只有当前是医生管理页面才加载医生图表
  if (props.activeTab === 'doctors') {
    nextTick(() => {
      loadDoctorDistribution()
      loadWorkloadRanking()
    })
  }
})

// 趋势图相关
const trendTimeUnit = ref('month')
const trendDateRange = ref([])
const trendChart = ref(null)
const trendLoading = ref(false)
let trendInstance = null

// 获取趋势样式类
const getTrendClass = (trend) => {
  if (trend > 0) return 'trend-up'
  if (trend < 0) return 'trend-down'
  return 'trend-zero'
}

// 初始化日期范围
const initDateRange = () => {
  const end = new Date()
  const start = new Date()
  if (trendTimeUnit.value === 'month') {
    start.setMonth(end.getMonth() - 5)
  } else if (trendTimeUnit.value === 'week') {
    start.setDate(end.getDate() - 6 * 7)
  } else if (trendTimeUnit.value === 'day') {
    start.setDate(end.getDate() - 29)
  } else if (trendTimeUnit.value === 'year') {
    start.setFullYear(end.getFullYear() - 2)
  }
  start.setHours(0, 0, 0, 0)
  trendDateRange.value = [start, end]
}

// 时间单位变化
const onTimeUnitChange = () => {
  initDateRange()
  loadTrendData()
}

// 日期范围变化
const onDateRangeChange = () => {
  loadTrendData()
}

// 加载趋势数据
async function loadTrendData() {
  if (!trendDateRange.value || trendDateRange.value.length !== 2) return
  
  trendLoading.value = true
  try {
    const params = {
      start_date: trendDateRange.value[0].toISOString().split('T')[0],
      end_date: trendDateRange.value[1].toISOString().split('T')[0],
      unit: trendTimeUnit.value
    }
    const res = await axios.get(`${BASE_URL}/stats/trend`, { params })
    updateTrendChart(res.data)
  } catch (err) {
    console.error('加载趋势数据失败:', err)
    ElMessage.error('加载趋势数据失败')
  } finally {
    trendLoading.value = false
  }
}

// 更新趋势图
function updateTrendChart(data) {
  nextTick(() => {
    if (!trendChart.value) return
    
    if (trendInstance) {
      trendInstance.dispose()
    }
    
    trendInstance = echarts.init(trendChart.value)
    
    // 格式化标签（周格式优化）
    let labels = data.labels
    if (data.unit === 'week') {
      labels = labels.map(label => {
        const match = label.match(/W(\d+)/)
        if (match) {
          return `第${parseInt(match[1])}周`
        }
        return label
      })
    }
    
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: function(params) {
          const point = params[0]
          return `${point.name}<br/>病历数: ${point.value} 条`
        }
      },
      grid: {
        top: 30,
        bottom: 30,
        left: 50,
        right: 30,
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: labels,
        axisLabel: {
          rotate: labels.length > 12 ? 45 : 0,
          interval: 0
        }
      },
      yAxis: {
        type: 'value',
        name: '病历数 (条)',
        nameLocation: 'middle',
        nameGap: 40
      },
      series: [{
        name: '病历数量',
        type: 'line',
        data: data.values,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          width: 3,
          color: '#2563eb'
        },
        areaStyle: {
          opacity: 0.2,
          color: '#2563eb'
        },
        itemStyle: {
          color: '#2563eb'
        },
        emphasis: {
          focus: 'series'
        }
      }]
    }
    
    trendInstance.setOption(option)
  })
}

// ========== 医生管理页面图表 ==========
// 科室医生分布饼图
const doctorPieChart = ref(null)
let doctorPieInstance = null
const doctorChartLoading = ref(false)

// 医生工作量排行榜
const workloadChart = ref(null)
let workloadInstance = null
const workloadLoading = ref(false)
const workloadDateRange = ref([])

// ========== 仪表盘页面图表 ==========
// 科室同比对比图
const yoyChart = ref(null)
let yoyInstance = null
const yoyLoading = ref(false)
const yoyYear = ref(new Date().getFullYear())
const availableYears = ref([])

// 初始化工作量日期范围（不设置默认值，显示全部）
const initWorkloadDateRange = () => {
  workloadDateRange.value = []  // 空数组表示不限制时间
}

// 加载科室医生分布图
async function loadDoctorDistribution() {
  // 非管理员不执行
  if (userInfo.value.role !== 'admin') return
  // 等待 DOM 渲染
  await nextTick()
  
  // 如果元素还不存在，延迟重试
 if (!doctorPieChart.value) {
  console.log('doctorPieChart 元素不存在，使用 DOM 查找')
  // 使用独立的 class 查找
  const chartDom = document.querySelector('.doctor-pie-chart')
  if (chartDom) {
    updateDoctorPieChartWithDom(chartDom)
  } else {
    console.log('1秒后重试...')
    setTimeout(() => loadDoctorDistribution(), 500)
  }
  return
}
  
  console.log('开始加载科室医生分布')
  doctorChartLoading.value = true
  try {
    const res = await axios.get(`${BASE_URL}/stats/doctor/distribution`)
    console.log('科室医生分布数据:', res.data)
    updateDoctorPieChart(res.data)
  } catch (err) {
    console.error('加载医生分布失败:', err)
  } finally {
    doctorChartLoading.value = false
  }
}

// 备用渲染函数
function updateDoctorPieChartWithDom(dom) {
  axios.get(`${BASE_URL}/stats/doctor/distribution`)
    .then(res => {
      const data = res.data
      if (window.doctorPieInstance) window.doctorPieInstance.dispose()
      window.doctorPieInstance = echarts.init(dom)
      window.doctorPieInstance.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c}人)' },
        legend: { orient: 'vertical', left: 'left' },
        series: [{
          type: 'pie',
          radius: '55%',
          data: data.map(item => ({ name: item.department, value: item.count })),
          label: { show: true, formatter: '{b}: {d}%' }
        }]
      })
      console.log('医生分布图渲染成功（备用方式）')
    })
    .catch(err => console.error('加载失败:', err))
}

// 更新医生分布饼图
function updateDoctorPieChart(data) {
  nextTick(() => {
    if (!doctorPieChart.value) return
    if (doctorPieInstance) doctorPieInstance.dispose()
    
    doctorPieInstance = echarts.init(doctorPieChart.value)
    
    const option = {
      tooltip: { 
        trigger: 'item', 
        formatter: '{b}: {d}% ({c}人)'
      },
      legend: { 
        orient: 'vertical', 
        left: 'left',
        formatter: (name) => {
          const item = data.find(d => d.department === name)
          return `${name} (${item?.count || 0}人)`
        }
      },
      series: [{
        type: 'pie',
        radius: '55%',
        center: ['50%', '50%'],
        data: data.map(item => ({ name: item.department, value: item.count })),
        label: { show: true, formatter: '{b}: {d}%' },
        emphasis: { scale: true }
      }]
    }
    doctorPieInstance.setOption(option)
  })
}

// 加载医生工作量排行榜
async function loadWorkloadRanking() {
  if (userInfo.value.role !== 'admin') return
  if (props.activeTab !== 'doctors' && props.activeTab !== 'doctors-workload') return
  
  workloadLoading.value = true
  try {
    const params = {
      limit: 1000
    }
    
    if (workloadDateRange.value && workloadDateRange.value.length === 2) {
      params.start_date = workloadDateRange.value[0].toISOString().split('T')[0]
      params.end_date = workloadDateRange.value[1].toISOString().split('T')[0]
    }
    
    if (workloadDeptFilter.value) {
      params.department = workloadDeptFilter.value
    }
    
    const res = await axios.get(`${BASE_URL}/stats/doctor/workload`, { params })
    
    workloadData.value = res.data
    totalWorkload.value = workloadData.value.reduce((sum, d) => sum + d.count, 0)
    
    // ⭐ 调用过滤，会自动更新当前视图
    filterWorkloadData()
    
  } catch (err) {
    console.error('加载工作量排行失败:', err)
  } finally {
    workloadLoading.value = false
  }
}

// 备用渲染函数
function updateWorkloadChartWithDom(dom) {
  axios.get(`${BASE_URL}/stats/doctor/workload`)
    .then(res => {
      const data = res.data
      if (window.workloadInstance) window.workloadInstance.dispose()
      window.workloadInstance = echarts.init(dom)
      window.workloadInstance.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { top: 30, bottom: 30, left: 100, right: 30 },
        xAxis: { type: 'value', name: '接诊量 (人)' },
        yAxis: { type: 'category', data: data.map(d => d.name) },
        series: [{
          type: 'bar',
          data: data.map(d => d.count),
          itemStyle: { color: '#2563eb', borderRadius: [0, 4, 4, 0] },
          label: { show: true, position: 'right' }
        }]
      })
      console.log('工作量排行图渲染成功（备用方式）')
    })
    .catch(err => console.error('加载失败:', err))
}

// 更新工作量排行柱状图（竖向）
function updateWorkloadChart() {
  nextTick(() => {
    if (!workloadChart.value) return
    if (workloadInstance) workloadInstance.dispose()
    
    workloadInstance = echarts.init(workloadChart.value)
    
    const data = filteredWorkloadData.value
    const names = data.map(item => item.name)
    const counts = data.map(item => item.count)
    
    console.log('渲染图表，医生数量:', names.length)
    
    // 如果没有数据，显示提示
    if (names.length === 0) {
      workloadInstance.setOption({
        title: {
          text: '暂无数据',
          left: 'center',
          top: 'center',
          textStyle: { color: '#999', fontSize: 14 }
        }
      })
      return
    }
    
    const option = {
      title: {
        text: workloadDeptFilter.value ? `${workloadDeptFilter.value}医生接诊量排行` : '全院医生接诊量排行',
        left: 'center',
        top: 0,
        textStyle: { fontSize: 14 }
      },
      tooltip: { 
        trigger: 'axis', 
        axisPointer: { type: 'shadow' }, 
        formatter: '{b}<br/>接诊量: {c} 人'
      },
      grid: { 
        top: 60, 
        bottom: 30, 
        left: 80, 
        right: 50,
        containLabel: true 
      },
      // 数据缩放 - 医生数量超过10个时显示滚动条（X轴滚动）
      dataZoom: names.length > 10 ? [
        {
          type: 'slider',
          show: true,
          start: 0,
          end: names.length > 20 ? 40 : 60,
          xAxisIndex: 0,
          bottom: 20
        },
        {
          type: 'inside',
          xAxisIndex: 0,
          zoomOnMouseWheel: true,
          moveOnMouseMove: true
        }
      ] : [],
      xAxis: { 
        type: 'category', 
        data: names, 
        axisLabel: { 
          fontSize: 11,
          rotate: names.length > 8 ? 45 : 0,
          interval: 0
        },
        axisLine: { show: true },
        axisTick: { show: true }
      },
      yAxis: { 
        type: 'value', 
        name: '接诊量 (人)', 
        nameLocation: 'middle', 
        nameGap: 45,
        axisLabel: { fontSize: 11 },
        splitLine: { lineStyle: { color: '#e2e8f0', type: 'dashed' } }
      },
      series: [{
        type: 'bar',
        data: counts,
        itemStyle: { 
          color: '#2563eb', 
          borderRadius: [4, 4, 0, 0],
          shadowColor: 'rgba(0,0,0,0.1)',
          shadowBlur: 4
        },
        label: { 
          show: true, 
          position: 'top', 
          formatter: '{c}',
          fontSize: 11,
          fontWeight: 'bold'
        },
        barWidth: '60%'
      }]
    }
    workloadInstance.setOption(option)
    
    // 点击图表查看医生详情
    workloadInstance.off('click')
    workloadInstance.on('click', (params) => {
      if (params.componentType === 'series') {
        const doctor = filteredWorkloadData.value[params.dataIndex]
        if (doctor) {
          viewDoctorDetail(doctor)
        }
      }
    })
  })
}

// 加载科室同比对比图
async function loadYoYComparison() {
  console.log('loadYoYComparison 被调用')
  console.log('yoyChart.value:', yoyChart.value)
  console.log('当前 activeTab:', props.activeTab)
  
  if (!yoyYear.value) return
  
  yoyLoading.value = true
  try {
    const res = await axios.get(`${BASE_URL}/stats/department/yoy`, { 
      params: { year: yoyYear.value }
    })
    console.log('同比数据返回:', res.data)
    console.log('科室数量:', res.data.departments?.length)
    console.log('今年数据:', res.data.current)
    console.log('去年数据:', res.data.last_year_counts)
    
    updateYoYChart(res.data)
  } catch (err) {
    console.error('加载同比数据失败:', err)
  } finally {
    yoyLoading.value = false
  }
}

// 初始化可选年份（当前年份往前推4年）
const initAvailableYears = () => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let i = currentYear - 4; i <= currentYear; i++) {
    years.push(i)
  }
  availableYears.value = years
}

// 更新同比对比图
function updateYoYChart(data) {
  nextTick(() => {
    if (!yoyChart.value) {
      console.warn('yoyChart 元素不存在')
      return
    }
    
    // 检查数据是否有效
    if (!data || !data.departments || data.departments.length === 0) {
      console.warn('同比数据为空')
      if (yoyInstance) yoyInstance.dispose()
      yoyInstance = echarts.init(yoyChart.value)
      yoyInstance.setOption({
        title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: '#999' } }
      })
      return
    }
    
    if (yoyInstance) yoyInstance.dispose()
    
    yoyInstance = echarts.init(yoyChart.value)
    
    // 计算同比增长率并生成颜色
    const growthColors = data.departments.map(dept => {
      const growth = data.growth[dept]
      if (growth > 0) return '#10b981'      // 正增长绿色
      if (growth < 0) return '#ef4444'      // 负增长红色
      return '#f59e0b'                      // 持平橙色
    })
    
    const option = {
      tooltip: { 
        trigger: 'axis', 
        axisPointer: { type: 'shadow' },
        formatter: function(params) {
          const point = params[0]
          const growth = data.growth[point.name]
          const lastYearCount = data.last_year_counts[point.dataIndex]
          const arrow = growth > 0 ? '↑' : growth < 0 ? '↓' : '→'
          const color = growth > 0 ? '#10b981' : growth < 0 ? '#ef4444' : '#f59e0b'
          return `
            <div style="font-weight: bold; margin-bottom: 4px;">${point.name}</div>
            <div>今年: <span style="color: #3b82f6; font-weight: bold;">${point.value}</span> 例</div>
            <div>去年: <span style="color: #94a3b8;">${lastYearCount}</span> 例</div>
            <div>同比增长: <span style="color: ${color};">${arrow} ${Math.abs(growth)}%</span></div>
          `
        }
      },
      legend: { 
        data: ['今年', '去年'],
        right: 10,
        top: 0
      },
      grid: { 
        top: 50, 
        bottom: 30, 
        left: 80, 
        right: 50,
        containLabel: true
      },
      xAxis: { 
        type: 'category', 
        data: data.departments, 
        axisLabel: { 
          rotate: 45, 
          interval: 0,
          fontSize: 11,
          margin: 10
        },
        axisLine: { lineStyle: { color: '#94a3b8' } }
      },
      yAxis: { 
        type: 'value', 
        name: '病历数 (例)', 
        nameLocation: 'middle', 
        nameGap: 45,
        axisLabel: { fontSize: 11 },
        splitLine: { lineStyle: { color: '#e2e8f0', type: 'dashed' } }
      },
      series: [
        {
          name: '今年',
          type: 'bar',
          data: data.current.map(item => item.count),
          itemStyle: { 
            color: '#3b82f6',
            borderRadius: [4, 4, 0, 0],
            shadowColor: 'rgba(0, 0, 0, 0.1)',
            shadowBlur: 4
          },
          barWidth: '35%',
          label: {
            show: true,
            position: 'top',
            formatter: '{c}',
            fontSize: 11,
            color: '#1e293b'
          }
        },
        {
          name: '去年',
          type: 'bar',
          data: data.last_year_counts,
          itemStyle: { 
            color: '#cbd5e1',
            borderRadius: [4, 4, 0, 0]
          },
          barWidth: '35%',
          label: {
            show: true,
            position: 'top',
            formatter: '{c}',
            fontSize: 11,
            color: '#64748b'
          }
        }
      ]
    }
    
    yoyInstance.setOption(option)
    console.log('同比图表渲染完成，科室数量:', data.departments.length)
  })
}

// 科室运营页面选中的科室
const selectedDeptForStats = ref('心内科')

// 科室统计数据
const deptStatsData = ref({
  total: 0,
  doctor_count: 0,
  today_new: 0,
  month_new: 0,
  totalTrend: 0,
  doctor_trend: 0,
  today_trend: 0,
  month_trend: 0
})


// 加载科室统计数据
async function loadDeptStatsData() {
  if (!selectedDeptForStats.value) return
  
  console.log('开始加载科室统计数据，科室:', selectedDeptForStats.value)
  
  try {
    // 1. 获取当前科室统计
    const statsRes = await axios.get(`${BASE_URL}/stats/department`)
    const deptStat = statsRes.data.stats?.find(s => s.department === selectedDeptForStats.value) || {}
    
    // 2. 获取科室医生数
    const doctorsRes = await axios.get(`${BASE_URL}/doctors/list`, {
      params: { department: selectedDeptForStats.value }
    })
    const doctorCount = doctorsRes.data.doctors?.length || 0
    
    // 3. 获取上月数据（用于总数和本月新增环比）
    let lastMonthTotal = 0
    let lastMonthNew = 0
    try {
      const lastMonthRes = await axios.get(`${BASE_URL}/stats/department/month`, {
        params: { department: selectedDeptForStats.value }
      })
      const lastMonth = lastMonthRes.data.stats?.[0] || {}
      lastMonthTotal = lastMonth.total || 0
      lastMonthNew = lastMonth.month || 0
    } catch (err) {
      console.warn('获取上月数据失败:', err)
    }
    
    // 4. 获取昨日数据（用于今日新增环比）
    let yesterdayNew = 0
    try {
      const yesterdayRes = await axios.get(`${BASE_URL}/stats/department/yesterday`, {
        params: { department: selectedDeptForStats.value }
      })
      yesterdayNew = yesterdayRes.data.stats?.[0]?.today || 0
    } catch (err) {
      console.warn('获取昨日数据失败:', err)
    }
    
    // 5. 计算环比
    const totalTrend = lastMonthTotal ? ((deptStat.total - lastMonthTotal) / lastMonthTotal * 100).toFixed(1) : 0
    const monthTrend = lastMonthNew ? ((deptStat.month - lastMonthNew) / lastMonthNew * 100).toFixed(1) : 0
    
    // 今日环比特殊处理（昨日为0的情况）
    let todayTrend = 0
    if (yesterdayNew === 0 && deptStat.today > 0) {
      todayTrend = 100
    } else if (yesterdayNew > 0) {
      todayTrend = ((deptStat.today - yesterdayNew) / yesterdayNew * 100).toFixed(1)
    }
    
    deptStatsData.value = {
      total: deptStat.total || 0,
      doctor_count: doctorCount,
      today_new: deptStat.today || 0,
      month_new: deptStat.month || 0,
      totalTrend: parseFloat(totalTrend),
      doctor_trend: 0,
      today_trend: parseFloat(todayTrend),
      month_trend: parseFloat(monthTrend)
    }
    
    console.log('科室统计数据:', deptStatsData.value)
  } catch (err) {
    console.error('加载科室统计数据失败:', err)
  }
}

// 医生接诊量排行相关
const workloadViewType = ref('chart')  // chart 或 table
const workloadData = ref([])           // 原始数据
const filteredWorkloadData = ref([])   // 筛选后的数据
const workloadDeptFilter = ref('')     // 科室筛选
const workloadDoctorSearch = ref('')   // 医生搜索
const totalWorkload = ref(0)           // 总接诊量
const workloadSortType = ref('count')  // 排序方式
const workloadSortOrder = ref('desc')  // 排序方向

// 医生详情
const showDoctorDetail = ref(false)
const selectedDoctor = ref(null)
const doctorTrendLoading = ref(false)
const doctorRecentRecords = ref([])
let doctorTrendInstance = null
const doctorTrendChart = ref(null)

// 筛选工作量数据
function filterWorkloadData() {
  let filtered = [...workloadData.value]
  
  // 科室筛选
  if (workloadDeptFilter.value) {
    filtered = filtered.filter(d => d.department === workloadDeptFilter.value)
  }
  
  // 医生姓名搜索
  if (workloadDoctorSearch.value) {
    const keyword = workloadDoctorSearch.value.toLowerCase()
    filtered = filtered.filter(d => d.name.toLowerCase().includes(keyword))
  }
  
  // 排序
  if (workloadSortType.value === 'count') {
    filtered.sort((a, b) => {
      if (workloadSortOrder.value === 'desc') return b.count - a.count
      return a.count - b.count
    })
  } else if (workloadSortType.value === 'name') {
    filtered.sort((a, b) => a.name.localeCompare(b.name))
  }
  
  // ⭐ 更新表格数据（无论当前是什么视图）
  filteredWorkloadData.value = filtered
  totalWorkload.value = filteredWorkloadData.value.reduce((sum, d) => sum + d.count, 0)
  
  // ⭐ 如果是图表视图，更新图表
  if (workloadViewType.value === 'chart') {
    if (workloadChart.value) {
      updateWorkloadChart()
    } else {
      // 如果元素不存在，等待一下再试
      nextTick(() => {
        if (workloadChart.value) {
          updateWorkloadChart()
        }
      })
    }
  }
}

// 按接诊量排序
function sortWorkloadByCount() {
  workloadSortType.value = 'count'
  workloadSortOrder.value = workloadSortOrder.value === 'desc' ? 'asc' : 'desc'
  filterWorkloadData()
  updateWorkloadChart()
}

// 按姓名排序
function sortWorkloadByName() {
  workloadSortType.value = 'name'
  workloadSortOrder.value = 'asc'
  filterWorkloadData()
  updateWorkloadChart()
}

// 视图切换
function onWorkloadViewChange() {
  if (workloadViewType.value === 'chart') {
    updateWorkloadChart()
  }
}

// 获取百分比
function getPercentage(count) {
  if (totalWorkload.value === 0) return 0
  return Math.round((count / totalWorkload.value) * 100)
}

// 查询按钮点击事件
const handleQuery = async () => {
  await loadWorkloadRanking()
  
  // 强制刷新图表
  if (workloadInstance) {
    workloadInstance.resize()
  }
}

// 查看医生详情
async function viewDoctorDetail(doctor) {
  console.log('查看医生详情:', doctor)
  
  selectedDoctor.value = doctor
  showDoctorDetail.value = true
  
  try {
    // 确保传递的是医生名字
    console.log('请求参数 - 医生名:', doctor.name)
    
    const recordsRes = await axios.get(`${BASE_URL}/records/list`, {
      params: {
        doctor_name: doctor.name,  // 确保这里是 doctor.name
        limit: 10,
        offset: 0
      }
    })
    
    console.log('API完整返回:', recordsRes.data)
    console.log('返回的记录数:', recordsRes.data.records?.length)
    
    // 打印每条记录的医生名，验证是否筛选成功
    recordsRes.data.records?.forEach((record, idx) => {
      console.log(`记录${idx + 1}: 患者=${record.name}, 医生=${record.doctor_name}`)
    })
    
    // 格式化记录
    doctorRecentRecords.value = (recordsRes.data.records || []).map(record => ({
      admission_date: record.admission_date,
      patient_name: record.name,
      diagnosis: record.diagnosis
    }))
    
  } catch (err) {
    console.error('加载医生详情失败:', err)
    doctorRecentRecords.value = []
  }
}

// 更新医生趋势图
function updateDoctorTrendChart(data) {
  nextTick(() => {
    if (!doctorTrendChart.value) return
    if (doctorTrendInstance) doctorTrendInstance.dispose()
    
    doctorTrendInstance = echarts.init(doctorTrendChart.value)
    
    doctorTrendInstance.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: data.months },
      yAxis: { type: 'value', name: '接诊量 (人)' },
      series: [{
        data: data.counts,
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.3 },
        lineStyle: { color: '#2563eb', width: 3 },
        symbol: 'circle',
        symbolSize: 8
      }]
    })
  })
}

// 监听 activeTab 变化
// watch(() => props.activeTab, (newVal) => {
//   if (newVal === 'dashboard') {
//     loadRecords()
//     loadOverallStats()
//     loadDeptStats()
//     loadYoYComparison()
//     loadTrendData()
//   }
//   if (newVal === 'records') {
//     loadRecords()
//   }
//   if (newVal === 'doctors') {
//     loadDoctors()
//     // 延迟一下加载图表，确保 DOM 已渲染
//     setTimeout(() => {
//       loadDoctorDistribution()
//       loadWorkloadRanking()
//     }, 100)
//   }
// })

watch(() => props.activeTab, (newVal) => {
  // 运营看板子视图
  if (newVal === 'dashboard' || newVal === 'dashboard-doctor' || newVal === 'dashboard-dept' || newVal === 'dashboard-trend') {
    if (newVal === 'dashboard') {
      loadRecords()
      loadOverallStats()
      loadDeptStats()
      loadTrendData()
      loadDeptStatsData()
    }
    if (newVal === 'dashboard-doctor') {
      loadWorkloadRanking()
    }
    if (newVal === 'dashboard-dept') {
      loadDeptStats()
      loadYoYComparison()
      loadDoctorDistribution()
    }
    if (newVal === 'dashboard-trend') {
      loadTrendData()
    }
  }
  // 病历管理子视图
  else if (newVal === 'records' || newVal === 'records-stats') {
    if (newVal === 'records') {
      loadRecords()
    }
    if (newVal === 'records-stats') {
      loadDeptStats()
    }
  }
  // 医生管理子视图
  else if (newVal === 'doctors' || newVal === 'doctors-workload') {
    if (newVal === 'doctors') {
      loadDoctors()
    }
    if (newVal === 'doctors-workload') {
      loadWorkloadRanking()
    }
  }
})


</script>


<style scoped>
.admin-dashboard {
  width: 100%;
}

.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 24px 32px;
  margin-bottom: 24px;
  color: white;
}
.welcome-banner h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
}
.welcome-banner p {
  margin: 0;
  opacity: 0.9;
}

.welcome-banner-mini {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 12px;
  padding: 16px 24px;
  margin-bottom: 20px;
  color: white;
}
.welcome-banner-mini h3 {
  margin: 0;
  font-size: 18px;
}

.stats-row {
  margin-bottom: 24px;
}
.stat-card {
  border-radius: 12px;
  text-align: center;
}
.stat-label {
  color: #64748b;
  font-size: 14px;
}
.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #1e293b;
  margin-top: 8px;
}

.chart-card {
  margin-bottom: 24px;
  border-radius: 12px;
}
.chart {
  height: 350px;
  width: 100%;
}

.table-card {
  border-radius: 12px;
}
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}
.filter-group {
  display: flex;
  align-items: center;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
.drawer-content {
  padding: 0 20px;
}
.drawer-content h4 {
  margin: 16px 0 8px;
  font-weight: 600;
}
.drawer-content pre {
  background: #f8fafc;
  padding: 12px;
  border-radius: 4px;
  white-space: pre-wrap;
}

.stat-trend {
  font-size: 12px;
  margin-top: 8px;
}
.trend-up {
  color: #10b981;
}
.trend-down {
  color: #ef4444;
}
.trend-zero {
  color: #94a3b8;
}
.trend-compare {
  color: #94a3b8;
  margin-left: 4px;
}
.chart-card .chart {
  height: 350px;
}
.charts-row {
  margin-top: 20px;
}
.chart-card .chart {
  height: 380px;
}
@media (max-width: 1200px) {
  .chart-card .chart {
    height: 320px;
  }
}
@media (max-width: 768px) {
  .charts-row .el-col {
    width: 100%;
    margin-bottom: 16px;
  }
}

</style>