from backend.flask import app

if __name__ == '__main__':
	app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5000)