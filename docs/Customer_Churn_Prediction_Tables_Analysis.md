# 客户流失预测 - 数据表结构完整分析

## 概述
本文档基于InvestCloud平台四大核心表的完整结构分析，重新定义了用户级别的客户流失预测策略和数据架构。

## 核心发现：预测层级重新定义

### 关键洞察
通过深入分析USERS表结构，我们发现应将预测重点从**账户级别**提升到**用户级别**：

```
用户 (USERS) - 主预测目标
   ↓ (一对多)
账户 (beamaccount) - 聚合到用户级别
   ↓ (一对多)  
交易记录 (IDRTRANSACTION) - 用户行为分析
资产价值 (PROFITANDLOSSLITE) - 投资表现分析
```

### 流失标签重新定义
**基于USERS.STATUS字段的流失标签**:
```sql
CASE 
    WHEN STATUS = 'A' THEN 0  -- 活跃用户 (Active)
    WHEN STATUS = 'R' THEN 0  -- 重新激活用户 (Reactivated) 
    WHEN STATUS IN ('S', 'L') THEN 1  -- 流失用户 (Suspended/Locked)
    ELSE NULL  -- 数据质量问题
END AS churn_label
```

## 四大核心表深度分析

### 1. USERS表 (用户维度主表) 🌟🌟🌟🌟🌟

#### 表结构价值
| 字段类别 | 关键字段 | 流失预测价值 | 特征工程方向 |
|----------|----------|--------------|--------------|
| **用户状态** | STATUS | ⭐⭐⭐⭐⭐ | **直接流失标签** |
| **身份标识** | USERNAME, TENANTID | ⭐⭐⭐⭐⭐ | 用户唯一标识和分层 |
| **联系信息** | EMAILADDRESS, PHONE | ⭐⭐⭐⭐ | 参与度和信息完整性 |
| **地理信息** | STATEPROVINCE, CITY | ⭐⭐⭐ | 地理风险和财富分层 |
| **个人信息** | DATEOFBIRTH, NAME | ⭐⭐ | 人口统计学特征 |
| **安全设置** | SECRETQUESTION* | ⭐⭐⭐ | 安全参与度指标 |

#### 核心特征工程
```python
# 用户参与度综合评分
user_engagement_features = [
    'contact_completeness',      # 联系方式完整度 (邮箱+电话数量)
    'security_setup_depth',     # 安全设置完整度 (问题数量)
    'profile_completeness',     # 档案完整度 (非空字段比例)
    'geographic_wealth_tier'    # 基于州的财富分层
]

# 用户状态历史(如果可获得)
user_status_features = [
    'status_change_frequency',  # 状态变化频率
    'reactivation_history',     # 重激活历史
    'time_since_last_active'    # 距离最后活跃时间
]
```

---

### 2. beamaccount表 (账户维度) 🌟🌟🌟🌟

#### 表结构价值
| 字段类别 | 关键字段 | 流失预测价值 | 特征工程方向 |
|----------|----------|--------------|--------------|
| **流失标签** | ACCOUNTCLOSEDATE | ⭐⭐⭐⭐⭐ | 账户级别流失标签(次要) |
| **时间维度** | ACCOUNTOPENDATE | ⭐⭐⭐⭐⭐ | 账户年龄和生命周期 |
| **客户分类** | CLASSIFICATION1-5 | ⭐⭐⭐⭐ | 账户类型和投资策略 |
| **地理位置** | DOMICILESTATE | ⭐⭐⭐⭐ | 地理风险评分 |
| **财务承诺** | CAPITALCOMMITMENT* | ⭐⭐⭐ | 客户价值分层 |
| **服务关系** | ACCOUNTMANAGER | ⭐⭐⭐ | 服务质量代理指标 |

#### 用户级别聚合特征
```python
# 账户汇总特征(聚合到用户级别)
account_aggregation_features = [
    'total_accounts',           # 用户拥有的总账户数
    'active_accounts_ratio',    # 活跃账户比例
    'avg_account_age',          # 平均账户年龄
    'account_type_diversity',   # 账户类型多样性
    'max_capital_commitment',   # 最大资本承诺
    'geographic_diversification' # 地理分散度
]
```

---

### 3. IDRTRANSACTION表 (交易行为) 🌟🌟🌟🌟🌟

