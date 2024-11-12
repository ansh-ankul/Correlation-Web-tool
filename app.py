from flask import Flask, render_template, request, url_for
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import io
import base64

matplotlib.use('Agg') 
plt.rcParams.update({'font.size': 12})

app = Flask(__name__)

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
                try:
                    if file.filename.endswith('.csv'):
                        df = pd.read_csv(file)
                    elif file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
                        df = pd.read_excel(file)
                    else:
                        raise ValueError("Unsupported file type. Please upload a CSV or Excel file.")
                
                except Exception as e:
                    return render_template('heatmap.html', error=f"File reading error: {str(e)}")

                # Filter only numeric columns
                numeric_df = df.select_dtypes(include='number')
                
                if numeric_df.empty:
                    raise ValueError("No numeric columns found in the uploaded file.")

                corr_matrix = numeric_df.corr()

                # Create the heatmap and save it to a BytesIO object
                plt.figure(figsize=(12, 10)) 
                sns.set(font_scale=1.2)
                ax = sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, annot_kws={"size": 12}, cbar_kws={"shrink": 0.8})
                ax.tick_params(axis='both', which='major', labelsize=12)
                plt.tight_layout()

                img = io.BytesIO()
                plt.savefig(img, format='png', bbox_inches='tight')
                plt.close()
                img.seek(0)
                img_base64 = base64.b64encode(img.read()).decode('utf-8')
                img_data = f"data:image/png;base64,{img_base64}"

                # Render the image in the HTML
                return render_template('heatmap.html', heatmap=img_data)

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
