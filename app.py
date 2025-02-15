from flask import Flask, request, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/home')
def home():
    return render_template('index.html')

if __name__=='__main__':
    app.run(debug=True)