#### 表结构价值
| 字段类别 | 关键字段 | 流失预测价值 | 特征工程方向 |
|----------|----------|--------------|--------------|
| **交易金额** | BOOKAMOUNT | ⭐⭐⭐⭐⭐ | 交易规模和现金流 |
| **时间维度** | EVENTDATE, TRADEDATE | ⭐⭐⭐⭐⭐ | 交易频率和时间模式 |
| **损益核心** | BOOKTOTAL* | ⭐⭐⭐⭐⭐ | 投资表现核心指标 |
| **交易类型** | EVENTTYPE | ⭐⭐⭐⭐ | 交易行为模式分析 |
| **资产类别** | ASSETCLASS* | ⭐⭐⭐⭐ | 投资偏好和多样性 |
| **证券标识** | ENTERPRISESYMBOL | ⭐⭐⭐ | 投资集中度分析 |

#### 关键行为特征
```python
# 交易活跃度衰退指标
trading_activity_features = [
    'transaction_frequency_30d',      # 30天交易频率
    'transaction_frequency_decline',  # 频率下降趋势
    'days_since_last_transaction',   # 最后交易距今天数
    'avg_transaction_amount',        # 平均交易规模
    'transaction_volatility',        # 交易金额波动性
    'net_flow_trend'                # 资金净流向趋势
]

# 投资表现指标
investment_performance_features = [
    'total_realized_gain_loss',     # 总已实现损益
    'gain_loss_ratio',              # 收益损失比率
    'consecutive_loss_periods',     # 连续亏损期间
    'risk_adjusted_return',         # 风险调整收益
    'win_loss_transaction_ratio'    # 盈利交易比例
]
```

---

### 4. PROFITANDLOSSLITE表 (资产价值) 🌟🌟🌟🌟🌟

#### 表结构价值  
| 字段类别 | 关键字段 | 流失预测价值 | 特征工程方向 |
|----------|----------|--------------|--------------|
| **市值核心** | BOOKMARKETVALUE* | ⭐⭐⭐⭐⭐ | 资产价值趋势分析 |
| **损益核心** | BOOKUGL | ⭐⭐⭐⭐⭐ | 未实现损益和风险 |
| **时间序列** | BE_ASOF | ⭐⭐⭐⭐⭐ | 每日时间序列基础 |
| **持仓数据** | QUANTITY | ⭐⭐⭐⭐ | 仓位变化趋势 |
| **资产分类** | ASSETCLASS* | ⭐⭐⭐⭐ | 投资组合分析 |
| **成本基础** | AVERAGECOST* | ⭐⭐⭐ | 成本管理行为 |

#### 时间序列特征
```python
# 资产价值趋势特征
asset_value_features = [
    'market_value_trend_30d',       # 30天市值变化趋势
    'market_value_volatility',      # 市值波动性
    'unrealized_pnl_ratio',         # 未实现损益率
    'max_drawdown_depth',           # 最大回撤深度
    'portfolio_value_stability'     # 投资组合价值稳定性
]

# 投资组合多样性
portfolio_diversity_features = [
    'asset_class_count',            # 资产类别数量
    'position_concentration',       # 持仓集中度
    'sector_diversification',       # 行业分散度
    'geographic_exposure'           # 地理敞口分布
]
```

---

### 5. BeamAccountOverride表 (配置行为) 🌟🌟🌟

#### 流失预测价值: 🟢 较高

**特征工程价值:**
```python
# 用户配置参与度
configuration_engagement = [
    'config_modification_frequency', # 配置修改频率
    'last_config_change_days',      # 最后配置修改距今天数
    'config_field_diversity',       # 修改字段多样性
    'config_completeness_score'     # 配置完整性评分
]
```

---

### 6. USERDATA表 (扩展数据) 🌟

#### 流失预测价值: 🟡 较低
- 主要作为用户标识映射和数据质量评估
- 可用于用户来源渠道分析
- 直接预测价值有限

## 表间关联策略

### 🎯 核心关联关系 (已确认)
```sql
-- ✅ 确认的用户-账户关联架构
USERS u (主表)
├── USER_TO_ACCOUNT ua (中间映射表)
│   ├── 关联字段: u.USERNAME = ua.USERNAME
│   ├── 租户映射: ua.TENANTID (内外部用户分类)
│   └── 账户关联: ua.ACCOUNTID
├── beamaccount b (通过映射表关联)
│   └── 关联字段: ua.ACCOUNTID = b.ID
├── IDRTRANSACTION t (通过账户间接关联)
│   └── 关联字段: b.ACCOUNTSHORTNAME = t.ACCOUNTSHORTNAME
├── PROFITANDLOSSLITE p (通过账户间接关联)
│   └── 关联字段: b.ACCOUNTSHORTNAME = p.ACCOUNTSHORTNAME
└── BeamAccountOverride o (通过账户间接关联)
    └── 关联字段: ua.ACCOUNTID = o.AccountId
```

