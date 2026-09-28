import sys
import os
from datetime import datetime, timedelta

# Add parent directory to python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
from config import Config
from app.database import init_db
from app.sentiment import analyze_sentiment

SAMPLE_FEEDBACKS = [
    {
        "customer_name": "Aarav Sharma",
        "email": "aarav.sharma@example.com",
        "phone": "+91 98765 43210",
        "product_service": "SmartTrack Pro GPS Watch",
        "category": "Product",
        "rating": 5,
        "message": "The GPS watch is outstanding! Extremely accurate battery life, super fast sync, and brilliant display. Highly recommended to everyone.",
        "days_ago": 0  # Today
    },
    {
        "customer_name": "Priya Nair",
        "email": "priya.nair@example.com",
        "phone": "+91 98450 11223",
        "product_service": "Cloud Sync Subscription",
        "category": "Support",
        "rating": 5,
        "message": "Customer support team was exceptionally helpful, polite and resolved my billing query within 10 minutes. Fantastic service!",
        "days_ago": 0  # Today
    },
    {
        "customer_name": "Rohan Patel",
        "email": "rohan.patel@example.com",
        "phone": "+91 97234 56789",
        "product_service": "Express Home Delivery",
        "category": "Delivery",
        "rating": 1,
        "message": "Terrible delivery experience. The package was delayed by 6 days and the outer box was damaged and broken. Very disappointing and pathetic.",
        "days_ago": 1
    },
    {
        "customer_name": "Sneha Kulkarni",
        "email": "sneha.k@example.com",
        "phone": "+91 98111 22334",
        "product_service": "Customer Portal Website",
        "category": "Website",
        "rating": 4,
        "message": "The website design is clean, fast, and very easy to navigate. Would love to see dark mode added in the upcoming release.",
        "days_ago": 1
    },
    {
        "customer_name": "Vikram Malhotra",
        "email": "vikram.m@example.com",
        "phone": "+91 99887 76655",
        "product_service": "Annual Maintenance Service",
        "category": "Service",
        "rating": 4,
        "message": "The technician was courteous and professional. Service was completed on time with good attention to detail.",
        "days_ago": 2
    },
    {
        "customer_name": "Ananya Roy",
        "email": "ananya.roy@example.com",
        "phone": "+91 98300 45678",
        "product_service": "Mobile Banking Application",
        "category": "Product",
        "rating": 2,
        "message": "The latest app update is buggy and keeps crashing whenever I try to download PDF receipts. Please fix this frustrating error.",
        "days_ago": 3
    },
    {
        "customer_name": "Karthik Raja",
        "email": "karthik.raja@example.com",
        "phone": "+91 94440 98765",
        "product_service": "In-Store Experience",
        "category": "Staff",
        "rating": 5,
        "message": "The branch staff were friendly, welcoming, and guided me through the entire loan documentation smoothly. Delighted!",
        "days_ago": 3
    },
    {
        "customer_name": "Meera Iyer",
        "email": "meera.iyer@example.com",
        "phone": "+91 98201 54321",
        "product_service": "Ergonomic Office Chair",
        "category": "Product",
        "rating": 3,
        "message": "The chair build quality is average. Assembly was moderately complicated and lumbar support is neither great nor terrible.",
        "days_ago": 4
    },
    {
        "customer_name": "Aditya Verma",
        "email": "aditya.v@example.com",
        "phone": "+91 91670 12345",
        "product_service": "Broadband Fiber Net",
        "category": "Service",
        "rating": 1,
        "message": "Slow internet speeds constantly throughout the evening. Contacted support multiple times but received unhelpful generic replies. Awful.",
        "days_ago": 5
    },
    {
        "customer_name": "Divya Deshmukh",
        "email": "divya.d@example.com",
        "phone": "+91 97654 32109",
        "product_service": "Courier Delivery",
        "category": "Delivery",
        "rating": 4,
        "message": "Prompt delivery well before estimated time. Courier agent was polite and package arrived safely.",
        "days_ago": 5
    },
    {
        "customer_name": "Siddharth Jain",
        "email": "sid.jain@example.com",
        "phone": "+91 98920 67890",
        "product_service": "Checkout Payment Gateway",
        "category": "Website",
        "rating": 2,
        "message": "The payment page failed twice during UPI verification. It caused unnecessary frustration and delayed my order completion.",
        "days_ago": 6
    },
    {
        "customer_name": "Pooja Reddy",
        "email": "pooja.reddy@example.com",
        "phone": "+91 99490 87654",
        "product_service": "Help Desk Chatbot",
        "category": "Support",
        "rating": 3,
        "message": "The automated chatbot is okay for standard questions, but struggles to transfer to human representatives when issues get complex.",
        "days_ago": 7
    },
    {
        "customer_name": "Manish Gupta",
        "email": "manish.g@example.com",
        "phone": "+91 98100 11445",
        "product_service": "Noise-Cancelling Headphones",
        "category": "Product",
        "rating": 5,
        "message": "Flawless sound quality! Deep bass, crisp vocals, and super comfortable ear cushions for long work calls. Love it!",
        "days_ago": 8
    },
    {
        "customer_name": "Tanvi Joshi",
        "email": "tanvi.j@example.com",
        "phone": "+91 98220 33445",
        "product_service": "Showroom Assistance",
        "category": "Staff",
        "rating": 4,
        "message": "The sales executive was patient, knowledgeable, and answered all our questions regarding product warranty clearly.",
        "days_ago": 9
    },
    {
        "customer_name": "Rajesh Khanna",
        "email": "rajesh.k@example.com",
        "phone": "+91 98400 55667",
        "product_service": "Warranty Extension Pack",
        "category": "Other",
        "rating": 3,
        "message": "Fair pricing for extended protection plan. Documentation process took slightly longer than expected but finalized smoothly.",
        "days_ago": 10
    },
    {
        "customer_name": "Kavita Singhania",
        "email": "kavita.s@example.com",
        "phone": "+91 99301 22334",
        "product_service": "Same-Day Grocery Delivery",
        "category": "Delivery",
        "rating": 5,
        "message": "Delivered within 45 minutes! Produce was fresh, neat packaging, and delivery partner followed all delivery instructions accurately.",
        "days_ago": 11
    },
    {
        "customer_name": "Arjun Kapoor",
        "email": "arjun.k@example.com",
        "phone": "+91 98710 44556",
        "product_service": "E-Commerce Mobile Site",
        "category": "Website",
        "rating": 2,
        "message": "Mobile browsing is sluggish on older phones. The filter dropdown freezes occasionally and needs optimization.",
        "days_ago": 12
    },
    {
        "customer_name": "Deepa Menon",
        "email": "deepa.m@example.com",
        "phone": "+91 94470 66778",
        "product_service": "Customer Onboarding Call",
        "category": "Service",
        "rating": 5,
        "message": "Wonderful onboarding session! The account manager was well-prepared, helpful, and walk-through was very easy to follow.",
        "days_ago": 12
    },
    {
        "customer_name": "Nikhil Agarwal",
        "email": "nikhil.a@example.com",
        "phone": "+91 98310 88990",
        "product_service": "Technical Support Escalation",
        "category": "Support",
        "rating": 1,
        "message": "Rude and unhelpful agent who abruptly disconnected the support ticket without resolving the database connection issue. Unacceptable.",
        "days_ago": 13
    },
    {
        "customer_name": "Shalini Sen",
        "email": "shalini.s@example.com",
        "phone": "+91 98740 12398",
        "product_service": "Loyalty Rewards Club",
        "category": "Other",
        "rating": 4,
        "message": "Reward redemption was quick and seamless. Points system offers good value on frequent purchases.",
        "days_ago": 14
    },
    {
        "customer_name": "Gaurav Bansal",
        "email": "gaurav.b@example.com",
        "phone": "+91 98180 55443",
        "product_service": "Front Desk Reception",
        "category": "Staff",
        "rating": 3,
        "message": "Reception staff was okay. They took a few minutes to locate my appointment booking but polite overall.",
        "days_ago": 14
    }
]

def seed():
    """Populate database with sample feedback records."""
    init_db()
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()

    # Clear existing feedback to ensure clean seed
    cursor.execute("DELETE FROM feedback;")
    conn.commit()

    now = datetime.now()
    inserted_count = 0

    for item in SAMPLE_FEEDBACKS:
        created_dt = now - timedelta(days=item['days_ago'], hours=item['days_ago'] * 2, minutes=item['days_ago'] * 7)
        created_str = created_dt.strftime('%Y-%m-%d %H:%M:%S')

        sentiment_res = analyze_sentiment(item['message'], item['rating'])
        sentiment = sentiment_res['sentiment']
        sentiment_score = sentiment_res['score']

        cursor.execute(
            """
            INSERT INTO feedback 
            (customer_name, email, phone, product_service, category, rating, message, sentiment, sentiment_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item['customer_name'],
                item['email'],
                item['phone'],
                item['product_service'],
                item['category'],
                item['rating'],
                item['message'],
                sentiment,
                sentiment_score,
                created_str
            )
        )
        inserted_count += 1

    conn.commit()
    conn.close()
    print(f"[SUCCESS] Seeded {inserted_count} sample feedback entries across various categories and ratings!")

if __name__ == '__main__':
    seed()
