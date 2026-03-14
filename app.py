from flask import Flask, render_template, request, jsonify
import numpy as np
import random
import pandas as pd
import os
import scipy.optimize as spo
import optimization as op
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')## generates 5 random stock names

## optimization project routes
@app.route('/optimization')
def optimization():
    return render_template('optimization/index.html')

@app.route('/get_random_portfolio')
def get_random_portfolio():
    try:
        op_object = op.Optimize()
        
        results_as_object = op_object.optimize_portfolio()
        image = results_as_object.get('encoded_image') #encoded image
        allocs = results_as_object.get('allocs') #list
        computations = results_as_object.get('computations') #list
        symbols = results_as_object.get('symbols') #list

        #print(f'Allocs: {type(allocs)} \nComputation: {type(computations)} \nSymbols: {type(symbols)}')
        return jsonify({'image' : image, 'allocs': allocs, 'computations': computations, 'symbols': symbols})
    
    except Exception as e:
        return jsonify({'error' : str(e)})
    
## eda project routes
## optimization project routes
@app.route('/analysis-productivity')
def analysis_productivity():
    return render_template('analysis-productivity/index.html')

#Saves uploaded file into directory and return list of column names ## this function is for bet stats ..
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No Files Uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected File'})
    
    file_path = os.path.join('static', file.filename)
    file.save(file_path)
    #session['file_path'] = file_path # saves file_path in session to use among other functions
    #Use session.get('file_path'), where the string passed between [] above is passed into the session.get function, to get the file_path string set

    try:
        df  = pd.read_csv(file_path, sep=",", quotechar='"')
        info = df.columns.tolist()
        return jsonify({'info': info})
    except Exception as e:
        return jsonify({'error': str(e)})
    
#Send CSV contents over to front end
@app.route('/print_csv_headers')
def print_csv_headers():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'static', 'analysis-productivity', 'social_media_vs_productivity.csv')
        df = pd.read_csv(file_path, sep=',', quotechar='"') 
        columns = df.columns.tolist()
        dtypes = df.dtypes.apply(lambda x: x.name).to_dict()
        return jsonify({'columns':columns, 'dtypes':dtypes})
    except Exception as e:
        return jsonify({'error' : str(e)})

#Filter CSV contents over to front end
@app.route('/print_filtered_csv')
def print_filtered_csv():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'static', 'analysis-productivity', 'social_media_vs_productivity.csv')
        df = pd.read_csv(file_path, sep=',', quotechar='"')
        # Replace NaN or Infinite with None
        df = df.replace([np.nan, np.inf, -np.inf], None)
        # Filter data frame and make new data frame
        new_df = df.loc[df['age'] > 30, ['job_satisfaction_score', 'screen_time_before_sleep']].head(100)
        # Make data frame JSON transferrable
        new_df = new_df.to_dict(orient = 'records')
        return jsonify({'df':new_df})
    except Exception as e:
        return jsonify({'error' : str(e)})
    
#Fetch different sections
@app.route('/section_0')
def section_0():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'static', 'analysis-productivity', 'social_media_vs_productivity.csv')
        df = pd.read_csv(file_path, sep=',', quotechar='"') 
        buffer = io.StringIO()
        df.info(buf=buffer)
        output = buffer.getvalue()
        return jsonify(output=output)

    except Exception as e:
        return jsonify({'error' : str(e)})
    
@app.route('/section_1')
def section_1():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'static', 'analysis-productivity', 'social_media_vs_productivity.csv')
        df = pd.read_csv(file_path, sep=',', quotechar='"') 
        #Check correlations between attributes
        df_corr = df.corr(numeric_only=True)
        #Unstack to see pairs next to each other; easy access
        df_corr = df_corr.unstack()
        #Filter and sort highest correlations
        high_corr = df_corr[(df_corr > 0.5) & (df_corr < 1)]  # exclude 1 (self-correlation)
        high_corr = high_corr.sort_values(ascending=False)
        #Drop duplicates
        high_corr.drop_duplicates(inplace=True)
        high_corr = high_corr.rename('top_correlations')
        buffer = io.StringIO() 
        print(high_corr, file=buffer) #Send file to buffer from StringIO instead of python console
        output = buffer.getvalue()

        return jsonify(output=output)
    except Exception as e:
        return jsonify({'error' : str(e)})
    
