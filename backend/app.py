from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import plotly.express as px
import plotly  # Import plotly to use plotly.utils
import json

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# 📄 Load the Excel dataset
df = pd.read_excel('cleaned_health_data.xlsx')

# 🧹 Data cleaning
df.dropna(inplace=True)

# 📊 Endpoint 1: Disease Trends (Line Chart)
@app.route('/api/disease-trend', methods=['GET'])
def disease_trend():
    # Filter all diseases
    diseases = df.columns[2:]  # Exclude 'YEAR' and 'REGION' columns
    df_filtered = df[['YEAR', 'REGION'] + list(diseases)].melt(id_vars=['YEAR', 'REGION'], var_name='Disease', value_name='Cases')

    # Create a Plotly line chart
    fig = px.line(
        df_filtered,
        x="YEAR",
        y="Cases",
        color="Disease",
        title="Disease Trends Over Time",
        labels={"YEAR": "Year", "Cases": "Number of Cases"},
        template="plotly_dark"
    )

    # Convert the figure to JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify(graphJSON)

# 📊 Endpoint 2: Disease Comparison by Region (Bar Chart)
@app.route('/api/disease-comparison', methods=['GET'])
def disease_comparison():
    # Sum cases by region
    df_region_sum = df.groupby('REGION').sum().reset_index()
    df_melted = df_region_sum.melt(id_vars=['REGION'], var_name='Disease', value_name='Cases')

    # Create a Plotly bar chart
    fig = px.bar(
        df_melted,
        x="REGION",
        y="Cases",
        color="Disease",
        title="Regional Disease Cases",
        labels={"REGION": "Region", "Cases": "Number of Cases"},
        template="plotly_dark"
    )

    # Convert the figure to JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify(graphJSON)

# 📊 Endpoint 3: Disease Distribution (Pie Chart)
@app.route('/api/disease-distribution', methods=['GET'])
def disease_distribution():
    # Total cases for each disease
    disease_totals = df.drop(columns=['YEAR', 'REGION']).sum().reset_index()
    disease_totals.columns = ['Disease', 'Cases']

    # Create a Plotly pie chart
    fig = px.pie(
        disease_totals,
        names='Disease',
        values='Cases',
        title="Disease Distribution in Ghana",
        template="plotly_dark"
    )

    # Convert the figure to JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify(graphJSON)

# 📊 Endpoint 4: Disease Heatmap
@app.route('/api/disease-heatmap', methods=['GET'])
def disease_heatmap():
    # Group by year and disease
    df_grouped = df.groupby(['YEAR']).sum().reset_index()

    # Create a heatmap
    fig = px.imshow(
        df_grouped.set_index('YEAR').transpose(),
        title="Heatmap of Disease Cases Over Time",
        labels={'x': 'Year', 'y': 'Disease', 'color': 'Cases'},
        template="plotly_dark"
    )

    # Convert the figure to JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify(graphJSON)

# 📊 Endpoint 5: Predicted Disease Cases (Line Chart with Future Predictions)
@app.route('/api/disease-prediction', methods=['GET'])
def disease_prediction():
    try:
        # Calculate the yearly difference for each disease to estimate the trend
        diseases = df.columns[2:]  # Assuming the disease data starts from the 3rd column
        avg_increase = {}

        # Calculate average yearly increase for each disease
        for disease in diseases:
            yearly_diff = df.groupby('YEAR')[disease].sum().diff().dropna()
            avg_increase[disease] = yearly_diff.mean()

        # Project future cases for the next 30 years based on the average increase
        last_year = df['YEAR'].max()
        future_years = pd.DataFrame({'YEAR': range(last_year + 1, last_year + 31)})  # Next 30 years
        future_cases = future_years.copy()

        for disease, avg_inc in avg_increase.items():
            last_value = df[df['YEAR'] == last_year][disease].values[0]
            future_cases[disease] = last_value + (avg_inc * range(1, 31))  # Predict for 30 years

        # Melt the future cases DataFrame to long format for Plotly visualization
        future_cases_melted = future_cases.melt(id_vars=['YEAR'], var_name='Disease', value_name='Predicted Cases')

        # Create a Plotly line chart for future predictions
        fig = px.line(
            future_cases_melted,
            x="YEAR",
            y="Predicted Cases",
            color="Disease",
            title="Predicted Disease Cases for the Next 30 Years",
            labels={"YEAR": "Year", "Predicted Cases": "Number of Cases"},
            template="plotly_dark"
        )

        # Convert the figure to JSON for rendering on the frontend
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return jsonify(graphJSON)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 🚀 Run the app
if __name__ == '__main__':
    app.run(debug=True)
