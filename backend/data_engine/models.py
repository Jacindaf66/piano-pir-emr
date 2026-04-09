# backend/data_engine/models.py
"""
共享数据模型 - 用于数据生成和用户初始化
"""

# ========================
# 医生列表（唯一的真实数据源）
# ========================
DOCTORS = [
    {"username": "doc001", "name": "张明", "department": "心内科", "password": "123456", "title": "主任医师"},
    {"username": "doc002", "name": "李芳", "department": "心内科", "password": "123456", "title": "主治医师"},
    {"username": "doc003", "name": "王磊", "department": "心内科", "password": "123456", "title": "住院医师"},
    {"username": "doc004", "name": "陈丽", "department": "呼吸内科", "password": "123456", "title": "主任医师"},
    {"username": "doc005", "name": "赵强", "department": "呼吸内科", "password": "123456", "title": "主治医师"},
    {"username": "doc006", "name": "孙敏", "department": "呼吸内科", "password": "123456", "title": "住院医师"},
    {"username": "doc007", "name": "周华", "department": "神经内科", "password": "123456", "title": "主任医师"},
    {"username": "doc008", "name": "吴静", "department": "神经内科", "password": "123456", "title": "主治医师"},
    {"username": "doc009", "name": "郑伟", "department": "神经内科", "password": "123456", "title": "住院医师"},
    {"username": "doc010", "name": "王芳", "department": "骨科", "password": "123456", "title": "主任医师"},
    {"username": "doc011", "name": "林峰", "department": "骨科", "password": "123456", "title": "主治医师"},
    {"username": "doc012", "name": "郭强", "department": "骨科", "password": "123456", "title": "住院医师"},
    {"username": "doc013", "name": "宋阳", "department": "普外科", "password": "123456", "title": "主任医师"},
    {"username": "doc014", "name": "何璐", "department": "普外科", "password": "123456", "title": "主治医师"},
    {"username": "doc015", "name": "韩梅", "department": "普外科", "password": "123456", "title": "住院医师"},
    {"username": "doc016", "name": "曹峰", "department": "消化内科", "password": "123456", "title": "主任医师"},
    {"username": "doc017", "name": "彭静", "department": "消化内科", "password": "123456", "title": "主治医师"},
    {"username": "doc018", "name": "曾伟", "department": "消化内科", "password": "123456", "title": "住院医师"},
    {"username": "doc019", "name": "廖芳", "department": "内分泌科", "password": "123456", "title": "主任医师"},
    {"username": "doc020", "name": "苏强", "department": "内分泌科", "password": "123456", "title": "主治医师"},
]

# ========================
# 科室列表
# ========================
DEPARTMENTS = ["心内科", "呼吸内科", "神经内科", "骨科", "普外科", "消化内科", "内分泌科"]

# ========================
# 诊断字典
# ========================
DIAGNOSES = {
    "心内科": ["冠心病", "高血压III级", "心律失常", "心力衰竭", "心肌炎", "心绞痛"],
    "呼吸内科": ["急性支气管炎", "肺炎", "慢性阻塞性肺疾病", "哮喘", "肺气肿", "肺结核"],
    "神经内科": ["脑梗死", "短暂性脑缺血发作", "偏头痛", "帕金森病", "癫痫", "脑出血"],
    "骨科": ["腰椎间盘突出症", "颈椎病", "胫骨骨折", "股骨颈骨折", "关节炎", "骨质疏松"],
    "普外科": ["急性阑尾炎", "腹股沟疝", "胆囊结石", "甲状腺结节", "肠梗阻", "胰腺炎"],
    "消化内科": ["慢性胃炎", "胃溃疡", "肝硬化", "十二指肠溃疡", "结肠炎", "胆结石"],
    "内分泌科": ["2型糖尿病", "甲状腺功能亢进", "痛风", "甲减", "肥胖症", "高脂血症"]
}

# ========================
# 药品列表
# ========================
DRUGS = ["阿莫西林", "二甲双胍", "阿司匹林", "布洛芬", "硝苯地平", "头孢克肟", "奥美拉唑", "胰岛素"]

# ========================
# 治疗项目
# ========================
TREATMENTS = ["一级护理", "二级护理", "三级护理", "物理治疗", "康复训练", "针灸", "推拿", "心理咨询"]

# ========================
# 影像报告
# ========================
IMAGING_REPORTS = [
    "影像检查未见明显异常",
    "CT 显示轻度肺炎",
    "MRI 提示椎间盘突出",
    "X 光提示骨折愈合良好",
    "超声显示胆囊结石",
    "心电图提示心肌缺血"
]

# ========================
# 备注选项
# ========================
NOTES_OPTIONS = [
    "患者今日出院，情况稳定",
    "需复诊观察，两周后复查",
    "已转入康复科继续治疗",
    "服药情况良好，建议继续用药",
    "注意饮食控制，定期监测",
    "建议适当运动，避免劳累"
]

# ========================
# 辅助函数
# ========================
def get_doctors_by_department():
    """按科室分组返回医生列表"""
    doctors_by_dept = {}
    for doc in DOCTORS:
        dept = doc["department"]
        if dept not in doctors_by_dept:
            doctors_by_dept[dept] = []
        doctors_by_dept[dept].append(doc)
    return doctors_by_dept

def get_doctor_usernames():
    """返回所有医生用户名列表"""
    return [doc["username"] for doc in DOCTORS]