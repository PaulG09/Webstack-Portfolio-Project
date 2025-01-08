from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# Initialize the Flask application
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

# Database configuration
db_user = 'root'
db_password = '%40Santaclausian07'
db_host = 'localhost'
db_name = 'healthscope_ghana'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

# Data Model for Health Data
class HealthData(db.Model):
    __tablename__ = 'health_data'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    region = db.Column(db.String(50))
    cervical_cancer = db.Column(db.Float)
    diabetes_mellitus = db.Column(db.Float)
    hiv_aids_related_conditions = db.Column(db.Float)
    hypertension = db.Column(db.Float)
    meningitis = db.Column(db.Float)
    tuberculosis = db.Column(db.Float)
    liver_diseases = db.Column(db.Float)
    upper_respiratory_tract_infections = db.Column(db.Float)
    malaria_total = db.Column(db.Float)
    maternal_deaths_total = db.Column(db.Float)

# Load and insert data from Excel
def load_and_insert_data():
    excel_file = 'cleaned_health_data.xlsx'
    df = pd.read_excel(excel_file)
    try:
        for _, row in df.iterrows():
            health_data = HealthData(
                year=row['YEAR'],
                region=row['REGION'],
                cervical_cancer=row['Cervical Cancer'],
                diabetes_mellitus=row['Diabetes Mellitus'],
                hiv_aids_related_conditions=row['HIV/AIDS Related conditions'],
                hypertension=row['Hypertension'],
                meningitis=row['Meningitis'],
                tuberculosis=row['Tuberculosis'],
                liver_diseases=row['liver diseases'],
                upper_respiratory_tract_infections=row['Upper Respiratory Tract Infections'],
                malaria_total=row['MALARIA TOTAL'],
                maternal_deaths_total=row['MATERNAL DEATHS TOTAL']
            )
            db.session.add(health_data)
        db.session.commit()
        print("Data inserted successfully!")
    except IntegrityError as e:
        db.session.rollback()
        print(f"Error inserting data: {e}")

# Endpoint: Disease Trend (Interactive Line Chart)
@app.route('/api/disease-trend', methods=['GET'])
def disease_trend():
    data = HealthData.query.all()
    df = pd.DataFrame([(d.year, d.cervical_cancer, d.diabetes_mellitus, d.hiv_aids_related_conditions, d.hypertension, d.meningitis,
                        d.tuberculosis, d.liver_diseases, d.upper_respiratory_tract_infections, d.malaria_total, d.maternal_deaths_total)
                       for d in data],
                      columns=['Year', 'Cervical Cancer', 'Diabetes Mellitus', 'HIV/AIDS Related conditions', 'Hypertension',
                               'Meningitis', 'Tuberculosis', 'Liver diseases', 'Upper Respiratory Tract Infections',
                               'Malaria', 'Maternal Deaths'])

    fig = go.Figure()
    for disease in df.columns[1:]:
        fig.add_trace(go.Scatter(x=df['Year'], y=df[disease], mode='lines', name=disease))

    fig.update_layout(
        title='Disease Trends Over Time',
        xaxis_title='Year',
        yaxis_title='Cases',
        hovermode='closest',
        template='plotly_dark'
    )

    return jsonify(fig.to_json())

# Endpoint: Disease Comparison (Interactive Bar Chart)
@app.route('/api/disease-comparison', methods=['GET'])
def disease_comparison():
    data = HealthData.query.all()
    df = pd.DataFrame([(d.region, d.cervical_cancer, d.diabetes_mellitus, d.hiv_aids_related_conditions, d.hypertension, d.meningitis,
                        d.tuberculosis, d.liver_diseases, d.upper_respiratory_tract_infections, d.malaria_total, d.maternal_deaths_total)
                       for d in data],
                      columns=['Region', 'Cervical Cancer', 'Diabetes Mellitus', 'HIV/AIDS Related conditions', 'Hypertension',
                               'Meningitis', 'Tuberculosis', 'Liver diseases', 'Upper Respiratory Tract Infections',
                               'Malaria', 'Maternal Deaths'])

    fig = go.Figure()
    for disease in df.columns[1:]:
        fig.add_trace(go.Bar(x=df['Region'], y=df[disease], name=disease))

    fig.update_layout(
        title='Disease Comparison by Region',
        xaxis_title='Region',
        yaxis_title='Cases',
        barmode='group',
        template='plotly_dark'
    )

    return jsonify(fig.to_json())

