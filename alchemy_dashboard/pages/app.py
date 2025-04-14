from flask import Flask, render_template
from bokeh.embed import server_document

app = Flask(__name__)

@app.route('/')
def index():
    script = server_document('http://localhost:5007/alchemy_dashboard')
    return render_template('index_with_bokeh.html', bokeh_script=script)

if __name__ == '__main__':
    app.run(port=5000, debug=True)