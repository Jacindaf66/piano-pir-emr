# 🏥 PIANO 隐私电子病历查询系统

基于 **PIANO** (Private Information Access Now) 算法的隐私保护电子病历查询系统。该系统实现了单服务器子线性时间的隐私信息检索，确保医生查询病历时服务器无法知道查询的是哪位患者。

## 📋 项目简介

本项目是一个完整的医疗病历管理系统，核心特色是实现了 **PIANO 隐私查询算法**，保证：
- ✅ 服务器不知道医生查询的是哪条病历
- ✅ 查询时间复杂度为 O(√n)，比传统线性扫描快 100 倍
- ✅ 新老病历都支持隐私查询
- ✅ 完整的病历管理功能

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| 数据库 | SQLite + SQLAlchemy |
| 前端框架 | Vue3 + Vite |
| UI 组件库 | Element Plus |
| 图表库 | ECharts |
| 隐私算法 | PIANO PIR |
| 认证 | JWT + bcrypt |
| AI 问诊 | DeepSeek / 豆包 API |

## ✨ 功能特性

### 核心功能
- 🔐 **用户系统**：管理员/医生双角色，权限分离
- 📋 **病历管理**：增删改查、分页、搜索、筛选
- 🛡️ **隐私查询**：基于 PIANO 算法的隐私保护查询
- 📊 **数据统计**：科室分布、同比趋势、接诊排行
- 🤖 **AI 问诊**：智能诊断辅助（DeepSeek/豆包）

### 管理员功能
- 查看全院病历数据
- 医生账号管理（增删改查、重置密码）
- 科室运营分析
- 医生绩效看板

### 医生功能
- 查看本科室病历
- 新建病历
- AI 智能问诊
- 个人仪表盘

## 🚀 快速启动

### 环境要求
- Python 3.9+
- Node.js 16+
- npm 8+

### 后端安装与运行

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 生成数据库和预处理数据
python -m data_engine.generator
python -m data_engine.preprocessor
python -m core.piano_preprocess

# 启动后端服务
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 前端安装与运行
cd frontend
npm install
npm run dev

# 访问系统
前端地址：http://localhost:5173
后端 API 文档：http://127.0.0.1:8000/docs


# 📁 项目结构
piano-pir-emr/
├── backend/                    # 后端代码
│   ├── app/                    # FastAPI 应用
│   │   ├── api.py              # API 接口
│   │   ├── main.py             # 入口文件
│   │   ├── models.py           # 数据模型
│   │   ├── database.py         # 数据库连接
│   │   └── security.py         # 认证安全
│   ├── core/                   # 核心算法
│   │   ├── piano_core.py       # PIANO 服务器/客户端
│   │   └── piano_preprocess.py # 预处理
│   ├── data_engine/            # 数据生成
│   │   ├── generator.py        # 病历生成
│   │   └── preprocessor.py     # 数据预处理
│   └── storage/                # 数据存储
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── components/         # Vue 组件
│   │   ├── views/              # 页面视图
│   │   ├── utils/              # 工具函数
│   │   │   └── piano.js        # PIANO 客户端
│   │   └── router/             # 路由配置
│   └── public/                 # 静态资源
└── README.md                   # 项目说明