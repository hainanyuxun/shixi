# USERS表字段分析参考

## 表结构概述
USERS表是InvestCloud的用户管理表，存储所有用户的基本信息和状态。这是客户流失预测项目中的**用户维度核心表**，将分析重点从账户级别提升到用户级别。

## 流失预测层级重新定义

### 层级关系
```
用户 (USERS) 
   ↓ (一对多)
账户 (beamaccount)
   ↓ (一对多)  
交易记录 (IDRTRANSACTION)
资产价值 (PROFITANDLOSSLITE)
```

### 预测目标调整
- **主要目标**: 预测用户流失 (用户不再使用平台)
- **次要目标**: 预测账户流失 (特定账户关闭，但用户可能有其他账户)

## 关键字段分析

### 核心标识字段

#### USERNAME (必填)
- **数据类型**: VARCHAR2(100 BYTE)
- **业务含义**: 用户名，环境内必须唯一
- **流失预测价值**: ⭐⭐⭐⭐⭐ (用户唯一标识)
- **关联策略**: 通过USER_TO_ACCOUNT中间映射表关联到账户表

#### TENANTID (必填)
- **数据类型**: NUMBER(10,0)
- **业务含义**: 租户ID，区分内部员工和外部用户
- **流失预测价值**: ⭐⭐⭐⭐ (用户类型分层)
- **业务规则**: 
  - NeubergerBerman_Employee: 内部员工
  - NeubergerBerman_Users: 外部客户

### 用户状态字段 (核心流失标签)

#### STATUS
- **数据类型**: VARCHAR2(10 BYTE)
- **业务含义**: 用户状态标识
- **流失预测价值**: ⭐⭐⭐⭐⭐ (直接流失标签)
- **状态定义**:
  - **A** = Active (活跃用户)
  - **S** = Deactivated/Suspended (停用/暂停 - **潜在流失**)
  - **L** = Locked (锁定 - **流失风险**)
  - **R** = Reactivated (重新激活 - **回流用户**)

### 用户基本信息字段

#### 个人信息
- **FIRSTNAME, LASTNAME, MIDDLENAME**: 姓名信息
- **PREFERREDNAME**: 偏好姓名
- **DATEOFBIRTH**: 出生日期
- **流失预测价值**: ⭐⭐ (人口统计学特征)

#### 联系信息 (重要预测因子)
- **EMAILADDRESS** (主要邮箱)
- **EMAILADDRESS2** (备用邮箱)
- **PRIMARYPHONENUMBER** (主要电话)
- **PHONE2, PHONE3** (备用电话)
- **流失预测价值**: ⭐⭐⭐⭐ (联系方式完整性反映参与度)

#### 地理信息
- **ADDRESS1, ADDRESS2**: 地址信息
- **CITY**: 城市
- **STATEPROVINCE**: 州/省
- **COUNTRYORREGION**: 国家/地区
- **ZIPPOSTALCODE**: 邮政编码
- **流失预测价值**: ⭐⭐⭐ (地理分布和财富分层)

### 安全和参与度字段

#### 安全问题设置
- **SECRETQUESTION, SECRETQUESTION2, SECRETQUESTION3**: 安全问题
- **ANSWERTOSECRETQUESTION, ANSWERTOSECRETQUESTION2, ANSWERTOSECRETQUESTION3**: 安全问题答案
- **流失预测价值**: ⭐⭐⭐ (安全设置完整性反映参与度)

#### 其他标识
- **ALTID1, ALTID2, ALTID3**: 备用ID (灵活报告字段)
- **TAXID**: 税务ID (SSN后4位)
- **TITLE**: 用户职位
- **流失预测价值**: ⭐⭐ (补充信息)

## 流失标签重新定义

### 基于STATUS字段的流失定义
```sql
CASE 
    WHEN STATUS = 'A' THEN 0  -- 活跃用户
    WHEN STATUS = 'R' THEN 0  -- 重新激活用户 
    WHEN STATUS IN ('S', 'L') THEN 1  -- 流失用户
    ELSE NULL  -- 数据质量问题
END AS churn_label
```

### 多层次流失分析
1. **硬流失**: STATUS = 'S' (彻底停用)
2. **软流失**: STATUS = 'L' (临时锁定，可能恢复)
3. **活跃用户**: STATUS = 'A'
4. **回流用户**: STATUS = 'R' (特殊研究群体)

## 用户-账户关联策略 ✅ (已确认)

