#!/usr/bin/env python3
"""
InvestCloud Customer Churn Prediction Project - Account-Level Feature Engineering
Build predictive features for account-level churn prediction model.
Focus on account lifecycle, performance metrics, transaction patterns, and behavioral indicators.

Author: InvestCloud Intern
Purpose: Account-level churn prediction feature development
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import logging
from sklearn.preprocessing import LabelEncoder
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AccountLevelFeatureEngineering:
    """
    Account-level feature engineering for churn prediction.
    Creates features from account master, performance, and transaction data.
    """
    
    def __init__(self):
        """Initialize account-level feature engineering."""
        self.account_df = None
        self.performance_df = None
        self.transaction_df = None
        self.feature_df = None
        self.current_date = datetime.now()
        
        # Feature configuration
        self.performance_window_days = [30, 90, 180, 365]  # Analysis windows
        self.transaction_window_days = [30, 90, 180]       # Transaction analysis windows
        
    def load_data(self):
        """
        Load data from Oracle database.
        """
        try:
            logging.info("Loading data from Oracle database...")
            from account_level_data_extractor import AccountLevelDataExtractor
            
            # Create Oracle data extractor
            extractor = AccountLevelDataExtractor()
            
            # Initialize Oracle client
            if not extractor.initialize_oracle_client():
                logging.error("Oracle client initialization failed")
                return False
            
            # Connect to database
            if not extractor.connect_database():
                logging.error("Database connection failed")
                return False
            
            try:
                # Extract data
                results = extractor.extract_all_account_data()
                
                # Map to class attributes
                self.account_df = results.get('account')
                self.performance_df = results.get('performance')
                self.transaction_df = results.get('transaction')
                
                # Check if data was successfully loaded
                if any(df is None for df in [self.account_df, self.performance_df, self.transaction_df]):
                    logging.error("Some data tables failed to extract")
                    return False
                
                logging.info("Oracle data loading successful")
                
            finally:
                extractor.disconnect_database()
            
            # Data preprocessing
            self._preprocess_data()
            
            logging.info(f"Data loading completed - Accounts:{len(self.account_df)}, Performance:{len(self.performance_df)}, Transactions:{len(self.transaction_df)}")
            return True
            
        except Exception as e:
            logging.error(f"Data loading failed: {e}")
            return False
    

    
    def _preprocess_data(self):
        """Preprocess and clean extracted data."""
        logging.info("Preprocessing data...")
        
        # Convert date columns
        date_columns = {
            'account': ['ACCOUNTOPENDATE', 'ACCOUNTCLOSEDATE', 'CAPITALCOMMITMENTDATE', 
                       'BILLINGINCEPTIONDATE', 'INVESTMENTADVISORYTERMDATE', 'PERFBEGINDATE'],
            'performance': ['BE_ASOF'],
            'transaction': ['TRANSACTIONDATE', 'EFFECTIVEDATE']
        }
        
        # Process account data
        if self.account_df is not None:
            for col in date_columns['account']:
                if col in self.account_df.columns:
                    self.account_df[col] = pd.to_datetime(self.account_df[col], errors='coerce')
        
        # Process performance data
        if self.performance_df is not None:
            for col in date_columns['performance']:
                if col in self.performance_df.columns:
                    self.performance_df[col] = pd.to_datetime(self.performance_df[col], errors='coerce')
        
        # Process transaction data
        if self.transaction_df is not None:
            for col in date_columns['transaction']:
                if col in self.transaction_df.columns:
                    self.transaction_df[col] = pd.to_datetime(self.transaction_df[col], errors='coerce')
        
        logging.info("Data preprocessing completed")
    
    def build_account_lifecycle_features(self):
        """
        Build account lifecycle and demographic features.
        
        Returns:
            pd.DataFrame: Account lifecycle features
        """
        logging.info("Building account lifecycle features...")
        
        features = self.account_df[['ACCOUNTID', 'ACCOUNTSHORTNAME', 'CHURN_FLAG']].copy()
        
        # Account age in days
        features['account_age_days'] = (self.current_date - self.account_df['ACCOUNTOPENDATE']).dt.days
        features['account_age_years'] = features['account_age_days'] / 365.25
        
        # Account status and lifecycle features
        features['is_closed'] = self.account_df['ACCOUNTCLOSEDATE'].notna().astype(int)
        features['days_since_close'] = (self.current_date - self.account_df['ACCOUNTCLOSEDATE']).dt.days
        features['days_since_close'] = features['days_since_close'].fillna(-1)
        
        # Account type encoding
        le_account_type = LabelEncoder()
        features['account_type_encoded'] = le_account_type.fit_transform(
            self.account_df['ACCOUNTTYPE'].fillna('Unknown')
        )
        
        # Geographic features
        features['is_us_account'] = (self.account_df['DOMICILECOUNTRY'] == 'US').astype(int)
        features['is_high_tax_state'] = self.account_df['DOMICILESTATE'].isin(['CA', 'NY', 'NJ']).astype(int)
        
        # Currency features
        features['is_usd_account'] = (self.account_df['BOOKCCY'] == 'USD').astype(int)
        
        # Capital commitment features
        features['capital_commitment'] = self.account_df['CAPITALCOMMITMENTAMOUNT'].fillna(0)
        features['has_capital_commitment'] = (features['capital_commitment'] > 0).astype(int)
        features['log_capital_commitment'] = np.log1p(features['capital_commitment'])
        
        # Investment objectives encoding
        if 'ACCOUNTOBJECTIVE' in self.account_df.columns:
            le_objective = LabelEncoder()
            features['investment_objective_encoded'] = le_objective.fit_transform(
                self.account_df['ACCOUNTOBJECTIVE'].fillna('Unknown')
            )
        
        logging.info(f"Built {len(features.columns)} account lifecycle features")
        return features
    
    def build_account_performance_features(self):
        """
        Build account performance and portfolio features from PROFITANDLOSSLITE data.
        
        Returns:
            pd.DataFrame: Account performance features
        """
        logging.info("Building account performance features...")
        
        if self.performance_df is None or len(self.performance_df) == 0:
            logging.warning("No performance data available")
            return pd.DataFrame()
        
        # Group by account for aggregation
        account_features = []
        
        for account in self.performance_df['ACCOUNTSHORTNAME'].unique():
            account_data = self.performance_df[
                self.performance_df['ACCOUNTSHORTNAME'] == account
            ].copy()
            
            # Sort by date
            account_data = account_data.sort_values('BE_ASOF')
            
            features = {'ACCOUNTSHORTNAME': account}
            
            # Current portfolio value
            latest_data = account_data.iloc[-1] if len(account_data) > 0 else None
            if latest_data is not None:
                features['current_market_value'] = latest_data['BOOKMARKETVALUEPERIODEND']
                features['current_unrealized_pnl'] = latest_data['BOOKUGL']
            else:
                features['current_market_value'] = 0
                features['current_unrealized_pnl'] = 0
            
            # Portfolio value statistics for different time windows
            for window_days in self.performance_window_days:
                cutoff_date = self.current_date - timedelta(days=window_days)
                window_data = account_data[account_data['BE_ASOF'] >= cutoff_date]
                
                if len(window_data) > 0:
                    # Market value statistics
                    features[f'avg_market_value_{window_days}d'] = window_data['BOOKMARKETVALUEPERIODEND'].mean()
                    features[f'max_market_value_{window_days}d'] = window_data['BOOKMARKETVALUEPERIODEND'].max()
                    features[f'min_market_value_{window_days}d'] = window_data['BOOKMARKETVALUEPERIODEND'].min()
                    features[f'std_market_value_{window_days}d'] = window_data['BOOKMARKETVALUEPERIODEND'].std()
                    
                    # P&L statistics
                    features[f'avg_unrealized_pnl_{window_days}d'] = window_data['BOOKUGL'].mean()
                    features[f'total_unrealized_pnl_{window_days}d'] = window_data['BOOKUGL'].sum()
                    
                    # Value trend (slope of market value over time)
                    if len(window_data) > 1:
                        x = np.arange(len(window_data))
                        y = window_data['BOOKMARKETVALUEPERIODEND'].values
                        slope, _ = np.polyfit(x, y, 1)
                        features[f'market_value_trend_{window_days}d'] = slope
                    else:
                        features[f'market_value_trend_{window_days}d'] = 0
                else:
                    # Fill with zeros if no data in window
                    for metric in ['avg_market_value', 'max_market_value', 'min_market_value', 
                                 'std_market_value', 'avg_unrealized_pnl', 'total_unrealized_pnl',
                                 'market_value_trend']:
                        features[f'{metric}_{window_days}d'] = 0
            
            # Asset diversification features
            asset_classes = account_data['ASSETCLASSLEVEL1'].value_counts()
            features['num_asset_classes'] = len(asset_classes)
            features['top_asset_class_concentration'] = asset_classes.iloc[0] / len(account_data) if len(asset_classes) > 0 else 0
            
            # Most common asset class
            if len(asset_classes) > 0:
                features['primary_asset_class'] = asset_classes.index[0]
            else:
                features['primary_asset_class'] = 'Unknown'
            
            account_features.append(features)
        
        # Convert to DataFrame
        performance_features = pd.DataFrame(account_features)
        
        # Encode primary asset class
        if 'primary_asset_class' in performance_features.columns:
            le_asset = LabelEncoder()
            performance_features['primary_asset_class_encoded'] = le_asset.fit_transform(
                performance_features['primary_asset_class'].fillna('Unknown')
            )
        
        logging.info(f"Built {len(performance_features.columns)} account performance features")
        return performance_features
    
    def build_account_transaction_features(self):
        """
        Build account transaction behavior features from IDRTRANSACTION data.
        
        Returns:
            pd.DataFrame: Account transaction features
        """
        logging.info("Building account transaction features...")
        
        if self.transaction_df is None or len(self.transaction_df) == 0:
            logging.warning("No transaction data available")
            return pd.DataFrame()
        
        account_features = []
        
        for account in self.transaction_df['ACCOUNTSHORTNAME'].unique():
            account_txns = self.transaction_df[
                self.transaction_df['ACCOUNTSHORTNAME'] == account
            ].copy()
            
            # Sort by date
            account_txns = account_txns.sort_values('TRANSACTIONDATE')
            
            features = {'ACCOUNTSHORTNAME': account}
            
            # Overall transaction statistics
            features['total_transactions'] = len(account_txns)
            features['total_transaction_volume'] = account_txns['BOOKAMOUNT'].abs().sum()
            features['avg_transaction_size'] = account_txns['BOOKAMOUNT'].abs().mean()
            features['max_transaction_size'] = account_txns['BOOKAMOUNT'].abs().max()
            
            # Transaction type diversity
            event_types = account_txns['EVENTTYPE'].value_counts()
            features['num_transaction_types'] = len(event_types)
            
            # Most common transaction type
            if len(event_types) > 0:
                features['primary_transaction_type'] = event_types.index[0]
                features['primary_transaction_type_pct'] = event_types.iloc[0] / len(account_txns)
            else:
                features['primary_transaction_type'] = 'Unknown'
                features['primary_transaction_type_pct'] = 0
            
            # Time-windowed transaction features
            for window_days in self.transaction_window_days:
                cutoff_date = self.current_date - timedelta(days=window_days)
                window_txns = account_txns[account_txns['TRANSACTIONDATE'] >= cutoff_date]
                
                if len(window_txns) > 0:
                    features[f'transaction_count_{window_days}d'] = len(window_txns)
                    features[f'transaction_volume_{window_days}d'] = window_txns['BOOKAMOUNT'].abs().sum()
                    features[f'avg_transaction_size_{window_days}d'] = window_txns['BOOKAMOUNT'].abs().mean()
                    features[f'transaction_frequency_{window_days}d'] = len(window_txns) / window_days
                    
                    # Net cash flow
                    features[f'net_cash_flow_{window_days}d'] = window_txns['BOOKAMOUNT'].sum()
                    
                    # Days since last transaction
                    if len(window_txns) > 0:
                        last_txn_date = window_txns['TRANSACTIONDATE'].max()
                        features[f'days_since_last_transaction'] = (self.current_date - last_txn_date).days
                    else:
                        features[f'days_since_last_transaction'] = 9999
                else:
                    # Fill with zeros if no transactions in window
                    for metric in ['transaction_count', 'transaction_volume', 'avg_transaction_size',
                                 'transaction_frequency', 'net_cash_flow']:
                        features[f'{metric}_{window_days}d'] = 0
                    features[f'days_since_last_transaction'] = 9999
            
            account_features.append(features)
        
        # Convert to DataFrame
        transaction_features = pd.DataFrame(account_features)
        
        # Encode primary transaction type
        if 'primary_transaction_type' in transaction_features.columns:
            le_txn_type = LabelEncoder()
            transaction_features['primary_transaction_type_encoded'] = le_txn_type.fit_transform(
                transaction_features['primary_transaction_type'].fillna('Unknown')
            )
        
        logging.info(f"Built {len(transaction_features.columns)} account transaction features")
        return transaction_features
    
    def build_integrated_features(self):
        """
        Build all account-level features and integrate them.
        
        Returns:
            pd.DataFrame: Complete feature dataset for modeling
        """
        logging.info("Building integrated account-level feature set...")
        
        # Build individual feature sets
        lifecycle_features = self.build_account_lifecycle_features()
        performance_features = self.build_account_performance_features()
        transaction_features = self.build_account_transaction_features()
        
        # Start with lifecycle features (contains target variable)
        integrated_features = lifecycle_features.copy()
        
        # Merge performance features
        if len(performance_features) > 0:
            integrated_features = integrated_features.merge(
                performance_features, 
                on='ACCOUNTSHORTNAME', 
                how='left'
            )
        
        # Merge transaction features
        if len(transaction_features) > 0:
            integrated_features = integrated_features.merge(
                transaction_features, 
                on='ACCOUNTSHORTNAME', 
                how='left'
            )
        
        # Fill missing values with appropriate defaults
        numeric_columns = integrated_features.select_dtypes(include=[np.number]).columns
        integrated_features[numeric_columns] = integrated_features[numeric_columns].fillna(0)
        
        # Create risk score features
        self._create_risk_score_features(integrated_features)
        
        logging.info(f"Integrated feature set built with {len(integrated_features.columns)} features")
        logging.info(f"Feature dataset shape: {integrated_features.shape}")
        
        self.feature_df = integrated_features
        return integrated_features
    
    def _create_risk_score_features(self, df):
        """
        Create composite risk score features.
        
        Args:
            df (pd.DataFrame): Feature dataframe to add risk scores to
        """
        # Performance risk score
        if 'std_market_value_365d' in df.columns and 'avg_market_value_365d' in df.columns:
            df['portfolio_volatility_score'] = df['std_market_value_365d'] / (df['avg_market_value_365d'] + 1)
        else:
            df['portfolio_volatility_score'] = 0
        
        # Activity risk score
        if 'transaction_frequency_90d' in df.columns:
            df['low_activity_score'] = np.where(df['transaction_frequency_90d'] < 0.1, 1, 0)
        else:
            df['low_activity_score'] = 0
        
        # Value decline risk score
        if 'market_value_trend_180d' in df.columns:
            df['declining_value_score'] = np.where(df['market_value_trend_180d'] < 0, 1, 0)
        else:
            df['declining_value_score'] = 0
        
        # Composite churn risk score
        df['composite_churn_risk'] = (
            df.get('portfolio_volatility_score', 0) * 0.3 +
            df.get('low_activity_score', 0) * 0.4 +
            df.get('declining_value_score', 0) * 0.3
        )
    
    def generate_feature_report(self):
        """Generate comprehensive feature engineering report."""
        if self.feature_df is None:
            logging.warning("No features generated yet")
            return
        
        logging.info("Generating feature engineering report...")
        
        report = []
        report.append("=" * 80)
        report.append("ACCOUNT-LEVEL CHURN PREDICTION - FEATURE ENGINEERING REPORT")
        report.append("=" * 80)
        report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Dataset summary
        report.append("DATASET SUMMARY:")
        report.append(f"  • Total Accounts: {len(self.feature_df):,}")
        report.append(f"  • Total Features: {len(self.feature_df.columns):,}")
        report.append(f"  • Churned Accounts: {self.feature_df['CHURN_FLAG'].sum():,} ({self.feature_df['CHURN_FLAG'].mean()*100:.1f}%)")
        report.append("")
        
        # Feature categories
        lifecycle_cols = [col for col in self.feature_df.columns if any(x in col.lower() for x in ['age', 'type', 'commitment', 'objective'])]
        performance_cols = [col for col in self.feature_df.columns if any(x in col.lower() for x in ['market_value', 'pnl', 'asset'])]
        transaction_cols = [col for col in self.feature_df.columns if any(x in col.lower() for x in ['transaction', 'volume', 'frequency'])]
        risk_cols = [col for col in self.feature_df.columns if any(x in col.lower() for x in ['risk', 'score', 'volatility'])]
        
        report.append("FEATURE CATEGORIES:")
        report.append(f"  • Account Lifecycle Features: {len(lifecycle_cols)}")
        report.append(f"  • Performance Features: {len(performance_cols)}")
        report.append(f"  • Transaction Behavior Features: {len(transaction_cols)}")
        report.append(f"  • Risk Score Features: {len(risk_cols)}")
        report.append("")
        
        # Data quality check
        report.append("DATA QUALITY:")
        missing_data = self.feature_df.isnull().sum()
        problematic_features = missing_data[missing_data > 0]
        
        if len(problematic_features) > 0:
            report.append(f"  • Features with missing values: {len(problematic_features)}")
            for feature, missing_count in problematic_features.head(5).items():
                missing_pct = missing_count / len(self.feature_df) * 100
                report.append(f"    - {feature}: {missing_count} ({missing_pct:.1f}%)")
        else:
            report.append("  • No missing values detected ✓")
        report.append("")
        
        # Feature correlation with target
        report.append("TOP 15 FEATURES BY CHURN CORRELATION:")
        numeric_features = self.feature_df.select_dtypes(include=[np.number]).columns
        correlations = self.feature_df[numeric_features].corrwith(self.feature_df['CHURN_FLAG'])
        top_correlations = correlations.abs().sort_values(ascending=False).head(15)
        
        for feature, corr in top_correlations.items():
            if feature != 'CHURN_FLAG':
                report.append(f"  • {feature}: {corr:.3f}")
        
        report_text = "\n".join(report)
        
        # Save report
        report_filename = f'../data/reports/account_feature_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        os.makedirs(os.path.dirname(report_filename), exist_ok=True)
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        logging.info(f"Feature report saved to: {report_filename}")
        print(report_text)
    
    def save_features(self, filename=None):
        """Save engineered features to CSV file."""
        if self.feature_df is None:
            logging.warning("No features to save")
            return
        
        if filename is None:
            filename = f'../data/processed/account_churn_features_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.feature_df.to_csv(filename, index=False)
        
        logging.info(f"Features saved to {filename}")
        print(f"💾 Features saved to {filename}")

def main():
    """
    Main function for account-level feature engineering.
    """
    print("🔧 InvestCloud Customer Churn Prediction - Account-Level Feature Engineering")
    print("=" * 85)
    print("📊 Using Oracle database data source")
    
    # Initialize feature engineering
    feature_eng = AccountLevelFeatureEngineering()
    
    # Load data
    if not feature_eng.load_data():
        print("❌ Data loading failed, program exiting")
        return
    
    # Build features
    features_df = feature_eng.build_integrated_features()
    
    # Generate report
    feature_eng.generate_feature_report()
    
    # Save features
    feature_eng.save_features()
    
    print("\n✅ Account-level feature engineering completed!")
    print("🎯 Ready to proceed with model development")

if __name__ == "__main__":
    main() 