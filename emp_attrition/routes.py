from flask import render_template, request
from emp_attrition.dashboard import app


@app.server.route('/dashboard')
def dashboard():
	return app.index()

@app.server.route('/')
def home():
	return render_template('index.html')

@app.server.route('/about')
def about():
	return render_template('about.html')



