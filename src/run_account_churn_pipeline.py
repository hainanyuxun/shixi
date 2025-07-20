#!/usr/bin/env python3
"""
InvestCloud Customer Churn Prediction Project - Account-Level Pipeline Runner
Unified pipeline for running the complete account-level churn prediction workflow.
Includes data extraction, EDA, feature engineering, and model development.

Author: InvestCloud Intern
Purpose: Complete account-level churn prediction pipeline
"""

import sys
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def print_banner():
    """Print project banner."""
    print("=" * 90)
    print("InvestCloud Customer Churn Prediction - Account-Level Analysis Pipeline")
    print("=" * 90)
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("British Manager: Focus on account-level churn prediction for business impact")
    print()

def print_menu():
    """Print pipeline menu options."""
    print("📋 Pipeline Options:")
    print("1. Complete Pipeline (EDA → Feature Engineering → Model Development)")
    print("2. Data Extraction Only")
    print("3. Exploratory Data Analysis (EDA) Only")
    print("4. Feature Engineering Only")
    print("5. Model Development Only")
    print("6. Exit")
    print()

def validate_oracle_environment():
    """Validate Oracle environment setup."""
    print("🔍 Validating Oracle environment...")
    
    # Check Oracle Instant Client
    oracle_client_path = r"C:\oracle\instantclient_21_18"
    if not os.path.exists(oracle_client_path):
        print(f"❌ Oracle Instant Client not found at: {oracle_client_path}")
        print("Please install Oracle Instant Client or modify the path in data extractor")
        return False
    
    # Check oracledb package
    try:
        import oracledb
        print("✅ oracledb package available")
    except ImportError:
        print("❌ oracledb package not installed")
        print("Please run: pip install oracledb")
        return False
    
    print("✅ Oracle environment validation passed")
    return True

def get_data_source_choice():
    """Get user choice for data source."""
    print("\n📊 Data Source Selection:")
    print("1. Oracle Database (UAT environment - real data)")
    print("2. Sample Data (for testing and development)")
    
    while True:
        try:
            choice = input("\nSelect data source (1-2): ").strip()
            if choice == '1':
                if validate_oracle_environment():
                    return True
                else:
                    print("\n⚠️ Oracle environment validation failed. Using sample data instead.")
                    return False
            elif choice == '2':
                return False
            else:
                print("❌ Invalid choice. Please enter 1 or 2.")
        except KeyboardInterrupt:
            print("\n\n👋 Operation cancelled by user")
            sys.exit(0)

def run_data_extraction(use_oracle=False):
    """Run data extraction process."""
    print("\n" + "="*60)
    print("🗄️ STEP 1: DATA EXTRACTION")
    print("="*60)
    
    if not use_oracle:
        print("📝 Using sample data - no extraction needed")
        return True
    
    try:
        from account_level_data_extractor import AccountLevelDataExtractor
        
        # Create data extractor
        extractor = AccountLevelDataExtractor()
        
        # Initialize Oracle client
        if not extractor.initialize_oracle_client():
            print("❌ Oracle client initialization failed")
            return False
        
        # Connect to database
        if not extractor.connect_database():
            print("❌ Database connection failed")
            return False
        
        # Extract all data
        results = extractor.extract_all_account_data()
        
        # Close connection
        extractor.disconnect_database()
        
        # Check results
        success_count = sum(1 for df in results.values() if df is not None)
        total_count = len(results)
        
        if success_count == total_count:
            print(f"✅ Data extraction completed successfully ({success_count}/{total_count} tables)")
            return True
        else:
            print(f"⚠️ Partial data extraction ({success_count}/{total_count} tables)")
            return False
        
    except Exception as e:
        print(f"❌ Data extraction failed: {e}")
        return False

def run_exploratory_data_analysis(use_oracle=False):
    """Run exploratory data analysis."""
    print("\n" + "="*60)
    print("📊 STEP 2: EXPLORATORY DATA ANALYSIS")
    print("="*60)
    
    try:
        from account_level_eda import AccountLevelEDA
        
        # Initialize EDA
        eda = AccountLevelEDA()
        
        # Load data
        if not eda.load_data(use_oracle=use_oracle):
            print("❌ EDA data loading failed")
            return False
        
        # Run complete EDA
        eda.run_complete_eda()
        
        print("✅ Exploratory Data Analysis completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ EDA failed: {e}")
        return False

def run_feature_engineering(use_oracle=False):
    """Run feature engineering process."""
    print("\n" + "="*60)
    print("🔧 STEP 3: FEATURE ENGINEERING")
    print("="*60)
    
    try:
        from account_level_feature_engineering import AccountLevelFeatureEngineering
        
        # Initialize feature engineering
        feature_eng = AccountLevelFeatureEngineering()
        
        # Load data
        if not feature_eng.load_data(use_oracle=use_oracle):
            print("❌ Feature engineering data loading failed")
            return False
        
        # Build features
        features_df = feature_eng.build_integrated_features()
        
        if features_df is None or len(features_df) == 0:
            print("❌ Feature engineering failed - no features generated")
            return False
        
        # Generate report
        feature_eng.generate_feature_report()
        
        # Save features
        feature_eng.save_features()
        
        print("✅ Feature Engineering completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Feature engineering failed: {e}")
        return False

