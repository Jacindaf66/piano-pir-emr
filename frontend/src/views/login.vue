<template>
  <div class="login-page">
    <div class="login-box">
      <h2>仁爱医院电子病历管理系统</h2>
      <p>基于轻量级 PIR 隐私检索技术</p>

      <el-tabs v-model="activeTab" class="tab-switch">
        <!-- 登录 -->
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" class="form" @keyup.enter="handleLogin">
            <el-form-item>
              <el-input v-model="loginForm.username" placeholder="账号" clearable />
            </el-form-item>
            <el-form-item>
              <el-input v-model="loginForm.password" type="password" placeholder="密码" clearable show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" block @click="handleLogin" :loading="logLoading">
                登录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 注册 -->
        <el-tab-pane label="注册" name="register">
          <el-form :model="regForm" :rules="regRules" ref="regFormRef" class="form" @keyup.enter="handleRegister">
            <el-form-item prop="username">
              <el-input 
                v-model="regForm.username" 
                placeholder="账号（用于登录，不可重复）" 
                clearable
                @blur="checkUsername"
              />
              <div v-if="usernameExists" style="color: #f56c6c; font-size: 12px; margin-top: 4px;">
                该账号已存在，请更换
              </div>
            </el-form-item>
            
            <el-form-item prop="name">
              <el-input v-model="regForm.name" placeholder="姓名" clearable />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input 
                v-model="regForm.password" 
                type="password" 
                placeholder="密码（至少6位数字或字母）" 
                clearable 
                show-password
              />
            </el-form-item>
            
            <el-form-item prop="confirmPassword">
              <el-input 
                v-model="regForm.confirmPassword" 
                type="password" 
                placeholder="确认密码" 
                clearable 
                show-password
              />
            </el-form-item>
            
            <el-form-item prop="department">
              <el-select v-model="regForm.department" placeholder="请选择科室" style="width: 100%">
                <el-option label="心内科" value="心内科" />
                <el-option label="呼吸内科" value="呼吸内科" />
                <el-option label="神经内科" value="神经内科" />
                <el-option label="骨科" value="骨科" />
                <el-option label="普外科" value="普外科" />
                <el-option label="消化内科" value="消化内科" />
                <el-option label="内分泌科" value="内分泌科" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" block @click="handleRegister" :loading="regLoading">
                注册医生账号
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      
      <div class="demo-tip">
        <el-divider>演示账号</el-divider>
        <div class="demo-accounts">
          <div>管理员: admin / 123456</div>
          <div>医生: test_doctor / 123456</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const activeTab = ref('login')
const regFormRef = ref(null)

// 登录
const loginForm = ref({ username: '', password: '' })
const logLoading = ref(false)

// 注册
const regForm = reactive({
  username: '',
  name: '',
  password: '',
  confirmPassword: '',
  department: ''
})
const regLoading = ref(false)
const usernameExists = ref(false)

// 密码验证规则：至少6位数字或字母
const validatePassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度至少6位'))
  } else if (!/^[A-Za-z0-9]+$/.test(value)) {
    callback(new Error('密码只能包含数字和字母'))
  } else {
    callback()
  }
}

// 确认密码验证
const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
  } else if (value !== regForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

// 科室验证
const validateDepartment = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请选择科室'))
  } else {
    callback()
  }
}

// 注册表单验证规则
const regRules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { min: 3, max: 20, message: '账号长度在3到20个字符', trigger: 'blur' },
    { pattern: /^[A-Za-z0-9_]+$/, message: '账号只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 10, message: '姓名长度在2到10个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, validator: validatePassword, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ],
  department: [
    { required: true, validator: validateDepartment, trigger: 'change' }
  ]
}

// 检查用户名是否已存在
const checkUsername = async () => {
  if (!regForm.username || regForm.username.length < 3) {
    usernameExists.value = false
    return
  }
  
  try {
    // 注意：这里需要添加一个检查用户名是否存在的接口
    // 暂时通过尝试登录来检查（不推荐，最好后端添加 /check-username 接口）
    // 为了更好的体验，建议后端添加一个检查接口
    console.log('检查用户名:', regForm.username)
    usernameExists.value = false
  } catch (err) {
    console.error('检查用户名失败:', err)
  }
}

// 登录处理
const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    ElMessage.warning('请输入账号和密码')
    return
  }
  
  logLoading.value = true
  try {
    const res = await axios.post('http://127.0.0.1:8000/api/login', {
      username: loginForm.value.username,
      password: loginForm.value.password
    })
    
    localStorage.setItem('token', res.data.token)
    localStorage.setItem('userInfo', JSON.stringify({
      username: res.data.username,
      name: res.data.name,
      role: res.data.role,
      department: res.data.department
    }))
    
    axios.defaults.headers.common['Authorization'] = `Bearer ${res.data.token}`
    
    ElMessage.success(`登录成功！欢迎 ${res.data.name}`)
    router.push('/')
    
  } catch (err) {
    console.error('登录错误:', err)
    ElMessage.error(err.response?.data?.detail || '登录失败')
  } finally {
    logLoading.value = false
  }
}

// 注册处理
const handleRegister = async () => {
  // 表单验证
  if (!regFormRef.value) return
  
  await regFormRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.warning('请正确填写所有字段')
      return
    }
    
    regLoading.value = true
    try {
      const res = await axios.post('http://127.0.0.1:8000/api/register', {
        username: regForm.username,
        password: regForm.password,
        name: regForm.name,
        department: regForm.department
      })
      
      ElMessage.success('注册成功！请登录')
      
      // 清空表单
      regForm.username = ''
      regForm.name = ''
      regForm.password = ''
      regForm.confirmPassword = ''
      regForm.department = ''
      usernameExists.value = false
      
      // 切换到登录 Tab，并自动填充用户名
      activeTab.value = 'login'
      if (res.data.username) {
        loginForm.value.username = res.data.username
      }
      
    } catch (err) {
      console.error('注册错误:', err)
      if (err.response?.status === 400 && err.response?.data?.detail === '用户名已存在') {
        usernameExists.value = true
        ElMessage.error('该用户名已存在，请更换')
      } else {
        ElMessage.error(err.response?.data?.detail || '注册失败，请稍后重试')
      }
    } finally {
      regLoading.value = false
    }
  })
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 450px;
  background: white;
  padding: 40px 35px;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  text-align: center;
}

.login-box h2 {
  color: #1976D2;
  margin-bottom: 8px;
  font-size: 24px;
}

.login-box p {
  color: #999;
  font-size: 13px;
  margin-bottom: 20px;
}

.tab-switch {
  margin-top: 20px;
}

.form {
  margin-top: 20px;
}

.demo-tip {
  margin-top: 20px;
}

.demo-accounts {
  font-size: 12px;
  color: #666;
  text-align: left;
  padding: 0 10px;
}

.demo-accounts div {
  margin: 5px 0;
  font-family: monospace;
}
</style>