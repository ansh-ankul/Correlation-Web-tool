from flask import Flask, render_template, request, url_for
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import io
import base64
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

matplotlib.use('Agg') 
plt.rcParams.update({'font.size': 12})

app = Flask(__name__)

@app.route('/')
def home():
    logger.info("Rendering home page.")
    return render_template('index.html')

@app.route('/heatmap')
def heatmap():
    logger.info("Rendering heatmap page.")
    return render_template('heatmap.html')

@app.route('/datasets')
def datasets():
    logger.info("Rendering datasets page.")
    return render_template('datasets.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        try:
            logger.info("File upload initiated.")
            file = request.files['file']

            if not file or file.filename == '':
                logger.error("No file selected.")
                return render_template('heatmap.html', error="No file selected. Please upload a CSV or Excel file.")

            try:
                if file.filename.endswith('.csv'):
                    logger.info("Reading CSV file.")
                    df = pd.read_csv(file)
                elif file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
                    logger.info("Reading Excel file.")
                    df = pd.read_excel(file)
                else:
                    raise ValueError("Unsupported file type. Please upload a CSV or Excel file.")
            except Exception as e:
                logger.error(f"File reading error: {str(e)}")
                return render_template('heatmap.html', error=f"File reading error: {str(e)}")

            # Filter only numeric columns
            numeric_df = df.select_dtypes(include='number')
            if numeric_df.empty:
                logger.error("No numeric columns found in the uploaded file.")
                return render_template('heatmap.html', error="No numeric columns found in the uploaded file.")

            logger.info("Generating correlation matrix.")
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

            logger.info("Heatmap generated successfully.")
            # Render the image in the HTML
            return render_template('heatmap.html', heatmap=img_data)

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return render_template('heatmap.html', error=f"An error occurred: {str(e)}")

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        user_input = request.form['message']
        response = f"Echo: {user_input}"
        logger.info(f"User input received: {user_input}")
        return render_template('chatbot.html', user_input=user_input, response=response)
    logger.info("Rendering chatbot page.")
    return render_template('chatbot.html')

if __name__ == "__main__":
    logger.info("Starting Flask application.")
    app.run(host='0.0.0.0', port=5000)

