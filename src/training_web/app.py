from flask import Flask, request

app = Flask(__name__)

@app.route('/classify', methods=['POST'])
def classify():
    data = request.get_json()
    paragraph = data['paragraph']
    label = data['label']
    # Here, you can process the classification as needed
    print(f"Classified paragraph as: {label}")
    return {'status': 'success'}

if __name__ == '__main__':
    app.run(debug=True)
