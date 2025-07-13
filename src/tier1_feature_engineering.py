#!/usr/bin/env python3
"""
InvestCloud Customer Churn Prediction Project - Tier-1 Core Feature Engineering
Build highest predictive value features based on EDA insights:
1. Transaction behavior decay features
2. Investment performance deterioration features
3. Account relationship complexity decline features
4. User engagement decline features
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import logging
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Tier1FeatureEngineering:
    """Tier-1 Core Feature Engineering"""
    
    def __init__(self):
        """Initialize feature engineering"""
        self.accounts_df = None
        self.transactions_df = None
        self.pnl_df = None
        self.feature_df = None
        self.current_date = datetime.now()
        
    def load_data(self):
        """Load sample data"""
        try:
            logging.info("Loading sample data...")
            
            # Load three core data tables
            self.accounts_df = pd.read_csv('Account_sampledata.csv')
            self.transactions_df = pd.read_csv('Transaction_sampledata.csv')
            self.pnl_df = pd.read_csv('PNL_sampledata.csv')
            
            # Data preprocessing
            self._preprocess_data()
            
            logging.info(f"Data loading completed - Accounts:{len(self.accounts_df)}, Transactions:{len(self.transactions_df)}, PNL:{len(self.pnl_df)}")
            return True
            
        except Exception as e:
            logging.error(f"Data loading failed: {e}")
            return False
    
    def _preprocess_data(self):
        """Data preprocessing"""
        # Process date fields
        if 'ACCOUNTOPENDATE' in self.accounts_df.columns:
            self.accounts_df['ACCOUNTOPENDATE'] = pd.to_datetime(self.accounts_df['ACCOUNTOPENDATE'])
        if 'ACCOUNTCLOSEDATE' in self.accounts_df.columns:
            self.accounts_df['ACCOUNTCLOSEDATE'] = pd.to_datetime(self.accounts_df['ACCOUNTCLOSEDATE'])
        
        if 'EVENTDATE' in self.transactions_df.columns:
            self.transactions_df['EVENTDATE'] = pd.to_datetime(self.transactions_df['EVENTDATE'])
        if 'TRADEDATE' in self.transactions_df.columns:
            self.transactions_df['TRADEDATE'] = pd.to_datetime(self.transactions_df['TRADEDATE'])
        
        if 'BE_ASOF' in self.pnl_df.columns:
            self.pnl_df['BE_ASOF'] = pd.to_datetime(self.pnl_df['BE_ASOF'])
        
        # Ensure correct data types
        numeric_cols_trans = ['ACCOUNTID', 'BOOKAMOUNT', 'QUANTITY', 'BOOKTOTALLOSS', 'BOOKTOTALGAIN']
        for col in numeric_cols_trans:
            if col in self.transactions_df.columns:
                self.transactions_df[col] = pd.to_numeric(self.transactions_df[col], errors='coerce')
        
        logging.info("Data preprocessing completed")
    
    def build_tier1_features(self):
        """Build Tier-1 core features"""
        logging.info("=== Starting Tier-1 Core Feature Engineering ===")
        
        # Create feature dataframe based on account ID
        self.feature_df = self.accounts_df[['ID']].copy()
        self.feature_df.columns = ['ACCOUNT_ID']
        
        # Add basic target variable and account information
        self.feature_df = self.feature_df.merge(
            self.accounts_df[['ID', 'CHURN_FLAG', 'CLASSIFICATION1', 'DOMICILESTATE', 
                             'ACCOUNTOPENDATE', 'ACCOUNTCLOSEDATE', 'ACCOUNTSTATUS']],
            left_on='ACCOUNT_ID', right_on='ID', how='left'
        ).drop('ID', axis=1)
        
        # 1. Build transaction behavior decay features
        self._build_transaction_behavior_features()
        
        # 2. Build investment performance features
        self._build_investment_performance_features()
        
        # 3. Build account lifecycle features
        self._build_account_lifecycle_features()
        
        # 4. Build risk scoring features
        self._build_risk_scoring_features()
        
        logging.info(f"Tier-1 feature engineering completed, generated {len(self.feature_df.columns)-1} features")
        return self.feature_df
    
    def _build_transaction_behavior_features(self):
        """Build transaction behavior decay features"""
        logging.info("Building transaction behavior decay features...")
        
        # Calculate transaction behavior features for each account
        transaction_features = []
        
        for account_id in self.feature_df['ACCOUNT_ID']:
            # Get transaction records for this account
            account_transactions = self.transactions_df[
                self.transactions_df['ACCOUNTID'] == account_id
            ].copy()
            
            if len(account_transactions) == 0:
                # Accounts with no transaction records
                features = {
                    'ACCOUNT_ID': account_id,
                    'total_transactions': 0,
                    'transaction_frequency_30d': 0,
                    'transaction_frequency_90d': 0,
                    'days_since_last_transaction': 9999,
                    'avg_transaction_amount': 0,
                    'total_transaction_volume': 0,
                    'transaction_volatility': 0,
                    'net_cash_flow': 0,
                    'inflow_outflow_ratio': 0,
                    'total_realized_gain': 0,
                    'total_realized_loss': 0,
                    'gain_loss_ratio': 0,
                    'transaction_trend_30d': 0,
                    'large_transaction_count': 0,
                    'transaction_consistency_score': 0
                }
            else:
                # Calculate various transaction behavior metrics
                current_date = self.current_date
                
                # Time window calculations
                transactions_30d = account_transactions[
                    account_transactions['EVENTDATE'] >= (current_date - timedelta(days=30))
                ]
                transactions_90d = account_transactions[
                    account_transactions['EVENTDATE'] >= (current_date - timedelta(days=90))
                ]
                
                # Basic statistics
                total_transactions = len(account_transactions)
                transaction_freq_30d = len(transactions_30d)
                transaction_freq_90d = len(transactions_90d)
                
                # Last transaction time
                last_transaction_date = account_transactions['EVENTDATE'].max()
                days_since_last = (current_date - last_transaction_date).days if pd.notna(last_transaction_date) else 9999
                
                # Transaction amount statistics
                amounts = account_transactions['BOOKAMOUNT'].dropna()
                avg_amount = amounts.mean() if len(amounts) > 0 else 0
                total_volume = amounts.abs().sum() if len(amounts) > 0 else 0
                volatility = amounts.std() if len(amounts) > 1 else 0
                
                # Cash flow analysis
                inflows = amounts[amounts > 0].sum() if len(amounts) > 0 else 0
                outflows = amounts[amounts < 0].sum() if len(amounts) > 0 else 0
                net_cash_flow = inflows + outflows  # outflows are negative
                inflow_outflow_ratio = abs(inflows / outflows) if outflows != 0 else (1 if inflows > 0 else 0)
                
                # Profit/loss analysis
                total_gain = account_transactions['BOOKTOTALGAIN'].fillna(0).sum()
                total_loss = account_transactions['BOOKTOTALLOSS'].fillna(0).sum()
                gain_loss_ratio = total_gain / total_loss if total_loss > 0 else (1 if total_gain > 0 else 0)
                
                # Trend analysis
                amounts_30d = transactions_30d['BOOKAMOUNT'].dropna()
                trend_30d = amounts_30d.mean() if len(amounts_30d) > 0 else 0
                
                # Large transaction count
                if len(amounts) > 0:
                    large_threshold = amounts.quantile(0.9) if len(amounts) > 10 else amounts.abs().mean() * 2
                    large_transaction_count = len(amounts[amounts.abs() >= large_threshold])
                else:
                    large_transaction_count = 0
                
                # Transaction consistency score (based on standard deviation of transaction intervals)
                if len(account_transactions) > 2:
                    dates = account_transactions['EVENTDATE'].sort_values()
                    intervals = dates.diff().dt.days.dropna()
                    consistency_score = 1 / (1 + intervals.std()) if len(intervals) > 0 and intervals.std() > 0 else 1
                else:
                    consistency_score = 0
                
                features = {
                    'ACCOUNT_ID': account_id,
                    'total_transactions': total_transactions,
                    'transaction_frequency_30d': transaction_freq_30d,
                    'transaction_frequency_90d': transaction_freq_90d,
                    'days_since_last_transaction': days_since_last,
                    'avg_transaction_amount': avg_amount,
                    'total_transaction_volume': total_volume,
                    'transaction_volatility': volatility,
                    'net_cash_flow': net_cash_flow,
                    'inflow_outflow_ratio': inflow_outflow_ratio,
                    'total_realized_gain': total_gain,
                    'total_realized_loss': total_loss,
                    'gain_loss_ratio': gain_loss_ratio,
                    'transaction_trend_30d': trend_30d,
                    'large_transaction_count': large_transaction_count,
                    'transaction_consistency_score': consistency_score
                }
            
            transaction_features.append(features)
        
        # Convert to DataFrame and merge with feature_df
        trans_features_df = pd.DataFrame(transaction_features)
        self.feature_df = self.feature_df.merge(trans_features_df, on='ACCOUNT_ID', how='left')
        
        logging.info(f"Transaction behavior features completed: {len(trans_features_df.columns)-1} features")
    
    def _build_investment_performance_features(self):
        """Build investment performance deterioration features"""
        logging.info("Building investment performance features...")
        
        # For each account, calculate investment performance metrics
        performance_features = []
        
        for account_id in self.feature_df['ACCOUNT_ID']:
            # Get PNL records for this account
            # Note: Adjust field name based on actual data structure
            account_pnl = self.pnl_df[
                self.pnl_df['ACCOUNT_ID'] == account_id
            ].copy() if 'ACCOUNT_ID' in self.pnl_df.columns else pd.DataFrame()
            
            if len(account_pnl) == 0:
                # No PNL records
                features = {
                    'ACCOUNT_ID': account_id,
                    'current_portfolio_value': 0,
                    'portfolio_volatility': 0,
                    'unrealized_pnl': 0,
                    'total_return_pct': 0,
                    'max_drawdown': 0,
                    'portfolio_diversification': 0,
                    'value_at_risk': 0
                }
            else:
                # Calculate investment performance metrics
                # Using available fields, mapping to meaningful metrics
                current_value = account_pnl['DAY_BOOK_MARKET_VALUE'].fillna(0).sum() if 'DAY_BOOK_MARKET_VALUE' in account_pnl.columns else 0
                
                # Portfolio volatility (standard deviation of daily values)
                values = account_pnl['DAY_BOOK_MARKET_VALUE'].dropna() if 'DAY_BOOK_MARKET_VALUE' in account_pnl.columns else pd.Series()
                volatility = values.std() if len(values) > 1 else 0
                
                # Unrealized P&L
                unrealized_pnl = account_pnl['UNREALIZED_PL'].fillna(0).sum() if 'UNREALIZED_PL' in account_pnl.columns else 0
                
                # Total return percentage
                if len(values) > 1:
                    initial_value = values.iloc[0] if values.iloc[0] != 0 else 1
                    final_value = values.iloc[-1]
                    total_return_pct = (final_value - initial_value) / initial_value * 100
                else:
                    total_return_pct = 0
                
                # Maximum drawdown
                if len(values) > 1:
                    peak = values.expanding().max()
                    drawdown = (values - peak) / peak
                    max_drawdown = drawdown.min() * 100
                else:
                    max_drawdown = 0
                
                # Portfolio diversification (number of unique securities)
                diversification = account_pnl['SECURITY_ID'].nunique() if 'SECURITY_ID' in account_pnl.columns else 0
                
                # Value at Risk (simplified as 5th percentile of daily returns)
                if len(values) > 10:
                    returns = values.pct_change().dropna()
                    var_5pct = returns.quantile(0.05) * 100
                else:
                    var_5pct = 0
                
                features = {
                    'ACCOUNT_ID': account_id,
                    'current_portfolio_value': current_value,
                    'portfolio_volatility': volatility,
                    'unrealized_pnl': unrealized_pnl,
                    'total_return_pct': total_return_pct,
                    'max_drawdown': max_drawdown,
                    'portfolio_diversification': diversification,
                    'value_at_risk': var_5pct
                }
            
            performance_features.append(features)
        
        # Convert to DataFrame and merge
        perf_features_df = pd.DataFrame(performance_features)
        self.feature_df = self.feature_df.merge(perf_features_df, on='ACCOUNT_ID', how='left')
        
        logging.info(f"Investment performance features completed: {len(perf_features_df.columns)-1} features")
    
    def _build_account_lifecycle_features(self):
        """Build account lifecycle features"""
        logging.info("Building account lifecycle features...")
        
        # Calculate account age
        self.feature_df['account_age_years'] = (
            self.current_date - self.feature_df['ACCOUNTOPENDATE']
        ).dt.days / 365.25
        
        # Account status encoding
        status_map = {'OPEN': 1, 'CLOSED': 0}
        self.feature_df['account_status_encoded'] = self.feature_df['ACCOUNTSTATUS'].map(status_map).fillna(0)
        
        # Days since account closure (for closed accounts)
        self.feature_df['days_since_closure'] = np.where(
            self.feature_df['ACCOUNTSTATUS'] == 'CLOSED',
            (self.current_date - self.feature_df['ACCOUNTCLOSEDATE']).dt.days,
            0
        )
        
        # Customer value tier based on account age
        self.feature_df['value_tier'] = pd.cut(
            self.feature_df['account_age_years'],
            bins=[0, 2, 5, 10, float('inf')],
            labels=[1, 2, 3, 4]  # 1=New, 2=Growing, 3=Mature, 4=Long-term
        ).astype(float)
        
        # Geographic risk (state-based churn rate encoding)
        state_risk_map = {'CA': 3, 'NY': 2, 'FL': 1, 'NJ': 1}  # Based on EDA findings
        self.feature_df['geographic_risk'] = self.feature_df['DOMICILESTATE'].map(state_risk_map).fillna(1)
        
        logging.info("Account lifecycle features completed: 5 features")
    
    def _build_risk_scoring_features(self):
        """Build risk scoring features"""
        logging.info("Building risk scoring features...")
        
        # Comprehensive risk score based on multiple factors
        risk_factors = []
        
        # Transaction activity risk
        self.feature_df['transaction_activity_risk'] = np.where(
            self.feature_df['days_since_last_transaction'] > 365, 3,
            np.where(self.feature_df['days_since_last_transaction'] > 180, 2, 1)
        )
        
        # Portfolio performance risk
        self.feature_df['portfolio_performance_risk'] = np.where(
            self.feature_df['total_return_pct'] < -10, 3,
            np.where(self.feature_df['total_return_pct'] < 0, 2, 1)
        )
        
        # Account relationship risk
        self.feature_df['account_relationship_risk'] = np.where(
            self.feature_df['account_age_years'] > 15, 3,  # Counter-intuitive but based on EDA
            np.where(self.feature_df['account_age_years'] > 10, 2, 1)
        )
        
        # Cash flow risk
        self.feature_df['cash_flow_risk'] = np.where(
            self.feature_df['net_cash_flow'] < -50000, 3,
            np.where(self.feature_df['net_cash_flow'] < 0, 2, 1)
        )
        
        # Portfolio concentration risk
        self.feature_df['concentration_risk'] = np.where(
            self.feature_df['portfolio_diversification'] < 3, 3,
            np.where(self.feature_df['portfolio_diversification'] < 5, 2, 1)
        )
        
        # Engagement decline risk
        self.feature_df['engagement_decline_risk'] = np.where(
            self.feature_df['transaction_frequency_30d'] == 0, 3,
            np.where(self.feature_df['transaction_frequency_90d'] < 2, 2, 1)
        )
        
        # Calculate comprehensive risk score
        risk_columns = [
            'transaction_activity_risk', 'portfolio_performance_risk', 
            'account_relationship_risk', 'cash_flow_risk', 
            'concentration_risk', 'engagement_decline_risk'
        ]
        
        self.feature_df['comprehensive_risk_score'] = self.feature_df[risk_columns].sum(axis=1)
        
        # Adjusted risk score (weighted by account value)
        self.feature_df['adjusted_risk_score'] = self.feature_df['comprehensive_risk_score'] * np.log1p(
            self.feature_df['current_portfolio_value'].fillna(0)
        )
        
        logging.info("Risk scoring features completed: 8 features")
    
    def generate_feature_report(self):
        """Generate feature engineering report"""
        logging.info("=== Generating Feature Engineering Report ===")
        
        print("\n" + "="*80)
        print("InvestCloud Tier-1 Feature Engineering Report")
        print("="*80)
        print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Feature summary
        print(f"\n📊 Feature Summary:")
        print(f"  • Total Features: {len(self.feature_df.columns) - 1}")
        print(f"  • Total Accounts: {len(self.feature_df)}")
        print(f"  • Churn Rate: {self.feature_df['CHURN_FLAG'].mean():.1%}")
        
        # Feature categories
        print(f"\n🎯 Feature Categories:")
        print(f"  • Transaction Behavior Features: 13")
        print(f"  • Investment Performance Features: 7") 
        print(f"  • Account Lifecycle Features: 5")
        print(f"  • Risk Scoring Features: 8")
        
        # Data quality check
        print(f"\n🔍 Data Quality Check:")
        missing_data = self.feature_df.isnull().sum()
        problematic_features = missing_data[missing_data > 0]
        
        if len(problematic_features) > 0:
            print(f"  • Features with missing values: {len(problematic_features)}")
            for feature, missing_count in problematic_features.head(5).items():
                missing_pct = missing_count / len(self.feature_df) * 100
                print(f"    - {feature}: {missing_count} ({missing_pct:.1f}%)")
        else:
            print(f"  • No missing values detected ✓")
        
        # Feature correlation with target
        print(f"\n📈 Top 10 Features by Churn Correlation:")
        numeric_features = self.feature_df.select_dtypes(include=[np.number]).columns
        correlations = self.feature_df[numeric_features].corrwith(self.feature_df['CHURN_FLAG'])
        top_correlations = correlations.abs().sort_values(ascending=False).head(10)
        
        for feature, corr in top_correlations.items():
            if feature != 'CHURN_FLAG':
                print(f"  • {feature}: {corr:.3f}")
        
        # Risk distribution
        print(f"\n⚠️ Risk Score Distribution:")
        risk_stats = self.feature_df['comprehensive_risk_score'].describe()
        high_risk_count = len(self.feature_df[self.feature_df['comprehensive_risk_score'] >= 15])
        high_risk_pct = high_risk_count / len(self.feature_df) * 100
        
        print(f"  • Mean Risk Score: {risk_stats['mean']:.1f}")
        print(f"  • High Risk Accounts (≥15): {high_risk_count} ({high_risk_pct:.1f}%)")
        print(f"  • Risk Score Range: {risk_stats['min']:.0f} - {risk_stats['max']:.0f}")
        
        # Business insights
        print(f"\n💡 Key Business Insights:")
        insights = [
            f"📈 Average days since last transaction: {self.feature_df['days_since_last_transaction'].mean():.0f} days",
            f"💰 Average portfolio value: ${self.feature_df['current_portfolio_value'].mean():,.0f}",
            f"📊 Average account age: {self.feature_df['account_age_years'].mean():.1f} years",
            f"🎯 High-risk account identification enables proactive retention strategies"
        ]
        
        for insight in insights:
            print(f"  • {insight}")
        
        print(f"\n✅ Feature engineering completed successfully!")
        print(f"🎯 Ready for model development and validation")
    
    def save_features(self, filename='tier1_features.csv'):
        """Save features to CSV file"""
        self.feature_df.to_csv(filename, index=False)
        logging.info(f"Features saved to {filename}")
        print(f"💾 Features saved to {filename}")

def main():
    """Main function"""
    print("🔧 InvestCloud Customer Churn Prediction - Tier-1 Feature Engineering")
    print("=" * 75)
    
    # Initialize feature engineering
    feature_eng = Tier1FeatureEngineering()
    
    # Load data
    if not feature_eng.load_data():
        print("❌ Data loading failed, program exiting")
        return
    
    # Build features
    features_df = feature_eng.build_tier1_features()
    
    # Generate report
    feature_eng.generate_feature_report()
    
    # Save features
    feature_eng.save_features()
    
    print("\n✅ Tier-1 feature engineering completed!")
    print("🎯 Ready to proceed to baseline model development")

if __name__ == "__main__":
    main() 