import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os

class InflationPredictor:
    def __init__(self, data_path):
        """
        Initialize the InflationPredictor with CPI data.
        
        Args:
            data_path (str): Path to the processed CPI data CSV file
        """
        self.data_path = data_path
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.data = None  # Store the raw data
        self.load_and_prepare_data()
        
    def load_and_prepare_data(self):
        """Load and prepare the CPI data for modeling."""
        # Read the data
        self.data = pd.read_csv(self.data_path)  # Store the raw data
        
        # Convert REF_DATE to datetime
        self.data['REF_DATE'] = pd.to_datetime(self.data['REF_DATE'])
        
        # Filter for Canada only to simplify the analysis
        self.data = self.data[self.data['GEO'] == 'Canada']
        
        # Pivot the data to get product groups as columns
        pivot_df = self.data.pivot(
            index='REF_DATE',
            columns='Products and product groups',
            values='VALUE'
        ).reset_index()
        
        # Calculate percentage changes
        numeric_cols = pivot_df.select_dtypes(include=[np.number]).columns
        self.feature_names = [col for col in numeric_cols if col != 'All-items']
        
        # Calculate percentage changes with proper handling of zeros and infinities
        pct_changes = pivot_df[numeric_cols].pct_change(fill_method=None)
        pct_changes = pct_changes.replace([np.inf, -np.inf], np.nan)
        pct_changes = pct_changes.fillna(0)
        # Store the correlation matrix for later use
        self.corr_matrix = pct_changes.corr()
        
        # Drop the first row (NaN due to pct_change)
        pct_changes = pct_changes.iloc[1:]
        pivot_df = pivot_df.iloc[1:]
        
        # Prepare features and target
        X = pct_changes[self.feature_names]
        y = pct_changes['All-items']
        
        # Remove any remaining NaN values
        mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[mask]
        y = y[mask]
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale the features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train the model
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate the model
        y_pred = self.model.predict(X_test_scaled)
        self.metrics = {
            'mae': mean_absolute_error(y_test, y_pred),
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'r2': r2_score(y_test, y_pred)
        }
        
    def predict_inflation_impact(self, changes):
        """
        Predict the overall inflation impact given changes in specific product groups.
        
        Args:
            changes (dict): Dictionary of product group changes (e.g., {'Transportation': 0.05})
            
        Returns:
            float: Predicted overall inflation impact
        """
        # Get the base weights from the data
        weights = self.data[self.data['Products and product groups'] != 'All-items'].groupby('Products and product groups')['VALUE'].mean()
        weights = weights / weights.sum()  # Normalize weights
        
        # Initialize impact calculation
        direct_impact = 0
        indirect_impact = 0
        
        # Calculate direct impact using actual weights
        for group, change in changes.items():
            if group in weights:
                direct_impact += weights[group] * change
        
        # Calculate indirect impact through correlations
        for group, change in changes.items():
            if group in self.corr_matrix.columns:
                # Get correlations with all other groups
                correlations = self.corr_matrix[group]
                
                # For each other product group
                for other_group, corr in correlations.items():
                    if other_group in weights:
                        # Calculate the indirect effect using just the correlation
                        indirect_effect = weights[other_group] * change * corr
                        indirect_impact += indirect_effect
        
        # Combine direct and indirect impacts
        total_impact = direct_impact + indirect_impact
        
        return total_impact
    
    def get_feature_importance(self):
        """
        Get the importance of each feature in the model.
        
        Returns:
            pandas.DataFrame: DataFrame with feature names and their importance scores
        """
        if not self.model:
            raise ValueError("Model not trained. Call load_and_prepare_data first.")
            
        importance_df = pd.DataFrame({
            'Feature': self.feature_names,
            'Importance': self.model.feature_importances_
        })
        return importance_df.sort_values('Importance', ascending=False)
    
    def save_model(self, model_path='models/inflation_predictor.joblib'):
        """Save the trained model and scaler."""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }, model_path)
        
    @classmethod
    def load_model(cls, model_path='models/inflation_predictor.joblib'):
        """Load a saved model."""
        saved_data = joblib.load(model_path)
        predictor = cls.__new__(cls)
        predictor.model = saved_data['model']
        predictor.scaler = saved_data['scaler']
        predictor.feature_names = saved_data['feature_names']
        return predictor 

    def get_correlated_changes(self, product_changes):
        """
        Given a dict of user-specified changes, generate a full vector of changes
        for all product groups using the correlation matrix.
        
        Args:
            product_changes (dict): e.g., {'Housing (1986 definition)': 0.05}
            
        Returns:
            dict: All product groups with correlated changes
        """
        # Start with zeros for all product groups
        correlated = {name: 0.0 for name in self.feature_names}
        
        # For each specified change
        for group, change in product_changes.items():
            if group in self.corr_matrix.columns:
                # Get correlations with all other groups
                correlations = self.corr_matrix[group]
                
                # Apply correlated changes to all other groups
                for other_group in self.feature_names:
                    if other_group != group:  # Skip the original group
                        corr = correlations[other_group]
                        # Calculate the correlated change using just the correlation
                        correlated_change = change * corr
                        
                        # Add to the existing correlated change
                        correlated[other_group] += correlated_change
        
        return correlated 