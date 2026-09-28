import os
from app import create_app
from app.database import init_db

app = create_app()

if __name__ == '__main__':
    # Automatically initialize SQLite database tables if missing
    init_db(app)
    port = int(os.environ.get('PORT', 5000))
    print(f" * Customer Feedback Dashboard running on http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=True)
