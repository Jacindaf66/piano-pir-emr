<template>
  <div class="doctor-dashboard">
    
    <!-- ========== 运营看板（所有子视图） ========== -->
    <template v-if="activeTab === 'dashboard' || activeTab === 'dashboard-profile' || activeTab === 'dashboard-dept' || activeTab === 'dashboard-trend'">
      
      <!-- 欢迎语（根据子视图显示不同标题） -->
      <div class="welcome-banner">
        <h2>欢迎回来，{{ userInfo.name }}医生！</h2>
        <p v-if="activeTab === 'dashboard'">实时监控 - 今日科室运营数据</p>
        <p v-if="activeTab === 'dashboard-profile'">个人中心 - 我的工作概况</p>
        <p v-if="activeTab === 'dashboard-dept'">科室运营 - 本科室病历统计</p>
        <p v-if="activeTab === 'dashboard-trend'">趋势分析 - 病历变化趋势</p>
        <p>科室：{{ userInfo.department }} | 今天是 {{ currentDate }}，祝您工作愉快！</p>
      </div>

      <!-- 统计卡片（所有子视图都显示） -->
      <el-row :gutter="16" class="stats-row">
        <el-col :span="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-label">本科室病历总数</div>
            <div class="stat-value">{{ deptStats.total || 0 }}</div>
            <div class="stat-trend" :class="getTrendClass(deptStats.totalTrend)">
              {{ deptStats.totalTrend > 0 ? '↑' : deptStats.totalTrend < 0 ? '↓' : '→' }} 
              {{ Math.abs(deptStats.totalTrend || 0) }}%
              <span class="trend-compare">较上月</span>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-label">本月新增</div>
            <div class="stat-value">{{ deptStats.month || 0 }}</div>
            <div class="stat-trend" :class="getTrendClass(deptStats.monthTrend)">
              {{ deptStats.monthTrend > 0 ? '↑' : deptStats.monthTrend < 0 ? '↓' : '→' }} 
              {{ Math.abs(deptStats.monthTrend || 0) }}%
              <span class="trend-compare">较上月</span>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-label">今日新增</div>
            <div class="stat-value">{{ deptStats.today || 0 }}</div>
            <div class="stat-trend" :class="getTrendClass(deptStats.todayTrend)">
              {{ deptStats.todayTrend > 0 ? '↑' : deptStats.todayTrend < 0 ? '↓' : '→' }} 
              {{ Math.abs(deptStats.todayTrend || 0) }}%
              <span class="trend-compare">较昨日</span>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- ========== 实时监控视图 ========== -->
      <template v-if="activeTab === 'dashboard'">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: 600;">{{ userInfo.department }}科室病历趋势</span>
              <div>
                <el-radio-group v-model="trendTimeUnit" size="small" @change="onTimeUnitChange">
                  <el-radio-button value="day">日</el-radio-button>
                  <el-radio-button value="week">周</el-radio-button>
                  <el-radio-button value="month">月</el-radio-button>
                  <el-radio-button value="year">年</el-radio-button>
                </el-radio-group>
                <el-date-picker
                  v-model="trendDateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  size="small"
                  style="width: 260px; margin-left: 12px;"
                  :clearable="false"
                  @change="onDateRangeChange"
                />
              </div>
            </div>
          </template>
          <div ref="trendChart" class="chart" v-loading="chartLoading"></div>
        </el-card>
      </template>

<!-- ========== 个人中心视图 ========== -->
<template v-if="activeTab === 'dashboard-profile'">
  
<!-- 顶部个人信息卡片 -->
<div class="profile-card-simple">
  <div class="profile-left">
    <!-- 头像：仅显示，不可点击 -->
    <div class="profile-avatar">
<el-avatar 
  :size="80" 
  :src="userAvatar" 
  class="profile-avatar-img"
  :style="{ backgroundColor: userAvatar ? 'transparent' : avatarColor }"
>
  <el-icon :size="40"><UserFilled /></el-icon>
</el-avatar>
    </div>
    <div class="profile-info">
      <h3>{{ profileForm.name || userInfo.name }}</h3>
      <div class="profile-meta">
        <span class="meta-item">🏥 {{ profileForm.department || userInfo.department }}</span>
        <span class="meta-item">{{ profileForm.title || '主治医师' }}</span>
        <span class="meta-item">📅 入职 {{ (profileForm.join_date || '2024-01-01').split('-')[0] }}年</span>
      </div>
    </div>
  </div>
  <div class="profile-right">
    <div class="welcome-text">
      <span class="greeting">{{ greetingText }}</span>
      <span class="emoji">😊</span>
    </div>
    <div class="date-text">{{ currentDate }}</div>
    <el-button type="primary" link size="small" class="profile-edit-btn" @click="showProfileEdit = true">
      <el-icon><Edit /></el-icon>
      个人资料
    </el-button>
  </div>
</div>

  <!-- 统计卡片区域（4个卡片） -->
  <el-row :gutter="20" class="stats-cards">
    <!-- 卡片1：总接诊量 -->
    <el-col :xs="24" :sm="12" :md="6">
      <div class="stat-card-item">
        <div class="stat-icon total-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ doctorStats.total || 0 }}</div>
          <div class="stat-label">总接诊量</div>
          <div class="stat-trend" :class="doctorStats.totalTrend > 0 ? 'trend-up' : doctorStats.totalTrend < 0 ? 'trend-down' : 'trend-zero'">
            {{ doctorStats.totalTrend > 0 ? '↑' : doctorStats.totalTrend < 0 ? '↓' : '→' }}
            {{ Math.abs(doctorStats.totalTrend) }}% 较上月
          </div>
        </div>
      </div>
    </el-col>

    <!-- 卡片2：本月接诊 -->
    <el-col :xs="24" :sm="12" :md="6">
      <div class="stat-card-item">
        <div class="stat-icon month-icon">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ doctorStats.month || 0 }}</div>
          <div class="stat-label">本月接诊</div>
          <div class="stat-trend" :class="doctorStats.monthTrend > 0 ? 'trend-up' : doctorStats.monthTrend < 0 ? 'trend-down' : 'trend-zero'">
            {{ doctorStats.monthTrend > 0 ? '↑' : doctorStats.monthTrend < 0 ? '↓' : '→' }}
            {{ Math.abs(doctorStats.monthTrend) }}% 较上月
          </div>
        </div>
      </div>
    </el-col>

    <!-- 卡片3：今日接诊 -->
    <el-col :xs="24" :sm="12" :md="6">
      <div class="stat-card-item">
        <div class="stat-icon today-icon">
          <el-icon><Sunrise /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ deptStats.today || 0 }}</div>
          <div class="stat-label">今日接诊</div>
          <div class="stat-trend" :class="deptStats.todayTrend > 0 ? 'trend-up' : deptStats.todayTrend < 0 ? 'trend-down' : 'trend-zero'">
            {{ deptStats.todayTrend > 0 ? '↑' : deptStats.todayTrend < 0 ? '↓' : '→' }}
            {{ Math.abs(deptStats.todayTrend) }}% 较昨日
          </div>
        </div>
      </div>
    </el-col>

    <!-- 卡片4：科室排名 -->
    <el-col :xs="24" :sm="12" :md="6">
      <div class="stat-card-item">
        <div class="stat-icon rank-icon">
          <el-icon><Trophy /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ doctorRank.rank || '-' }}</div>
          <div class="stat-label">科室排名</div>
          <div class="stat-rank-detail">全院第 {{ doctorRank.rank || '-' }} 名 / 共 {{ doctorRank.total || '-' }} 人</div>
        </div>
      </div>
    </el-col>
  </el-row>

  <!-- 图表和记录双栏布局 -->
  <el-row :gutter="20">
    <!-- 左侧：接诊趋势图 -->
    <el-col :xs="24" :lg="14">
      <div class="chart-card-wrapper">
        <div class="card-header">
          <div class="header-title">
            <el-icon><TrendCharts /></el-icon>
            <span>接诊趋势</span>
          </div>
          <div class="header-subtitle">近12个月接诊量变化</div>
        </div>
        <div class="chart-container">
          <div ref="doctorTrendChart" class="trend-chart" v-loading="doctorTrendLoading"></div>
        </div>
      </div>
    </el-col>

    <!-- 右侧：近期接诊记录 -->
    <el-col :xs="24" :lg="10">
      <div class="records-card-wrapper">
        <div class="card-header">
          <div class="header-title">
            <el-icon><List /></el-icon>
            <span>近期接诊记录</span>
          </div>
          <el-button type="primary" link size="small" @click="goToRecords">
            查看全部 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        <div class="records-list" v-if="doctorRecentRecords.length > 0">
          <div v-for="(record, idx) in doctorRecentRecords" :key="idx" class="record-item" @click="viewRecordById(record.record_id)">
            <div class="record-date">
              <div class="date-day">{{ record.admission_date?.split('-')[2] || '--' }}</div>
              <div class="date-month">{{ record.admission_date?.substring(5) || '--' }}</div>
            </div>
            <div class="record-info">
              <div class="record-name">{{ record.patient_name }}</div>
              <div class="record-diagnosis">{{ record.diagnosis || '暂无诊断' }}</div>
            </div>
            <div class="record-arrow">
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
        <div v-else class="empty-records">
          <el-empty description="暂无接诊记录" :image-size="100" />
        </div>
      </div>
    </el-col>
  </el-row>

  <!-- 个人资料编辑对话框 -->
  <el-dialog v-model="showProfileEdit" title="编辑个人资料" width="500px" :before-close="handleDialogClose">
    <el-form :model="profileForm" label-width="80px">
