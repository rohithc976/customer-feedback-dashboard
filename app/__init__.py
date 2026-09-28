import os
from flask import Flask
from config import Config
from app.database import close_db

def create_app(config_class=Config):
    """
    Application factory pattern for Flask Customer Feedback Dashboard.
    Configures database teardown, registers blueprints, and adds custom filters.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )
    app.config.from_object(config_class)

    # Register database connection cleanup on app teardown
    app.teardown_appcontext(close_db)

    # Register blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    # Custom Jinja filters for presentation
    @app.template_filter('datetime_format')
    def datetime_format(value, format_str='%b %d, %Y - %I:%M %p'):
        if not value:
            return ''
        try:
            # Handles 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD'
            if isinstance(value, str):
                if ' ' in value:
                    dt = datetime.strptime(value.split('.')[0], '%Y-%m-%d %H:%M:%S')
                else:
                    dt = datetime.strptime(value, '%Y-%m-%d')
                return dt.strftime(format_str)
            return value.strftime(format_str)
        except Exception:
            return str(value)

    from datetime import datetime
    app.jinja_env.filters['datetime_format'] = datetime_format

    return app