@app.route('/section_2')
def section_2():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'static', 'analysis-productivity', 'social_media_vs_productivity.csv')
        df = pd.read_csv(file_path, sep=',', quotechar='"') 
        result = df.dtypes #Returns new DF, but does not print to console (for .describe())
        output = df.dtypes.apply(lambda x: x.name).to_dict()
        return jsonify(output=output)
    except Exception as e:
        return jsonify({'error' : str(e)})
    
@app.route('/section_3')
def section_3():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'static', 'analysis-productivity', 'social_media_vs_productivity.csv')
        df = pd.read_csv(file_path, sep=',', quotechar='"') 
        #dfjs = df_job_satifaction_social_media, check correlations between social media and job satisfaction
        dfjs = df.iloc[:, [3, 8, 10, 11, 14, 17, 18]]
        dfjs_corr = dfjs.corr()
        dfjs_corr_unstacked = dfjs_corr.unstack()
        dfjs_corr_unstacked = dfjs_corr_unstacked[(dfjs_corr_unstacked < 1)].sort_values(ascending=False)
        dfjs_corr_unstacked.drop_duplicates(inplace=True)
        dfjs_corr_unstacked = dfjs_corr_unstacked.rename('more_correlations')
        buffer = io.StringIO() 
        print(dfjs_corr_unstacked, file=buffer) #Send file to buffer from StringIO instead of python console - note that need to print the series bc does not print itself to console
        output = buffer.getvalue()
        return jsonify(output=output)
    except Exception as e:
        return jsonify({'error' : str(e)})
    
@app.route('/section_4')
def section_4():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'static', 'analysis-productivity', 'social_media_vs_productivity.csv')
        df = pd.read_csv(file_path, sep=',', quotechar='"') 

        dfjs = df.iloc[:, [3, 8, 10, 11, 14, 17, 18]]
        corr_matrix = dfjs.corr()

        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', linewidths=0.5)
        plt.title('Correlation Heatmap')
        plt.tight_layout()

        # Save plot to a buffer
        buf = io.BytesIO() 
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)

        #Encode as base64
        encoded = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        return jsonify({'image' : f'data:image/png;base64,{encoded}'})
    
    except Exception as e:
        return jsonify({'error' : str(e)})
    
@app.route('/section_5')
def section_5():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'static', 'analysis-productivity', 'social_media_vs_productivity.csv')
        df = pd.read_csv(file_path, sep=',', quotechar='"') 
        result = df.groupby('age')[['daily_social_media_time', 'actual_productivity_score', 'screen_time_before_sleep']].agg('mean')
        result = result.reset_index()
        output = result.to_dict(orient = 'records')
        return jsonify(output=output)
    except Exception as e:
        return jsonify({'error' : str(e)})

@app.route('/section_6')
def section_6():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'static', 'analysis-productivity', 'social_media_vs_productivity.csv')
        df = pd.read_csv(file_path, sep=',', quotechar='"') 
        # Try grouping with age bins to point differences
        bins = [0, 30, 40, 50, 60, 100]
        labels = ['<30', '31-40', '41-50', '51-60', '60+']
        df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels, right=True)

        # Group by age group and take mean of selected columns
        grouped = df.groupby('age_group')[['daily_social_media_time', 'actual_productivity_score', 'screen_time_before_sleep']].agg(['mean', 'median'])
        grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]
        result = grouped.reset_index() #turn index (since group by turns into it's own column) into column for front end rendering
        output = result.to_dict(orient = 'records')
        return jsonify({'columns' : result.columns.tolist(), 'output' : output})

    except Exception as e:
        return jsonify({'error' : str(e)})

@app.route('/section_7')
def section_7():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'static', 'analysis-productivity', 'social_media_vs_productivity.csv')
        df = pd.read_csv(file_path, sep=',', quotechar='"') 

        #See distribution of screen time before sleep
        plt.figure(figsize=(10, 8))
        plt.hist(df['screen_time_before_sleep'], bins=10, edgecolor='black')
        plt.title('Distribution of Screen Time Before Sleep')
        plt.xlabel('Hours')
        plt.ylabel('Frequency')
        plt.show()
        plt.tight_layout

        # Save plot to a buffer
        buf = io.BytesIO() 
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)

        #Encode as base64
        encoded = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        return jsonify({'image' : f'data:image/png;base64,{encoded}'})
    except Exception as e:
        return jsonify({'error' : str(e)})
    
