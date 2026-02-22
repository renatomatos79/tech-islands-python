from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello, Python API!"})

# If the script is executed directly, __name__ is set to '__main__'.
# ===> python app.py
# If the script is imported into another module, __name__ will be the filename (e.g., 'app').

if __name__ == '__main__':
    app.run(debug=True)
