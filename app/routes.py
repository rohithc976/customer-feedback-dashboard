import math
import re
import csv
import io
from datetime import datetime
from functools import wraps
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, abort, jsonify, make_response, send_file
)
from werkzeug.security import check_password_hash
from app.database import query_db, execute_db
from app.sentiment import analyze_sentiment
from app.reports_pdf import generate_pdf_report
from config import Config

bp = Blueprint('main', __name__)

ALLOWED_CATEGORIES = ['Product', 'Service', 'Staff', 'Support', 'Delivery', 'Website', 'Other']

def login_required(f):
    """Decorator to protect admin routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in with administrator credentials to access this page.', 'warning')
            return redirect(url_for('main.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# ---------------------------------------------------------
# AUTHENTICATION ROUTES
# ---------------------------------------------------------

@bp.route('/')
def index():
    """Home redirect: admin dashboard if logged in, else feedback submission."""
    if session.get('admin_logged_in'):
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.feedback_form'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Administrator login page with hashed password validation."""
    if session.get('admin_logged_in'):
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('login.html', username=username)

        user = query_db("SELECT * FROM users WHERE username = ?", (username,), one=True)

        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['admin_logged_in'] = True
            session['admin_id'] = user['id']
            session['admin_username'] = user['username']
            flash(f"Welcome back, {user['username']}! Logged in successfully.", 'success')

            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')


@bp.route('/logout')
def logout():
    """Log out admin and clear session."""
    session.clear()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('main.login'))


# ---------------------------------------------------------
# PUBLIC CUSTOMER FEEDBACK SUBMISSION
# ---------------------------------------------------------

