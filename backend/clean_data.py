import pandas as pd

# Load the Excel file
file_path = 'CASES BY REGIONAL LEVEL.xlsx'
data = pd.read_excel('CASES BY REGIONAL LEVEL.xlsx')


# Clean the dataset
data.columns = data.iloc[0]  # Set the first row as the header
data = data.drop(0)  # Drop the first row
data = data.reset_index(drop=True)

# Fill missing values with 0
data = data.infer_objects(copy=False)
data = data.fillna(0)


# Convert all relevant columns to numeric
for col in data.columns[2:]:
    data[col] = pd.to_numeric(data[col], errors='coerce')

# Filter for specific diseases
diseases = [
    'Cervical Cancer', 'Diabetes Mellitus', 'HIV/AIDS Related conditions',
    'Hypertension', 'Meningitis', 'Tuberculosis',
    'liver diseases', 'Upper Respiratory Tract Infections',
    'MALARIA TOTAL', 'MATERNAL DEATHS TOTAL'
]
filtered_data = data[['YEAR', 'REGION'] + diseases]

# Save the cleaned dataset
filtered_data.to_excel('cleaned_health_data.xlsx', index=False)

print('Cleaned dataset saved as "cleaned_health_data.xlsx"')