@app.route('/section_8')
def section_8():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'static', 'analysis-productivity', 'social_media_vs_productivity.csv')
        df = pd.read_csv(file_path, sep=',', quotechar='"') 


        bins = [0, 18, 30, 40, 50, 60, 100]
        labels = ['<18', '18-30', '31-40', '41-50', '51-60', '60+']
        df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels, right=True)
        df.groupby('age_group')['screen_time_before_sleep'].mean().plot(kind='bar')
        plt.figure(figsize=(10, 8))
        plt.title('Avg Screen Time Before Sleep by Age Group')
        plt.ylabel('Hours')
        plt.xlabel('Age Group')
        plt.show()
        sns.boxplot(x='age_group', y='screen_time_before_sleep', data=df)
        plt.title('Screen Time Distribution by Age Group')
        plt.show()
        plt.tight_layout

        # Save plot to a buffer
        buf = io.BytesIO() 
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)

        #Encode as base64
        encoded = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        return jsonify({'image' : f'data:image/png;base64,{encoded}'})
    except Exception as e:
        return jsonify({'error' : str(e)})

@app.route('/section_9')
def section_9():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'static', 'analysis-productivity', 'social_media_vs_productivity.csv')
        df = pd.read_csv(file_path, sep=',', quotechar='"') 

        screen_bins = [0, 1, 2, 3, 5]
        screen_labels = ['<1', '1-2', '2-3', '3-5']
        df['screen_group'] = pd.cut(df['screen_time_before_sleep'], bins=screen_bins, labels=screen_labels, right=True)
        age_bins = [0, 20, 30, 40, 100]
        age_labels = ['<20', '21-30', '31-40', '40+']
        df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels)
        cross_tab = df.groupby(['age_group', 'screen_group']).size().unstack()
        print(cross_tab)

        plt.figure(figsize=(10,8))
        sns.heatmap(cross_tab, annot=True, fmt='d', cmap='YlGnBu')
        plt.title('Screen Time Before Sleep Across Age Groups')
        plt.ylabel('Age Group')
        plt.xlabel('Screen Time Group')
        plt.show()
        plt.tight_layout

        # Save plot to a buffer
        buf = io.BytesIO() 
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)

        #Encode as base64
        encoded = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        return jsonify({'image' : f'data:image/png;base64,{encoded}'})
    except Exception as e:
        return jsonify({'error' : str(e)})
    
@app.route('/section_10')
def section_10():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'static', 'analysis-productivity', 'social_media_vs_productivity.csv')
        df = pd.read_csv(file_path, sep=',', quotechar='"') 

        age_range = [0, 18, 30, 50, 70]
        age_range_labels = ['0-18', '18-30', '30-50', '50-70']
        df['age_range'] = pd.cut(df['age'], bins=age_range, labels=age_range_labels)
        actual_productivity_range = [0, 2, 4, 6, 8, 10]
        actual_productivity_range_labels = ['0-2', '2-4', '4-6', '6-8', '8-10']
        df['actual_productivity_range'] = pd.cut(df['actual_productivity_score'], bins=actual_productivity_range, labels=actual_productivity_range_labels)
        df_ct_demographic_productivity = df.groupby(['gender', 'age_range', 'actual_productivity_range']).size().unstack('actual_productivity_range')
        plt.figure(figsize=(10,8))
        sns.heatmap(df_ct_demographic_productivity, annot=True, fmt='d', cmap='YlGnBu')
        plt.title('Productivity across age groups')
        plt.ylabel('Age Group/Gender')
        plt.xlabel('Productivity')
        plt.show()
        plt.tight_layout

        # Save plot to a buffer
        buf = io.BytesIO() 
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)

        #Encode as base64
        encoded = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        return jsonify({'image' : f'data:image/png;base64,{encoded}'})
    except Exception as e:
        return jsonify({'error' : str(e)})
    
