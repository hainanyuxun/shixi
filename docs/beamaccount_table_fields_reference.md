# BEAMACCOUNT 表字段参考（客户流失预测项目）

## 一级重要字段（核心预测特征）

### 🎯 流失标签相关
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **ACCOUNTCLOSEDATE** | TIMESTAMP(6) | 05/22/2018 | 账户关闭日期，NULL=活跃客户 | **目标变量构建** - 流失标签定义 |
| **ACCOUNTSTATUS** | VARCHAR2(20) | OPEN/CLOSED | 当前账户状态 | 验证流失标签 |
| **ACCOUNTREOPENDATE** | TIMESTAMP(6) | - | 账户重新开设日期 | 识别重新激活客户 |

### 📅 时间维度特征
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **ACCOUNTOPENDATE** | DATE | 01/01/2018 | 账户开设日期 | **客户任期计算** - 生命周期特征 |
| **BILLINGINCEPTIONDATE** | TIMESTAMP(6) | - | 账费开始日期 | 计费关系时长 |
| **INVESTMENTADVISORYTERMDATE** | TIMESTAMP(6) | - | 投资咨询终止日期 | 服务变化信号 |
| **PERFBEGINDATE** | DATE | - | 绩效计算开始日期 | 投资表现追踪起点 |

### 👤 客户基本特征
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **CLASSIFICATION1** | VARCHAR2(100) | JOINT | 账户分类（个人/联名/信托等） | **账户类型编码** - 分类特征 |
| **ACCOUNTTYPE** | VARCHAR2(50) | Joint Right Of Survivorship | 详细账户类型 | 细分客户群体 |
| **ACCOUNTOWNERTYPE** | VARCHAR2(50) | Person | 账户拥有者类型 | 客户性质分类 |
| **CUSTOMERTAXSTATUS** | VARCHAR2(50) | Taxable | 税务状态 | 税务复杂度指标 |

### 🌍 地理位置特征  
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **DOMICILECOUNTRY** | VARCHAR2(30) | US | 注册国家 | **地理风险评分** |
| **DOMICILESTATE** | VARCHAR2(2) | FL | 注册州 | 区域经济环境因子 |
| **LOCATION** | VARCHAR2(50) | North America | 账户拥有者位置 | 地理聚类特征 |

## 二级重要字段（支撑特征）

### 💰 财务相关
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **BOOKCCY** | VARCHAR2(5) | USD | 基础货币 | 货币风险指标 |
| **CAPITALATRISK** | NUMBER(22,5) | - | 风险资本 | 风险承受度 |
| **CAPITALCOMMITMENTAMOUNT** | NUMBER(20,5) | 2,356,000 | 资本承诺金额 | 客户价值分层 |
| **CAPITALCOMMITMENTDATE** | TIMESTAMP(6) | - | 资本承诺日期 | 承诺时长 |

### 🎯 投资策略相关
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **ACCOUNTOBJECTIVE** | VARCHAR2(40) | International Equity | 账户投资目标 | 投资偏好分类 |
| **ACCOUNTSUBOBJECTIVE** | VARCHAR2(40) | Gain Deferral | 子投资目标 | 细分投资策略 |
| **ACCOUNTSTRATEGYNAME** | VARCHAR2(100) | Multi Strategy | 当前账户策略 | 策略复杂度 |
| **CLASSIFICATION2** | VARCHAR2(30) | MSCI EAFE | 基准名称 | 业绩比较基准 |
| **CLASSIFICATION3** | VARCHAR2(30) | Low Tracking Error | 跟踪分析 | 风险偏好 |
| **CLASSIFICATION4** | VARCHAR2(30) | Multi-Factor | 投资策略 | 策略类型 |
| **CLASSIFICATION5** | VARCHAR2(100) | ESG Tilt | ESG实施 | ESG偏好 |

### 🔧 操作和服务特征
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **ACCOUNTMANAGER** | VARCHAR2(50) | ISG | 投资顾问代表代码 | 顾问关系质量 |
| **DISCRETIONARYSTATUS** | VARCHAR2(20) | Discretionary | 全权委托状态 | 服务模式 |
| **DEFAULTLOTRELIEFMETHOD** | VARCHAR2(8) | STTS | 默认税务减免方法 | 税务管理复杂度 |
| **ALLOWCASHTRANSFER** | VARCHAR2(1) | - | 允许现金转账 | 操作便利性 |
| **PROXYVOTING** | VARCHAR2(1) | 2 | 代理投票包含标志 | 参与度指标 |

### 🏢 托管和平台特征
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **PBCODE** | VARCHAR2(50) | NFS | 券商/托管代码 | 平台便利性 |
| **PBNAME** | VARCHAR2(50) | - | 券商/托管全名 | 托管关系 |
| **ACCOUNTSOURCE** | VARCHAR2(50) | GREEN IC/ODYSSEY | 账户来源 | 获客渠道 |