<el-form-item label="头像">
  <div class="avatar-editor">
    <!-- 头像预览 -->
    <div class="avatar-preview">
      <el-avatar :size="80" :src="userAvatar" :style="{ backgroundColor: avatarColor }">
        <el-icon :size="40"><UserFilled /></el-icon>
      </el-avatar>
      <div class="preview-tip">预览</div>
    </div>
    
    <!-- 颜色选择器 -->
    <div class="color-picker-section">
      <div class="section-title">背景颜色</div>
      <el-color-picker 
        v-model="avatarColor" 
        show-alpha 
        :predefine="predefineColors"
        @change="onColorChange"
      />
      <div class="color-value">当前色值：{{ avatarColor }}</div>
    </div>
    
    <!-- 上传图片 -->
    <div class="upload-section">
      <div class="section-title">自定义图片</div>
      <div class="upload-buttons">
        <el-button type="primary" @click="uploadAvatar">
          <el-icon><Upload /></el-icon>
          上传图片
        </el-button>
        <el-button @click="clearAvatarImage" :disabled="!userAvatar">
          <el-icon><Delete /></el-icon>
          清除图片
        </el-button>
      </div>
      <div class="upload-tip">支持 JPG、PNG 格式，建议使用正方形图片</div>
      <input type="file" ref="avatarInput" style="display: none" accept="image/jpeg,image/png" @change="handleAvatarChange" />
    </div>
  </div>
</el-form-item>
      <el-form-item label="姓名">
        <el-input v-model="profileForm.name" disabled />
      </el-form-item>
      <el-form-item label="科室">
        <el-input v-model="profileForm.department" disabled />
      </el-form-item>
      <el-form-item label="职称">
        <el-select v-model="profileForm.title" placeholder="请选择职称">
          <el-option label="住院医师" value="住院医师" />
          <el-option label="主治医师" value="主治医师" />
          <el-option label="副主任医师" value="副主任医师" />
          <el-option label="主任医师" value="主任医师" />
        </el-select>
      </el-form-item>
      <el-form-item label="联系电话">
        <el-input v-model="profileForm.phone" placeholder="请输入联系电话" />
      </el-form-item>
      <el-form-item label="电子邮箱">
        <el-input v-model="profileForm.email" placeholder="请输入电子邮箱" />
      </el-form-item>
      <el-form-item label="入职日期">
        <el-date-picker v-model="profileForm.join_date" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
      </el-form-item>
      <el-form-item label="个人简介">
        <el-input v-model="profileForm.bio" type="textarea" :rows="3" placeholder="擅长领域、个人介绍等" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" @click="saveProfile">保存</el-button>
    </template>
  </el-dialog>
