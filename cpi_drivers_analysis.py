import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
df = pd.read_csv('data/processed/cpi_wide_format.csv')

# Convert REF_DATE to datetime and set as index
df['REF_DATE'] = pd.to_datetime(df['REF_DATE'])
df.set_index('REF_DATE', inplace=True)

# Drop any columns with all NaN values
df = df.dropna(axis=1, how='all')

# Fill remaining NaN values with forward fill
df = df.ffill()

# List of gas/fuel related components to exclude
gas_components = [
    'Gasoline',
    'Fuel oil and other fuels',
    'Natural gas',
    'Fuel, parts and supplies for recreational vehicles',
    'Fuel, parts and supplies for passenger vehicles'
]

# Remove gas/fuel components
df = df.drop(columns=[col for col in df.columns if any(gas in col for gas in gas_components)])

# Calculate percentage changes for all columns
df_pct_change = df.pct_change()

# Drop the first row which will be NaN after pct_change
df_pct_change = df_pct_change.dropna()

# Separate target and features
X = df_pct_change.drop('All-items', axis=1)
y = df_pct_change['All-items']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Random Forest model
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train_scaled, y_train)

# Make predictions
y_pred = rf.predict(X_test_scaled)

# Calculate error metrics
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

# Print error metrics
print("\nModel Performance Metrics (excluding gas/fuel):")
print(f"Mean Absolute Error (MAE): {mae:.6f}")
print(f"Mean Squared Error (MSE): {mse:.6f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.6f}")
print(f"R-squared Score: {r2:.6f}")

# Get feature importances
feature_importances = pd.DataFrame({
    'feature': X.columns,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

# Plot top 20 features
plt.figure(figsize=(12, 8))
sns.barplot(data=feature_importances.head(20), x='importance', y='feature')
plt.title('Top 20 Drivers of All-items CPI Changes (Excluding Gas/Fuel)')
plt.xlabel('Feature Importance')
plt.ylabel('CPI Component')
plt.tight_layout()
plt.savefig('cpi_drivers_no_gas.png')
plt.close()

# Print top 20 drivers
print("\nTop 20 Drivers of All-items CPI Changes (excluding gas/fuel):")
print(feature_importances.head(20))

# Calculate correlation matrix for top 20 features
top_features = feature_importances.head(20)['feature'].tolist()
correlation_matrix = df_pct_change[['All-items'] + top_features].corr()

# Plot correlation heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f')
plt.title('Correlation Matrix of Top 20 Drivers with All-items CPI Changes (Excluding Gas/Fuel)')
plt.tight_layout()
plt.savefig('cpi_correlation_no_gas.png')
plt.close()

# Plot actual vs predicted values
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title('Actual vs Predicted CPI Changes (Excluding Gas/Fuel)')
plt.tight_layout()
plt.savefig('actual_vs_predicted_no_gas.png')
plt.close()

# Additional analysis: Cumulative importance
feature_importances['cumulative_importance'] = feature_importances['importance'].cumsum()
plt.figure(figsize=(12, 6))
plt.plot(range(1, len(feature_importances) + 1), feature_importances['cumulative_importance'], 'b-')
plt.axhline(y=0.8, color='r', linestyle='--', label='80% of total importance')
plt.xlabel('Number of Features')
plt.ylabel('Cumulative Importance')
plt.title('Cumulative Feature Importance (Excluding Gas/Fuel)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('cumulative_importance_no_gas.png')
plt.close()

# Print how many features explain 80% of the variance
n_features_80 = len(feature_importances[feature_importances['cumulative_importance'] <= 0.8])
print(f"\nNumber of features needed to explain 80% of variance: {n_features_80}")
print("\nThese features are:")
print(feature_importances.head(n_features_80)[['feature', 'importance', 'cumulative_importance']]) 