@bp.route('/feedback', methods=['GET', 'POST'])
def feedback_form():
    """Public customer feedback submission form with validation and sentiment analysis."""
    if request.method == 'POST':
        customer_name = request.form.get('customer_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        product_service = request.form.get('product_service', '').strip()
        category = request.form.get('category', '').strip()
        rating_raw = request.form.get('rating', '').strip()
        message = request.form.get('message', '').strip()

        errors = []

        if not customer_name or len(customer_name) < 2:
            errors.append("Customer name must be at least 2 characters long.")

        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not email or not re.match(email_pattern, email):
            errors.append("Please provide a valid email address (e.g. name@example.com).")

        if not phone or len(phone) < 7:
            errors.append("Please enter a valid phone number (at least 7 digits).")

        if not product_service:
            errors.append("Product or Service name is required.")

        if category not in ALLOWED_CATEGORIES:
            errors.append(f"Please select a valid category from the list.")

        try:
            rating = int(rating_raw)
            if rating < 1 or rating > 5:
                errors.append("Rating must be between 1 and 5 stars.")
        except (ValueError, TypeError):
            errors.append("Please select a valid star rating (1 to 5).")
            rating = 5

        if not message or len(message) < 10:
            errors.append("Feedback message must be at least 10 characters long.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'feedback_form.html',
                customer_name=customer_name,
                email=email,
                phone=phone,
                product_service=product_service,
                selected_category=category,
                rating=rating,
                message=message,
                categories=ALLOWED_CATEGORIES
            )

        # Perform Sentiment Analysis
        sentiment_result = analyze_sentiment(message, rating)
        sentiment = sentiment_result['sentiment']
        sentiment_score = sentiment_result['score']

        # Insert feedback into SQLite database
        execute_db(
            """
            INSERT INTO feedback 
            (customer_name, email, phone, product_service, category, rating, message, sentiment, sentiment_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (customer_name, email, phone, product_service, category, rating, message, sentiment, sentiment_score)
        )

        flash(f"Thank you, {customer_name}! Your feedback has been recorded successfully.", 'success')
        return redirect(url_for('main.feedback_form', submitted='true'))

    submitted = request.args.get('submitted') == 'true'
    return render_template(
        'feedback_form.html',
        categories=ALLOWED_CATEGORIES,
        submitted=submitted
    )


# ---------------------------------------------------------
# ADMIN DASHBOARD
# ---------------------------------------------------------

@bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard with interactive charts, KPIs, and recent feedback."""
    # Summary KPIs
    total_feedback_row = query_db("SELECT COUNT(*) AS total FROM feedback", one=True)
    total_feedback = total_feedback_row['total'] if total_feedback_row else 0

    avg_rating_row = query_db("SELECT ROUND(AVG(rating), 2) AS avg_rate FROM feedback", one=True)
    avg_rating = avg_rating_row['avg_rate'] if avg_rating_row and avg_rating_row['avg_rate'] is not None else 0.0

    pos_count_row = query_db("SELECT COUNT(*) AS count FROM feedback WHERE sentiment = 'Positive'", one=True)
    pos_count = pos_count_row['count'] if pos_count_row else 0

    neu_count_row = query_db("SELECT COUNT(*) AS count FROM feedback WHERE sentiment = 'Neutral'", one=True)
    neu_count = neu_count_row['count'] if neu_count_row else 0

    neg_count_row = query_db("SELECT COUNT(*) AS count FROM feedback WHERE sentiment = 'Negative'", one=True)
    neg_count = neg_count_row['count'] if neg_count_row else 0

    # Today's feedback count
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_count_row = query_db("SELECT COUNT(*) AS count FROM feedback WHERE DATE(created_at) = DATE(?)", (today_str,), one=True)
    today_count = today_count_row['count'] if today_count_row else 0

    # Recent Feedback (last 6 entries)
    recent_feedbacks = query_db(
        "SELECT * FROM feedback ORDER BY id DESC LIMIT 6"
    )

    # 1. Rating Distribution (1 to 5 stars)
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    rating_rows = query_db("SELECT rating, COUNT(*) AS count FROM feedback GROUP BY rating")
    for r in rating_rows:
        rating_counts[r['rating']] = r['count']

    # 2. Sentiment Distribution
    sentiment_data = {
        'Positive': pos_count,
        'Neutral': neu_count,
        'Negative': neg_count
    }

    # 3. Category Distribution
    category_rows = query_db("SELECT category, COUNT(*) AS count FROM feedback GROUP BY category ORDER BY count DESC")
    category_labels = [r['category'] for r in category_rows] if category_rows else ALLOWED_CATEGORIES
    category_counts = [r['count'] for r in category_rows] if category_rows else [0] * len(ALLOWED_CATEGORIES)

    # 4. Trend Timeline (Grouped by date for last 14 active days)
    trend_rows = query_db(
        """
        SELECT DATE(created_at) AS f_date, COUNT(*) AS count 
        FROM feedback 
        GROUP BY DATE(created_at) 
        ORDER BY DATE(created_at) ASC 
        LIMIT 14
        """
    )
    trend_labels = [r['f_date'] for r in trend_rows]
    trend_counts = [r['count'] for r in trend_rows]

    stats = {
        'total_feedback': total_feedback,
        'avg_rating': avg_rating,
        'positive_count': pos_count,
        'neutral_count': neu_count,
        'negative_count': neg_count,
        'today_count': today_count,
        'positive_pct': round((pos_count / total_feedback * 100), 1) if total_feedback > 0 else 0,
        'neutral_pct': round((neu_count / total_feedback * 100), 1) if total_feedback > 0 else 0,
        'negative_pct': round((neg_count / total_feedback * 100), 1) if total_feedback > 0 else 0,
    }

    chart_payload = {
        'ratings': {
            'labels': ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'],
            'data': [rating_counts[1], rating_counts[2], rating_counts[3], rating_counts[4], rating_counts[5]]
        },
        'sentiments': {
            'labels': ['Positive', 'Neutral', 'Negative'],
            'data': [pos_count, neu_count, neg_count]
        },
        'categories': {
            'labels': category_labels,
            'data': category_counts
        },
        'trends': {
            'labels': trend_labels,
            'data': trend_counts
        }
    }

    return render_template(
        'dashboard.html',
        stats=stats,
        recent_feedbacks=recent_feedbacks,
        chart_payload=chart_payload
    )


@bp.route('/api/dashboard-stats')
@login_required
def api_dashboard_stats():
    """API endpoint for live dashboard data fetching."""
    total_feedback_row = query_db("SELECT COUNT(*) AS total FROM feedback", one=True)
    total_feedback = total_feedback_row['total'] if total_feedback_row else 0
    avg_rating_row = query_db("SELECT ROUND(AVG(rating), 2) AS avg_rate FROM feedback", one=True)
    avg_rating = avg_rating_row['avg_rate'] if avg_rating_row and avg_rating_row['avg_rate'] is not None else 0.0

    return jsonify({
        'total_feedback': total_feedback,
        'avg_rating': avg_rating
    })


# ---------------------------------------------------------
# FEEDBACK MANAGEMENT (SEARCH, FILTER, SORT, PAGINATE)
# ---------------------------------------------------------

@bp.route('/feedback/list')
@bp.route('/feedback/manage')
@login_required
def feedback_list():
    """Admin feedback management table with dynamic searching, multi-filter, and pagination."""
    # Query parameters
    search_q = request.args.get('q', '').strip()
    filter_rating = request.args.get('rating', '').strip()
    filter_category = request.args.get('category', '').strip()
    filter_sentiment = request.args.get('sentiment', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    sort_by = request.args.get('sort', 'newest').strip()

    try:
        page = max(1, int(request.args.get('page', 1)))
    except (ValueError, TypeError):
        page = 1

    per_page = Config.ITEMS_PER_PAGE

    # Dynamic SQL builder
    where_clauses = ["1=1"]
    params = []

    if search_q:
        where_clauses.append("(customer_name LIKE ? OR email LIKE ? OR product_service LIKE ? OR message LIKE ?)")
        wildcard_search = f"%{search_q}%"
        params.extend([wildcard_search, wildcard_search, wildcard_search, wildcard_search])

    if filter_rating and filter_rating.isdigit():
        where_clauses.append("rating = ?")
        params.append(int(filter_rating))

    if filter_category and filter_category in ALLOWED_CATEGORIES:
        where_clauses.append("category = ?")
        params.append(filter_category)

    if filter_sentiment and filter_sentiment in ['Positive', 'Neutral', 'Negative']:
        where_clauses.append("sentiment = ?")
        params.append(filter_sentiment)

    if date_from:
        where_clauses.append("DATE(created_at) >= DATE(?)")
        params.append(date_from)

    if date_to:
        where_clauses.append("DATE(created_at) <= DATE(?)")
        params.append(date_to)

    where_sql = " AND ".join(where_clauses)

    # Count total records matching filter criteria
    count_query = f"SELECT COUNT(*) AS total FROM feedback WHERE {where_sql}"
    total_row = query_db(count_query, params, one=True)
    total_records = total_row['total'] if total_row else 0
    total_pages = max(1, math.ceil(total_records / per_page))
    if page > total_pages:
        page = total_pages

    # Sorting
    sort_orders = {
        'newest': 'id DESC',
        'oldest': 'id ASC',
        'rating_high': 'rating DESC, id DESC',
        'rating_low': 'rating ASC, id DESC',
        'customer_asc': 'customer_name ASC',
    }
    order_clause = sort_orders.get(sort_by, 'id DESC')

    # Data query with pagination
    offset = (page - 1) * per_page
    data_query = f"""
        SELECT * FROM feedback 
        WHERE {where_sql} 
        ORDER BY {order_clause} 
        LIMIT ? OFFSET ?
    """
    query_params = list(params) + [per_page, offset]
    feedbacks = query_db(data_query, query_params)

    return render_template(
        'feedback_list.html',
        feedbacks=feedbacks,
        total_records=total_records,
        page=page,
        total_pages=total_pages,
        categories=ALLOWED_CATEGORIES,
        # Active filters passed back to preserve state
        q=search_q,
        rating=filter_rating,
        category=filter_category,
        sentiment=filter_sentiment,
        date_from=date_from,
        date_to=date_to,
        sort=sort_by
    )


# ---------------------------------------------------------
# FEEDBACK DETAILS & DELETION
# ---------------------------------------------------------

@bp.route('/feedback/<int:feedback_id>')
@login_required
def feedback_detail(feedback_id):
    """View detailed customer feedback item including sentiment audit breakdown."""
    feedback = query_db("SELECT * FROM feedback WHERE id = ?", (feedback_id,), one=True)
    if not feedback:
        abort(404)

    # Re-evaluate sentiment details for forensic breakdown display
    sentiment_breakdown = analyze_sentiment(feedback['message'], feedback['rating'])

    return render_template(
        'feedback_detail.html',
        feedback=feedback,
        sentiment_breakdown=sentiment_breakdown
    )


@bp.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
@login_required
def feedback_delete(feedback_id):
    """Delete a feedback entry permanently."""
    feedback = query_db("SELECT id, customer_name FROM feedback WHERE id = ?", (feedback_id,), one=True)
    if not feedback:
        abort(404)

    execute_db("DELETE FROM feedback WHERE id = ?", (feedback_id,))
    flash(f"Feedback entry #{feedback_id} from '{feedback['customer_name']}' has been permanently deleted.", 'success')
    return redirect(url_for('main.feedback_list'))


# ---------------------------------------------------------
# REPORTS & EXPORTS
# ---------------------------------------------------------

@bp.route('/reports')
@login_required
def reports():
    """Comprehensive executive analytics report."""
    # Summary Metrics
    total_feedback_row = query_db("SELECT COUNT(*) AS total FROM feedback", one=True)
    total_feedback = total_feedback_row['total'] if total_feedback_row else 0

    avg_rating_row = query_db("SELECT ROUND(AVG(rating), 2) AS avg_rate FROM feedback", one=True)
    avg_rating = avg_rating_row['avg_rate'] if avg_rating_row and avg_rating_row['avg_rate'] is not None else 0.0

    pos_count_row = query_db("SELECT COUNT(*) AS count FROM feedback WHERE sentiment = 'Positive'", one=True)
    pos_count = pos_count_row['count'] if pos_count_row else 0

    neu_count_row = query_db("SELECT COUNT(*) AS count FROM feedback WHERE sentiment = 'Neutral'", one=True)
    neu_count = neu_count_row['count'] if neu_count_row else 0

    neg_count_row = query_db("SELECT COUNT(*) AS count FROM feedback WHERE sentiment = 'Negative'", one=True)
    neg_count = neg_count_row['count'] if neg_count_row else 0

    summary_stats = {
        'total_feedback': total_feedback,
        'avg_rating': avg_rating,
        'positive_count': pos_count,
        'neutral_count': neu_count,
        'negative_count': neg_count,
        'positive_pct': round((pos_count / total_feedback * 100), 1) if total_feedback > 0 else 0,
        'neutral_pct': round((neu_count / total_feedback * 100), 1) if total_feedback > 0 else 0,
        'negative_pct': round((neg_count / total_feedback * 100), 1) if total_feedback > 0 else 0,
    }

    # Category Statistics
    category_stats_raw = query_db("""
        SELECT 
            category,
            COUNT(*) AS count,
            ROUND(AVG(rating), 2) AS avg_rating,
            SUM(CASE WHEN sentiment = 'Positive' THEN 1 ELSE 0 END) AS pos_cnt
        FROM feedback 
        GROUP BY category 
        ORDER BY count DESC
    """)
    category_stats = []
    for c in category_stats_raw:
        c_count = c['count']
        c_pct = round((c_count / total_feedback * 100), 1) if total_feedback > 0 else 0
        pos_pct = round((c['pos_cnt'] / c_count * 100), 1) if c_count > 0 else 0
        category_stats.append({
            'category': c['category'],
            'count': c_count,
            'percentage': c_pct,
            'avg_rating': c['avg_rating'] if c['avg_rating'] is not None else 0.0,
            'positive_pct': pos_pct
        })

    # Rating Statistics
    rating_stats_raw = query_db("""
        SELECT 
            rating AS stars,
            COUNT(*) AS count
        FROM feedback 
        GROUP BY rating 
        ORDER BY rating DESC
    """)
    rating_stats = []
    for r in rating_stats_raw:
        r_count = r['count']
        r_pct = round((r_count / total_feedback * 100), 1) if total_feedback > 0 else 0
        rating_stats.append({
            'stars': r['stars'],
            'count': r_count,
            'percentage': r_pct
        })

    # Monthly Statistics
    monthly_stats_raw = query_db("""
        SELECT 
            strftime('%Y-%m', created_at) AS month_period,
            COUNT(*) AS count,
            ROUND(AVG(rating), 2) AS avg_rating,
            SUM(CASE WHEN sentiment = 'Positive' THEN 1 ELSE 0 END) AS pos_count,
            SUM(CASE WHEN sentiment = 'Negative' THEN 1 ELSE 0 END) AS neg_count
        FROM feedback 
        GROUP BY strftime('%Y-%m', created_at) 
        ORDER BY month_period DESC
    """)
    monthly_stats = []
    for m in monthly_stats_raw:
        m_count = m['count']
        pos_pct = round((m['pos_count'] / m_count * 100), 1) if m_count > 0 else 0
        neg_pct = round((m['neg_count'] / m_count * 100), 1) if m_count > 0 else 0
        monthly_stats.append({
            'month': m['month_period'],
            'count': m_count,
            'avg_rating': m['avg_rating'] if m['avg_rating'] is not None else 0.0,
            'pos_pct': pos_pct,
            'neg_pct': neg_pct
        })

    return render_template(
        'reports.html',
        summary_stats=summary_stats,
        category_stats=category_stats,
        rating_stats=rating_stats,
        monthly_stats=monthly_stats,
        generated_at=datetime.now().strftime('%B %d, %Y - %I:%M %p')
    )


@bp.route('/reports/export/csv')
@login_required
def export_csv():
    """Export all feedback records to CSV file."""
    feedbacks = query_db("SELECT * FROM feedback ORDER BY id ASC")

    output = io.StringIO()
    writer = csv.writer(output)

    # Write CSV Header
    writer.writerow([
        'Feedback ID',
        'Customer Name',
        'Email Address',
        'Phone Number',
        'Product / Service',
        'Category',
        'Rating (Stars)',
        'Sentiment',
        'Sentiment Score',
        'Feedback Message',
        'Created Date'
    ])

    for f in feedbacks:
        writer.writerow([
            f['id'],
            f['customer_name'],
            f['email'],
            f['phone'],
            f['product_service'],
            f['category'],
            f['rating'],
            f['sentiment'],
            f.get('sentiment_score', 0.0),
            f['message'],
            f['created_at']
        ])

    csv_data = output.getvalue()
    output.close()

    filename = f"feedback_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@bp.route('/reports/export/pdf')
@login_required
def export_pdf():
    """Generate and download executive PDF analytics report using ReportLab."""
    # Fetch summary metrics
    total_feedback_row = query_db("SELECT COUNT(*) AS total FROM feedback", one=True)
    total_feedback = total_feedback_row['total'] if total_feedback_row else 0
    avg_rating_row = query_db("SELECT ROUND(AVG(rating), 2) AS avg_rate FROM feedback", one=True)
    avg_rating = avg_rating_row['avg_rate'] if avg_rating_row and avg_rating_row['avg_rate'] is not None else 0.0

    pos_count = query_db("SELECT COUNT(*) AS count FROM feedback WHERE sentiment = 'Positive'", one=True)['count']
    neu_count = query_db("SELECT COUNT(*) AS count FROM feedback WHERE sentiment = 'Neutral'", one=True)['count']
    neg_count = query_db("SELECT COUNT(*) AS count FROM feedback WHERE sentiment = 'Negative'", one=True)['count']

    today_str = datetime.now().strftime('%Y-%m-%d')
    today_count = query_db("SELECT COUNT(*) AS count FROM feedback WHERE DATE(created_at) = DATE(?)", (today_str,), one=True)['count']

    summary_stats = {
        'total_feedback': total_feedback,
        'avg_rating': avg_rating,
        'positive_count': pos_count,
        'neutral_count': neu_count,
        'negative_count': neg_count,
        'today_count': today_count,
        'positive_pct': round((pos_count / total_feedback * 100), 1) if total_feedback > 0 else 0,
        'neutral_pct': round((neu_count / total_feedback * 100), 1) if total_feedback > 0 else 0,
        'negative_pct': round((neg_count / total_feedback * 100), 1) if total_feedback > 0 else 0,
    }

    # Category stats
    cat_rows = query_db("""
        SELECT category, COUNT(*) AS count, ROUND(AVG(rating), 2) AS avg_rating,
        SUM(CASE WHEN sentiment = 'Positive' THEN 1 ELSE 0 END) AS pos_cnt
        FROM feedback GROUP BY category ORDER BY count DESC
    """)
    category_stats = []
    for c in cat_rows:
        c_count = c['count']
        category_stats.append({
            'category': c['category'],
            'count': c_count,
            'percentage': round((c_count / total_feedback * 100), 1) if total_feedback > 0 else 0,
            'avg_rating': c['avg_rating'] if c['avg_rating'] is not None else 0.0,
            'positive_pct': round((c['pos_cnt'] / c_count * 100), 1) if c_count > 0 else 0
        })

    # Rating stats
    rate_rows = query_db("SELECT rating AS stars, COUNT(*) AS count FROM feedback GROUP BY rating ORDER BY rating DESC")
    rating_stats = []
    for r in rate_rows:
        r_count = r['count']
        rating_stats.append({
            'stars': r['stars'],
            'count': r_count,
            'percentage': round((r_count / total_feedback * 100), 1) if total_feedback > 0 else 0
        })

    # Recent feedback samples
    recent_feedbacks = query_db("SELECT * FROM feedback ORDER BY id DESC LIMIT 8")

    pdf_buffer = generate_pdf_report(summary_stats, category_stats, rating_stats, recent_feedbacks)
    filename = f"Customer_Feedback_Report_{datetime.now().strftime('%Y%m%d')}.pdf"

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


# ---------------------------------------------------------
# ERROR HANDLERS
# ---------------------------------------------------------

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