</template>

    </template>

    <!-- ========== 病历管理（所有子视图） ========== -->
    <template v-if="activeTab === 'records' || activeTab === 'records-stats'">
      
      <!-- 病历检索视图 -->
      <template v-if="activeTab === 'records'">
        <div class="welcome-banner-mini">
          <h3>病历管理 - {{ userInfo.department }}科室</h3>
        </div>

        <div class="action-bar">
          <el-button type="primary" @click="showCreateRecord = true">
            <el-icon><Plus /></el-icon>
            新建病历
          </el-button>
        </div>

        <el-card shadow="hover" class="table-card">
          <template #header>
            <div class="table-header">
              <span style="font-weight: 600;">病历列表</span>
              <el-input 
                v-model="searchKeyword" 
                placeholder="搜索病历号/患者..." 
                prefix-icon="Search" 
                style="width: 240px" 
                clearable
                @input="searchRecords"
              />
            </div>
          </template>
          <el-table :data="records" stripe v-loading="loading">
            <el-table-column prop="record_id" label="病历号" width="150" />
            <el-table-column prop="name" label="患者姓名" width="100" />
            <el-table-column prop="gender" label="性别" width="60" :formatter="(r) => r.gender === 'M' ? '男' : '女'" />
            <el-table-column prop="age" label="年龄" width="60" />
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

    <!-- ========== AI问诊 ========== -->
    <template v-if="activeTab === 'ai-assistant'">
      <div class="welcome-banner-mini">
        <h3>AI智能问诊助手</h3>
        <p>基于人工智能的诊断辅助系统</p>
      </div>
      
      <div class="ai-chat-container">
        <div class="ai-model-selector">
          <el-radio-group v-model="aiModel" size="small">
            <el-radio-button value="deepseek">DeepSeek</el-radio-button>
            <el-radio-button value="doubao">豆包</el-radio-button>
          </el-radio-group>
          <el-button size="small" @click="clearChat" :disabled="aiMessages.length === 1">
            <el-icon><Delete /></el-icon>
            清空对话
          </el-button>
        </div>
        
        <div class="chat-messages" ref="chatMessagesRef">
          <div v-for="(msg, idx) in aiMessages" :key="idx" :class="['message', msg.role]">
            <div class="message-avatar">
              <el-avatar :size="36" :icon="msg.role === 'user' ? UserFilled : Service" />
            </div>
            <div class="message-content">
              <div class="message-name">{{ msg.role === 'user' ? userInfo.name : '仁爱医助' }}</div>
              <div class="message-text" v-html="formatMessageText(msg.content)"></div>
              <div class="message-time">{{ msg.time }}</div>
            </div>
          </div>
          <div v-if="aiLoading" class="message assistant">
            <div class="message-avatar">
              <el-avatar :size="36" :icon="Service" />
            </div>
            <div class="message-content">
              <div class="message-name">仁爱医助</div>
              <div class="message-text typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="quick-inputs">
          <span class="quick-label">快捷输入：</span>
          <el-tag 
            v-for="tag in quickTags" 
            :key="tag"
            size="small"
            @click="addQuickInput(tag)"
          >
            {{ tag }}
          </el-tag>
        </div>
        
        <div class="chat-input">
          <el-input
            v-model="aiInput"
            type="textarea"
            :rows="3"
            placeholder="请描述患者症状、病史、检查结果等... (Ctrl + Enter 发送)"
            @keyup.enter.ctrl="sendMessage"
          />
          <div class="input-actions">
            <span class="input-hint">💡 支持自然语言描述，AI会为您分析诊断</span>
            <el-button type="primary" @click="sendMessage" :loading="aiLoading">
              <el-icon><Promotion /></el-icon>
              发送
            </el-button>
          </div>
        </div>
      </div>
    </template>

    <!-- 病历详情抽屉 -->
    <el-drawer v-model="showDetail" title="病历详情" size="50%">
      <div v-loading="detailLoading" class="drawer-content">
        <div v-if="currentDetail">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="病历号">{{ currentDetail.record_id }}</el-descriptions-item>
            <el-descriptions-item label="姓名">{{ currentDetail.name }}</el-descriptions-item>
            <el-descriptions-item label="性别">
              <el-tag size="small" :type="currentDetail.gender === 'M' ? 'primary' : 'danger'" effect="plain">
                {{ currentDetail.gender === 'M' ? '男' : '女' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="年龄">{{ currentDetail.age }}岁</el-descriptions-item>
            <el-descriptions-item label="身份证">{{ currentDetail.id_card || '未知' }}</el-descriptions-item>
            <el-descriptions-item label="入院日期">{{ currentDetail.admission_date || '未知' }}</el-descriptions-item>
            <el-descriptions-item label="出院日期">{{ currentDetail.discharge_date || '未出院' }}</el-descriptions-item>
            <el-descriptions-item label="科室">{{ currentDetail.department }}</el-descriptions-item>
            <el-descriptions-item label="主治医生">{{ currentDetail.doctor_id }} - {{ currentDetail.doctor_name }}</el-descriptions-item>
          </el-descriptions>

          <el-divider />
          
          <h4>诊断</h4>
          <p>{{ currentDetail.diagnosis || '暂无诊断' }}</p>

          <h4>治疗项目</h4>
          <ul>
            <li v-for="(item, idx) in currentDetail.treatments" :key="idx">{{ item }}</li>
            <li v-if="!currentDetail.treatments || currentDetail.treatments.length === 0">暂无治疗项目</li>
          </ul>

          <h4>处方</h4>
          <el-table :data="currentDetail.prescriptions" size="small" border style="width: 100%">
            <el-table-column prop="drug" label="药品" />
            <el-table-column prop="dosage" label="用量" v-if="currentDetail.prescriptions.length && currentDetail.prescriptions[0]?.dosage" />
          </el-table>
          <div v-if="!currentDetail.prescriptions || currentDetail.prescriptions.length === 0" class="empty-data">
            暂无处方
          </div>

          <h4>检验结果</h4>
          <pre class="pre-content">{{ currentDetail.lab_results || '暂无检验结果' }}</pre>

          <h4>影像报告</h4>
          <p>{{ currentDetail.imaging_reports || '暂无影像报告' }}</p>

          <h4>备注</h4>
          <p>{{ currentDetail.notes || '暂无备注' }}</p>
        </div>
      </div>
    </el-drawer>

    <!-- 创建病历对话框 -->
    <el-dialog v-model="showCreateRecord" title="新建病历" width="700px">
      <el-form :model="newRecord" :rules="recordRules" ref="recordFormRef" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="患者姓名" prop="name">
              <el-input v-model="newRecord.name" placeholder="请输入患者姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-select v-model="newRecord.gender" placeholder="请选择" style="width: 100%">
                <el-option label="男" value="M" />
                <el-option label="女" value="F" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="年龄" prop="age">
              <el-input-number v-model="newRecord.age" :min="0" :max="120" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="身份证号" prop="id_card">
              <el-input v-model="newRecord.id_card" placeholder="18位身份证号" />
            </el-form-item>
         </el-col>
        </el-row>
        
        <el-form-item label="科室" prop="department">
          <el-select v-model="newRecord.department" placeholder="请选择科室" @change="onDepartmentChange" style="width: 100%">
            <el-option v-for="dept in departments" :key="dept" :label="dept" :value="dept" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="主治医生" prop="doctor_id">
          <el-select v-model="newRecord.doctor_id" placeholder="请选择医生" style="width: 100%">
            <el-option v-for="doc in availableDoctors" :key="doc.id" :label="doc.name" :value="doc.id" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="入院日期" prop="admission_date">
          <el-date-picker v-model="newRecord.admission_date" type="date" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        
        <el-form-item label="诊断" prop="diagnosis">
          <el-input v-model="newRecord.diagnosis" type="textarea" :rows="2" placeholder="请输入诊断" />
        </el-form-item>
        
<el-form-item label="治疗项目">
  <el-select 
    v-model="newRecord.treatments" 
    multiple
    filterable
    allow-create
    default-first-option
    placeholder="请选择或输入治疗项目"
    style="width: 100%"
  >
    <el-option 
      v-for="item in treatmentOptions" 
      :key="item" 
      :label="item" 
      :value="item" 
    />
  </el-select>
</el-form-item>
        
        <el-form-item label="处方">
          <div v-for="(pres, idx) in newRecord.prescriptions" :key="idx" class="prescription-item">
            <el-input v-model="pres.drug" placeholder="药品名称" style="width: 40%" />
            <el-input v-model="pres.dosage" placeholder="用法用量" style="width: 40%; margin-left: 10px" />
            <el-button type="danger" link @click="removePrescription(idx)" style="margin-left: 10px">删除</el-button>
          </div>
          <el-button type="primary" link @click="addPrescription">+ 添加药品</el-button>
        </el-form-item>

        <el-form-item label="检验结果">
          <div v-for="(value, key) in newRecord.lab_results" :key="key" class="lab-item">
            <span style="width: 100px">{{ key }}：</span>
            <el-input v-model="newRecord.lab_results[key]" placeholder="结果值" style="width: 200px" />
            <el-button type="danger" link @click="delete newRecord.lab_results[key]">删除</el-button>
          </div>
          <div class="add-lab">
            <el-input v-model="newLabKey" placeholder="项目名称" style="width: 150px" />
            <el-input v-model="newLabValue" placeholder="结果值" style="width: 150px; margin-left: 10px" />
            <el-button type="primary" link @click="addLabItem" style="margin-left: 10px">添加</el-button>
          </div>
        </el-form-item>

        <el-form-item label="影像报告">
          <el-select 
            v-model="newRecord.imaging_reports" 
            placeholder="请选择或输入"
            filterable
            allow-create
            default-first-option
            style="width: 100%"
          >
            <el-option label="影像检查未见明显异常" value="影像检查未见明显异常" />
            <el-option label="CT 显示轻度肺炎" value="CT 显示轻度肺炎" />
            <el-option label="MRI 提示椎间盘突出" value="MRI 提示椎间盘突出" />
            <el-option label="X 光提示骨折愈合良好" value="X 光提示骨折愈合良好" />
            <el-option label="超声显示胆囊结石" value="超声显示胆囊结石" />
            <el-option label="心电图提示心肌缺血" value="心电图提示心肌缺血" />
          </el-select>
        </el-form-item>

        <el-form-item label="备注" prop="notes">
          <el-input v-model="newRecord.notes" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateRecord = false">取消</el-button>
        <el-button type="primary" @click="createRecord" :loading="createLoading">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch, onUnmounted, reactive, computed } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, MagicStick, ChatDotRound, CopyDocument, Document,
  Service, Promotion, UserFilled, Delete, User, OfficeBuilding, Message,
  Check, Calendar, Sunrise, TrendCharts, List, ArrowRight, Trophy,
  Camera, Edit, Upload,
} from '@element-plus/icons-vue'
import { marked } from 'marked'

