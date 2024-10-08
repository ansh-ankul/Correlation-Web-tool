from flask import Flask, render_template, request
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-GUI rendering
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

                # Load the file based on its type
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

                # Generate the heatmap for numeric columns
                corr_matrix = numeric_df.corr()

                # Create the heatmap
                plt.figure(figsize=(10, 8))
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
                heatmap_path = os.path.join('static', 'heatmap.png')
                plt.savefig(heatmap_path)
                plt.close()

                return render_template('heatmap.html', heatmap='heatmap.png')

        except Exception as e:
            # Catch any other exceptions and display the error
            return render_template('heatmap.html', error=f"An error occurred: {str(e)}")

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        user_input = request.form['message']
        response = f"Echo: {user_input}"  # Basic chatbot response for now
        return render_template('chatbot.html', user_input=user_input, response=response)
    return render_template('chatbot.html')

if __name__ == "__main__":
    app.run(debug=True)

