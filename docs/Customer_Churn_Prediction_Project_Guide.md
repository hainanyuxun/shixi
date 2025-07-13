# InvestCloud客户流失预测项目完整指南

## 项目重新定义与战略价值

### 核心发现：用户级别预测的商业价值
基于InvestCloud四大核心表的深度分析，我们重新定义了项目架构，将预测重点从传统的**账户级别**提升到**用户级别**，这带来了显著的商业价值提升：

**架构层级**:
```
📊 用户级别主预测 (USERS.STATUS) - 最高商业价值
    ↓ 聚合数据源
💼 账户管理特征 (beamaccount) - 投资复杂度和关系深度
    ↓ 行为数据源  
💰 交易行为分析 (IDRTRANSACTION) - 活跃度和投资表现
    ↓ 价值数据源
📈 资产价值趋势 (PROFITANDLOSSLITE) - 财务健康状况
```

### 重新定义的项目目标

#### 🎯 主要目标: 用户级别流失预测
- **目标定义**: 预测用户在未来30/60/90天内状态变为'S'或'L'的概率
- **商业意义**: 识别有完全流失风险的高价值用户
- **干预价值**: 针对用户整体价值进行精准挽回投资

#### 🔄 次要目标: 账户级别风险评估  
- **目标定义**: 预测特定账户关闭风险
- **商业意义**: 支持更细粒度的风险管理
- **运营价值**: 优化账户服务和产品推荐

#### 🚀 延伸目标: 用户生命周期价值优化
- **重激活预测**: 识别'R'状态用户的重激活模式
- **价值提升**: 预测用户价值增长潜力
- **挽回策略**: 基于流失原因的个性化挽回方案

### 流失标签体系
```sql
-- 主要流失标签: USERS.STATUS
CASE 
    WHEN STATUS = 'A' THEN 0  -- 活跃用户 (Active)
    WHEN STATUS = 'R' THEN 0  -- 重新激活用户 (Reactivated)
    WHEN STATUS IN ('S', 'L') THEN 1  -- 流失用户 (Suspended/Locked)
    ELSE NULL  -- 数据质量问题
END AS user_churn_label

-- 次要流失标签: beamaccount.ACCOUNTCLOSEDATE  
CASE 
    WHEN ACCOUNTCLOSEDATE IS NULL THEN 0  -- 活跃账户
    ELSE 1  -- 已关闭账户
END AS account_churn_label
```

## 数据架构深度分析

### 四大核心表的预测价值重新评估

#### 1. USERS表 - 🌟🌟🌟🌟🌟 (核心主表)
**战略作用**: 用户维度主表，提供直接流失标签和参与度特征
```python
# 关键特征类别
user_features = {
    'primary_label': 'STATUS',  # 直接流失标签
    'engagement': ['EMAILADDRESS', 'PHONE*', 'SECRETQUESTION*'],
    'demographics': ['DATEOFBIRTH', 'STATEPROVINCE'],
    'tenant_type': 'TENANTID'  # 内外部用户分层
}
```

#### 2. beamaccount表 - 🌟🌟🌟🌟🌟 (关系复杂度)
**战略作用**: 用户投资关系复杂度和价值承诺分析
```python
# 用户级别聚合特征
account_aggregation = {
    'relationship_complexity': ['total_accounts', 'account_type_diversity'],
    'financial_commitment': ['CAPITALCOMMITMENT*', 'avg_account_age'],
    'geographic_diversification': ['DOMICILESTATE*'],
    'service_relationship': ['ACCOUNTMANAGER*']
}
```

#### 3. IDRTRANSACTION表 - 🌟🌟🌟🌟🌟 (行为预警)
**战略作用**: 用户交易行为变化，最强流失预警信号
```python
# 核心行为特征
transaction_features = {
    'activity_decline': ['frequency_30d', 'days_since_last'],
    'financial_performance': ['realized_gain_loss', 'total_pnl'],
    'cash_flow_pattern': ['net_inflow_outflow', 'transaction_volatility'],
    'investment_behavior': ['asset_class_diversity', 'trading_patterns']
}
```

