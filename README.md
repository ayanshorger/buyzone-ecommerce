<img width="948" height="375" alt="Screenshot 2026-11-14 094231" src="https://github.com/user-attachments/assets/98e12884-9e2e-4732-a4ad-76a41496649b" />
<img width="951" height="377" alt="Screenshot 2026-11-14 094217" src="https://github.com/user-attachments/assets/e59440d1-8132-4d6d-ab38-ef25553a4758" />
<img width="948" height="401" alt="Screenshot 2026-11-14 094135" src="https://github.com/user-attachments/assets/0f10577e-3350-4628-8c12-ed0ae10a9e34" />
<img width="949" height="359" alt="Screenshot 2026-11-14 094118" src="https://github.com/user-attachments/assets/94ec0cb2-2eff-4413-b8be-54c42753e14f" />
# Buyzone - E-Commerce Web Application 

A complete, production-grade, end-to-end e-commerce web application built using **Python, Django, SQLite, HTML5, CSS3, and JavaScript**. 

Designed to provide the premier shopping experience of **Amazon** and **Flipkart**, Buyzone includes dynamic catalog browsing, real-time multi-criteria filtering, persistent carts, promo code discounts, multi-step checkout with simulated payments, order lifecycle tracking with visual timelines, customer product reviews, and full administration capabilities.

---

## 🌟 Key Features

### 1. Inspired UI/UX
- **Top Navigation Bar**: Brand logo, delivery location PIN code modal, global keyword search bar with department category selector, account dropdown, wishlist link with badge counter, and shopping cart with live item badge.
- **Departments Sub-Ribbon**: Fast access to *All Products*, *Electronics*, *Mobiles & Tech*, *Fashion*, *Home & Living*, *Appliances*, and *Deals of the Day*.
- **Interactive Hero Carousel**: Auto-rotating promotional banners with direct call-to-actions.
- **Deals of the Day**: Live real-time ticking flash sale countdown timer with discount percentage badges.
- **Department Showcases**: Curated rails for bestsellers, trending gadgets, and premium fashion.

### 2. Product Catalog & Filtering (PLP)
- **Multi-Faceted Sidebar Filters**:
  - Category hierarchy & subcategories.
  - Price range min/max filter.
  - Brand multi-select checkboxes.
  - Minimum customer rating filter (4★ & above, 3★ & above).
  - Discount threshold filters (10%+, 25%+, 40%+).
  - "In Stock Only" toggle.
- **Sorting Options**: Featured, Price: Low to High, Price: High to Low, Average Customer Rating, and Newest Arrivals.
- **Responsive Grid & Pagination**: Product cards with rating pills, original MRP strike-through, selling price, and savings badge.

### 3. Product Detail Page (PDP)
- **Interactive Image Gallery**: Thumbnail switcher and mouse hover zoom effect.
- **Pricing & Savings Block**: Detailed breakdown of MRP, selling price, and net customer savings.
- **Special Offers & Discounts**: Bank discount highlights and EMI promotions.
- **Delivery PIN Code Estimator**: Interactive Indian PIN code delivery calculator providing accurate delivery dates.
- **Key Highlights & Technical Specifications**: Structured bullet points and detailed technical specs table.
- **Customer Reviews & Ratings**:
  - Star rating breakdown distribution bar chart (5★ to 1★).
  - Verified buyer review badges.
  - Interactive modal for submitting new reviews with star rating picker.
- **Similar / Related Products**: Recommendations from the same department.

### 4. Shopping Cart & Wishlist
- Persists in SQLite database for authenticated users and in session for guest visitors.
- Quantity adjustment stepper (`+` and `-`) with real-time total updates.
- **Promo Coupon System**: Validates promo codes with minimum purchase checks (e.g., `BUYZONE10`, `WELCOME50`, `SUPERDEAL`).
- Delivery charge logic: **FREE Delivery** on orders of ₹499 and above.
- **Wishlist**: Save favorite items with 1-click "Move to Cart".

### 5. Multi-Step Checkout & Simulated Payments
- **Step 1: Delivery Address**:
  - Select from saved addresses or add a new delivery address inline.
- **Step 2: Order Items Summary**:
  - Instant review of products being purchased.
- **Step 3: Payment Options**:
  - **UPI / QR Code**: Interactive dynamic QR code simulation for Google Pay, PhonePe, and Paytm, or UPI ID entry.
  - **Credit / Debit Card**: Simulated card processor with cardholder, number, expiry, and CVV.
  - **Net Banking**: Bank selector dropdown.
  - **Cash on Delivery (COD)**: Doorstep cash/UPI option.
- **Inventory Stock Management**: Automatic stock decrement upon order placement.
- **Order Confirmation**: Clean confirmation screen with unique order tracking number (`BZ-XXXXXX`).

### 6. Order History & Live Tracking
- **My Orders Dashboard**: Overview of all previous purchases with thumbnail cards and status tags.
- **Order Tracking Stepper**: Visual 5-step status timeline (`Ordered` -> `Confirmed` -> `Shipped` -> `Out for Delivery` -> `Delivered`).
- **Shipment Activity Log**: Chronological notes and updates for package progress.
- **Order Cancellation**: 1-click cancellation for unfulfilled orders with automatic inventory restocking.
- **Tax Invoice**: Clean printable / PDF-ready tax invoice with GSTIN and itemized receipt.

### 7. User Authentication & Profile
- Registration with first/last name, username, email, phone, and password validation.
- Login with session persistence and "next" redirect support.
- Address Book: Manage multiple delivery addresses (Home vs Work) with default address toggle.
- Profile dashboard displaying personal information and recent orders.

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.10+
- Django 5+ or 6+

### 2. Navigate to Project Directory
```powershell
cd C:\Users\ayans\.gemini\antigravity\scratch\buyzone
```

### 3. Run Database Seeder (Already Executed)
The database already has categories, 20+ realistic products with high-resolution imagery, coupons, and demo accounts:
```powershell
python manage.py seed_buyzone
```

### 4. Start the Development Server
```powershell
python manage.py runserver 127.0.0.1:8000
```

Open your browser and visit: **http://127.0.0.1:8000**

---

## 🔑 Pre-Configured Demo Credentials

| Role | Username | Password | Notes |
|---|---|---|---|
| **Demo Shopper** | `shopper` | `shopper123` | Pre-configured with saved delivery addresses and sample orders |
| **Super Admin** | `admin` | `admin123` | Full Django Admin access at `/admin/` |

---

## 🧪 Running Automated Tests

Run the test suite to verify catalog search, cart operations, coupons, order placement, and cancellation:
```powershell
python manage.py test
```
All 7 unit and integration tests will execute and verify end-to-end functionality.

## Devloped by Ayan Shorger