### 🔗 关联映射表详细信息
```sql
-- USER_TO_ACCOUNT 表结构
CREATE TABLE USER_TO_ACCOUNT (
    ACCOUNTID NUMBER(10,0) NOT NULL,     -- 关联到beamaccount.ID
    USERNAME VARCHAR2(100) NOT NULL,     -- 关联到USERS.USERNAME  
    TENANTID NUMBER(10,0) NOT NULL       -- 租户分类
);

-- 租户映射规则
TENANTID 映射规则:
- NeubergerBerman_Employee → 内部员工 (来源: USERACCT_INTERNAL文件)
- NeubergerBerman_Users → 外部客户 (来源: USERACCT_EXTERNAL文件)
```

### 📊 优化后的数据聚合策略
```sql
-- 用户级别特征聚合 (基于确认的关联关系)
WITH user_account_bridge AS (
    -- Step 1: 建立用户-账户桥接表
    SELECT 
        ua.USERNAME,
        ua.ACCOUNTID,
        ua.TENANTID,
        CASE 
            WHEN ua.TENANTID = (SELECT ID FROM TENANT WHERE NAME = 'NeubergerBerman_Employee') 
            THEN 'Internal_Employee'
            WHEN ua.TENANTID = (SELECT ID FROM TENANT WHERE NAME = 'NeubergerBerman_Users')
            THEN 'External_Client' 
            ELSE 'Other'
        END as user_type
    FROM USER_TO_ACCOUNT ua
),
user_comprehensive_features AS (
    -- Step 2: 用户级别全面特征聚合
    SELECT 
        u.USERNAME,
        u.STATUS as user_status,
        uab.user_type,
        
        -- 账户维度汇总
        COUNT(DISTINCT b.ID) as total_accounts,
        COUNT(DISTINCT CASE WHEN b.ACCOUNTCLOSEDATE IS NULL THEN b.ID END) as active_accounts,
        COUNT(DISTINCT b.CLASSIFICATION1) as account_type_diversity,
        AVG(SYSDATE - b.ACCOUNTOPENDATE) as avg_account_age_days,
        SUM(COALESCE(b.CAPITALCOMMITMENTAMOUNT, 0)) as total_capital_commitment,
        
        -- 资产价值汇总 (最新数据)
        SUM(p.BOOKMARKETVALUEPERIODEND) as total_portfolio_value,
        SUM(p.BOOKUGL) as total_unrealized_pnl,
        COUNT(DISTINCT p.ASSETCLASSLEVEL1) as asset_class_diversity,
        STDDEV(p.BOOKMARKETVALUEPERIODEND) as portfolio_volatility,
        
        -- 交易行为汇总 (最近90天)
        COUNT(t.EVENTDATE) as total_transactions_90d,
        SUM(ABS(t.BOOKAMOUNT)) as total_transaction_volume,
        MAX(t.EVENTDATE) as last_transaction_date,
        SYSDATE - MAX(t.EVENTDATE) as days_since_last_transaction,
        SUM(t.BOOKTOTALGAIN) as total_realized_gain,
        SUM(t.BOOKTOTALLOSS) as total_realized_loss,
        
        -- 配置行为汇总
        COUNT(o.FieldName) as config_modifications,
        MAX(o.LastModified) as last_config_change
        
    FROM USERS u
    JOIN user_account_bridge uab ON u.USERNAME = uab.USERNAME
    JOIN beamaccount b ON uab.ACCOUNTID = b.ID
    LEFT JOIN PROFITANDLOSSLITE p ON b.ACCOUNTSHORTNAME = p.ACCOUNTSHORTNAME
        AND p.BE_ASOF = (SELECT MAX(BE_ASOF) FROM PROFITANDLOSSLITE)  -- 最新数据
    LEFT JOIN IDRTRANSACTION t ON b.ACCOUNTSHORTNAME = t.ACCOUNTSHORTNAME
        AND t.EVENTDATE >= SYSDATE - 90  -- 最近90天交易
    LEFT JOIN BeamAccountOverride o ON uab.ACCOUNTID = o.AccountId
    
    GROUP BY u.USERNAME, u.STATUS, uab.user_type
)
SELECT * FROM user_comprehensive_features;
```

