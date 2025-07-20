#!/usr/bin/env python3
"""
InvestCloud Customer Churn Prediction Project - Account-Level Model Development
Develop and evaluate machine learning models for account-level churn prediction.
Implements multiple algorithms and provides comprehensive evaluation metrics.

Author: InvestCloud Intern
Purpose: Account-level churn prediction model training and evaluation
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, classification_report, confusion_matrix,
    precision_recall_curve, roc_curve
)
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import logging
from datetime import datetime
import joblib
import os

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Set font for plots
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class AccountChurnModelDevelopment:
    """
    Account-level churn prediction model development and evaluation.
    Trains multiple ML models and provides comprehensive performance analysis.
    """
    
    def __init__(self):
        """Initialize model development framework."""
        self.feature_df = None
        self.X = None
        self.y = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.scaler = None
        self.models = {}
        self.model_results = {}
        
        # Model configuration
        self.test_size = 0.2
        self.random_state = 42
        self.cv_folds = 5
        
    def load_feature_data(self, file_path=None):
        """
        Load feature data from CSV file.
        
        Args:
            file_path (str): Path to feature CSV file. If None, looks for latest file.
        """
        try:
            if file_path is None:
                # Look for latest feature file
                data_dir = '../data/processed'
                if os.path.exists(data_dir):
                    feature_files = [f for f in os.listdir(data_dir) if f.startswith('account_churn_features')]
                    if feature_files:
                        feature_files.sort(reverse=True)  # Get latest
                        file_path = os.path.join(data_dir, feature_files[0])
                    else:
                        logging.error("No feature files found. Please run feature engineering first.")
                        return False
                else:
                    logging.error("Data directory not found. Please run feature engineering first.")
                    return False
            
            logging.info(f"Loading feature data from: {file_path}")
            self.feature_df = pd.read_csv(file_path)
            
            # Basic data validation
            if 'CHURN_FLAG' not in self.feature_df.columns:
                raise ValueError("CHURN_FLAG column not found in feature data")
            
            logging.info(f"Feature data loaded successfully: {self.feature_df.shape}")
            logging.info(f"Churn rate: {self.feature_df['CHURN_FLAG'].mean():.3f}")
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to load feature data: {e}")
            return False
    
    def prepare_model_data(self):
        """
        Prepare data for model training.
        Split into features and target, train/test sets.
        """
        logging.info("Preparing model data...")
        
        # Exclude non-feature columns
        exclude_cols = ['ACCOUNTID', 'ACCOUNTSHORTNAME', 'CHURN_FLAG']
        feature_cols = [col for col in self.feature_df.columns if col not in exclude_cols]
        
        # Features and target
        self.X = self.feature_df[feature_cols].copy()
        self.y = self.feature_df['CHURN_FLAG'].copy()
        
        # Handle missing values
        self.X = self.X.fillna(0)
        
        # Train/test split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, 
            test_size=self.test_size, 
            random_state=self.random_state, 
            stratify=self.y
        )
        
        # Scale features
        self.scaler = StandardScaler()
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)
        
        logging.info(f"Model data prepared:")
        logging.info(f"  • Training set: {self.X_train.shape[0]} samples")
        logging.info(f"  • Test set: {self.X_test.shape[0]} samples")
        logging.info(f"  • Features: {self.X_train.shape[1]}")
        logging.info(f"  • Train churn rate: {self.y_train.mean():.3f}")
        logging.info(f"  • Test churn rate: {self.y_test.mean():.3f}")
    
    def train_logistic_regression(self):
        """Train and evaluate Logistic Regression model."""
        logging.info("Training Logistic Regression model...")
        
        # Train model
        lr_model = LogisticRegression(
            random_state=self.random_state,
            class_weight='balanced',
            max_iter=1000
        )
        lr_model.fit(self.X_train_scaled, self.y_train)
        
        # Store model
        self.models['Logistic Regression'] = lr_model
        
        # Evaluate model
        results = self._evaluate_model(lr_model, self.X_test_scaled, self.y_test, 'Logistic Regression')
        self.model_results['Logistic Regression'] = results
        
        # Feature importance (coefficients)
        feature_importance = pd.DataFrame({
            'feature': self.X.columns,
            'importance': abs(lr_model.coef_[0])
        }).sort_values('importance', ascending=False)
        
        results['feature_importance'] = feature_importance
        
        logging.info("Logistic Regression training completed")
        return lr_model, results
    
    def train_random_forest(self):
        """Train and evaluate Random Forest model."""
        logging.info("Training Random Forest model...")
        
        # Train model
        rf_model = RandomForestClassifier(
            n_estimators=100,
            random_state=self.random_state,
            class_weight='balanced',
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5
        )
        rf_model.fit(self.X_train, self.y_train)
        
        # Store model
        self.models['Random Forest'] = rf_model
        
        # Evaluate model
        results = self._evaluate_model(rf_model, self.X_test, self.y_test, 'Random Forest')
        self.model_results['Random Forest'] = results
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.X.columns,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        results['feature_importance'] = feature_importance
        
        logging.info("Random Forest training completed")
        return rf_model, results
    
    def _evaluate_model(self, model, X_test, y_test, model_name):
        """
        Comprehensive model evaluation.
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test target
            model_name (str): Name of the model
        
        Returns:
            dict: Evaluation results
        """
        # Predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        results = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'confusion_matrix': confusion_matrix(y_test, y_pred),
            'classification_report': classification_report(y_test, y_pred),
            'y_test': y_test,
            'y_pred': y_pred,
            'y_pred_proba': y_pred_proba
        }
        
        # Cross-validation scores
        if hasattr(model, 'predict_proba'):
            cv_scores = cross_val_score(
                model, self.X_train_scaled if model_name == 'Logistic Regression' else self.X_train, 
                self.y_train, cv=self.cv_folds, scoring='roc_auc'
            )
        else:
            cv_scores = cross_val_score(
                model, self.X_train_scaled if model_name == 'Logistic Regression' else self.X_train, 
                self.y_train, cv=self.cv_folds, scoring='accuracy'
            )
        
        results['cv_mean'] = cv_scores.mean()
        results['cv_std'] = cv_scores.std()
        
        return results
    
    def train_all_models(self):
        """Train all models and compare performance."""
        logging.info("Training all models...")
        
        # Prepare data
        self.prepare_model_data()
        
        # Train models
        self.train_logistic_regression()
        self.train_random_forest()
        
        # Generate comparison report
        self.generate_model_comparison_report()
        
        logging.info("All models trained successfully")
    
    def generate_model_comparison_report(self):
        """Generate comprehensive model comparison report."""
        logging.info("Generating model comparison report...")
        
        report = []
        report.append("=" * 80)
        report.append("ACCOUNT-LEVEL CHURN PREDICTION - MODEL PERFORMANCE REPORT")
        report.append("=" * 80)
        report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Test Set Size: {len(self.y_test)} accounts")
        report.append(f"Test Set Churn Rate: {self.y_test.mean():.3f}")
        report.append("")
        
        # Model performance comparison
        report.append("MODEL PERFORMANCE COMPARISON:")
        report.append("-" * 50)
        
        for model_name, results in self.model_results.items():
            report.append(f"\n{model_name.upper()}:")
            report.append(f"  • Accuracy: {results['accuracy']:.3f}")
            report.append(f"  • Precision: {results['precision']:.3f}")
            report.append(f"  • Recall: {results['recall']:.3f}")
            report.append(f"  • F1 Score: {results['f1_score']:.3f}")
            report.append(f"  • ROC AUC: {results['roc_auc']:.3f}")
            report.append(f"  • CV Score: {results['cv_mean']:.3f} ± {results['cv_std']:.3f}")
        
        # Best model selection
        best_model_name = max(self.model_results.keys(), 
                            key=lambda x: self.model_results[x]['roc_auc'])
        
        report.append(f"\nBEST MODEL: {best_model_name}")
        report.append(f"Best ROC AUC: {self.model_results[best_model_name]['roc_auc']:.3f}")
        
        # Feature importance for best model
        if 'feature_importance' in self.model_results[best_model_name]:
            feature_imp = self.model_results[best_model_name]['feature_importance']
            report.append(f"\nTOP 15 MOST IMPORTANT FEATURES ({best_model_name}):")
            for i, (_, row) in enumerate(feature_imp.head(15).iterrows()):
                report.append(f"  {i+1:2d}. {row['feature']}: {row['importance']:.4f}")
        
        # Business insights
        report.append("\nBUSINESS INSIGHTS:")
        churn_precision = self.model_results[best_model_name]['precision']
        churn_recall = self.model_results[best_model_name]['recall']
        
        report.append(f"  • Model can identify {churn_recall:.1%} of churning accounts")
        report.append(f"  • {churn_precision:.1%} of accounts flagged as high-risk will actually churn")
        report.append(f"  • Recommended for deployment: {'Yes' if churn_precision > 0.3 and churn_recall > 0.5 else 'Needs improvement'}")
        
        report_text = "\n".join(report)
        
        # Save report
        report_filename = f'../data/reports/account_model_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        os.makedirs(os.path.dirname(report_filename), exist_ok=True)
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        logging.info(f"Model comparison report saved to: {report_filename}")
        print(report_text)
    
    def create_performance_visualizations(self):
        """Create model performance visualizations."""
        logging.info("Creating performance visualizations...")
        
        # Set up figure
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Account Churn Prediction - Model Performance Analysis', fontsize=16)
        
        # 1. ROC Curves
        ax1 = axes[0, 0]
        for model_name, results in self.model_results.items():
            fpr, tpr, _ = roc_curve(results['y_test'], results['y_pred_proba'])
            ax1.plot(fpr, tpr, label=f"{model_name} (AUC = {results['roc_auc']:.3f})")
        
        ax1.plot([0, 1], [0, 1], 'k--', label='Random')
        ax1.set_xlabel('False Positive Rate')
        ax1.set_ylabel('True Positive Rate')
        ax1.set_title('ROC Curves')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Precision-Recall Curves
        ax2 = axes[0, 1]
        for model_name, results in self.model_results.items():
            precision, recall, _ = precision_recall_curve(results['y_test'], results['y_pred_proba'])
            ax2.plot(recall, precision, label=f"{model_name}")
        
        ax2.set_xlabel('Recall')
        ax2.set_ylabel('Precision')
        ax2.set_title('Precision-Recall Curves')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Model Comparison Bar Chart
        ax3 = axes[1, 0]
        metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']
        x = np.arange(len(metrics))
        width = 0.35
        
        for i, (model_name, results) in enumerate(self.model_results.items()):
            values = [results[metric] for metric in metrics]
            ax3.bar(x + i*width, values, width, label=model_name)
        
        ax3.set_xlabel('Metrics')
        ax3.set_ylabel('Score')
        ax3.set_title('Model Performance Comparison')
        ax3.set_xticks(x + width/2)
        ax3.set_xticklabels(metrics, rotation=45)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Confusion Matrix for Best Model
        best_model_name = max(self.model_results.keys(), 
                            key=lambda x: self.model_results[x]['roc_auc'])
        cm = self.model_results[best_model_name]['confusion_matrix']
        
        ax4 = axes[1, 1]
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax4)
        ax4.set_xlabel('Predicted')
        ax4.set_ylabel('Actual')
        ax4.set_title(f'Confusion Matrix - {best_model_name}')
        
        plt.tight_layout()
        
        # Save plot
        plot_filename = f'../outputs/account_model_performance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        os.makedirs(os.path.dirname(plot_filename), exist_ok=True)
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        
        logging.info(f"Performance visualizations saved to: {plot_filename}")
        plt.show()
    
    def save_best_model(self):
        """Save the best performing model."""
        if not self.model_results:
            logging.warning("No models trained yet")
            return
        
        # Find best model
        best_model_name = max(self.model_results.keys(), 
                            key=lambda x: self.model_results[x]['roc_auc'])
        best_model = self.models[best_model_name]
        
        # Save model and scaler
        model_filename = f'../models/best_account_churn_model_{datetime.now().strftime("%Y%m%d_%H%M%S")}.joblib'
        scaler_filename = f'../models/account_feature_scaler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.joblib'
        
        os.makedirs(os.path.dirname(model_filename), exist_ok=True)
        
        joblib.dump(best_model, model_filename)
        joblib.dump(self.scaler, scaler_filename)
        
        # Save model metadata
        metadata = {
            'model_name': best_model_name,
            'model_type': type(best_model).__name__,
            'performance_metrics': self.model_results[best_model_name],
            'feature_names': list(self.X.columns),
            'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'n_features': len(self.X.columns),
            'n_training_samples': len(self.y_train)
        }
        
        metadata_filename = f'../models/account_model_metadata_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(metadata_filename, 'w') as f:
            for key, value in metadata.items():
                f.write(f"{key}: {value}\n")
        
        logging.info(f"Best model ({best_model_name}) saved to: {model_filename}")
        print(f"💾 Best model ({best_model_name}) saved!")
        print(f"   Model: {model_filename}")
        print(f"   Scaler: {scaler_filename}")
        print(f"   Metadata: {metadata_filename}")

def main():
    """
    Main function for account-level churn model development.
    """
    print("🤖 InvestCloud Customer Churn Prediction - Account-Level Model Development")
    print("=" * 85)
    
    # Initialize model development
    model_dev = AccountChurnModelDevelopment()
    
    # Load feature data
    if not model_dev.load_feature_data():
        print("❌ Feature data loading failed, program exiting")
        return
    
    # Train all models
    model_dev.train_all_models()
    
    # Create visualizations
    model_dev.create_performance_visualizations()
    
    # Save best model
    model_dev.save_best_model()
    
    print("\n✅ Account-level model development completed!")
    print("🎯 Models are ready for deployment and testing")

if __name__ == "__main__":
    main() 