@app.route('/section_11')
def section_11():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'static', 'analysis-productivity', 'social_media_vs_productivity.csv')
        df = pd.read_csv(file_path, sep=',', quotechar='"') 

        age_range = [0, 18, 30, 50, 70]
        age_range_labels = ['0-18', '18-30', '30-50', '50-70']
        df['age_range'] = pd.cut(df['age'], bins=age_range, labels=age_range_labels)
        actual_productivity_range = [0, 2, 4, 6, 8, 10]
        actual_productivity_range_labels = ['0-2', '2-4', '4-6', '6-8', '8-10']
        df['actual_productivity_range'] = pd.cut(df['actual_productivity_score'], bins=actual_productivity_range, labels=actual_productivity_range_labels)
        df_ct_demographic_productivity = df.groupby(['gender', 'age_range', 'actual_productivity_range']).size().unstack('actual_productivity_range')
        
        df_ct_demographic_productivity_percentage_per_group = df_ct_demographic_productivity.div(df_ct_demographic_productivity.sum(axis=1), axis=0)
        df_ct_demographic_productivity_percentage_per_group_formatted = df_ct_demographic_productivity_percentage_per_group.applymap(lambda x: f"{x*100:.2f}%")
        #above line not necessary, just testing formatting

        plt.figure(figsize=(10,8))
        sns.heatmap(df_ct_demographic_productivity_percentage_per_group, annot=True, fmt='.1%', cmap='YlGnBu')
        plt.title('Productivity across age groups')
        plt.ylabel('Age Group/Gender')
        plt.xlabel('Productivity')
        plt.show()
        plt.tight_layout

        # Save plot to a buffer
        buf = io.BytesIO() 
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)

        #Encode as base64
        encoded = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        return jsonify({'image' : f'data:image/png;base64,{encoded}'})
    except Exception as e:
        return jsonify({'error' : str(e)})
    
@app.route('/section_12')
def section_12():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'static', 'analysis-productivity', 'social_media_vs_productivity.csv')
        df = pd.read_csv(file_path, sep=',', quotechar='"') 
        #Bin age into ranges
        age_range = [0, 18, 30, 50, 70]
        age_range_labels = ['0-18', '18-30', '30-50', '50-70']
        df['age_range'] = pd.cut(df['age'], bins=age_range, labels=age_range_labels)
        
        result = df.groupby(['age_range', 'gender'])['actual_productivity_score'].median().unstack().reset_index()
        result.columns.name = None
        output=result.to_dict(orient='records')

        return jsonify({'columns' : result.columns.tolist(), 'output' : output})

    except Exception as e:
        return jsonify({'error' : str(e)})
    

@app.route('/section_13')
def section_13():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'static', 'analysis-productivity', 'social_media_vs_productivity.csv')
        df = pd.read_csv(file_path, sep=',', quotechar='"') 
        #Bin age into ranges
        age_range = [0, 18, 30, 50, 70]
        age_range_labels = ['0-18', '18-30', '30-50', '50-70']
        df['age_range'] = pd.cut(df['age'], bins=age_range, labels=age_range_labels)
        
        result = df.groupby(['age_range', 'gender']).size().unstack().reset_index()
        result.columns.name = None
        output=result.to_dict(orient='records')

        return jsonify({'columns' : result.columns.tolist(), 'output' : output})

    except Exception as e:
        return jsonify({'error' : str(e)})
    
## SCRUM project
## optimization project routes
@app.route('/scrum')
def scrum():
    return render_template('scrum/index.html')

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

USER_STORY_FILE = DATA_DIR / "scrum/user_story.csv"
EMPLOYEE_FILE = DATA_DIR / "scrum/employee.csv"
ASSIGN_FILE = DATA_DIR / "scrum/assign_user_story.csv"
SPRINT_FILE = DATA_DIR / "scrum/sprint.csv"