# Endpoint: Disease Distribution (Interactive Pie Chart)
@app.route('/api/disease-distribution', methods=['GET'])
def disease_distribution():
    data = HealthData.query.all()
    df = pd.DataFrame([(d.cervical_cancer, d.diabetes_mellitus, d.hiv_aids_related_conditions, d.hypertension, d.meningitis,
                        d.tuberculosis, d.liver_diseases, d.upper_respiratory_tract_infections, d.malaria_total, d.maternal_deaths_total)
                       for d in data],
                      columns=['Cervical Cancer', 'Diabetes Mellitus', 'HIV/AIDS Related conditions', 'Hypertension',
                               'Meningitis', 'Tuberculosis', 'Liver diseases', 'Upper Respiratory Tract Infections',
                               'Malaria', 'Maternal Deaths'])

    disease_totals = df.sum()
    fig = go.Figure(data=[go.Pie(labels=disease_totals.index, values=disease_totals, hole=0.3)])

    fig.update_layout(
        title='Disease Distribution Across Categories',
        template='plotly_dark'
    )

    return jsonify(fig.to_json())

# Endpoint: Disease Prediction (Forecasting)
@app.route('/api/disease-prediction', methods=['GET'])
def disease_prediction():
    # Query data from the database
    data = HealthData.query.all()
    df = pd.DataFrame([(d.year, d.cervical_cancer, d.diabetes_mellitus, d.hiv_aids_related_conditions, d.hypertension, d.meningitis,
        d.tuberculosis, d.liver_diseases, d.upper_respiratory_tract_infections, d.malaria_total, d.maternal_deaths_total)
        for d in data],
        columns=['Year', 'Cervical Cancer', 'Diabetes Mellitus', 'HIV/AIDS Related conditions', 'Hypertension',
            'Meningitis', 'Tuberculosis', 'Liver diseases', 'Upper Respiratory Tract Infections',
            'Malaria', 'Maternal Deaths'])
    forecasted_data = {}
    model = LinearRegression()
    
        # Future years to predict for (2025-2030)
        # future_years = np.array(range(2025, 2031)).reshape(-1, 1)
    for disease in df.columns[1:]:  # Loop through each disease column
            # Use the 'Year' column as the feature (X) and the disease column as the target (y)
            X = df[['Year']]  # Independent variable: Year
            y = df[disease]   # Dependent variable: Disease data
    
            # Fit the model
            model.fit(X, y)
    
            # Forecast future years
            forecasted_values = model.predict(future_years)
    
            # Store the forecasted data (historical + forecasted)
            forecasted_data[disease] = list(df[disease]) + list(forecasted_values)
    
        # Create Plotly figure for predictions
    fig = go.Figure()
    for disease in df.columns[1:]:
            fig.add_trace(go.Scatter(x=list(df['Year']) + list(future_years.flatten()),
                y=forecasted_data[disease], mode='lines', name=disease))
    fig.update_layout(
                title='Disease Predictions (Forecasted Cases)',
                xaxis_title='Year',
                yaxis_title='Cases',
                hovermode='closest',
                template='plotly_dark'
                )
    
        # Return the figure in JSON format
    return jsonify(fig.to_json())


# Endpoint: Disease Heatmap
@app.route('/api/disease-heatmap', methods=['GET'])
def disease_heatmap():
    data = HealthData.query.all()
    df = pd.DataFrame([(d.year, d.cervical_cancer, d.diabetes_mellitus, d.hiv_aids_related_conditions, d.hypertension, d.meningitis,
                        d.tuberculosis, d.liver_diseases, d.upper_respiratory_tract_infections, d.malaria_total, d.maternal_deaths_total)
                       for d in data],
                      columns=['Year', 'Cervical Cancer', 'Diabetes Mellitus', 'HIV/AIDS Related conditions', 'Hypertension',
                               'Meningitis', 'Tuberculosis', 'Liver diseases', 'Upper Respiratory Tract Infections',
                               'Malaria', 'Maternal Deaths'])

    correlation_matrix = df.corr()
    fig = go.Figure(data=go.Heatmap(z=correlation_matrix.values, x=correlation_matrix.columns, y=correlation_matrix.columns, colorscale='Viridis'))

    fig.update_layout(
        title='Disease Heatmap (Correlation Matrix)',
        template='plotly_dark'
    )

    return jsonify(fig.to_json())

# Main entry point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        load_and_insert_data()
    app.run(debug=True)