## 预测架构重新设计

### 两层预测模型
1. **用户级别主模型**: 预测用户整体流失风险 (基于USERS.STATUS)
2. **账户级别辅助模型**: 预测特定账户关闭风险 (基于beamaccount.ACCOUNTCLOSEDATE)

### 特征重要性排序
```python
feature_importance_ranking = {
    'tier_1_critical': [
        'user_status_history',           # 用户状态变化
        'transaction_frequency_decline', # 交易频率下降
        'market_value_trend',           # 资产价值趋势
        'unrealized_pnl_deterioration'  # 投资表现恶化
    ],
    'tier_2_important': [
        'account_aggregation_metrics',   # 账户汇总指标
        'user_engagement_score',        # 用户参与度
        'investment_performance_ratio', # 投资表现比率
        'portfolio_diversification'    # 投资组合多样性
    ],
    'tier_3_supporting': [
        'demographic_features',         # 人口统计学
        'geographic_risk_factors',     # 地理风险因素
        'configuration_behavior',      # 配置行为
        'service_relationship_quality' # 服务关系质量
    ]
}
```

## 数据质量评估

### ✅ 高质量方面
1. **流失标签明确**: USERS.STATUS字段提供清晰的流失定义
2. **时间序列完整**: 所有表都有明确的时间维度字段
3. **关联关系清晰**: 表间通过ACCOUNTSHORTNAME等字段可以良好关联
4. **业务逻辑完整**: 从用户到交易的完整业务链条

### ✅ 已解决的关键问题
1. **✅ 用户-账户关联**: 已确认通过USER_TO_ACCOUNT中间表关联
   - 关联方式: `USERS.USERNAME = USER_TO_ACCOUNT.USERNAME`
   - 账户桥接: `USER_TO_ACCOUNT.ACCOUNTID = beamaccount.ID`
   - 租户分类: 通过TENANTID区分内外部用户

### ⚠️ 仍需关注的问题
2. **数据完整性**: 某些财务字段(如CAPITALCOMMITMENT)可能存在大量NULL值
3. **时间一致性**: 确保跨表的时间字段对齐和一致性
4. **数据倾斜**: 需要评估流失用户与活跃用户的分布比例
5. **映射表质量**: 验证USER_TO_ACCOUNT表的数据完整性

## 建模优势分析

### 🎯 相比传统客户流失预测的优势
1. **丰富的行为数据**: 交易行为、资产变化提供深度行为洞察
2. **财务表现指标**: 投资损益直接反映客户满意度
3. **多层次预测**: 用户级别和账户级别的双重预测能力  
4. **时间序列丰富**: 每日资产价值快照提供高频时间序列特征

### 📊 特征工程优势
1. **衍生特征丰富**: 可以构建复杂的趋势、波动性、比率类特征
2. **业务意义明确**: 每个特征都有清晰的金融业务解释
3. **预警信号多样**: 从交易频率到投资表现的多维度预警
4. **客户分层精细**: 基于资产规模、投资策略的精细分层

## 实施建议

### Phase 1: 数据探索和关联确认 (第1周)
```sql
-- 1. 确认用户-账户关联关系
-- 2. 数据质量评估和清洗
-- 3. 流失标签分布分析
-- 4. 基础统计分析和EDA
```

### Phase 2: 特征工程和基线模型 (第2周)  
```python
# 1. 用户级别特征聚合
# 2. 时间序列特征构建
# 3. 基线模型训练和评估
# 4. 特征重要性分析
```

### Phase 3: 高级建模和优化 (第3周)
```python
# 1. 高级模型训练(XGBoost, LightGBM)
# 2. 模型解释性分析(SHAP)
# 3. 业务规则集成
# 4. 预测阈值优化
```

### Phase 4: 部署和应用 (第4周)
```python
# 1. 模型部署和API开发
# 2. 预测界面开发
# 3. 业务应用场景设计
# 4. 文档和培训材料
```

## 更新历史
- 2024-12-19: 完整重构，基于四大核心表的深度分析
- 2024-12-19: 重新定义用户级别预测策略
- 2024-12-19: 添加特征重要性排序和建模架构

## 后续重点任务
- [x] 完成四大核心表结构分析
- [x] ✅ 确认用户-账户关联方式 (USER_TO_ACCOUNT中间表)
- [ ] 验证映射表数据质量和完整性
- [ ] 实施基于确认架构的用户级别特征聚合
- [ ] 构建两层预测模型架构
- [ ] 优化跨表查询性能 