def load_csv(path: Path) -> pd.DataFrame:
    """Load a CSV into a DataFrame. Return empty DataFrame if missing."""
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def save_csv(df: pd.DataFrame, path: Path) -> None:
    """Save DataFrame back to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/fetch_sprint", methods=["POST"])
def fetch_sprint():
    sprint_df = load_csv(SPRINT_FILE)

    if sprint_df.empty:
        return jsonify([])

    if "current_sprint" not in sprint_df.columns:
        return jsonify({"error": "sprint.csv missing current_sprint column"}), 500

    current = sprint_df[sprint_df["current_sprint"].astype(str) == "Yes"]

    if current.empty:
        return jsonify([])

    return jsonify(current.to_dict(orient="records"))


@app.route("/api/fetch_sprint_stories", methods=["POST"])
def fetch_sprint_stories():
    selected_status = request.form.get("itemText")

    user_story_df = load_csv(USER_STORY_FILE)

    if user_story_df.empty:
        return jsonify([])

    required_cols = {"user_story_name", "current_sprint", "status"}
    if not required_cols.issubset(user_story_df.columns):
        return jsonify({
            "error": f"user_story.csv missing required columns: {sorted(required_cols)}"
        }), 500

    stories = user_story_df[user_story_df["current_sprint"].astype(str) == "Yes"].copy()

    if selected_status and selected_status != "All":
        stories = stories[stories["status"].astype(str) == selected_status]

    return jsonify(stories.to_dict(orient="records"))


@app.route("/api/fetch_assign_members", methods=["POST"])
def fetch_assign_members():
    user_story_name = request.form.get("itemText")

    if not user_story_name:
        return jsonify({"error": "Missing itemText"}), 400

    assign_df = load_csv(ASSIGN_FILE)
    employee_df = load_csv(EMPLOYEE_FILE)

    if assign_df.empty or employee_df.empty:
        return jsonify([])

    required_assign_cols = {"employee_id", "user_story_name"}
    required_employee_cols = {"employee_id", "employee_name", "role"}

    if not required_assign_cols.issubset(assign_df.columns):
        return jsonify({
            "error": f"assign_user_story.csv missing required columns: {sorted(required_assign_cols)}"
        }), 500

    if not required_employee_cols.issubset(employee_df.columns):
        return jsonify({
            "error": f"employee.csv missing required columns: {sorted(required_employee_cols)}"
        }), 500

    assign_df["employee_id"] = assign_df["employee_id"].astype(str)
    employee_df["employee_id"] = employee_df["employee_id"].astype(str)

    assigned = assign_df[assign_df["user_story_name"].astype(str) == user_story_name]

    if assigned.empty:
        return jsonify([])

    merged = assigned.merge(employee_df, on="employee_id", how="inner")

    return jsonify(merged.to_dict(orient="records"))


@app.route("/api/fetch_story_points", methods=["POST"])
def fetch_story_points():
    user_story_name = request.form.get("itemText")

    if not user_story_name:
        return jsonify({"error": "Missing itemText"}), 400

    user_story_df = load_csv(USER_STORY_FILE)

    if user_story_df.empty:
        return jsonify([])

    required_cols = {"user_story_name", "story_points", "status"}
    if not required_cols.issubset(user_story_df.columns):
        return jsonify({
            "error": f"user_story.csv missing required columns: {sorted(required_cols)}"
        }), 500

    story = user_story_df[user_story_df["user_story_name"].astype(str) == user_story_name]

    if story.empty:
        return jsonify([])

    return jsonify(story.to_dict(orient="records"))


@app.route("/api/update_status", methods=["POST"])
def update_status():
    new_status = request.form.get("newStatusText")
    user_story_name = request.form.get("userStoryText")

    if not new_status or not user_story_name:
        return jsonify({
            "status": "error",
            "message": "Missing newStatusText or userStoryText"
        }), 400

    user_story_df = load_csv(USER_STORY_FILE)

    if user_story_df.empty:
        return jsonify({
            "status": "error",
            "message": "user_story.csv not found or empty"
        }), 404

    if "user_story_name" not in user_story_df.columns or "status" not in user_story_df.columns:
        return jsonify({
            "status": "error",
            "message": "user_story.csv missing required columns"
        }), 500

    mask = user_story_df["user_story_name"].astype(str) == user_story_name

    if not mask.any():
        return jsonify({
            "status": "error",
            "message": "User story not found"
        }), 404

    user_story_df.loc[mask, "status"] = new_status
    save_csv(user_story_df, USER_STORY_FILE)

    return jsonify({
        "status": "success",
        "message": "Status updated successfully"
    })


@app.route("/api/update_phase", methods=["POST"])
def update_phase():
    new_phase = request.form.get("newPhaseText")
    phase_number = request.form.get("phaseNumberText")

    if not new_phase or not phase_number:
        return jsonify({
            "status": "error",
            "message": "Missing newPhaseText or phaseNumberText"
        }), 400

    sprint_df = load_csv(SPRINT_FILE)

    if sprint_df.empty:
        return jsonify({
            "status": "error",
            "message": "sprint.csv not found or empty"
        }), 404

    if "phase_number" not in sprint_df.columns or "phase" not in sprint_df.columns:
        return jsonify({
            "status": "error",
            "message": "sprint.csv missing required columns"
        }), 500

    sprint_df["phase_number"] = sprint_df["phase_number"].astype(str)
    mask = sprint_df["phase_number"] == str(phase_number)

    if not mask.any():
        return jsonify({
            "status": "error",
            "message": "Sprint phase_number not found"
        }), 404

    sprint_df.loc[mask, "phase"] = new_phase
    save_csv(sprint_df, SPRINT_FILE)

    return jsonify({
        "status": "success",
        "message": "Phase updated successfully"
    })



if __name__ == '__main__':
    app.run(debug=True)
    