### 确认的关联关系
```sql
-- ✅ 已确认的关联方式: USER_TO_ACCOUNT中间映射表
SELECT 
    u.USERNAME,
    u.STATUS as user_status,
    ua.TENANTID,
    CASE 
        WHEN ua.TENANTID = (SELECT ID FROM TENANT WHERE NAME = 'NeubergerBerman_Employee') 
        THEN 'Internal_Employee'
        ELSE 'External_Client' 
    END as user_type,
    b.ACCOUNTSHORTNAME,
    b.ACCOUNTCLOSEDATE,
    CASE WHEN b.ACCOUNTCLOSEDATE IS NULL THEN 0 ELSE 1 END as account_churn
FROM USERS u
JOIN USER_TO_ACCOUNT ua ON u.USERNAME = ua.USERNAME
JOIN beamaccount b ON ua.ACCOUNTID = b.ID
```

### 用户级别聚合特征
```sql
-- 用户级别的账户汇总 (基于确认的关联关系)
SELECT 
    u.USERNAME,
    u.STATUS as user_status,
    CASE 
        WHEN ua.TENANTID = (SELECT ID FROM TENANT WHERE NAME = 'NeubergerBerman_Employee') 
        THEN 'Internal_Employee'
        ELSE 'External_Client' 
    END as user_type,
    COUNT(b.ACCOUNTSHORTNAME) as total_accounts,
    SUM(CASE WHEN b.ACCOUNTCLOSEDATE IS NULL THEN 1 ELSE 0 END) as active_accounts,
    SUM(CASE WHEN b.ACCOUNTCLOSEDATE IS NOT NULL THEN 1 ELSE 0 END) as closed_accounts,
    AVG(SYSDATE - b.ACCOUNTOPENDATE) as avg_account_age_days,
    COUNT(DISTINCT b.CLASSIFICATION1) as account_type_diversity
FROM USERS u
JOIN USER_TO_ACCOUNT ua ON u.USERNAME = ua.USERNAME
JOIN beamaccount b ON ua.ACCOUNTID = b.ID
GROUP BY u.USERNAME, u.STATUS, ua.TENANTID
```

## 特征工程建议

### 1. 用户参与度特征 (一级重要)
- **信息完整度**: 统计非空字段数量
- **联系方式多样性**: 邮箱和电话数量
- **安全设置完整性**: 安全问题设置数量
- **地址信息完整性**: 地址字段完整程度

### 2. 用户档案特征 (二级重要)
- **年龄**: 基于DATEOFBIRTH计算
- **地理位置**: 基于STATEPROVINCE的风险评分
- **用户类型**: 基于TENANTID的内外部分类

### 3. 账户汇总特征 (一级重要)
- **账户数量**: 用户拥有的总账户数
- **活跃账户比例**: 未关闭账户比例
- **账户价值汇总**: 所有账户的总资产
- **交易活跃度汇总**: 所有账户的交易频率总和

### 4. 历史行为特征 (一级重要)
- **状态变化历史**: 如果有历史状态数据
- **最后活跃时间**: 最近一次状态更新或交易时间
- **重激活模式**: R状态的用户特征分析

## 数据质量考量

### 关键验证点
1. **USERNAME唯一性**: 确保没有重复用户名
2. **STATUS有效性**: 确认所有状态值都在预期范围内
3. **TENANTID一致性**: 验证租户分类的正确性
4. **✅ 关联完整性**: 已确认通过USER_TO_ACCOUNT中间表关联

### 缺失值处理策略
- **联系信息**: 缺失可能指示参与度低
- **地址信息**: 缺失可能影响地理分析
- **个人信息**: 缺失可能指示隐私偏好

## 预测模型调整建议

### 两层预测模型
1. **用户级别模型**: 预测用户整体流失风险
2. **账户级别模型**: 预测特定账户关闭风险

### 特征重要性重排
- **用户状态历史** (如果可获得)
- **账户汇总指标** (数量、价值、活跃度)
- **用户参与度指标** (信息完整性)
- **交易行为汇总** (跨所有账户)
- **地理和人口统计学特征**

## 业务价值提升

### 用户级别预测的优势
1. **更准确的风险识别**: 用户可能关闭一个账户但保留其他账户
2. **更有效的挽回策略**: 针对用户而非单一账户
3. **更全面的价值评估**: 考虑用户的总体价值
4. **更好的资源配置**: 根据用户级别风险分配客户经理资源

✅ **关联关系已确认**: 通过USER_TO_ACCOUNT中间映射表实现用户与账户的关联，为用户级别的流失预测提供了坚实的数据基础。现在可以直接开始用户级别的特征工程和模型开发。 