# 客户流失预测项目 (Customer Churn Prediction)

## 项目概述

这是一个基于InvestCloud平台的客户流失预测项目，通过分析用户行为、交易模式、资产价值变化等多维度数据，预测客户流失风险。

## 核心特性

### 🎯 预测目标
- **用户级别预测**: 基于USERS.STATUS字段的用户流失预测
- **账户级别预测**: 基于账户关闭日期的辅助预测
- **多层次风险评估**: 综合用户行为和投资表现的风险评分

### 📊 数据源
- **USERS表**: 用户基础信息和状态
- **beamaccount表**: 账户信息和生命周期
- **IDRTRANSACTION表**: 交易行为数据
- **PROFITANDLOSSLITE表**: 资产价值和损益数据

### 🔧 技术栈
- **Python 3.8+**: 主要开发语言
- **Pandas**: 数据处理和分析
- **Scikit-learn**: 机器学习建模
- **XGBoost/LightGBM**: 高级梯度提升算法
- **Matplotlib/Seaborn**: 数据可视化
- **Oracle Database**: 数据存储

## 项目结构

```
customer_churn_prediction/
├── README.md                           # 项目说明文档
├── requirements.txt                    # Python依赖包
├── .gitignore                         # Git忽略文件配置
│
├── docs/                              # 项目文档
│   ├── Customer_Churn_Prediction_Tables_Analysis.md
│   ├── Feature_Analysis_Oracle_Database.md
│   ├── Oracle_Database_Analysis.md
│   └── SQL_Data_Export_Guide.md
│
├── src/                               # 源代码目录
│   ├── baseline_model_development.py  # 基线模型开发
│   ├── tier1_feature_engineering.py   # 特征工程
│   ├── user_level_eda.py             # 用户级别探索性分析
│   ├── data_architecture_validation.py # 数据架构验证
│   └── Churn_model_sample.py         # 模型示例
│
├── models/                           # 训练好的模型
│   ├── best_model_logistic_regression.joblib
│   └── feature_scaler.joblib
│
├── data/                            # 数据目录 (不包含在版本控制中)
│   └── processed/
│       └── tier1_features.csv
│
└── outputs/                         # 输出结果
    ├── account_status_distribution.png
    ├── baseline_model_performance.png
    ├── transaction_patterns.png
    └── user_value_segmentation.png
```

## 安装和设置

### 1. 克隆项目
```bash
git clone https://github.com/your-username/customer_churn_prediction.git
cd customer_churn_prediction
```

### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 数据库配置
- 配置Oracle数据库连接
- 确保有相关表的访问权限
- 参考 `SQL_Data_Export_Guide.md` 进行数据导出

## 使用方法

### 数据源配置

项目支持两种数据源：

#### 🔷 方式1: Oracle数据库（推荐用于生产环境）
1. **安装Oracle Instant Client**
   - 下载并解压Oracle Instant Client到 `C:\oracle\instantclient_21_18`
   - 或修改 `src/oracle_data_extractor.py` 中的路径配置

2. **配置数据库连接**
   ```python
   # 在 oracle_data_extractor.py 中配置
   username = "BGRO_citangk"
   password = "Cici0511"
   dsn = "UAT7ora:1521/ORAUAT7PRIV"
   ```

3. **运行数据提取**
   ```bash
   cd src
   python oracle_data_extractor.py
   ```

#### 🔷 方式2: 样本CSV文件（用于测试和开发）
使用项目根目录下的样本数据文件进行测试。

### 核心流程

#### 1. 数据预处理和特征工程
```bash
cd src
# 交互式选择数据源
python run_feature_engineering.py

# 或直接指定数据源
python tier1_feature_engineering.py  # 使用样本数据
```

#### 2. 探索性数据分析
```bash
cd src
python user_level_eda.py
```

#### 3. 模型训练
```bash
cd src
python baseline_model_development.py
```

#### 4. 数据架构验证
```bash
cd src
python data_architecture_validation.py
```

## 核心功能

### 🔍 特征工程
- **用户参与度评分**: 基于联系信息完整度、安全设置等
- **交易行为分析**: 频率衰退、金额波动、时间模式
- **投资表现指标**: 收益率、风险调整收益、最大回撤
- **资产价值趋势**: 市值变化、未实现损益、投资组合稳定性

### 📈 模型算法
- **逻辑回归**: 基线模型，提供良好的可解释性
- **随机森林**: 处理非线性关系和特征交互
- **XGBoost**: 高性能梯度提升算法
- **LightGBM**: 快速训练的梯度提升框架

### 📊 评估指标
- **准确率 (Accuracy)**: 整体预测正确率
- **精确率 (Precision)**: 流失预测的准确性
- **召回率 (Recall)**: 流失客户的识别率
- **F1-Score**: 精确率和召回率的调和平均
- **AUC-ROC**: 模型区分能力评估

## 业务价值

### 💼 应用场景
1. **客户保留策略**: 识别高风险客户，制定个性化保留方案
2. **资源优化配置**: 将有限的客户服务资源投入到关键客户
3. **产品改进指导**: 基于流失原因分析改进产品和服务
4. **收入预测**: 预测客户流失对收入的影响

### 📋 输出结果
- **客户风险评分**: 0-1之间的流失概率评分
- **风险因素分析**: 主要影响流失的特征因素
- **客户分层**: 基于风险评分的客户分层管理
- **预警报告**: 定期的高风险客户预警列表

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系信息

- 项目维护者: [Your Name]
- 邮箱: [your.email@example.com]
- 项目链接: [https://github.com/your-username/customer_churn_prediction](https://github.com/your-username/customer_churn_prediction)

## 更新日志

### v1.0.0 (2024-12-19)
- 初始版本发布
- 完成基础特征工程和模型开发
- 实现用户级别流失预测
- 添加数据架构验证功能

---

**注意**: 本项目包含敏感的客户数据，请确保在使用过程中遵守相关的数据保护法规和公司政策。 