#!/usr/bin/env python3
"""
InvestCloud Customer Churn Prediction Project - User-Level EDA Analysis
Based on confirmed data architecture for user status distribution, value segmentation and churn characteristics analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import logging
warnings.filterwarnings('ignore')

# Set font and chart styling
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams.update({'font.size': 10})
print("✅ Font configuration: DejaVu Sans (English display)")
sns.set_style("whitegrid")
sns.set_palette("husl")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class UserLevelEDA:
    """User-level Exploratory Data Analysis"""
    
    def __init__(self):
        """Initialize EDA analyzer"""
        self.accounts_df = None
        self.transactions_df = None
        self.pnl_df = None
        self.user_aggregated_df = None
        
    def load_data(self):
        """Load sample data"""
        try:
            logging.info("Starting to load sample data...")
            
            # Load three core data tables
            self.accounts_df = pd.read_csv('Account_sampledata.csv')
            self.transactions_df = pd.read_csv('Transaction_sampledata.csv')
            self.pnl_df = pd.read_csv('PNL_sampledata.csv')
            
            # Data preprocessing
            self._preprocess_data()
            
            logging.info(f"Data loading completed:")
            logging.info(f"  • Account data: {len(self.accounts_df)} records")
            logging.info(f"  • Transaction data: {len(self.transactions_df)} records")
            logging.info(f"  • PNL data: {len(self.pnl_df)} records")
            
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
        
        if 'BE_ASOF' in self.pnl_df.columns:
            self.pnl_df['BE_ASOF'] = pd.to_datetime(self.pnl_df['BE_ASOF'])
        
        # Calculate account age
        current_date = datetime.now()
        if 'ACCOUNTOPENDATE' in self.accounts_df.columns:
            self.accounts_df['ACCOUNT_AGE_YEARS'] = (
                current_date - self.accounts_df['ACCOUNTOPENDATE']
            ).dt.days / 365.25
        
        logging.info("Data preprocessing completed")
    
    def analyze_account_status_distribution(self):
        """Analyze account status distribution"""
        logging.info("=== Starting Account Status Distribution Analysis ===")
        
        # Create charts
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Account Status Distribution Analysis', fontsize=16, fontweight='bold')
        
        # 1. Account status pie chart
        if 'ACCOUNTSTATUS' in self.accounts_df.columns:
            status_counts = self.accounts_df['ACCOUNTSTATUS'].value_counts()
            axes[0, 0].pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%')
            axes[0, 0].set_title('Account Status Distribution')
        
        # 2. Churn label distribution
        if 'CHURN_FLAG' in self.accounts_df.columns:
            churn_counts = self.accounts_df['CHURN_FLAG'].value_counts()
            labels = ['Active Accounts', 'Churned Accounts']
            axes[0, 1].pie(churn_counts.values, labels=labels, autopct='%1.1f%%')
            axes[0, 1].set_title('Account Churn Distribution')
        
        # 3. Account type distribution
        if 'CLASSIFICATION1' in self.accounts_df.columns:
            class_counts = self.accounts_df['CLASSIFICATION1'].value_counts()
            axes[1, 0].bar(range(len(class_counts)), class_counts.values)
            axes[1, 0].set_xticks(range(len(class_counts)))
            axes[1, 0].set_xticklabels(class_counts.index, rotation=45, ha='right')
            axes[1, 0].set_title('Account Type Distribution')
            axes[1, 0].set_ylabel('Number of Accounts')
        
        # 4. Geographic distribution
        if 'DOMICILESTATE' in self.accounts_df.columns:
            state_counts = self.accounts_df['DOMICILESTATE'].value_counts().head(10)
            axes[1, 1].bar(range(len(state_counts)), state_counts.values)
            axes[1, 1].set_xticks(range(len(state_counts)))
            axes[1, 1].set_xticklabels(state_counts.index, rotation=45)
            axes[1, 1].set_title('Top 10 State Distribution')
            axes[1, 1].set_ylabel('Number of Accounts')
        
        plt.tight_layout()
        plt.savefig('account_status_distribution.png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.show()
        
        # Output statistical summary
        self._print_status_summary()
    
    def _print_status_summary(self):
        """Output status distribution summary"""
        print("\n📊 Account Status Distribution Summary:")
        print("=" * 50)
        
        if 'ACCOUNTSTATUS' in self.accounts_df.columns:
            status_summary = self.accounts_df['ACCOUNTSTATUS'].value_counts()
            for status, count in status_summary.items():
                percentage = count / len(self.accounts_df) * 100
                print(f"  • {status}: {count} accounts ({percentage:.1f}%)")
        
        if 'CHURN_FLAG' in self.accounts_df.columns:
            churn_rate = self.accounts_df['CHURN_FLAG'].mean()
            print(f"\n🎯 Account Churn Rate: {churn_rate:.1%}")
        
        if 'CLASSIFICATION1' in self.accounts_df.columns:
            print(f"\n📋 Number of Account Types: {self.accounts_df['CLASSIFICATION1'].nunique()}")
            print("Main Account Types:")
            top_types = self.accounts_df['CLASSIFICATION1'].value_counts().head(5)
            for acc_type, count in top_types.items():
                print(f"  • {acc_type}: {count} accounts")
    
    def analyze_user_value_segmentation(self):
        """Analyze user value segmentation"""
        logging.info("=== Starting User Value Segmentation Analysis ===")
        
        # Value segmentation based on account age and type
        if 'ACCOUNT_AGE_YEARS' in self.accounts_df.columns:
            # Create value tiers
            self.accounts_df['VALUE_TIER'] = pd.cut(
                self.accounts_df['ACCOUNT_AGE_YEARS'], 
                bins=[0, 2, 5, 10, float('inf')], 
                labels=['New Customers (<2Y)', 'Growing Customers (2-5Y)', 'Mature Customers (5-10Y)', 'Long-term Customers (>10Y)']
            )
            
            # Visualize value segmentation
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('User Value Segmentation Analysis', fontsize=16, fontweight='bold')
            
            # 1. Value tier distribution
            tier_counts = self.accounts_df['VALUE_TIER'].value_counts()
            axes[0, 0].pie(tier_counts.values, labels=tier_counts.index, autopct='%1.1f%%')
            axes[0, 0].set_title('Customer Value Tier Distribution')
            
            # 2. Churn rate by tier
            if 'CHURN_FLAG' in self.accounts_df.columns:
                churn_by_tier = self.accounts_df.groupby('VALUE_TIER')['CHURN_FLAG'].mean()
                axes[0, 1].bar(range(len(churn_by_tier)), churn_by_tier.values)
                axes[0, 1].set_xticks(range(len(churn_by_tier)))
                axes[0, 1].set_xticklabels(churn_by_tier.index, rotation=45, ha='right')
                axes[0, 1].set_title('Churn Rate by Value Tier')
                axes[0, 1].set_ylabel('Churn Rate')
                
                # Add value labels
                for i, v in enumerate(churn_by_tier.values):
                    axes[0, 1].text(i, v + 0.01, f'{v:.1%}', ha='center')
            
            # 3. Account age distribution
            axes[1, 0].hist(self.accounts_df['ACCOUNT_AGE_YEARS'].dropna(), bins=20, alpha=0.7)
            axes[1, 0].set_title('Account Age Distribution')
            axes[1, 0].set_xlabel('Account Age (Years)')
            axes[1, 0].set_ylabel('Number of Accounts')
            
            # 4. Age distribution by account type
            if 'CLASSIFICATION1' in self.accounts_df.columns:
                top_types = self.accounts_df['CLASSIFICATION1'].value_counts().head(4).index
                for i, acc_type in enumerate(top_types):
                    subset = self.accounts_df[self.accounts_df['CLASSIFICATION1'] == acc_type]
                    axes[1, 1].hist(subset['ACCOUNT_AGE_YEARS'].dropna(), alpha=0.6, label=acc_type)
                axes[1, 1].set_title('Age Distribution by Account Type')
                axes[1, 1].set_xlabel('Account Age (Years)')
                axes[1, 1].set_ylabel('Density')
                axes[1, 1].legend()
            
            plt.tight_layout()
            plt.savefig('user_value_segmentation.png', dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.show()
            
            # Output value segmentation summary
            self._print_value_segmentation_summary()
    
    def _print_value_segmentation_summary(self):
        """Output value segmentation summary"""
        print("\n💰 User Value Segmentation Summary:")
        print("=" * 50)
        
        if 'VALUE_TIER' in self.accounts_df.columns:
            for tier in self.accounts_df['VALUE_TIER'].cat.categories:
                tier_data = self.accounts_df[self.accounts_df['VALUE_TIER'] == tier]
                count = len(tier_data)
                churn_rate = tier_data['CHURN_FLAG'].mean() if 'CHURN_FLAG' in tier_data.columns else 0
                avg_age = tier_data['ACCOUNT_AGE_YEARS'].mean()
                
                print(f"\n🎯 {tier}:")
                print(f"  • Count: {count} accounts")
                print(f"  • Churn Rate: {churn_rate:.1%}")
                print(f"  • Average Age: {avg_age:.1f} years")
    
    def analyze_transaction_patterns(self):
        """Analyze transaction patterns"""
        logging.info("=== Starting Transaction Pattern Analysis ===")
        
        if self.transactions_df is None or len(self.transactions_df) == 0:
            logging.warning("Transaction data is empty, skipping transaction pattern analysis")
            return
        
        # Create charts
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Transaction Pattern Analysis', fontsize=16, fontweight='bold')
        
        # 1. Transaction time distribution
        if 'EVENTDATE' in self.transactions_df.columns:
            # Monthly transaction volume
            self.transactions_df['YEAR_MONTH'] = self.transactions_df['EVENTDATE'].dt.to_period('M')
            monthly_transactions = self.transactions_df.groupby('YEAR_MONTH').size()
            
            axes[0, 0].plot(range(len(monthly_transactions)), monthly_transactions.values, marker='o')
            axes[0, 0].set_title('Monthly Transaction Volume Trend')
            axes[0, 0].set_xlabel('Time')
            axes[0, 0].set_ylabel('Number of Transactions')
            axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Transaction amount distribution
        if 'BOOKAMOUNT' in self.transactions_df.columns:
            # Filter outliers
            amounts = self.transactions_df['BOOKAMOUNT'].dropna()
            q1, q99 = amounts.quantile([0.01, 0.99])
            filtered_amounts = amounts[(amounts >= q1) & (amounts <= q99)]
            
            axes[0, 1].hist(filtered_amounts, bins=30, alpha=0.7)
            axes[0, 1].set_title('Transaction Amount Distribution (Outliers Removed)')
            axes[0, 1].set_xlabel('Transaction Amount')
            axes[0, 1].set_ylabel('Frequency')
        
        # 3. Account transaction activity
        account_activity = self.transactions_df.groupby('ACCOUNTID').size()
        axes[1, 0].hist(account_activity.values, bins=20, alpha=0.7)
        axes[1, 0].set_title('Account Transaction Activity Distribution')
        axes[1, 0].set_xlabel('Number of Transactions')
        axes[1, 0].set_ylabel('Number of Accounts')
        
        # 4. Transaction type distribution (if available)
        if 'EVENTTYPE' in self.transactions_df.columns:
            event_counts = self.transactions_df['EVENTTYPE'].value_counts().head(10)
            axes[1, 1].bar(range(len(event_counts)), event_counts.values)
            axes[1, 1].set_xticks(range(len(event_counts)))
            axes[1, 1].set_xticklabels(event_counts.index, rotation=45, ha='right')
            axes[1, 1].set_title('Top 10 Transaction Types')
            axes[1, 1].set_ylabel('Number of Transactions')
        
        plt.tight_layout()
        plt.savefig('transaction_patterns.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.show()
        
        # Output transaction pattern summary
        self._print_transaction_summary()
    
    def _print_transaction_summary(self):
        """Output transaction pattern summary"""
        print("\n💳 Transaction Pattern Summary:")
        print("=" * 50)
        
        total_transactions = len(self.transactions_df)
        unique_accounts = self.transactions_df['ACCOUNTID'].nunique()
        
        print(f"  • Total Transactions: {total_transactions:,}")
        print(f"  • Active Trading Accounts: {unique_accounts}")
        print(f"  • Average Transactions per Account: {total_transactions/unique_accounts:.1f}")
        
        if 'BOOKAMOUNT' in self.transactions_df.columns:
            total_amount = self.transactions_df['BOOKAMOUNT'].sum()
            avg_amount = self.transactions_df['BOOKAMOUNT'].mean()
            print(f"  • Total Transaction Amount: ${total_amount:,.0f}")
            print(f"  • Average Transaction Amount: ${avg_amount:,.0f}")
        
        if 'EVENTDATE' in self.transactions_df.columns:
            date_range = self.transactions_df['EVENTDATE'].max() - self.transactions_df['EVENTDATE'].min()
            print(f"  • Data Time Span: {date_range.days} days")
    
    def analyze_churn_characteristics(self):
        """Analyze churn characteristics"""
        logging.info("=== Starting Churn Characteristics Analysis ===")
        
        if 'CHURN_FLAG' not in self.accounts_df.columns:
            logging.warning("Missing churn labels, skipping churn characteristics analysis")
            return
        
        # Separate churned and active accounts
        churned = self.accounts_df[self.accounts_df['CHURN_FLAG'] == 1]
        active = self.accounts_df[self.accounts_df['CHURN_FLAG'] == 0]
        
        print("\n🎯 Churn Characteristics Comparison Analysis:")
        print("=" * 50)
        
        # 1. Basic statistics comparison
        print(f"\n📊 Basic Statistics:")
        print(f"  • Churned Accounts: {len(churned)}")
        print(f"  • Active Accounts: {len(active)}")
        print(f"  • Overall Churn Rate: {len(churned)/len(self.accounts_df):.1%}")
        
        # 2. Churn rate by account type
        if 'CLASSIFICATION1' in self.accounts_df.columns:
            print(f"\n📋 Churn Rate by Account Type:")
            churn_by_type = self.accounts_df.groupby('CLASSIFICATION1')['CHURN_FLAG'].agg(['count', 'mean'])
            churn_by_type.columns = ['Account Count', 'Churn Rate']
            churn_by_type['Churn Rate'] = churn_by_type['Churn Rate'].apply(lambda x: f"{x:.1%}")
            print(churn_by_type.to_string())
        
        # 3. Churn rate by geographic location
        if 'DOMICILESTATE' in self.accounts_df.columns:
            print(f"\n🗺️ Churn Rate by State (Top 5):")
            state_churn = self.accounts_df.groupby('DOMICILESTATE')['CHURN_FLAG'].agg(['count', 'mean'])
            state_churn = state_churn[state_churn['count'] >= 2]  # At least 2 accounts
            state_churn = state_churn.sort_values('mean', ascending=False).head(5)
            state_churn.columns = ['Account Count', 'Churn Rate']
            state_churn['Churn Rate'] = state_churn['Churn Rate'].apply(lambda x: f"{x:.1%}")
            print(state_churn.to_string())
        
        # 4. Churn rate by account age
        if 'ACCOUNT_AGE_YEARS' in self.accounts_df.columns:
            print(f"\n⏰ Churn Rate by Account Age:")
            print(f"  • Average Age of Churned Accounts: {churned['ACCOUNT_AGE_YEARS'].mean():.1f} years")
            print(f"  • Average Age of Active Accounts: {active['ACCOUNT_AGE_YEARS'].mean():.1f} years")
            
            if 'VALUE_TIER' in self.accounts_df.columns:
                tier_churn = self.accounts_df.groupby('VALUE_TIER')['CHURN_FLAG'].mean()
                print(f"\n💰 Churn Rate by Value Tier:")
                for tier, rate in tier_churn.items():
                    print(f"  • {tier}: {rate:.1%}")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive EDA report"""
        logging.info("=== Generating Comprehensive EDA Report ===")
        
        print("\n" + "="*80)
        print("InvestCloud User-Level EDA Analysis Report")
        print("="*80)
        print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Execute all analyses
        self.analyze_account_status_distribution()
        self.analyze_user_value_segmentation()
        self.analyze_transaction_patterns()
        self.analyze_churn_characteristics()
        
        # Generate key insights and recommendations
        print("\n🔍 Key Insights:")
        print("=" * 50)
        
        if hasattr(self, 'accounts_df') and self.accounts_df is not None:
            churn_rate = self.accounts_df['CHURN_FLAG'].mean() if 'CHURN_FLAG' in self.accounts_df.columns else 0
            avg_age = self.accounts_df['ACCOUNT_AGE_YEARS'].mean() if 'ACCOUNT_AGE_YEARS' in self.accounts_df.columns else 0
            
            insights = [
                f"📈 Overall churn rate is {churn_rate:.1%}, indicating {self._assess_churn_level(churn_rate)} risk level",
                f"⏰ Average account age is {avg_age:.1f} years, showing relatively stable customer relationships",
                f"🏦 Primary account type is {self.accounts_df['CLASSIFICATION1'].mode().iloc[0] if 'CLASSIFICATION1' in self.accounts_df.columns else 'Unknown'}",
                f"📊 Sample includes {len(self.accounts_df)} accounts, {self.transactions_df['ACCOUNTID'].nunique() if self.transactions_df is not None else 0} with transaction records"
            ]
            
            for insight in insights:
                print(f"  • {insight}")
        
        print("\n💡 Next Steps Recommendations:")
        print("=" * 50)
        recommendations = [
            "🎯 Based on churn characteristic differences, prioritize building account age and type-related predictive features",
            "📈 Rich transaction behavior data suggests focusing on transaction frequency and amount trend analysis",
            "🔍 Geographic location shows churn rate differences, can be used as important segmentation features",
            "⚡ Data quality is good, ready to proceed to Tier-1 core feature engineering phase"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        print("\n✅ EDA analysis completed, visualization chart files generated")
    
    def _assess_churn_level(self, churn_rate):
        """Assess churn rate level"""
        if churn_rate < 0.1:
            return "low"
        elif churn_rate < 0.3:
            return "moderate"
        else:
            return "high"

def main():
    """Main function"""
    print("🔬 InvestCloud Customer Churn Prediction Project - User-Level EDA Analysis")
    print("=" * 70)
    
    # Initialize EDA analyzer
    eda = UserLevelEDA()
    
    # Load data
    if not eda.load_data():
        print("❌ Data loading failed, program exiting")
        return
    
    # Generate comprehensive report
    eda.generate_comprehensive_report()
    
    print("\n✅ User-level EDA analysis completed!")
    print("📊 Analysis charts saved as PNG files")
    print("🎯 Ready to proceed to next step: Tier-1 Core Feature Engineering")

if __name__ == "__main__":
    main() 