#### 4. PROFITANDLOSSLITE表 - 🌟🌟🌟🌟🌟 (财务健康)
**战略作用**: 用户财务健康状况和投资表现时间序列
```python
# 时间序列特征
portfolio_features = {
    'value_trends': ['market_value_30d_change', 'volatility'],
    'performance_metrics': ['unrealized_pnl_ratio', 'max_drawdown'],
    'risk_indicators': ['portfolio_concentration', 'negative_periods'],
    'asset_allocation': ['asset_class_distribution', 'rebalancing_frequency']
}
```

### 表间关联策略确认

#### ✅ 确认的关键关联关系
```sql
-- 已确认的用户-账户关联架构
USERS u (主表)
├── USER_TO_ACCOUNT ua (核心中间映射表)
│   ├── 关联方式: u.USERNAME = ua.USERNAME
│   ├── 租户分类: ua.TENANTID (内外部用户)
│   └── 账户桥接: ua.ACCOUNTID → b.ID
├── beamaccount b (通过映射表关联)
├── IDRTRANSACTION t (通过b.ACCOUNTSHORTNAME关联)
├── PROFITANDLOSSLITE p (通过b.ACCOUNTSHORTNAME关联)
└── BeamAccountOverride o (通过ua.ACCOUNTID关联)
```

#### 🎯 关联策略优势分析
```python
# 数据架构优势
architecture_benefits = {
    'clear_mapping': 'USERNAME字段提供明确的用户标识',
    'tenant_separation': '内外部用户通过TENANTID清晰分离',
    'one_to_many': '一个用户可对应多个账户的完整支持',
    'data_integrity': '中间映射表确保关联关系的完整性',
    'scalability': '支持用户-账户关系的灵活扩展'
}
```

#### 📋 数据关联实施计划 (已简化)
1. **✅ Phase 1**: 关联方式已确认 - USER_TO_ACCOUNT表
2. **Phase 2**: 验证映射表数据完整性和质量
3. **Phase 3**: 基于确认架构实施特征聚合流程

## 特征工程战略重构

### 特征分层体系 (基于预测价值和业务意义)

#### 🔥 一级核心特征 (Tier 1 - Critical) - 权重60%

##### 1. 用户交易行为衰退特征
```python
# 最强预测信号 - 基于IDRTRANSACTION表
behavioral_decline_features = {
    'transaction_frequency_decline': {
        'definition': '近30天 vs 历史90天交易频率比',
        'importance': '⭐⭐⭐⭐⭐',
        'business_logic': '交易活动急剧下降是流失最强信号'
    },
    'days_since_last_transaction': {
        'definition': '最后一次交易距今天数',
        'importance': '⭐⭐⭐⭐⭐', 
        'business_logic': '交易停滞直接预示用户脱离'
    },
    'net_cash_flow_trend': {
        'definition': '(流入-流出)/总交易额的趋势',
        'importance': '⭐⭐⭐⭐⭐',
        'business_logic': '持续资金流出表明转移资产意图'
    }
}
```

##### 2. 用户投资表现恶化特征  
```python
# 财务健康指标 - 基于PROFITANDLOSSLITE表
financial_health_features = {
    'unrealized_pnl_deterioration': {
        'definition': '未实现损益占总市值比例的下降',
        'importance': '⭐⭐⭐⭐⭐',
        'business_logic': '投资亏损直接影响满意度'
    },
    'portfolio_value_decline': {
        'definition': '30天资产总价值变化率',
        'importance': '⭐⭐⭐⭐⭐',
        'business_logic': '资产缩水增加流失风险'
    },
    'consecutive_loss_periods': {
        'definition': '连续负收益的天数',
        'importance': '⭐⭐⭐⭐',
        'business_logic': '持续亏损削弱用户信心'
    }
}
```

