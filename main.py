from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import fitz
import zlib
import PIL.Image
import pyzbar.pyzbar
import base45
import cbor2
import os
import json

app = Flask(__name__)
CORS(app)

@app.route('/pdf2id', methods = ['POST'])
def pdf2id():
    print('==> function starts')
    if request.method == 'POST':
        print(request.files)
        file_val = request.files['file']
        f = open("tmp/cert.pdf", "wb")
        f.write(file_val.read())
        f.close()
    
    doc = fitz.open("tmp/cert.pdf")
    for i in range(len(doc)):
        for img in doc.get_page_images(i):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n < 5 and xref==4:
                pix.save("tmp/qrcode.png")
            pix = None
    
    data = pyzbar.pyzbar.decode(PIL.Image.open("tmp/qrcode.png"))
    cert = data[0].data.decode()
    b45data = cert.replace("HC1:", "")
    zlibdata = base45.b45decode(b45data)
    cbordata = zlib.decompress(zlibdata)
    decoded = cbor2.loads(cbordata)
    result = cbor2.loads(decoded.value[2])[-260][1]
    print(result)
    return jsonify(data=json.dumps(result))
        
        
@app.route("/")
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
