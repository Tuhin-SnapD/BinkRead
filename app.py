from flask import Flask, render_template, request
from transformers import pipeline, AutoTokenizer
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
       

       pdf_text = pdf_text.replace("\n", " ").replace("  ", " ") # cleans the pdf text by removing mid-sentence line breaks and double spaces.

       # Now we will break the pdf text into small chunks of 4000 character and summarizes them
       chunksize = 4000
       start = 0
       Complete_summary = ""

          # In the with the help of bard model, the pipeline summarizes the pdf for us.
       summarizer = pipeline("summarization", model="facebook/bart-large-cnn")  #Loading the model that will summarizes the pdf

           #Initialize it for token count checking so that model won't get choke on too many tokens it can't handle it, which will helps in preventing crash       
       tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")

       while(start<len(pdf_text)):
           chunk = pdf_text[start:start+chunksize] # We will break the chunk after every 4000 characters
           # But pdf_text[:4000] : This will cut in the middle of a word, which can break meaning and mess up tokenization.
           last_space_index = chunk.rfind(" ")   # So we will find the last occurence of space within the 4000 character limit.

           # If there is not space:
           if last_space_index == -1:
               last_space_index = chunksize # Fallback

           chunk_text = pdf_text[start:start+last_space_index]  #Store the chunk
           
           #Before calling the summarizer we will skip the chunks that will exceed the token limit
           if len(tokenizer.encode(chunk_text)) > 1024:
                print("Skipping a chunk because it exceeds the token limit")
                start += last_space_index + 1
                continue

           # Now Summarize this chunk_text         
           #We store the summary in a variable
           summary = summarizer(chunk_text, max_length=300, min_length=100)
           Complete_summary += summary[0]['summary_text'] + "\n\n"
           print(summary)
           start = start+last_space_index+1  # Now move to next chunk 

       return render_template("index.html",summary=Complete_summary)
   return "Error"
       
       
       
       
       

if __name__ == '__main__':
    app.run(debug=True)