##### 3. 用户关系复杂度下降特征
```python
# 关系深度变化 - 基于beamaccount表聚合
relationship_depth_features = {
    'account_closure_acceleration': {
        'definition': '账户关闭速度加快',
        'importance': '⭐⭐⭐⭐⭐',
        'business_logic': '简化关系预示准备离开'
    },
    'capital_commitment_reduction': {
        'definition': '资本承诺金额的减少趋势',
        'importance': '⭐⭐⭐⭐',
        'business_logic': '承诺减少表明信心下降'
    },
    'service_relationship_instability': {
        'definition': '投资顾问变更频率',
        'importance': '⭐⭐⭐',
        'business_logic': '服务关系不稳定影响满意度'
    }
}
```

#### ⭐ 二级重要特征 (Tier 2 - Important) - 权重30%

##### 4. 用户参与度下降特征
```python
# 平台参与度 - 基于USERS + BeamAccountOverride表
engagement_decline_features = {
    'information_maintenance_decay': {
        'definition': '联系信息和安全设置的更新频率下降',
        'importance': '⭐⭐⭐⭐',
        'business_logic': '参与度下降反映脱离意图'
    },
    'configuration_activity_decline': {
        'definition': '账户配置修改频率的下降',
        'importance': '⭐⭐⭐',
        'business_logic': '主动管理减少表明关注度降低'
    }
}
```

##### 5. 用户投资组合优化特征
```python
# 投资行为变化 - 基于资产配置分析
portfolio_optimization_features = {
    'asset_allocation_simplification': {
        'definition': '投资组合复杂度的简化趋势',
        'importance': '⭐⭐⭐',
        'business_logic': '简化配置可能预示离开准备'
    },
    'risk_tolerance_changes': {
        'definition': '风险偏好的显著变化',
        'importance': '⭐⭐⭐',
        'business_logic': '风险偏好变化可能反映生活阶段变化'
    }
}
```

#### 🎯 三级支撑特征 (Tier 3 - Supporting) - 权重10%

##### 6. 用户生命周期和价值特征
```python
# 背景上下文特征
lifecycle_value_features = {
    'customer_tenure': {
        'definition': '用户与平台关系的总时长',
        'importance': '⭐⭐',
        'business_logic': '长期客户流失损失更大'
    },
    'demographic_risk_factors': {
        'definition': '基于年龄、地理位置的风险评分',
        'importance': '⭐⭐',
        'business_logic': '某些人群有特定流失模式'
    },
    'market_environment_sensitivity': {
        'definition': '对市场波动的敏感性',
        'importance': '⭐⭐',
        'business_logic': '市场环境影响用户行为'
    }
}
```

### 二级重要特征

#### 4. 行为模式特征
```python
behavioral_patterns = [
    'buy_sell_ratio',  # 买入卖出比率
    'trading_intensity_score',  # 交易强度评分
    'asset_class_diversity',  # 资产类别多样性
    'strategy_consistency',  # 投资策略一致性
    'fee_sensitivity',  # 费用敏感性
    'market_timing_behavior'  # 市场时机把握行为
]
```

### 关键衍生特征
```python
derived_features = [
    'user_engagement_score',  # 用户参与度综合评分
    'financial_health_score',  # 财务健康评分
    'churn_risk_indicators',  # 流失风险指标组合
    'reactivation_potential',  # 重激活潜力评分
    'customer_lifetime_value'  # 客户生命周期价值
]
```

## 数据关联策略

### 用户-账户关联
需要确认USERS表与beamaccount表的关联方式，可能的关联字段：
- TAXID (税务ID)
- USERNAME (用户名)
- 其他业务字段