//AI
// 配置 marked
marked.setOptions({
  breaks: true,  // 支持换行
  gfm: true      // GitHub Flavored Markdown
})

// 基础配置
const BASE_URL = 'http://127.0.0.1:8000/api'
const token = localStorage.getItem('token')
const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{"name":"未知","department":"未知","role":"doctor"}'))

// 请求头统一配置
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
axios.defaults.baseURL = BASE_URL

// AI 对话相关
const aiLoading = ref(false)
const aiModel = ref('doubao')  // 默认使用 doubao
const aiInput = ref('')
const chatMessagesRef = ref(null)

// AI 消息列表
const aiMessages = ref([
  {
    role: 'assistant',
    content: '您好，我是仁爱医助！👋\n\n请描述患者的症状、病史或检查结果，我会为您提供专业的诊断建议。\n\n您可以这样描述：\n• "患者发热38.5度，咳嗽3天，伴有头痛"\n• "高血压病史5年，最近头晕血压160/100"\n• "糖尿病患者，血糖控制不佳，空腹12.8"',
    time: new Date().toLocaleTimeString()
  }
])

// 快捷输入模板
const quickTags = [
  '发热38.5度，咳嗽3天，咳黄痰',
  '头痛头晕，血压160/100',
  '上腹痛，饭后加重，反酸',
  '腰痛放射至右腿，久坐加重',
  '胸闷气短，活动后明显',
  '糖尿病患者，血糖空腹12.8',
  '患者乏力、消瘦1个月'
]

const emit = defineEmits(['menu-change'])

// 跳转到病历管理页面
const goToRecords = () => {
  // 触发父组件切换菜单
  emit('menu-change', 'records')
}

// 根据病历ID查看详情
const viewRecordById = (recordId) => {
  const record = records.value.find(r => r.record_id === recordId)
  if (record) {
    viewRecord(record)
  }
}

// 医生排名
const doctorRank = ref({
  rank: 0,
  total: 0
})

// 用户头像（留空使用默认头像）
const userAvatar = ref('')

// 入职年份
const joinYear = ref('2023')

// 问候语
const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '凌晨好'
  if (hour < 12) return '早上好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  if (hour < 22) return '晚上好'
  return '夜深了'
})

// 个人资料编辑
const showProfileEdit = ref(false)
//头像文件上传
const avatarInput = ref(null)

// 个人资料表单
const profileForm = ref({
  name: userInfo.value.name || '',
  department: userInfo.value.department || '',
  title: '主治医师',
  phone: '',
  email: ''
})

// 更换头像（点击触发文件选择）
const changeAvatar = () => {
  avatarInput.value?.click()
}

// 保存个人资料111
const saveProfile = async () => {
  try {
    let avatarValue = profileForm.value.avatar
    // 如果有上传图片，用图片
    if (userAvatar.value) {
      avatarValue = userAvatar.value
    }
    
    const dataToSave = {
      title: profileForm.value.title,
      phone: profileForm.value.phone,
      email: profileForm.value.email,
      join_date: profileForm.value.join_date,
      bio: profileForm.value.bio,
      avatar: avatarValue
    }
    
    await axios.post(`${BASE_URL}/user/profile`, dataToSave)
    ElMessage.success('个人资料更新成功')
    showProfileEdit.value = false
    await loadUserProfile()
  } catch (err) {
    console.error('保存失败:', err)
    ElMessage.error('保存失败，请重试')
  }
}

// 加载个人资料111
const loadUserProfile = async () => {
  try {
    const res = await axios.get(`${BASE_URL}/user/profile`)
    console.log('加载个人资料:', res.data)
    
    profileForm.value = {
      name: res.data.name || userInfo.value.name,
      department: res.data.department || userInfo.value.department,
      gender: res.data.gender || '男',
      birth_date: res.data.birth_date || '',
      title: res.data.title || '主治医师',
      phone: res.data.phone || '',
      email: res.data.email || '',
      join_date: res.data.join_date || '',
      bio: res.data.bio || '',
      avatar: res.data.avatar || ''
    }
    
    // ⭐ 关键：同步主界面的头像颜色和图片
    if (res.data.avatar) {
      if (res.data.avatar.startsWith('data:image') || res.data.avatar.startsWith('http')) {
        userAvatar.value = res.data.avatar
        avatarColor.value = '#3b82f6'
      } else {
        // 颜色格式
        avatarColor.value = res.data.avatar
        userAvatar.value = ''
      }
    } else {
      avatarColor.value = '#3b82f6'
      userAvatar.value = ''
    }
    
    // console.log('主界面头像颜色:', avatarColor.value)
    // console.log('主界面头像图片:', userAvatar.value)
    
    if (res.data.join_date) {
      joinYear.value = res.data.join_date.split('-')[0]
    }
  } catch (err) {
    console.error('加载个人资料失败:', err)
  }
}

// 预定义颜色
const predefineColors = ref([
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
  '#8b5cf6', '#ec489a', '#06b6d4', '#84cc16',
  '#f97316', '#14b8a6', '#6366f1', '#a855f7'
])

// 头像颜色
const avatarColor = ref('#3b82f6')

// 颜色变化
const onColorChange = (color) => {
  userAvatar.value = ''
  avatarColor.value = color
  profileForm.value.avatar = color
  console.log('颜色已更改:', color)
}

// 清除图片
const clearAvatarImage = () => {
  userAvatar.value = ''
  profileForm.value.avatar = avatarColor.value
  ElMessage.info('已清除自定义图片')
}

// 上传头像
const uploadAvatar = () => {
  avatarInput.value?.click()
}

// 处理图片上传
const handleAvatarChange = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // 验证文件类型
  if (!file.type.includes('image')) {
    ElMessage.error('请选择图片文件')
    return
  }
  
  // 验证文件大小（限制2MB）
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过2MB')
    return
  }
  
  const reader = new FileReader()
  reader.onload = (e) => {
    userAvatar.value = e.target.result
    profileForm.value.avatar = e.target.result
    ElMessage.success('图片上传成功')
  }
  reader.onerror = () => {
    ElMessage.error('图片读取失败')
  }
  reader.readAsDataURL(file)
  
  // 清空input，允许重新上传同一文件
  event.target.value = ''
}

