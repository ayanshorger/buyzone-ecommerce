from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile, Address
from store.models import Category, Product, ProductImage, Review
from cart.models import Coupon
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Seeds database with realistic Buyzone categories, products, coupons, and test users'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting Buyzone database seeding...'))

        # 1. Create Superuser and Demo Shopper
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@buyzone.com',
                'first_name': 'Admin',
                'last_name': 'Buyzone',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created superuser: admin / admin123'))
        else:
            admin_user.set_password('admin123')
            admin_user.save()

        shopper_user, created = User.objects.get_or_create(
            username='shopper',
            defaults={
                'email': 'shopper@buyzone.com',
                'first_name': 'Rahul',
                'last_name': 'Sharma',
            }
        )
        if created:
            shopper_user.set_password('shopper123')
            shopper_user.save()
            self.stdout.write(self.style.SUCCESS('Created demo shopper: shopper / shopper123'))
        else:
            shopper_user.set_password('shopper123')
            shopper_user.save()

        # Reviewer Users
        reviewer_names = [
            ('priya_p', 'Priya Patel'),
            ('arjun_v', 'Arjun Verma'),
            ('neha_k', 'Neha Kapoor'),
            ('rohit_s', 'Rohit Sen'),
            ('ananya_d', 'Ananya Das'),
        ]
        reviewers = []
        for uname, full in reviewer_names:
            u, _ = User.objects.get_or_create(
                username=uname,
                defaults={'first_name': full.split()[0], 'last_name': full.split()[1], 'email': f"{uname}@example.com"}
            )
            u.set_password('demo123')
            u.save()
            reviewers.append(u)

        # 2. Add Addresses for Shopper
        Address.objects.get_or_create(
            user=shopper_user,
            full_name='Rahul Sharma',
            phone='+91 98765 43210',
            street_address='Flat 402, Green Glen Layout, Bellandur',
            landmark='Opposite Central Mall',
            city='Bengaluru',
            state='Karnataka',
            postal_code='560103',
            address_type='HOME',
            is_default=True
        )

        Address.objects.get_or_create(
            user=shopper_user,
            full_name='Rahul Sharma (Work)',
            phone='+91 98765 43210',
            street_address='Tower B, 7th Floor, RMZ Ecoworld',
            landmark='Outer Ring Road',
            city='Bengaluru',
            state='Karnataka',
            postal_code='560103',
            address_type='WORK',
            is_default=False
        )

        # 3. Coupons
        coupons_data = [
            {'code': 'BUYZONE10', 'type': 'PERCENT', 'value': Decimal('10.00'), 'min': Decimal('499.00'), 'max': Decimal('500.00')},
            {'code': 'WELCOME50', 'type': 'FIXED', 'value': Decimal('50.00'), 'min': Decimal('299.00'), 'max': None},
            {'code': 'SUPERDEAL', 'type': 'PERCENT', 'value': Decimal('20.00'), 'min': Decimal('1499.00'), 'max': Decimal('1000.00')},
            {'code': 'MEGA200', 'type': 'FIXED', 'value': Decimal('200.00'), 'min': Decimal('1999.00'), 'max': None},
        ]
        for c in coupons_data:
            Coupon.objects.update_or_create(
                code=c['code'],
                defaults={
                    'discount_type': c['type'],
                    'discount_value': c['value'],
                    'min_purchase': c['min'],
                    'max_discount': c['max'],
                    'is_active': True
                }
            )

        # 4. Categories & Subcategories
        categories_map = {
            'Electronics': {
                'icon': 'fa-laptop',
                'image_url': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&auto=format&fit=crop&q=80',
                'desc': 'Laptops, tablets, monitors, and computer accessories.',
                'subcategories': ['Laptops & PCs', 'Audio & Headphones', 'Tablets & E-Readers', 'PC Gaming']
            },
            'Mobiles & Tech': {
                'icon': 'fa-mobile-screen-button',
                'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&auto=format&fit=crop&q=80',
                'desc': 'Flagship 5G smartphones, smartwatches, and chargers.',
                'subcategories': ['Flagship Smartphones', 'Budget Phones', 'Smartwatches', 'Mobile Accessories']
            },
            'Fashion & Apparel': {
                'icon': 'fa-shirt',
                'image_url': 'https://images.unsplash.com/photo-1445205170230-053b83016050?w=800&auto=format&fit=crop&q=80',
                'desc': 'Trending fashion, sneakers, casual wear, and luxury timepieces.',
                'subcategories': ["Men's Fashion", "Women's Fashion", 'Sneakers & Shoes', 'Watches & Bags']
            },
            'Home & Living': {
                'icon': 'fa-couch',
                'image_url': 'https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop&q=80',
                'desc': 'Furniture, ergonomic desk setups, cookware, and cozy home decor.',
                'subcategories': ['Living Room & Decor', 'Cookware & Dining', 'Lighting & Lamps']
            },
            'Appliances & TV': {
                'icon': 'fa-tv',
                'image_url': 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=800&auto=format&fit=crop&q=80',
                'desc': 'Smart 4K televisions, smart espresso machines, and air purifiers.',
                'subcategories': ['Smart 4K TVs', 'Kitchen Appliances', 'Smart Home Gadgets']
            },
            'Beauty & Wellness': {
                'icon': 'fa-spray-can-sparkles',
                'image_url': 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800&auto=format&fit=crop&q=80',
                'desc': 'Skin care essentials, luxury perfumes, and personal grooming.',
                'subcategories': ['Grooming & Shaving', 'Fragrances & Perfumes', 'Skin & Hair Care']
            }
        }

        cat_objs = {}
        for order_idx, (cat_name, cat_data) in enumerate(categories_map.items()):
            parent_cat, _ = Category.objects.update_or_create(
                name=cat_name,
                defaults={
                    'icon': cat_data['icon'],
                    'image_url': cat_data['image_url'],
                    'description': cat_data['desc'],
                    'is_featured': True,
                    'order': order_idx
                }
            )
            cat_objs[cat_name] = parent_cat

            for sub_name in cat_data['subcategories']:
                sub_cat, _ = Category.objects.update_or_create(
                    name=sub_name,
                    defaults={
                        'parent': parent_cat,
                        'icon': cat_data['icon'],
                        'image_url': cat_data['image_url'],
                        'description': f"{sub_name} in {cat_name}",
                        'is_featured': False,
                        'order': 1
                    }
                )
                cat_objs[sub_name] = sub_cat

        # 5. Realistic Products
        products_data = [
            # Mobiles & Tech
            {
                'title': 'Apple iPhone 15 Pro (128 GB, Natural Titanium)',
                'brand': 'Apple',
                'category': 'Flagship Smartphones',
                'sku': 'BZ-APL-IP15P-NAT',
                'mrp': Decimal('134900.00'),
                'selling': Decimal('119900.00'),
                'stock': 42,
                'is_featured': True,
                'is_deal': True,
                'is_bestseller': True,
                'image': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800&auto=format&fit=crop&q=80',
                'gallery': [
                    'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800&auto=format&fit=crop&q=80',
                    'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&auto=format&fit=crop&q=80',
                ],
                'short_desc': 'Aerospace-grade titanium design with A17 Pro chip, 48MP main camera, and USB-C speed.',
                'desc': 'iPhone 15 Pro is forged in aerospace-grade titanium, featuring the revolutionary A17 Pro chip that delivers unparalleled graphics performance for next-gen gaming. The customized Action button provides quick access to your favorite feature. With a 48MP main sensor, 3x Telephoto camera, and blazing USB 3 transfer speeds, experience mobile innovation at its pinnacle.',
                'highlights': [
                    '6.1-inch Super Retina XDR OLED display with ProMotion 120Hz',
                    'A17 Pro chip with 6-core GPU for console-level gaming',
                    '48MP Pro camera system with 4K60 ProRes spatial video capture',
                    'All-day battery life with up to 23 hours video playback',
                    'Universal USB-C port with USB 3 speeds up to 10Gbps'
                ],
                'specs': {
                    'Display': '6.1-inch Super Retina XDR OLED (2556 x 1179 px)',
                    'Processor': 'A17 Pro Bionic Chip (3nm)',
                    'RAM & Storage': '8GB RAM, 128GB NVMe',
                    'Main Camera': '48MP + 12MP Ultra-wide + 12MP Telephoto 3x',
                    'Battery': '3274 mAh with 20W Fast Charging',
                    'OS': 'iOS 17 (Upgradable)',
                    'Warranty': '1 Year Apple International Warranty'
                }
            },
            {
                'title': 'Samsung Galaxy S24 Ultra 5G (Titanium Gray, 256GB)',
                'brand': 'Samsung',
                'category': 'Flagship Smartphones',
                'sku': 'BZ-SAM-S24U-TGR',
                'mrp': Decimal('129999.00'),
                'selling': Decimal('114999.00'),
                'stock': 35,
                'is_featured': True,
                'is_deal': True,
                'is_bestseller': True,
                'image': 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=800&auto=format&fit=crop&q=80',
                'gallery': [
                    'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=800&auto=format&fit=crop&q=80',
                ],
                'short_desc': 'Galaxy AI with Circle to Search, 200MP camera, built-in S-Pen, and Snapdragon 8 Gen 3.',
                'desc': 'Meet Galaxy S24 Ultra, the ultimate form of Galaxy with a new titanium exterior and flat 6.8-inch display. Packed with Galaxy AI, easily search anything you see on screen, translate voice calls live in real-time, and format notes effortlessly. Powered by the customized Snapdragon 8 Gen 3 for Galaxy and Quad Telephoto with 100x Space Zoom.',
                'highlights': [
                    'Galaxy AI: Circle to Search, Live Call Translate, Note Assist',
                    '200MP primary sensor with Super Quad Pixel AF & 5x Optical Periscope',
                    'Built-in ultra-responsive S Pen for sketching and productivity',
                    'Snapdragon 8 Gen 3 for Galaxy with vapor chamber cooling',
                    'Corning Gorilla Armor anti-reflective scratch shield'
                ],
                'specs': {
                    'Display': '6.8-inch Dynamic AMOLED 2X, QHD+ 120Hz',
                    'Processor': 'Snapdragon 8 Gen 3 for Galaxy (4nm)',
                    'RAM & Storage': '12GB RAM, 256GB UFS 4.0',
                    'Camera': '200MP + 50MP + 12MP + 10MP with 100x Digital Zoom',
                    'Battery': '5000 mAh with 45W Super Fast Charging',
                    'Water Resistance': 'IP68 Certified'
                }
            },
            {
                'title': 'OnePlus 12 5G (Silky Black, 16GB RAM, 512GB Storage)',
                'brand': 'OnePlus',
                'category': 'Flagship Smartphones',
                'sku': 'BZ-OP-12-BLK',
                'mrp': Decimal('69999.00'),
                'selling': Decimal('64999.00'),
                'stock': 28,
                'is_featured': True,
                'is_deal': False,
                'is_bestseller': False,
                'image': 'https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800&auto=format&fit=crop&q=80',
                'gallery': [],
                'short_desc': '4th Gen Hasselblad Camera for Mobile, 5400 mAh Battery with 100W SUPERVOOC charging.',
                'desc': 'The OnePlus 12 redefines smooth performance with Snapdragon 8 Gen 3, up to 16GB LPDDR5X RAM, and the next-generation Dual Cryo-velocity VC cooling system. Enjoy stunning visuals on the 2K 120Hz ProXDR display with peak 4500 nits brightness and iconic Hasselblad imaging.',
                'highlights': [
                    'Snapdragon 8 Gen 3 processor with 16GB LPDDR5X RAM',
                    '100W Wired + 50W Wireless AIRVOOC Charging',
                    '4th Gen Hasselblad Camera System with 64MP Periscope Telephoto',
                    '2K 120Hz ProXDR Display with Dolby Vision & DisplayMate A+'
                ],
                'specs': {
                    'Display': '6.82-inch 2K ProXDR LTPO AMOLED',
                    'Processor': 'Qualcomm Snapdragon 8 Gen 3',
                    'Battery': '5400 mAh Dual-Cell',
                    'Charging': '100W SUPERVOOC (Charger in box)'
                }
            },
            {
                'title': 'Apple Watch Series 9 GPS (45mm Starlight Aluminum, Sport Band)',
                'brand': 'Apple',
                'category': 'Smartwatches',
                'sku': 'BZ-APL-W9-45ST',
                'mrp': Decimal('44900.00'),
                'selling': Decimal('38990.00'),
                'stock': 50,
                'is_featured': True,
                'is_deal': True,
                'is_bestseller': True,
                'image': 'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=800&auto=format&fit=crop&q=80',
                'gallery': [],
                'short_desc': 'Powerful S9 SiP chip, double tap gesture, bright 2000-nit display, and advanced health sensors.',
                'desc': 'Smarter. Brighter. Mightier. Apple Watch Series 9 features the custom Apple silicon S9 SiP, an intuitive magic way to interact with double tap without touching the screen, and a display twice as bright. Track workouts, heart rate, ECG, blood oxygen, and sleep stages.',
                'highlights': [
                    'Double tap gesture for easy one-handed control',
                    '2000-nit Always-On Retina display',
                    'ECG app and Blood Oxygen monitoring sensor',
                    'Crash Detection and Fall Detection with Emergency SOS'
                ],
                'specs': {
                    'Case Size': '45mm Aluminum Case',
                    'Connectivity': 'GPS, Wi-Fi 4, Bluetooth 5.3',
                    'Battery': '18 hours normal use, 36 hours low power mode',
                    'Compatibility': 'Requires iPhone Xs or later with iOS 17'
                }
            },

            # Laptops & Electronics
            {
                'title': 'Apple MacBook Air 15-inch M3 Chip (16GB Unified Memory, 512GB SSD)',
                'brand': 'Apple',
                'category': 'Laptops & PCs',
                'sku': 'BZ-APL-MBA15-M3',
                'mrp': Decimal('154900.00'),
                'selling': Decimal('139900.00'),
                'stock': 22,
                'is_featured': True,
                'is_deal': False,
                'is_bestseller': True,
                'image': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80',
                'gallery': [
                    'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=80',
                ],
                'short_desc': 'Liquid Retina display, M3 speed, up to 18 hours of battery life, and MagSafe 3 charging.',
                'desc': 'Lean, mean, M3 machine. MacBook Air with M3 delivers game-changing speed and AI capabilities in an extraordinarily thin 11.5mm aluminum enclosure. With up to 18 hours of battery life and support for up to two external displays, it is the world’s most popular laptop perfected.',
                'highlights': [
                    '15.3-inch Liquid Retina Display with 500 nits and True Tone',
                    'Apple M3 chip with 8-core CPU and 10-core GPU',
                    '16GB Unified Memory and 512GB Superfast SSD',
                    'Fanless, completely silent design',
                    'Six-speaker sound system with Spatial Audio'
                ],
                'specs': {
                    'Display': '15.3-inch Liquid Retina (2880 x 1864)',
                    'Processor': 'Apple M3 8-Core CPU',
                    'Memory': '16GB Unified Memory',
                    'Storage': '512GB PCIe SSD',
                    'Weight': '1.51 kg',
                    'OS': 'macOS Sonoma'
                }
            },
            {
                'title': 'Dell XPS 14 OLED Laptop (Intel Core Ultra 7, 32GB RAM, 1TB SSD, RTX 4050)',
                'brand': 'Dell',
                'category': 'Laptops & PCs',
                'sku': 'BZ-DELL-XPS14-U7',
                'mrp': Decimal('229990.00'),
                'selling': Decimal('199990.00'),
                'stock': 14,
                'is_featured': True,
                'is_deal': True,
                'is_bestseller': False,
                'image': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&auto=format&fit=crop&q=80',
                'gallery': [],
                'short_desc': '3.2K InfinityEdge OLED Touchscreen, CNC Machined Aluminum, dedicated NVIDIA GeForce RTX graphics.',
                'desc': 'Engineered to empower creators and executive power users. The Dell XPS 14 combines Intel Core Ultra 7 processor with dedicated NVIDIA GeForce RTX 4050 graphics and an immersive 3.2K OLED 120Hz InfinityEdge display inside an iconic minimalist chassis with seamless glass touchpad.',
                'highlights': [
                    '14.5-inch 3.2K (3200 x 2000) 120Hz OLED Touchscreen',
                    'Intel Core Ultra 7 155H with Intel AI Boost NPU',
                    'NVIDIA GeForce RTX 4050 Laptop GPU (6GB GDDR6)',
                    'Seamless glass touchpad with haptic feedback'
                ],
                'specs': {
                    'Processor': 'Intel Core Ultra 7 155H (16 Cores, 22 Threads)',
                    'Memory': '32GB LPDDR5x 7467MHz',
                    'Storage': '1TB M.2 PCIe NVMe SSD',
                    'Graphics': 'NVIDIA RTX 4050 6GB GDDR6',
                    'Weight': '1.68 kg'
                }
            },
            {
                'title': 'Sony WH-1000XM5 Wireless Noise Canceling Headphones (Silver)',
                'brand': 'Sony',
                'category': 'Audio & Headphones',
                'sku': 'BZ-SNY-WH1000XM5-SLV',
                'mrp': Decimal('34990.00'),
                'selling': Decimal('26990.00'),
                'stock': 60,
                'is_featured': True,
                'is_deal': True,
                'is_bestseller': True,
                'image': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80',
                'gallery': [
                    'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80',
                ],
                'short_desc': 'Industry-leading noise cancellation with 2 processors, 8 microphones, and 30-hour battery.',
                'desc': 'Sony’s WH-1000XM5 headphones rewrite the rules for distraction-free listening. Two processors control 8 microphones for unprecedented noise cancellation and crystal-clear call quality. With newly developed carbon fiber drivers, enjoy Hi-Res Audio and up to 30 hours of continuous wireless playback.',
                'highlights': [
                    'Auto NC Optimizer dynamically adjusts to wearing conditions and environment',
                    'Magnificent sound with newly engineered 30mm carbon driver units',
                    'Crystal clear hands-free calling with 4 beamforming microphones and AI noise reduction',
                    'Up to 30 hours battery life with quick charging (3 min charge for 3 hours playback)'
                ],
                'specs': {
                    'Driver Unit': '30mm, dome type (CCAW Voice coil)',
                    'Frequency Response': '4 Hz - 40,000 Hz',
                    'Bluetooth Version': '5.2 with LDAC, AAC, SBC',
                    'Battery Life': '30 Hours (NC ON), 40 Hours (NC OFF)'
                }
            },
            {
                'title': 'Bose QuietComfort Ultra Wireless Earbuds with Immersive Audio',
                'brand': 'Bose',
                'category': 'Audio & Headphones',
                'sku': 'BZ-BSE-QCU-BLK',
                'mrp': Decimal('29900.00'),
                'selling': Decimal('24900.00'),
                'stock': 40,
                'is_featured': False,
                'is_deal': True,
                'is_bestseller': False,
                'image': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop&q=80',
                'gallery': [],
                'short_desc': 'Spatialized audio for more natural listening, world-class noise cancellation, CustomTune technology.',
                'desc': 'Bose QuietComfort Ultra Earbuds deliver groundbreaking spatial audio that places what you hear right in front of you. CustomTune technology personalizes the noise cancellation and sound performance to fit your ears precisely.',
                'highlights': [
                    'Bose Immersive Audio pushes boundaries of spatial acoustic realism',
                    'World-class noise cancellation and Aware Mode with ActiveSense',
                    'Up to 6 hours of listening time (24 hours total with case)',
                    'Touch controls on both earbuds for volume and mode toggles'
                ],
                'specs': {
                    'Connectivity': 'Bluetooth 5.3',
                    'Water Resistance': 'IPX4 Splashproof',
                    'Charging': 'USB-C and optional Qi Wireless case'
                }
            },

            # Appliances & TV
            {
                'title': 'Sony BRAVIA XR 55-inch 4K Ultra HD Smart OLED Google TV',
                'brand': 'Sony',
                'category': 'Smart 4K TVs',
                'sku': 'BZ-SNY-A80L-55',
                'mrp': Decimal('189900.00'),
                'selling': Decimal('149990.00'),
                'stock': 18,
                'is_featured': True,
                'is_deal': False,
                'is_bestseller': True,
                'image': 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=800&auto=format&fit=crop&q=80',
                'gallery': [],
                'short_desc': 'Cognitive Processor XR, XR OLED Contrast Pro, Acoustic Surface Audio+, 120Hz for PS5 gaming.',
                'desc': 'Step into true cinematic wonder. Pure black and vibrant color are controlled by the intelligence of Cognitive Processor XR. Acoustic Surface Audio+ turns the screen itself into a multi-channel speaker for sound that matches what you see precisely.',
                'highlights': [
                    'Cognitive Processor XR understands how humans see and hear',
                    'XR OLED Contrast Pro for infinite contrast and deep cinematic blacks',
                    'Acoustic Surface Audio+ with dual subwoofers built right into the screen',
                    'HDMI 2.1 with 4K/120fps, VRR, and ALLM for next-gen consoles'
                ],
                'specs': {
                    'Screen Size': '55 Inches OLED (3840 x 2160)',
                    'Refresh Rate': '120 Hz Native',
                    'Audio Output': '50W (Dolby Atmos & DTS Digital Surround)',
                    'Smart OS': 'Google TV with Voice Search'
                }
            },
            {
                'title': 'DeLonghi Magnifica S Automatic Espresso & Cappuccino Coffee Maker',
                'brand': 'DeLonghi',
                'category': 'Kitchen Appliances',
                'sku': 'BZ-DLG-MAGS-SS',
                'mrp': Decimal('54990.00'),
                'selling': Decimal('42990.00'),
                'stock': 19,
                'is_featured': True,
                'is_deal': True,
                'is_bestseller': False,
                'image': 'https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=800&auto=format&fit=crop&q=80',
                'gallery': [],
                'short_desc': 'Integrated burr grinder, traditional milk frother, twin-shot brewing, 15-bar pump pressure.',
                'desc': 'Brew café-quality espresso, silky lattes, and rich cappuccinos from freshly ground beans at the touch of a button. Featuring a built-in steel burr grinder with 13 grind settings and manual steam wand for micro-foam art.',
                'highlights': [
                    '15-bar professional extraction pressure',
                    'Integrated silent conical burr grinder with 13 settings',
                    'Cappuccino system with adjustable steam wand',
                    'Compact removable brewing unit for effortless cleaning'
                ],
                'specs': {
                    'Water Tank Capacity': '1.8 Liters',
                    'Beans Container': '250 grams',
                    'Power': '1450 Watts',
                    'Body Material': 'Brushed Stainless Steel & Matte Black'
                }
            },
            {
                'title': 'Dyson V15 Detect Extra Cordless Vacuum Cleaner',
                'brand': 'Dyson',
                'category': 'Smart Home Gadgets',
                'sku': 'BZ-DYS-V15-EX',
                'mrp': Decimal('65900.00'),
                'selling': Decimal('56900.00'),
                'stock': 25,
                'is_featured': False,
                'is_deal': False,
                'is_bestseller': True,
                'image': 'https://images.unsplash.com/photo-1558317374-067fb5f30001?w=800&auto=format&fit=crop&q=80',
                'gallery': [],
                'short_desc': 'Laser reveals invisible microscopic dust, piezo sensor measures dirt particles, 240AW suction.',
                'desc': 'Dyson’s most powerful intelligent cordless vacuum. A precisely angled green beam reveals dust you cannot normally see on hard floors. Acoustic piezo sensor counts and measures the size of particles, automatically increasing suction when needed.',
                'highlights': [
                    'Fluffy Optic cleaner head reveals twice the invisible dust',
                    'Dyson Hyperdymium motor spins at up to 125,000rpm',
                    'Up to 60 minutes of fade-free run time',
                    'LCD screen reports real-time scientific proof of deep clean'
                ],
                'specs': {
                    'Suction Power': '240 Air Watts',
                    'Filtration': 'Whole-machine HEPA filtration traps 99.99% of particles',
                    'Bin Volume': '0.76 Liters',
                    'Weight': '3.0 kg'
                }
            },

            # Fashion & Shoes
            {
                'title': 'Nike Air Jordan 1 Retro High OG (Chicago Lost & Found, Red/White)',
                'brand': 'Nike',
                'category': 'Sneakers & Shoes',
                'sku': 'BZ-NKE-AJ1-CHI',
                'mrp': Decimal('19995.00'),
                'selling': Decimal('16995.00'),
                'stock': 30,
                'is_featured': True,
                'is_deal': True,
                'is_bestseller': True,
                'image': 'https://images.unsplash.com/photo-1552346154-21d32810aba3?w=800&auto=format&fit=crop&q=80',
                'gallery': [
                    'https://images.unsplash.com/photo-1552346154-21d32810aba3?w=800&auto=format&fit=crop&q=80',
                    'https://images.unsplash.com/photo-1607522370275-f14206abe5d3?w=800&auto=format&fit=crop&q=80'
                ],
                'short_desc': 'Iconic high-top silhouette in vintage Chicago colorway with premium distressed full-grain leather.',
                'desc': 'The timeless legend that started sneaker culture. Reimagining the classic 1985 silhouette with vintage cracked-leather accents, aged midsoles, and authentic OG Nike Air branding. An absolute must-have statement piece for any modern wardrobe.',
                'highlights': [
                    'Genuine leather upper for durability and premium hand-feel',
                    'Encapsulated Air-Sole unit provides lightweight cushioning',
                    'Solid rubber outsole with deep flex grooves for all-day traction',
                    'Includes spare set of white and black laces'
                ],
                'specs': {
                    'Colorway': 'Varsity Red / Black / Sail / Muslin',
                    'Sole Material': 'Rubber',
                    'Closure': 'Lace-Up',
                    'Origin': 'Authentic Nike Certified'
                }
            },
            {
                'title': 'Levi’s Men’s Type III Sherpa Trucker Denim Jacket (Fleece Lined)',
                'brand': "Levi's",
                'category': "Men's Fashion",
                'sku': 'BZ-LEV-SHERPA-BLU',
                'mrp': Decimal('7999.00'),
                'selling': Decimal('5499.00'),
                'stock': 45,
                'is_featured': False,
                'is_deal': False,
                'is_bestseller': True,
                'image': 'https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=800&auto=format&fit=crop&q=80',
                'gallery': [],
                'short_desc': 'Warm sherpa insulation, quilted lining in sleeves, classic copper snap buttons, 100% cotton denim.',
                'desc': 'The original jean jacket since 1967, winterized. Crafted with rugged non-stretch denim, cozy plush sherpa fleece on the collar and torso lining, and smooth quilted sleeve insulation.',
                'highlights': [
                    'Warm plush faux-sherpa lining on body and collar',
                    'Metal button snap front and button-flap chest pockets',
                    'Adjustable side waist tabs for custom fit',
                    'Machine wash cold, delicate cycle'
                ],
                'specs': {
                    'Material': '100% Cotton Outer, 100% Polyester Sherpa Lining',
                    'Fit': 'Regular Fit',
                    'Care': 'Machine Wash'
                }
            },
            {
                'title': 'Fossil Grant Chronograph Blue Dial Brown Leather Watch',
                'brand': 'Fossil',
                'category': 'Watches & Bags',
                'sku': 'BZ-FOS-GRNT-BLU',
                'mrp': Decimal('13495.00'),
                'selling': Decimal('8995.00'),
                'stock': 50,
                'is_featured': True,
                'is_deal': True,
                'is_bestseller': False,
                'image': 'https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800&auto=format&fit=crop&q=80',
                'gallery': [],
                'short_desc': 'Roman numeral indices, stopwatch chronograph subdials, 22mm genuine leather interchangeable strap.',
                'desc': 'Inspired by vintage clocks, the Grant chronograph features roman numeral markers with artistic balance. Deep ocean-blue dial paired with rich luggage-brown genuine leather.',
                'highlights': [
                    '44mm stainless steel case with mineral crystal lens',
                    'Chronograph movement with 3 stopwatch sub-eyes',
                    '50m water resistance (suitable for recreational swimming)',
                    'Interchangeable with all 22mm Fossil straps'
                ],
                'specs': {
                    'Case Diameter': '44 mm',
                    'Band Material': 'Genuine Cowhide Leather',
                    'Movement': 'Quartz Chronograph',
                    'Warranty': '2 Year International Warranty'
                }
            },
            {
                'title': 'Zara Structured Double-Breasted Wool Blend Blazer (Camel)',
                'brand': 'Zara',
                'category': "Women's Fashion",
                'sku': 'BZ-ZAR-BLZR-CAM',
                'mrp': Decimal('9990.00'),
                'selling': Decimal('6990.00'),
                'stock': 26,
                'is_featured': False,
                'is_deal': False,
                'is_bestseller': True,
                'image': 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=800&auto=format&fit=crop&q=80',
                'gallery': [],
                'short_desc': 'Tailored peak lapels, tortoiseshell buttons, padded shoulders, front flap pockets.',
                'desc': 'An enduring wardrobe essential. Structured blazer with pointed lapel collar, long sleeves with shoulder pads, front flap pockets, and front double-breasted button fastening in warm camel tan.',
                'highlights': [
                    'Premium woven wool-blend twill fabric',
                    'Structured silhouette with sharp shoulder padding',
                    'Satin inner lining for effortless layering',
                    'Dry clean recommended'
                ],
                'specs': {
                    'Outer Shell': '65% Polyester, 32% Wool, 3% Elastane',
                    'Lining': '100% Acetate',
                    'Color': 'Warm Camel Beige'
                }
            },

            # Home & Living
            {
                'title': 'Modern Ergonomic High-Back Mesh Desk Chair with Lumbar Support',
                'brand': 'ErgoZone',
                'category': 'Living Room & Decor',
                'sku': 'BZ-ERG-CHR-PRO',
                'mrp': Decimal('19999.00'),
                'selling': Decimal('12499.00'),
                'stock': 38,
                'is_featured': True,
                'is_deal': True,
                'is_bestseller': True,
                'image': 'https://images.unsplash.com/photo-1580481077195-c3a821a58875?w=800&auto=format&fit=crop&q=80',
                'gallery': [],
                'short_desc': '3D adjustable armrests, dynamic adaptive lumbar support, breathable German mesh back, tilt lock.',
                'desc': 'Upgrade your work-from-home setup with spine-aligning comfort. Engineered with breathable mesh, 135-degree synchro-tilt mechanism, 3D adjustable armrests, and certified Class 4 gas lift for all-day posture support.',
                'highlights': [
                    'Dynamic adaptive lumbar pillow conforms to natural spinal curve',
                    'Heavy-duty nylon base rated up to 150 kg weight capacity',
                    '3D adjustable armrests (Height, Angle, Fore-Aft)',
                    'Multi-lock recline up to 135 degrees for relaxation'
                ],
                'specs': {
                    'Frame Material': 'Reinforced Nylon & Aluminum',
                    'Seat Material': 'High-density molded foam + Mesh',
                    'Weight Capacity': '150 kg',
                    'Warranty': '3 Years Manufacturer Warranty'
                }
            },
            {
                'title': 'Staub Cast Iron Round Cocotte Dutch Oven (4-Quart, Cherry Red)',
                'brand': 'Staub',
                'category': 'Cookware & Dining',
                'sku': 'BZ-STB-DO4-RED',
                'mrp': Decimal('24990.00'),
                'selling': Decimal('18990.00'),
                'stock': 20,
                'is_featured': False,
                'is_deal': False,
                'is_bestseller': False,
                'image': 'https://images.unsplash.com/photo-1584990347449-39b03947477d?w=800&auto=format&fit=crop&q=80',
                'gallery': [],
                'short_desc': 'Enameled cast iron made in France, spikes on flat lid for continuous self-basting, oven safe to 500°F.',
                'desc': 'A culinary benchmark cherished by world-renowned chefs. Staub enameled cast iron cocottes retain heat evenly and continuously baste dishes with tiny lid moisture spikes for tender stews, braises, and artisan sourdough.',
                'highlights': [
                    'Rough black matte enamel interior ensures exceptional browning',
                    'Heavy, tight-fitting flat lid with spikes locks in moisture',
                    'Compatible with gas, induction, electric, and oven up to 500°F',
                    'Made in France with lifetime warranty'
                ],
                'specs': {
                    'Capacity': '3.8 Liters (4-Quart)',
                    'Diameter': '24 cm',
                    'Material': 'Enameled Cast Iron',
                    'Origin': 'France'
                }
            },
            {
                'title': 'Philips Hue White & Color Ambiance Smart LED Starter Kit',
                'brand': 'Philips',
                'category': 'Lighting & Lamps',
                'sku': 'BZ-PHL-HUE-KIT',
                'mrp': Decimal('14999.00'),
                'selling': Decimal('11499.00'),
                'stock': 40,
                'is_featured': False,
                'is_deal': True,
                'is_bestseller': False,
                'image': 'https://images.unsplash.com/photo-1550985543-f47f38aeee65?w=800&auto=format&fit=crop&q=80',
                'gallery': [],
                'short_desc': '16 million colors, warm-to-cool white light, Hue Bridge included, works with Alexa, Apple & Google.',
                'desc': 'Transform your home lighting with the Philips Hue Starter Kit. Set the mood with 16 million colors, sync lights to music and movies, and automate daily schedules effortlessly through voice or smart home apps.',
                'highlights': [
                    'Includes 3 E27 color smart bulbs and Hue Bridge hub',
                    'Sync with movies, gaming, and Spotify playlists',
                    'Works with Apple HomeKit, Amazon Alexa, Google Assistant'
                ],
                'specs': {
                    'Wattage': '9W (60W equivalent)',
                    'Brightness': '800 Lumens per bulb',
                    'Socket': 'E27 Screw Base'
                }
            },

            # Beauty & Wellness
            {
                'title': 'Dior Sauvage Eau de Parfum for Men (100 ml Vaporisateur)',
                'brand': 'Dior',
                'category': 'Fragrances & Perfumes',
                'sku': 'BZ-DIR-SVG-100',
                'mrp': Decimal('13500.00'),
                'selling': Decimal('11800.00'),
                'stock': 32,
                'is_featured': True,
                'is_deal': False,
                'is_bestseller': True,
                'image': 'https://images.unsplash.com/photo-1594035910387-fea47794261f?w=800&auto=format&fit=crop&q=80',
                'gallery': [],
                'short_desc': 'Sensual and mysterious with Calabrian bergamot, Papua New Guinean vanilla absolute, and amber.',
                'desc': 'An iconic fragrance composition inspired by wide-open spaces under a blue sky. Intense and smooth, blending juicy freshness of Calabrian bergamot with smoky accents of vanilla extract for a virile, noble signature trail.',
                'highlights': [
                    'Top notes: Reggio di Calabria Bergamot',
                    'Heart notes: Sichuan Pepper, Lavender, Star Anise',
                    'Base notes: Papua New Guinean Vanilla, Ambroxan',
                    'Long-lasting sillage (8-12 hours wear)'
                ],
                'specs': {
                    'Volume': '100 ml / 3.4 oz',
                    'Concentration': 'Eau de Parfum (EDP)',
                    'Origin': 'Made in France'
                }
            },
            {
                'title': 'Philips Norelco Series 9000 Prestige Wet & Dry Electric Shaver',
                'brand': 'Philips',
                'category': 'Grooming & Shaving',
                'sku': 'BZ-PHL-SH9-PRS',
                'mrp': Decimal('27995.00'),
                'selling': Decimal('21995.00'),
                'stock': 24,
                'is_featured': False,
                'is_deal': True,
                'is_bestseller': False,
                'image': 'https://images.unsplash.com/photo-1621607512214-68297480165e?w=800&auto=format&fit=crop&q=80',
                'gallery': [],
                'short_desc': 'NanoTech precision blades, BeardAdapt sensor checks hair density 500 times/sec, Qi Wireless charging.',
                'desc': 'Experience our closest electric shave that glides exceptionally smoothly over your skin. Extra-strong NanoTech precision blades and multidirectional contouring heads adapt seamlessly to every angle of your jaw.',
                'highlights': [
                    'NanoTech dual precision blades reinforced with nano particles',
                    'BeardAdapt sensor automatically adjusts power to hair thickness',
                    'Qi wireless charging pad included',
                    '100% waterproof for comfortable dry or wet shaving in the shower'
                ],
                'specs': {
                    'Battery': 'Li-ion with 60 minutes cordless shave time',
                    'Display': 'Digital numeric battery percentage indicator',
                    'Warranty': '2 Year Worldwide Guarantee'
                }
            }
        ]

        reviews_samples = [
            ("Spectacular quality and super fast delivery!", 5, "I ordered this during the festive deal and it arrived in 2 days. The packaging was pristine and product performance blew away my expectations. Buyzone is awesome!"),
            ("Value for money purchase", 4, "Really solid build and matches the description perfectly. Minus one star only because the delivery agent took an extra hour to locate my landmark, but the item itself is 10/10."),
            ("Genuine product, very happy!", 5, "100% authentic product verified on the official website. The discounts here beat other shopping sites."),
            ("Great product and finish", 5, "The design is top-notch. Using it everyday without any hassle. Highly recommended for anyone on the fence."),
            ("Decent product for the price point", 4, "Works exactly as expected. Battery life and build quality are satisfactory. Good deal overall.")
        ]

        # Seed products
        for p_data in products_data:
            cat_obj = cat_objs.get(p_data['category']) or cat_objs.get('Electronics')

            prod, created = Product.objects.update_or_create(
                sku=p_data['sku'],
                defaults={
                    'title': p_data['title'],
                    'brand': p_data['brand'],
                    'category': cat_obj,
                    'mrp_price': p_data['mrp'],
                    'selling_price': p_data['selling'],
                    'stock': p_data['stock'],
                    'short_description': p_data['short_desc'],
                    'description': p_data['desc'],
                    'highlights': p_data['highlights'],
                    'specifications': p_data['specs'],
                    'is_featured': p_data['is_featured'],
                    'is_deal_of_day': p_data['is_deal'],
                    'is_bestseller': p_data['is_bestseller'],
                    'main_image_url': p_data['image'],
                    'rating': 4.7,
                    'num_reviews': 0
                }
            )

            # Gallery images
            for idx, g_url in enumerate(p_data.get('gallery', [])):
                ProductImage.objects.get_or_create(
                    product=prod,
                    image_url=g_url,
                    defaults={'order': idx}
                )

            # Seed 2-4 reviews for each product
            Review.objects.filter(product=prod).delete()
            chosen_reviewers = random.sample(reviewers, random.randint(2, len(reviewers)))
            for rev_user in chosen_reviewers:
                sample_headline, sample_rating, sample_comment = random.choice(reviews_samples)
                Review.objects.create(
                    product=prod,
                    user=rev_user,
                    rating=sample_rating,
                    headline=sample_headline,
                    comment=sample_comment,
                    is_verified_purchase=True
                )
            prod.update_rating()

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(products_data)} products, categories, coupons, and users!'))