### 数据聚合查询示例
```sql
-- 用户级别特征聚合
WITH user_accounts AS (
    SELECT 
        u.USERNAME,
        u.STATUS,
        u.TENANTID,
        COUNT(b.ACCOUNTSHORTNAME) as total_accounts,
        SUM(CASE WHEN b.ACCOUNTCLOSEDATE IS NULL THEN 1 ELSE 0 END) as active_accounts,
        AVG(SYSDATE - b.ACCOUNTOPENDATE) as avg_account_age
    FROM USERS u
    JOIN USER_TO_ACCOUNT ua ON u.USERNAME = ua.USERNAME
    JOIN beamaccount b ON ua.ACCOUNTID = b.ID
    GROUP BY u.USERNAME, u.STATUS, u.TENANTID
),
user_transactions AS (
    SELECT 
        u.USERNAME,
        COUNT(t.EVENTDATE) as total_transactions,
        MAX(t.EVENTDATE) as last_transaction_date,
        SUM(t.BOOKAMOUNT) as total_transaction_amount,
        SUM(t.BOOKTOTALGAIN) as total_realized_gain,
        SUM(t.BOOKTOTALLOSS) as total_realized_loss
    FROM USERS u
    JOIN USER_TO_ACCOUNT ua ON u.USERNAME = ua.USERNAME  
    JOIN beamaccount b ON ua.ACCOUNTID = b.ID
    LEFT JOIN IDRTRANSACTION t ON b.ACCOUNTSHORTNAME = t.ACCOUNTSHORTNAME
    GROUP BY u.USERNAME
)
SELECT * FROM user_accounts ua
JOIN user_transactions ut ON ua.USERNAME = ut.USERNAME;
```

## 建模策略调整

### 两层预测架构
1. **用户级别主模型**: 预测用户整体流失风险
2. **账户级别辅助模型**: 支持更细粒度的风险分析

### 模型选择
- **主力模型**: XGBoost, LightGBM (处理复杂特征关系)
- **基线模型**: Logistic Regression, Random Forest
- **深度学习**: 考虑TabNet处理高维稀疏特征

### 评估指标调整
```python
evaluation_metrics = {
    'technical': ['AUC-ROC', 'Precision', 'Recall', 'F1-score'],
    'business': [
        'Top 10% precision',  # 高风险用户识别精度
        'Lift @ 10%',  # 提升度
        'Customer value preservation',  # 客户价值保护率
        'Reactivation prediction accuracy'  # 重激活预测精度
    ]
}
```

## 业务价值提升

### 用户级别预测的优势
1. **更全面的风险评估**: 考虑用户的总体资产和行为
2. **更精准的挽回策略**: 基于用户整体价值制定策略
3. **更有效的资源配置**: 避免对单一账户关闭过度反应
4. **更好的客户体验**: 理解用户的完整生命周期

### 商业应用场景
- **早期预警系统**: 识别有流失风险的高价值用户
- **个性化挽回**: 基于用户特征定制挽回方案
- **产品优化**: 分析用户流失原因优化服务
- **客户分层**: 基于流失风险进行客户分级管理

## 项目实施路线图 (重新优化)

### 🚀 Phase 1: 数据架构确认和EDA (第1周)

#### Week 1.1-1.3: 数据关联验证 ✅ (已完成)
```sql
-- ✅ 关联方式已确认: USER_TO_ACCOUNT中间表
-- 调整后的关键任务:
1. ✅ 确认关联架构: USERNAME → USER_TO_ACCOUNT → ACCOUNTID
2. 验证映射表数据质量和完整性
3. 测试内外部用户分类逻辑 (TENANTID)
4. 优化用户级别聚合查询性能
```

#### Week 1.4-1.7: 用户级别EDA
```python
# 核心分析任务
- 用户状态分布分析 (A/S/L/R比例)
- 用户价值分层 (基于总资产和交易量)
- 流失用户特征画像
- 时间序列趋势分析
```

### 🔬 Phase 2: 特征工程和基线建模 (第2周)

#### Week 2.1-2.4: 一级特征构建
```python
# 优先级顺序
1. 交易行为衰退特征 (IDRTRANSACTION聚合)
2. 投资表现恶化特征 (PROFITANDLOSSLITE聚合) 
3. 关系复杂度下降特征 (beamaccount聚合)
4. 用户参与度特征 (USERS + Override聚合)
```

#### Week 2.5-2.7: 基线模型建立
```python
# 模型对比实验
baseline_models = {
    'Logistic Regression': '可解释性基线',
    'Random Forest': '特征重要性分析', 
    'XGBoost': '性能基线',
    'LightGBM': '效率基线'
}
```

### 🎯 Phase 3: 高级建模和业务优化 (第3周)