## 三级重要字段（辅助信息）

### 📋 识别和追踪
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **ID** | NUMBER(10,0) | - | 账户唯一标识符 | 主键关联 |
| **ACCOUNTNUMBER** | VARCHAR2(50) | 52305681 | 账户号码 | 外部系统关联 |
| **ACCOUNTSHORTNAME** | VARCHAR2(50) | 52305681 | 账户短名称 | 识别码 |
| **ALTSYSTEMID1** | VARCHAR2(50) | NBJ041157 | 备用系统标识符1 | 跨系统对账 |

### 👥 组织结构
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **ACCOUNTDIVISIONCODE** | VARCHAR2(20) | 309 | 业务单元代码 | 内部组织结构 |
| **ACCOUNTDIVISIONNAME** | VARCHAR2(50) | Multi Asset Clients ISG | 业务单元名称 | 服务团队分类 |
| **TENANTID** | NUMBER(10,0) | - | 租户ID | 多租户架构标识 |

### 📊 自定义字段
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **USERDEFINEDDATE1** | TIMESTAMP(6) | 01/03/2018 | 用户定义日期1 | 灵活业务日期 |
| **USERDEFINEDMONEY1** | NUMBER(20,5) | 200,000 | 用户定义金额1 | 年度预算等 |
| **NEWISSUESTATUS** | VARCHAR2(100) | Annual Budget | 补充值字段名称 | 灵活业务指标 |

## 特征工程建议

### 🔄 衍生特征计算
```sql
-- 1. 账户年龄（天数）
FLOOR(SYSDATE - ACCOUNTOPENDATE) AS account_age_days

-- 2. 流失标签
CASE WHEN ACCOUNTCLOSEDATE IS NULL THEN 0 ELSE 1 END AS churn_flag

-- 3. 账户生存时间（对于已关闭账户）
CASE WHEN ACCOUNTCLOSEDATE IS NOT NULL 
     THEN FLOOR(ACCOUNTCLOSEDATE - ACCOUNTOPENDATE) 
     ELSE NULL END AS account_lifespan_days

-- 4. 地理风险评分（基于州）
CASE 
  WHEN DOMICILESTATE IN ('CA', 'NY', 'FL') THEN 'High_Wealth'
  WHEN DOMICILESTATE IN ('TX', 'IL', 'NJ') THEN 'Medium_Wealth' 
  ELSE 'Other' 
END AS geo_wealth_tier

-- 5. 账户复杂度评分
(CASE WHEN CLASSIFICATION1 = 'INDIVIDUAL' THEN 1 ELSE 2 END +
 CASE WHEN DISCRETIONARYSTATUS = 'Discretionary' THEN 1 ELSE 0 END +
 CASE WHEN CUSTOMERTAXSTATUS = 'Taxable' THEN 0 ELSE 1 END) AS complexity_score
```

### 📊 特征分组策略
```python
# 按重要性分组的特征集
feature_groups = {
    'core_demographic': [
        'CLASSIFICATION1', 'ACCOUNTTYPE', 'DOMICILESTATE', 
        'account_age_days', 'CUSTOMERTAXSTATUS'
    ],
    'investment_profile': [
        'ACCOUNTOBJECTIVE', 'ACCOUNTSTRATEGYNAME', 'CLASSIFICATION2',
        'CLASSIFICATION3', 'CLASSIFICATION4', 'DISCRETIONARYSTATUS'
    ],
    'service_relationship': [
        'ACCOUNTMANAGER', 'ACCOUNTSOURCE', 'PBCODE',
        'ALLOWCASHTRANSFER', 'PROXYVOTING'
    ],
    'financial_capacity': [
        'CAPITALCOMMITMENTAMOUNT', 'USERDEFINEDMONEY1', 'BOOKCCY'
    ]
}
```

### ⚠️ 数据质量注意事项
1. **缺失值处理**: 
   - CAPITALCOMMITMENTAMOUNT, CLASSIFICATION2-5 可能有大量NULL值
   - USERDEFINEDMONEY1 仅对特定账户类型有效

2. **编码策略**:
   - CLASSIFICATION1: 使用One-Hot编码或Target编码
   - DOMICILESTATE: 可以按经济区域分组
   - 日期字段: 转换为相对天数或分箱处理

3. **业务逻辑验证**:
   - ACCOUNTSTATUS与ACCOUNTCLOSEDATE的一致性
   - ACCOUNTOPENDATE不能晚于ACCOUNTCLOSEDATE
   - TENANTID过滤确保数据范围正确

---

**使用建议**: 
- 优先使用一级重要字段构建基线模型
- 二级字段用于模型优化和特征工程
- 三级字段主要用于数据验证和业务解释 