// 监听对话框关闭
const handleDialogClose = (done) => {
  // 检查是否有未保存的修改
  const hasChanges = originalProfileForm.value.title !== profileForm.value.title ||
                     originalProfileForm.value.phone !== profileForm.value.phone ||
                     originalProfileForm.value.email !== profileForm.value.email ||
                     originalProfileForm.value.join_date !== profileForm.value.join_date ||
                     originalProfileForm.value.bio !== profileForm.value.bio ||
                     originalProfileForm.value.avatar !== profileForm.value.avatar
  
  if (hasChanges) {
    ElMessageBox.confirm('您有未保存的修改，确定要关闭吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      // 用户点击确定，关闭对话框
      showProfileEdit.value = false
    }).catch(() => {
      // 用户点击取消，不关闭，恢复原数据
      profileForm.value = JSON.parse(JSON.stringify(originalProfileForm.value))
    })
  } else {
    // 没有修改，直接关闭
    showProfileEdit.value = false
  }
}

// 对话框关闭前的钩子（点击×或遮罩层时触发）
const handleBeforeClose = (done) => {
  const hasChanges = checkHasChanges()
  if (hasChanges) {
    ElMessageBox.confirm('您有未保存的修改，确定要关闭吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      // 用户点确定，关闭对话框
      done()
    }).catch(() => {
      // 用户点取消，不关闭
    })
  } else {
    // 没有修改，直接关闭
    done()
  }
}

// 取消按钮点击
const handleCancel = () => {
  const hasChanges = checkHasChanges()
  if (hasChanges) {
    ElMessageBox.confirm('您有未保存的修改，确定要取消吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      // 恢复原数据并关闭
      profileForm.value = JSON.parse(JSON.stringify(originalProfileForm.value))
      showProfileEdit.value = false
    }).catch(() => {
      // 用户点取消，什么都不做，对话框保持打开
    })
  } else {
    showProfileEdit.value = false
  }
}

// 检查是否有未保存的修改
const checkHasChanges = () => {
  return originalProfileForm.value.title !== profileForm.value.title ||
         originalProfileForm.value.phone !== profileForm.value.phone ||
         originalProfileForm.value.email !== profileForm.value.email ||
         originalProfileForm.value.join_date !== profileForm.value.join_date ||
         originalProfileForm.value.bio !== profileForm.value.bio ||
         originalProfileForm.value.avatar !== profileForm.value.avatar
}

// 保存原始数据的副本
const originalProfileForm = ref({})

// 添加快捷输入
function addQuickInput(text) {
  aiInput.value = text
}

// 发送消息
async function sendMessage() {
  if (!aiInput.value.trim() || aiLoading.value) return
  
  // 添加用户消息
  const userMsg = {
    role: 'user',
    content: aiInput.value,
    time: new Date().toLocaleTimeString()
  }
  aiMessages.value.push(userMsg)
  
  const userMessage = aiInput.value
  aiInput.value = ''
  aiLoading.value = true
  
  await nextTick()
  scrollToBottom()
  
  try {
    // 构建历史消息（最近10条，保留第一条欢迎语）
    const historyMessages = aiMessages.value
      .filter(m => m !== aiMessages.value[0])
      .slice(-10)
      .map(m => ({
        role: m.role,
        content: m.content
      }))
    
    const res = await axios.post(`${BASE_URL}/ai/chat`, {
      messages: historyMessages,
      model: aiModel.value
    })
    
    if (res.data.success) {
      aiMessages.value.push({
        role: 'assistant',
        content: res.data.content,
        time: new Date().toLocaleTimeString()
      })
    } else {
      throw new Error('AI响应失败')
    }
  } catch (err) {
    console.error('AI对话失败:', err)
    aiMessages.value.push({
      role: 'assistant',
      content: '抱歉，AI服务暂时不可用，请稍后重试。\n\n可能的原因：\n• 网络连接问题\n• API服务繁忙\n• 请检查后端服务是否正常运行',
      time: new Date().toLocaleTimeString()
    })
    ElMessage.error('AI服务调用失败')
  } finally {
    aiLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

// 清空对话
function clearChat() {
  aiMessages.value = [{
    role: 'assistant',
    content: '您好，我是仁爱医助！👋\n\n请描述患者的症状、病史或检查结果，我会为您提供专业的诊断建议。\n\n您可以这样描述：\n• "患者发热38.5度，咳嗽3天，伴有头痛"\n• "高血压病史5年，最近头晕血压160/100"\n• "糖尿病患者，血糖控制不佳，空腹12.8"',
    time: new Date().toLocaleTimeString()
  }]
  ElMessage.success('对话已清空')
}

// 滚动到底部
function scrollToBottom() {
  if (chatMessagesRef.value) {
    chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
  }
}

// 格式化消息文本
function formatMessageText(text) {
  if (!text) return ''
  
  // 使用 marked 渲染 Markdown
  try {
    let html = marked.parse(text)
    // 添加代码块样式
    html = html.replace(/<pre>/g, '<pre style="background:#f1f5f9;padding:12px;border-radius:8px;overflow-x:auto;">')
    return html
  } catch (e) {
    // 降级：简单处理换行
    return text.replace(/\n/g, '<br>')
  }
}

const props = defineProps({
  activeTab: {
    type: String,
    default: 'dashboard'
  }
})



// 日期
const currentDate = ref(new Date().toLocaleDateString('zh-CN', { 
  year: 'numeric', 
  month: 'long', 
  day: 'numeric',
  weekday: 'long'
}))

// 科室统计
const deptStats = ref({ total: 0, today: 0, month: 0 })

// 医生个人统计（用于个人中心）
const doctorStats = ref({
  total: 0,
  month: 0,
  totalTrend: 0,
  monthTrend: 0
})

// 医生接诊趋势
const doctorTrendLoading = ref(false)
const doctorTrendChart = ref(null)
let doctorTrendInstance = null

// 医生近期接诊记录
const doctorRecentRecords = ref([])

// 病历列表
const records = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchKeyword = ref('')
const loading = ref(false)
const chartLoading = ref(false)


// 详情
const showDetail = ref(false)
const detailLoading = ref(false)
const currentDetail = ref(null)
let pianoClient = null

// 新建病历
const departments = ref(['心内科', '呼吸内科', '神经内科', '骨科', '普外科', '消化内科', '内分泌科'])
const treatmentOptions = ref(['一级护理', '二级护理', '三级护理', '物理治疗', '药物治疗','康复训练', '针灸', '推拿'])
const showCreateRecord = ref(false)
const createLoading = ref(false)
const recordFormRef = ref(null)
const availableDoctors = ref([])
const selectedDept = ref('') // 修复未定义变量

const newRecord = reactive({
  name: '',
  gender: 'M',
  age: 30,
  id_card: '',
  department: '',
  doctor_id: '',
  admission_date: new Date(),
  diagnosis: '',
  treatments: [],
  prescriptions: [],
  lab_results: {},
  imaging_reports: '',
  notes: ''
})

const recordRules = {
  name: [{ required: true, message: '请输入患者姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  age: [{ required: true, message: '请输入年龄', trigger: 'blur' }],
  id_card: [{ required: true, message: '请输入身份证号', trigger: 'blur' }],
  department: [{ required: true, message: '请选择科室', trigger: 'change' }],
  doctor_id: [{ required: true, message: '请选择主治医生', trigger: 'change' }],
  admission_date: [{ required: true, message: '请选择入院日期', trigger: 'change' }],
  diagnosis: [{ required: true, message: '请输入诊断', trigger: 'blur' }]
}

// 新增检验项目的临时变量
const newLabKey = ref('')
const newLabValue = ref('')

// 添加检验项目
function addLabItem() {
  if (newLabKey.value && newLabValue.value) {
    newRecord.lab_results[newLabKey.value] = newLabValue.value
    newLabKey.value = ''
    newLabValue.value = ''
  }
}

// 加载科室统计
async function loadDeptStats() {
  try {
    const today = new Date().toISOString().split('T')[0]
    const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0]
    
    console.log('查询日期:', { today, yesterday })
    
    // 并行请求
    const [deptRes, todayRes, yesterdayRes, lastMonthRes] = await Promise.all([
      axios.get(`${BASE_URL}/stats/department`),
      axios.get(`${BASE_URL}/records/list`, {
        params: { admission_date: today, department: userInfo.value.department, limit: 1 }
      }),
      axios.get(`${BASE_URL}/records/list`, {
        params: { admission_date: yesterday, department: userInfo.value.department, limit: 1 }
      }),
      axios.get(`${BASE_URL}/stats/department/month`, {
        params: { department: userInfo.value.department }
      })
    ])
    
    const current = deptRes.data.stats?.[0] || {}
    const lastMonth = lastMonthRes.data.stats?.[0] || { total: 0, month: 0 }
    const todayNew = todayRes.data.total      // 今日新增
    const yesterdayNew = yesterdayRes.data.total  // 昨日新增（直接查询，最准确）
    
    console.log('今日新增:', todayNew, '昨日新增:', yesterdayNew)
    
    // 计算环比
    const totalTrend = lastMonth.total ? ((current.total - lastMonth.total) / lastMonth.total * 100).toFixed(1) : 0
    const monthTrend = lastMonth.month ? ((current.month - lastMonth.month) / lastMonth.month * 100).toFixed(1) : 0
    
    let todayTrend = 0
    if (yesterdayNew === 0 && todayNew > 0) {
      todayTrend = 100
    } else if (yesterdayNew > 0) {
      todayTrend = ((todayNew - yesterdayNew) / yesterdayNew * 100).toFixed(1)
    }
    
    deptStats.value = {
      total: current.total || 0,
      month: current.month || 0,
      today: todayNew,
      totalTrend: parseFloat(totalTrend),
      monthTrend: parseFloat(monthTrend),
      todayTrend: parseFloat(todayTrend)
    }
    
    console.log('最终统计:', deptStats.value)
  } catch (err) {
    console.error('加载科室统计失败:', err)
  }
}

// 加载医生个人统计数据
async function loadDoctorStats() {
  try {
    // 获取全部病历
    const res = await axios.get(`${BASE_URL}/records/list`, {
      params: { limit: 10000 }
    })
    
    const allRecords = res.data.records || []
    const records = allRecords.filter(r => r.doctor_name === userInfo.value.name)
    
    const total = records.length
    
    const oneMonthAgo = new Date()
    oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1)
    const oneMonthAgoStr = oneMonthAgo.toISOString().split('T')[0]
    const monthRecords = records.filter(r => r.admission_date >= oneMonthAgoStr)
    const month = monthRecords.length
    
    doctorStats.value = {
      total: total,
      month: month,
      totalTrend: 0,
      monthTrend: 0
    }
    
    doctorRecentRecords.value = records.slice(0, 5).map(r => ({
      admission_date: r.admission_date,
      patient_name: r.name,
      diagnosis: r.diagnosis,
      record_id: r.record_id
    }))
    
    // 获取医生排名
    try {
      const rankRes = await axios.get(`${BASE_URL}/stats/doctor/rank`, {
        params: { doctor_name: userInfo.value.name }
      })
      doctorRank.value = {
        rank: rankRes.data.rank,
        total: rankRes.data.total
      }
    } catch (err) {
      console.error('获取医生排名失败:', err)
      doctorRank.value = { rank: 0, total: 0 }
    }
    
    // ⭐ 加载个人资料（新增）
    await loadUserProfile()
    
    // 加载个人接诊趋势图
    await nextTick()
    if (doctorTrendChart.value) {
      initDoctorTrendChart(records)
    }
    
  } catch (err) {
    console.error('加载医生统计数据失败:', err)
  }
}

// 初始化个人接诊趋势图
function initDoctorTrendChart(records) {
  if (!doctorTrendChart.value) return
  if (doctorTrendInstance) doctorTrendInstance.dispose()
  
  // 按月份统计接诊量
  const monthMap = new Map()
  records.forEach(r => {
    const month = r.admission_date.substring(0, 7) // YYYY-MM
    monthMap.set(month, (monthMap.get(month) || 0) + 1)
  })
  
  const sortedMonths = Array.from(monthMap.keys()).sort()
  const counts = sortedMonths.map(m => monthMap.get(m))
  
  doctorTrendInstance = echarts.init(doctorTrendChart.value)
  doctorTrendInstance.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: sortedMonths },
    yAxis: { type: 'value', name: '接诊量' },
    series: [{
      type: 'line',
      data: counts,
      smooth: true,
      lineStyle: { color: '#2563eb', width: 3 },
      areaStyle: { opacity: 0.2 }
    }]
  })
}

