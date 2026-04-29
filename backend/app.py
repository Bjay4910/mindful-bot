import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")

# Allow all origins for development
CORS(app)
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