#### Week 3.1-3.4: 模型优化
```python
# 高级技术应用
advanced_techniques = {
    'Feature Selection': 'Recursive Feature Elimination',
    'Hyperparameter Tuning': 'Bayesian Optimization',
    'Ensemble Methods': 'Stacking + Blending',
    'Time Series': 'LSTM for portfolio trends'
}
```

#### Week 3.5-3.7: 业务规则集成
```python
# 业务逻辑增强
business_rules = {
    'High Value Protection': '高价值用户特殊预警阈值',
    'Reactivation Prediction': 'R状态用户的重激活模式',
    'Intervention Timing': '最佳干预时机识别',
    'Cost-Benefit Analysis': 'ROI导向的预警策略'
}
```

### 🚀 Phase 4: 部署和运营化 (第4周)

#### Week 4.1-4.4: 系统开发
```python
# 技术架构
deployment_stack = {
    'Backend': 'Flask + SQLAlchemy (Oracle连接)',
    'Frontend': 'Bootstrap + Chart.js (仪表盘)',
    'ML Pipeline': 'scikit-learn + joblib (模型服务)',
    'Database': 'Oracle + Redis (缓存)'
}
```

#### Week 4.5-4.7: 业务集成
```python
# 运营集成
operational_integration = {
    'Alert System': '实时风险预警',
    'Customer Segmentation': '基于流失风险的客户分层',
    'Intervention Workflows': '自动化挽回流程触发',
    'Performance Monitoring': '模型效果持续监控'
}
```

## 成功度量和KPI设计

### 📊 技术指标
```python
technical_kpis = {
    'Model Performance': {
        'AUC-ROC': '>= 0.85',
        'Precision@10%': '>= 0.7',  # 预测前10%高风险用户的准确率
        'Recall@High_Value': '>= 0.8'  # 高价值客户的召回率
    },
    'System Performance': {
        'Prediction Latency': '< 100ms',
        'Daily Batch Processing': '< 30min',
        'Model Drift Detection': 'Weekly monitoring'
    }
}
```

### 💼 业务指标  
```python
business_kpis = {
    'Value Protection': {
        'Customer Value Preserved': '通过预警保护的客户总价值',
        'Churn Rate Reduction': '流失率下降幅度',
        'False Positive Cost': '错误预警的运营成本'
    },
    'Operational Efficiency': {
        'Early Warning Period': '平均提前预警天数',
        'Intervention Success Rate': '挽回行动的成功率',
        'Resource Allocation ROI': '客户经理资源配置的投资回报'
    }
}
```

## 项目交付物清单

### 📋 Phase 1 交付物
- [ ] 数据关联验证报告
- [ ] 用户级别EDA报告
- [ ] 数据质量评估报告
- [ ] 特征工程计划

### 📋 Phase 2 交付物  
- [ ] 特征工程代码库
- [ ] 基线模型对比报告
- [ ] 特征重要性分析
- [ ] 模型性能基准

### 📋 Phase 3 交付物
- [ ] 优化模型及参数
- [ ] 模型解释性分析(SHAP)
- [ ] 业务规则集成文档
- [ ] 模型验证报告

### 📋 Phase 4 交付物
- [ ] 完整的Web应用系统
- [ ] 模型部署和API文档
- [ ] 用户操作手册
- [ ] 运营监控仪表盘

## 风险缓解和应急计划

### ⚠️ 主要风险点
1. **数据关联问题**: 如果USERS表与账户表关联复杂
   - **缓解方案**: 先进行账户级别建模，再聚合到用户级别

2. **特征稀疏性**: 如果某些关键特征缺失率过高
   - **缓解方案**: 开发缺失值智能填充策略

3. **模型性能不达标**: 如果AUC < 0.8
   - **缓解方案**: 结合外部数据源，增加时序特征深度

4. **业务接受度**: 如果预测结果与业务直觉不符
   - **缓解方案**: 增强模型可解释性，提供详细的特征贡献分析

这个重新设计的项目指南显著提升了商业价值和技术深度，更好地匹配了InvestCloud的实际业务场景。 