// 加载图表数据
async function loadAllRecordsForChart() {
  chartLoading.value = true
  try {
    const params = { limit: 1000, offset: 0, department: userInfo.value.department }
    const res = await axios.get('/records/list', { params })
    //updateChart(res.data.records)
  } catch (err) {
    console.error('加载图表数据失败:', err)
  } finally {
    chartLoading.value = false
  }
}

// 加载病历列表
async function loadRecords() {
  loading.value = true
  try {
    const params = {
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value,
      department: userInfo.value.role === 'doctor' ? userInfo.value.department : selectedDept.value
    }
    if (searchKeyword.value.trim()) params.search = searchKeyword.value.trim()
    
    const res = await axios.get('/records/list', { params })
    records.value = res.data.records
    total.value = res.data.total
  } catch (err) {
    console.error('加载病历列表失败:', err)
    ElMessage.error('加载病历列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
function searchRecords() {
  currentPage.value = 1
  loadRecords()
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


// 新建病历相关
function addPrescription() {
  newRecord.prescriptions.push({ drug: '', dosage: '' })
}

function removeLabItem(index) {
  newRecord.lab_items.splice(index, 1)
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

function removePrescription(index) {
  newRecord.prescriptions.splice(index, 1)
}


async function onDepartmentChange(dept) {
  if (!dept) {
    availableDoctors.value = []
    return
  }
  try {
    console.log('=== 请求科室医生 ===')
    console.log('选中科室（原始）:', dept)
    console.log('选中科室（编码）:', encodeURIComponent(dept))
    
    const res = await axios.get('/doctors/list', {
      params: { department: dept }
    })
    
    console.log('完整响应对象:', res)
    console.log('响应数据:', res.data)
    console.log('doctors数组:', res.data.doctors)
    console.log('doctors数组长度:', res.data.doctors?.length)
    
    availableDoctors.value = res.data.doctors || []
    
    // 临时：如果后端空，先用测试数据保证功能可用
    if (availableDoctors.value.length === 0) {
      availableDoctors.value = [
        { id: 'doc001', name: '张明' },
        { id: 'doc002', name: '李芳' },
        { id: 'doc003', name: '王磊' }
      ]
      ElMessage.warning('后端暂无该科室医生，已加载测试数据')
    }
    
    if (availableDoctors.value.length > 0) {
      newRecord.doctor_id = availableDoctors.value[0].id
    }
  } catch (err) {
    console.error('加载医生失败:', err)
    // 出错也用测试数据
    availableDoctors.value = [
      { id: 'doc001', name: '张明' },
      { id: 'doc002', name: '李芳' }
    ]
  }
}

//创建病历
async function createRecord() {
  if (!recordFormRef.value) return
  await recordFormRef.value.validate(async valid => {
    if (!valid) return
    createLoading.value = true
    try {
      const res = await axios.post('/records/create', {
        ...newRecord,
        admission_date: new Date(newRecord.admission_date).toISOString().split('T')[0],
        prescriptions: newRecord.prescriptions.filter(p => p.drug)
      })
      ElMessage.success('创建成功：' + res.data.record_id)
      showCreateRecord.value = false
      
      // 重置表单
      Object.assign(newRecord, {
        name: '', gender: 'M', age: 30, id_card: '', department: '',
        doctor_id: '', admission_date: new Date(), diagnosis: '',
        treatments: [], prescriptions: [], notes: ''
      })
      newRecord.lab_results = {}
      newRecord.imaging_reports = ''
      
      // 重新加载病历列表
      await loadRecords()
      await loadDeptStats()
      
      // ⭐ 延迟1秒后重新加载整个页面数据
      setTimeout(() => {
        location.reload()
      }, 1000)
      
    } catch (err) {
      ElMessage.error(err.response?.data?.detail || '创建失败')
    } finally {
      createLoading.value = false
    }
  })
}


// 监听标签页
watch(() => props.activeTab, (val) => {
  if (val === 'dashboard' || val === 'dashboard-profile') {
    if (val === 'dashboard') {
      loadDeptStats()
      loadAllRecordsForChart()
      loadTrendData()
    }
    if (val === 'dashboard-profile') {
      loadDoctorStats()
      loadUserProfile()
    }
  }
  else if (val === 'records' || val === 'records-stats') {
    if (val === 'records') {
      loadRecords()
    }
    if (val === 'records-stats') {
      loadDeptStats()
    }
  }
  else if (val === 'ai-assistant') {
    // 无需额外操作
  }
})

// 监听对话框打开，保存原始数据
watch(showProfileEdit, (val) => {
  if (val) {
    originalProfileForm.value = JSON.parse(JSON.stringify(profileForm.value))
  }
})

// 图表自适应
const resizeChart = () => trendInstance?.resize()

onMounted(() => {
  loadDeptStats()
  loadAllRecordsForChart()
  loadRecords()
  initDateRange()
  loadTrendData()
  window.addEventListener('resize', resizeChart)
  loadUserProfile()
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeChart)
  if (trendInstance) trendInstance.dispose()
})

// 获取趋势样式类
const getTrendClass = (trend) => {
  if (trend > 0) return 'trend-up'
  if (trend < 0) return 'trend-down'
  return 'trend-zero'
}



// 趋势图相关
const trendTimeUnit = ref('day')  // day, week, month, year
const trendDateRange = ref([])
const trendChart = ref(null)
let trendInstance = null

// 初始化日期范围（默认最近6个月）
const initDateRange = () => {
  const end = new Date()
  const start = new Date()
  if (trendTimeUnit.value === 'month') {
    start.setMonth(end.getMonth() - 5)
  } else if (trendTimeUnit.value === 'week') {
    start.setDate(end.getDate() - 6 * 7) // 最近6周
  } else if (trendTimeUnit.value === 'day') {
    start.setDate(end.getDate() - 29) // 最近30天
  } else if (trendTimeUnit.value === 'year') {
    start.setFullYear(end.getFullYear() - 2) // 最近3年
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
// async function loadTrendData() {
//   if (!trendDateRange.value || trendDateRange.value.length !== 2) return
  
//   chartLoading.value = true
//   try {
//     const params = {
//       department: userInfo.value.department,
//       start_date: trendDateRange.value[0].toISOString().split('T')[0],
//       end_date: trendDateRange.value[1].toISOString().split('T')[0],
//       unit: trendTimeUnit.value
//     }
//     const res = await axios.get(`${BASE_URL}/stats/trend`, { params })
//     updateChart(res.data)
//   } catch (err) {
//     console.error('加载趋势数据失败:', err)
//     ElMessage.error('加载趋势数据失败')
//   } finally {
//     chartLoading.value = false
//   }
// }
async function loadTrendData() {
  console.log('loadTrendData 被调用')
  console.log('trendDateRange:', trendDateRange.value)
  
  if (!trendDateRange.value || trendDateRange.value.length !== 2) {
    console.log('日期范围无效，初始化')
    initDateRange()
  }
  
  console.log('最终日期范围:', trendDateRange.value)
  console.log('时间单位:', trendTimeUnit.value)
  
  chartLoading.value = true
  try {
    const params = {
      department: userInfo.value.department,
      start_date: trendDateRange.value[0].toISOString().split('T')[0],
      end_date: trendDateRange.value[1].toISOString().split('T')[0],
      unit: trendTimeUnit.value
    }
    console.log('请求参数:', params)
    const res = await axios.get(`${BASE_URL}/stats/trend`, { params })
    console.log('返回数据:', res.data)
    updateChart(res.data)
  } catch (err) {
    console.error('加载趋势数据失败:', err)
  } finally {
    chartLoading.value = false
  }
}

// 更新图表
function updateChart(data) {
  nextTick(() => {
    if (!trendChart.value) return
    
    if (trendInstance) {
      trendInstance.dispose()
    }
    // 添加空值检查
    if (!data || !data.labels || !data.values) {
      console.warn('图表数据为空')
      return
    }

    trendInstance = echarts.init(trendChart.value)
    
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
        data: data.labels,
        axisLabel: {
          rotate: data.labels.length > 12 ? 45 : 0,
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
          color: '#10b981'
        },
        areaStyle: {
          opacity: 0.2,
          color: '#10b981'
        },
        itemStyle: {
          color: '#10b981'
        },
        emphasis: {
          focus: 'series'
        }
      }]
    }
    
    trendInstance.setOption(option)
  })
}

</script>

<style scoped>

.doctor-dashboard { width: 100%; }
.action-bar { margin-bottom: 20px; display: flex; justify-content: flex-end; }
.welcome-banner {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 16px; padding: 24px 32px; margin-bottom: 24px; color: white;
}
.welcome-banner h2 { margin: 0 0 8px; font-size: 24px; }
.welcome-banner p { margin: 0; opacity: 0.9; }
.welcome-banner-mini {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 12px; padding: 16px 24px; margin-bottom: 20px; color: white;
}
.welcome-banner-mini h3 { margin: 0; font-size: 18px; }
.stats-row { margin-bottom: 24px; }
.stat-card { border-radius: 12px; text-align: center; transition: all 0.3s; }
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 8px 16px rgba(0,0,0,0.1); }
.stat-label { color: #64748b; font-size: 14px; }
.stat-value { font-size: 32px; font-weight: 600; color: #1e293b; margin-top: 8px; }
.chart-card { margin-bottom: 24px; border-radius: 12px; }
.chart { height: 320px; width: 100%; }
.table-card { border-radius: 12px; }
.table-header {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 12px;
}
.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
.drawer-content { padding: 0 20px; }
.drawer-content h4 { margin: 16px 0 8px; font-weight: 600; color: #1e293b; }
.drawer-content pre {
  background: #f8fafc; padding: 12px; border-radius: 4px;
  white-space: pre-wrap; font-size: 12px; font-family: monospace;
}
.drawer-content ul { margin: 8px 0; padding-left: 20px; }
.drawer-content li { line-height: 1.6; color: #334155; }
.empty-data {
  color: #94a3b8; padding: 12px; text-align: center;
  background: #f8fafc; border-radius: 4px;
}
.prescription-item { display: flex; align-items: center; margin-bottom: 10px; }
.lab-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
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

.action-bar {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-bottom: 20px;
}

/* AI 对话样式 */
.ai-chat-container {
  height: 580px;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
  border-radius: 12px;
  overflow: hidden;
}

.ai-model-selector {
  padding: 12px 16px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  gap: 12px;
  animation: fadeIn 0.3s ease;
}

.message.user {
  flex-direction: row-reverse;
}

.message.user .message-content {
  background: #2563eb;
  color: white;
}

.message.assistant .message-content {
  background: white;
  color: #1e293b;
  border: 1px solid #e2e8f0;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 16px;
  word-wrap: break-word;
}

.message-name {
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 4px;
  opacity: 0.7;
}

.message-text {
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.message-text pre {
  background: #f1f5f9;
  padding: 10px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 12px;
  margin: 8px 0;
}

.message-time {
  font-size: 10px;
  margin-top: 4px;
  opacity: 0.5;
  text-align: right;
}

/* 打字动画 */
.typing span {
  display: inline-block;
  width: 8px;
  height: 8px;
  background: #94a3b8;
  border-radius: 50%;
  margin: 0 2px;
  animation: typing 1.4s infinite;
}

.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-8px); opacity: 1; }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 快捷输入 */
.quick-inputs {
  padding: 12px 16px;
  background: white;
  border-top: 1px solid #e2e8f0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  flex-shrink: 0;
}

.quick-label {
  font-size: 12px;
  color: #64748b;
}

.quick-inputs .el-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.quick-inputs .el-tag:hover {
  background: #2563eb;
  color: white;
  border-color: #2563eb;
}

/* 输入区域 */
.chat-input {
  padding: 16px;
  background: white;
  border-top: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.input-hint {
  font-size: 12px;
  color: #94a3b8;
}

.markdown-body {
  font-size: 14px;
  line-height: 1.6;
}

.markdown-body h1, .markdown-body h2, .markdown-body h3 {
  margin: 16px 0 8px 0;
  color: #1e293b;
}

.markdown-body h3 {
  font-size: 16px;
  font-weight: 600;
}

.markdown-body p {
  margin: 8px 0;
}

.markdown-body ul, .markdown-body ol {
  margin: 8px 0;
  padding-left: 20px;
}

.markdown-body li {
  margin: 4px 0;
}

.markdown-body strong {
  color: #2563eb;
}

.markdown-body code {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
}

.markdown-body pre {
  background: #f1f5f9;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
}

.markdown-body pre code {
  background: none;
  padding: 0;
}

.markdown-body hr {
  margin: 16px 0;
  border: none;
  border-top: 1px solid #e2e8f0;
}
/* ========== 个人中心样式 ========== */
/* 简约个人信息卡片（带渐变边框） */
.profile-card-simple {
  background: white;
  border-radius: 24px;
  padding: 24px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  position: relative;
  /* 渐变边框效果 */
  background: linear-gradient(white, white) padding-box,
              linear-gradient(135deg, #667eea, #764ba2, #f093fb, #4facfe) border-box;
  border: 2px solid transparent;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
  transition: all 0.3s ease;
}

.profile-card-simple:hover {
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.25);
  transform: translateY(-2px);
}

.profile-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.profile-avatar-img {
  border: 3px solid #e8f4f8;
  transition: all 0.3s ease;
}

.profile-info h3 {
  margin: 0 0 8px 0;
  font-size: 22px;
  font-weight: 600;
  color: #1e293b;
}

.profile-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.meta-item {
  font-size: 13px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 4px;
}

.profile-right {
  text-align: right;
}

.welcome-text {
  font-size: 18px;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 8px;
}

.greeting {
  margin-right: 6px;
}

.emoji {
  font-size: 20px;
}

.date-text {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 8px;
}

.profile-edit-btn {
  font-size: 13px;
  color: #3b82f6;
}

.profile-edit-btn:hover {
  color: #2563eb;
}

/* 头像上传样式 */
.avatar-upload {
  display: flex;
  align-items: center;
  gap: 16px;
}

.profile-right {
  text-align: right;
}

.welcome-text {
  font-size: 18px;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 8px;
}

.greeting {
  margin-right: 6px;
}

.emoji {
  font-size: 20px;
}

.date-text {
  font-size: 13px;
  color: #94a3b8;
}

/* 统计卡片 */
.stats-cards {
  margin-bottom: 24px;
}

.stat-card-item {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
}

.stat-card-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
}

.total-icon {
  background: #eff6ff;
  color: #3b82f6;
}

.month-icon {
  background: #ecfdf5;
  color: #10b981;
}

.today-icon {
  background: #fffbeb;
  color: #f59e0b;
}

.rank-icon {
  background: #fef3c7;
  color: #f59e0b;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  font-size: 11px;
  margin-top: 6px;
}

.stat-rank-detail {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
}

/* 图表和记录卡片 */
.chart-card-wrapper,
.records-card-wrapper {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  height: 100%;
  border: 1px solid #f0f0f0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.header-title .el-icon {
  font-size: 20px;
  color: #3b82f6;
}

.header-subtitle {
  font-size: 12px;
  color: #94a3b8;
}

.chart-container {
  height: 320px;
}

.trend-chart {
  width: 100%;
  height: 100%;
}

/* 近期接诊记录列表 */
.records-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: #fafbfc;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.record-item:hover {
  background: #f5f7fa;
  border-color: #e8edf2;
  transform: translateX(4px);
}

.record-date {
  text-align: center;
  min-width: 52px;
  padding: 6px 8px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.date-day {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.date-month {
  font-size: 10px;
  color: #94a3b8;
}

.record-info {
  flex: 1;
}

.record-name {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.record-diagnosis {
  font-size: 12px;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.record-arrow {
  color: #cbd5e1;
  transition: all 0.2s ease;
}

.record-item:hover .record-arrow {
  color: #3b82f6;
  transform: translateX(4px);
}

.empty-records {
  padding: 40px 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .profile-card-simple {
    flex-direction: column;
    text-align: center;
  }
  
  .profile-left {
    flex-direction: column;
  }
  
  .profile-right {
    text-align: center;
  }
  
  .profile-meta {
    justify-content: center;
  }
  
  .stat-card-item {
    padding: 16px;
  }
  
  .stat-value {
    font-size: 22px;
  }
  
  .stat-icon {
    width: 44px;
    height: 44px;
    font-size: 22px;
  }
}

.profile-edit-btn {
  margin-top: 8px;
  font-size: 13px;
  color: #3b82f6;
}

.profile-edit-btn:hover {
  color: #2563eb;
}

/* 头像上传样式 */
.avatar-upload {
  display: flex;
  align-items: center;
  gap: 16px;
}


/* 头像选择器样式 */
.avatar-selector {
  width: 100%;
}

.default-avatar-item:hover {
  transform: scale(1.1);
}

.avatar-editor {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  padding: 8px 0;
}

.avatar-preview {
  text-align: center;
  min-width: 100px;
}

.preview-tip {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 8px;
}

.color-picker-section,
.upload-section {
  flex: 1;
  min-width: 150px;
}

.section-title {
  font-size: 13px;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 10px;
}

.color-value {
  font-size: 12px;
  color: #64748b;
  margin-top: 8px;
}

.upload-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.upload-tip {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 8px;
}

</style>