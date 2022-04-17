
from flask import Flask, request, send_file
import pdf_compressor

app = Flask(__name__)

@app.route('/')
def form():
    return """
    <html>
        <body>
            <h1>Upload your PDF</h1>
            <form action="/transform" method="post" enctype="multipart/form-data">
                <input type="file" name="data_file" />
                mode
                <input type="number" value="3" min="1" max="10">
                <input type="submit"/>
            </form>
        </body>
    </html>
"""

@app.route('/transform', methods=["POST"])
def transform_view():
    request_file = request.files['data_file']
    request_file.save(request_file.filename)

    output_file =  pdf_compressor.get_filename(request_file.filename)+"_compressed.pdf"
    pdf_compressor.pdf_compressor(request_file.filename, output_file)

    return send_file(output_file, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)