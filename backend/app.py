import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from backend.limiter import limiter

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")

CORS(app, origins=[
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://mindful-bot-three.vercel.app"
])

limiter.init_app(app)


@app.errorhandler(429)
def ratelimit_handler(_):
    return jsonify({
        "error": "Rate limit exceeded. Please slow down.",
        "retry_after": "60 seconds",
    }), 429
from backend.routes.chat import chat_bp
from backend.routes.scores import scores_bp
from backend.routes.users import users_bp

app.register_blueprint(chat_bp, url_prefix="/api")
app.register_blueprint(scores_bp, url_prefix="/api")
app.register_blueprint(users_bp, url_prefix="/api")

@app.get("/api/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(port=5001, debug=True)
