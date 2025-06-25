from flask import Flask, render_template, request
from transformers import pipeline
import fitz
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

#Uploading pdf into database function
@app.route('/upload', methods=['POST'])
def upload_pdf():
   file = request.files['uploaded_file']
   if file and file.filename.endswith('.pdf'):
       pdf = fitz.open(stream=file.read(), filetype="pdf")
       pdf_text = ""
       # In this loop we r taking out all the text and storing it into a 'pdf_text' variable.
       for page in pdf:
           pdf_text += page.get_text()
       # In the with the help of bard model, the pipeline summarizes the pdf for us.
       summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

       #We store the summary in a variable
       summary = summarizer(pdf_text, max_length=500, min_length=30)
       print(summary)
       return render_template("index.html",summary=summary)
   return "Error"
       
       
       
       
       

if __name__ == '__main__':
    app.run(debug=True)