def run_model_development():
    """Run model development and training."""
    print("\n" + "="*60)
    print("🤖 STEP 4: MODEL DEVELOPMENT")
    print("="*60)
    
    try:
        from account_churn_model_development import AccountChurnModelDevelopment
        
        # Initialize model development
        model_dev = AccountChurnModelDevelopment()
        
        # Load feature data
        if not model_dev.load_feature_data():
            print("❌ Model development data loading failed")
            return False
        
        # Train all models
        model_dev.train_all_models()
        
        # Create visualizations
        model_dev.create_performance_visualizations()
        
        # Save best model
        model_dev.save_best_model()
        
        print("✅ Model Development completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Model development failed: {e}")
        return False

def run_complete_pipeline(use_oracle=False):
    """Run the complete churn prediction pipeline."""
    print("\n🚀 Starting Complete Account-Level Churn Prediction Pipeline")
    print("=" * 75)
    
    # Track pipeline progress
    steps_completed = 0
    total_steps = 4
    
    # Step 1: Data Extraction
    if run_data_extraction(use_oracle):
        steps_completed += 1
        print(f"📈 Pipeline Progress: {steps_completed}/{total_steps} steps completed")
    else:
        print("❌ Pipeline stopped due to data extraction failure")
        return False
    
    # Step 2: Exploratory Data Analysis
    if run_exploratory_data_analysis(use_oracle):
        steps_completed += 1
        print(f"📈 Pipeline Progress: {steps_completed}/{total_steps} steps completed")
    else:
        print("❌ Pipeline stopped due to EDA failure")
        return False
    
    # Step 3: Feature Engineering
    if run_feature_engineering(use_oracle):
        steps_completed += 1
        print(f"📈 Pipeline Progress: {steps_completed}/{total_steps} steps completed")
    else:
        print("❌ Pipeline stopped due to feature engineering failure")
        return False
    
    # Step 4: Model Development
    if run_model_development():
        steps_completed += 1
        print(f"📈 Pipeline Progress: {steps_completed}/{total_steps} steps completed")
    else:
        print("❌ Pipeline stopped due to model development failure")
        return False
    
    # Pipeline completion summary
    print("\n" + "="*75)
    print("🎉 COMPLETE PIPELINE EXECUTION SUMMARY")
    print("="*75)
    print("✅ All pipeline steps completed successfully!")
    print("\n📋 Deliverables Generated:")
    print("   • Data Quality Reports (../data/reports/)")
    print("   • EDA Analysis Charts (../outputs/)")
    print("   • Feature Engineering Report (../data/reports/)")
    print("   • Model Performance Report (../data/reports/)")
    print("   • Trained Model Files (../models/)")
    print("   • Performance Visualizations (../outputs/)")
    
    print("\n🎯 Business Impact:")
    print("   • Account-level churn prediction model ready for deployment")
    print("   • Comprehensive analysis of customer behavior patterns")
    print("   • Actionable insights for customer retention strategies")
    
    print("\n🚀 Next Steps:")
    print("   • Review model performance metrics and business impact")
    print("   • Deploy model to production environment")
    print("   • Set up monitoring and alerting for high-risk accounts")
    print("   • Develop targeted retention campaigns based on insights")
    
    return True

def main():
    """Main pipeline execution function."""
    print_banner()
    
    use_oracle = None
    
    while True:
        print_menu()
        
        try:
            choice = input("Select pipeline option (1-6): ").strip()
            
            # Get data source for pipeline options that need it
            if choice in ['1', '2', '3', '4'] and use_oracle is None:
                use_oracle = get_data_source_choice()
            
            if choice == '1':
                print("\n🔥 Starting Complete Pipeline...")
                success = run_complete_pipeline(use_oracle)
                if success:
                    print("\n🎊 Complete pipeline executed successfully!")
                    break
                else:
                    print("\n💥 Pipeline execution failed. Please check logs and try again.")
                    
            elif choice == '2':
                print("\n📦 Running Data Extraction Only...")
                success = run_data_extraction(use_oracle)
                if success:
                    print("\n✅ Data extraction completed!")
                else:
                    print("\n❌ Data extraction failed!")
                    
            elif choice == '3':
                print("\n📊 Running EDA Only...")
                success = run_exploratory_data_analysis(use_oracle)
                if success:
                    print("\n✅ EDA completed!")
                else:
                    print("\n❌ EDA failed!")
                    
            elif choice == '4':
                print("\n🔧 Running Feature Engineering Only...")
                success = run_feature_engineering(use_oracle)
                if success:
                    print("\n✅ Feature engineering completed!")
                else:
                    print("\n❌ Feature engineering failed!")
                    
            elif choice == '5':
                print("\n🤖 Running Model Development Only...")
                success = run_model_development()
                if success:
                    print("\n✅ Model development completed!")
                else:
                    print("\n❌ Model development failed!")
                    
            elif choice == '6':
                print("👋 Exiting pipeline...")
                sys.exit(0)
                
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                continue
            
            # Ask if user wants to continue with another option
            if choice != '1':  # Complete pipeline ends automatically
                continue_choice = input("\nWould you like to run another pipeline component? (y/n): ").strip().lower()
                if continue_choice != 'y':
                    break
                    
        except KeyboardInterrupt:
            print("\n\n👋 Pipeline interrupted by user")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            continue
    
    print("\n👋 Thank you for using the InvestCloud Account Churn Prediction Pipeline!")
    print("For questions or support, please contact the development team.")

if __name__ == "__main__":
    main() 