from flask import Flask, render_template, request
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Folder to store the uploaded files
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/heatmap')
def heatmap():
    return render_template('heatmap.html')

@app.route('/datasets')
def datasets():
    return render_template('datasets.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        try:
            file = request.files['file']
            if file:
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(file_path)

                try:
                    if file.filename.endswith('.csv'):
                        df = pd.read_csv(file_path)
                    elif file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
                        df = pd.read_excel(file_path)
                    else:
                        raise ValueError("Unsupported file type. Please upload a CSV or Excel file.")
                
                except Exception as e:
                    return render_template('heatmap.html', error=f"File reading error: {str(e)}")

                # Filter only numeric columns
                numeric_df = df.select_dtypes(include='number')
                
                if numeric_df.empty:
                    raise ValueError("No numeric columns found in the uploaded file.")

                corr_matrix = numeric_df.corr()

                # Create the heatmap 
                plt.figure(figsize=(12, 10)) 
                sns.set(font_scale=1.2)
                ax = sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, annot_kws={"size": 12}, cbar_kws={"shrink": 0.8})
                ax.tick_params(axis='both', which='major', labelsize=12)
                plt.tight_layout()
                heatmap_path = os.path.join('static', 'heatmap.png')
                plt.savefig(heatmap_path, bbox_inches='tight') 
                plt.close()


                return render_template('heatmap.html', heatmap='heatmap.png')

        except Exception as e:
            return render_template('heatmap.html', error=f"An error occurred: {str(e)}")

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        user_input = request.form['message']
        response = f"Echo: {user_input}" 
        return render_template('chatbot.html', user_input=user_input, response=response)
    return render_template('chatbot.html')

if __name__ == "__main__":
    app.run(debug=True)

