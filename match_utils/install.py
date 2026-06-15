# Copyright (c) 2026, match systems and contributors
# For license information, please see license.txt

import os

import frappe
from frappe.modules import get_module_path

HOME_PAGE_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Match Systems - حلول تخطيط موارد المؤسسات</title>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Cairo', sans-serif;
      background: linear-gradient(135deg, #e8f5e9 0%, #e1f5fe 50%, #f3e5f5 100%);
      margin: 0;
      padding: 0;
      color: #333;
      line-height: 1.6;
      min-height: 100vh;
      position: relative;
      overflow-x: hidden;
    }

    /* Animated Background */
    body::before {
      content: '';
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background:
        radial-gradient(circle at 20% 50%, rgba(139, 195, 74, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(3, 169, 244, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 40% 20%, rgba(156, 39, 176, 0.05) 0%, transparent 50%);
      animation: backgroundShift 15s ease infinite;
      z-index: -1;
    }

    @keyframes backgroundShift {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.8; transform: scale(1.1); }
    }

    /* Floating Shapes Animation */
    .floating-shape {
      position: fixed;
      border-radius: 50%;
      opacity: 0.1;
      animation: float 20s infinite ease-in-out;
      z-index: 0;
    }

    .shape1 {
      width: 300px;
      height: 300px;
      background: linear-gradient(135deg, #8bc34a, #03a9f4);
      top: 10%;
      left: 5%;
      animation-delay: 0s;
    }

    .shape2 {
      width: 200px;
      height: 200px;
      background: linear-gradient(135deg, #03a9f4, #9c27b0);
      bottom: 15%;
      right: 10%;
      animation-delay: 7s;
    }

    .shape3 {
      width: 150px;
      height: 150px;
      background: linear-gradient(135deg, #9c27b0, #8bc34a);
      top: 60%;
      left: 15%;
      animation-delay: 3s;
    }

    @keyframes float {
      0%, 100% { transform: translate(0, 0) rotate(0deg); }
      25% { transform: translate(30px, -30px) rotate(90deg); }
      50% { transform: translate(-20px, 20px) rotate(180deg); }
      75% { transform: translate(40px, 10px) rotate(270deg); }
    }

    /* Modern Header */
    header {
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(20px);
      color: #2c3e50;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px 40px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
      position: sticky;
      top: 0;
      z-index: 1000;
      border-bottom: 3px solid transparent;
      border-image: linear-gradient(90deg, #8bc34a, #03a9f4, #9c27b0) 1;
      animation: slideDown 0.8s ease;
    }

    @keyframes slideDown {
      from {
        transform: translateY(-100%);
        opacity: 0;
      }
      to {
        transform: translateY(0);
        opacity: 1;
      }
    }

    header img {
      height: 80px;
      animation: logoFloat 3s ease-in-out infinite;
      filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
    }

    @keyframes logoFloat {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-10px); }
    }

    header h1 {
      font-size: 2rem;
      font-weight: 700;
      background: linear-gradient(135deg, #8bc34a, #03a9f4, #9c27b0);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin: 0;
      animation: fadeIn 1s ease 0.3s both;
    }

    /* Hero Section */
    .hero {
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.85));
      backdrop-filter: blur(10px);
      padding: 100px 40px;
      margin: 40px;
      border-radius: 30px;
      text-align: center;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
      position: relative;
      overflow: hidden;
      border: 2px solid rgba(255, 255, 255, 0.8);
      z-index: 1;
    }

    .hero::before {
      content: '';
      position: absolute;
      top: -50%;
      right: -50%;
      width: 200%;
      height: 200%;
      background: conic-gradient(from 0deg, transparent, rgba(139, 195, 74, 0.1), transparent, rgba(3, 169, 244, 0.1), transparent);
      animation: rotate 20s linear infinite;
    }

    @keyframes rotate {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }

    .hero-content {
      position: relative;
      z-index: 2;
    }

    .company-badge {
      display: inline-block;
      background: linear-gradient(135deg, #8bc34a, #03a9f4);
      color: white;
      padding: 10px 30px;
      border-radius: 50px;
      font-weight: 600;
      font-size: 1.1rem;
      margin-bottom: 30px;
      box-shadow: 0 8px 25px rgba(139, 195, 74, 0.3);
      animation: bounceIn 1s ease;
    }

    @keyframes bounceIn {
      0% { transform: scale(0); opacity: 0; }
      50% { transform: scale(1.1); }
      100% { transform: scale(1); opacity: 1; }
    }

    .hero h2 {
      font-size: 3.5rem;
      background: linear-gradient(135deg, #8bc34a, #03a9f4, #9c27b0);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      font-weight: 700;
      margin-bottom: 25px;
      animation: fadeInUp 1s ease 0.2s both;
    }

    .hero p {
      font-size: 1.4rem;
      color: #555;
      margin-bottom: 35px;
      max-width: 900px;
      margin-left: auto;
      margin-right: auto;
      line-height: 2;
      animation: fadeInUp 1s ease 0.4s both;
    }

    .hero-buttons {
      display: flex;
      gap: 20px;
      justify-content: center;
      flex-wrap: wrap;
      animation: fadeInUp 1s ease 0.6s both;
    }

    .btn-primary, .btn-secondary {
      border: none;
      padding: 18px 40px;
      color: white;
      font-weight: bold;
      border-radius: 50px;
      text-decoration: none;
      display: inline-block;
      font-size: 1.1rem;
      transition: all 0.4s ease;
      position: relative;
      overflow: hidden;
    }

    .btn-primary {
      background: linear-gradient(135deg, #8bc34a, #03a9f4);
      box-shadow: 0 10px 30px rgba(139, 195, 74, 0.4);
    }

    .btn-secondary {
      background: linear-gradient(135deg, #03a9f4, #9c27b0);
      box-shadow: 0 10px 30px rgba(3, 169, 244, 0.4);
    }

    .btn-primary:hover, .btn-secondary:hover {
      transform: translateY(-5px) scale(1.05);
      box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
    }

    .btn-primary::before, .btn-secondary::before {
      content: '';
      position: absolute;
      top: 50%;
      left: 50%;
      width: 0;
      height: 0;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.3);
      transform: translate(-50%, -50%);
      transition: width 0.6s, height 0.6s;
    }

    .btn-primary:hover::before, .btn-secondary:hover::before {
      width: 300px;
      height: 300px;
    }

    @keyframes fadeInUp {
      from {
        opacity: 0;
        transform: translateY(40px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    /* Features Section */
    .features {
      margin: 80px 40px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 40px;
      position: relative;
      z-index: 1;
    }

    .feature-box {
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
      padding: 45px 35px;
      border-radius: 25px;
      text-align: center;
      box-shadow: 0 15px 40px rgba(0, 0, 0, 0.1);
      transition: all 0.5s ease;
      position: relative;
      overflow: hidden;
      border: 2px solid transparent;
      opacity: 0;
      transform: translateY(50px);
      animation: fadeInUp 0.8s ease forwards;
    }

    .feature-box:nth-child(1) {
      animation-delay: 0.1s;
      border-image: linear-gradient(135deg, #8bc34a, #66bb6a) 1;
    }
    .feature-box:nth-child(2) {
      animation-delay: 0.2s;
      border-image: linear-gradient(135deg, #03a9f4, #0288d1) 1;
    }
    .feature-box:nth-child(3) {
      animation-delay: 0.3s;
      border-image: linear-gradient(135deg, #9c27b0, #7b1fa2) 1;
    }
    .feature-box:nth-child(4) {
      animation-delay: 0.4s;
      border-image: linear-gradient(135deg, #ff9800, #f57c00) 1;
    }

    .feature-box::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
      transition: left 0.7s;
    }

    .feature-box:hover::before {
      left: 100%;
    }

    .feature-box:hover {
      transform: translateY(-15px) scale(1.03);
      box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
    }

    .feature-icon {
      width: 80px;
      height: 80px;
      margin: 0 auto 25px;
      border-radius: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2.5rem;
      transition: all 0.4s ease;
      animation: pulse 2s ease infinite;
    }

    @keyframes pulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.05); }
    }

    .feature-box:nth-child(1) .feature-icon {
      background: linear-gradient(135deg, #8bc34a, #66bb6a);
      box-shadow: 0 10px 30px rgba(139, 195, 74, 0.4);
    }

    .feature-box:nth-child(2) .feature-icon {
      background: linear-gradient(135deg, #03a9f4, #0288d1);
      box-shadow: 0 10px 30px rgba(3, 169, 244, 0.4);
    }

    .feature-box:nth-child(3) .feature-icon {
      background: linear-gradient(135deg, #9c27b0, #7b1fa2);
      box-shadow: 0 10px 30px rgba(156, 39, 176, 0.4);
    }

    .feature-box:nth-child(4) .feature-icon {
      background: linear-gradient(135deg, #ff9800, #f57c00);
      box-shadow: 0 10px 30px rgba(255, 152, 0, 0.4);
    }

    .feature-box:hover .feature-icon {
      transform: rotateY(360deg);
    }

    .feature-box h4 {
      font-weight: 600;
      color: #2c3e50;
      font-size: 1.5rem;
      margin-bottom: 20px;
    }

    .feature-box p {
      color: #666;
      font-size: 1.05rem;
      line-height: 1.8;
    }

    /* Contact Section */
    .contact {
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.85));
      backdrop-filter: blur(10px);
      padding: 80px 40px;
      text-align: center;
      margin: 80px 40px 0;
      border-radius: 30px;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
      position: relative;
      z-index: 1;
      border: 2px solid rgba(255, 255, 255, 0.8);
    }

    .contact h3 {
      font-size: 2.5rem;
      background: linear-gradient(135deg, #8bc34a, #03a9f4, #9c27b0);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 50px;
      font-weight: 700;
    }

    .contact-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 35px;
      margin-top: 50px;
      max-width: 1000px;
      margin-left: auto;
      margin-right: auto;
    }

    .contact-item {
      background: rgba(255, 255, 255, 0.9);
      padding: 35px;
      border-radius: 20px;
      box-shadow: 0 10px 35px rgba(0, 0, 0, 0.1);
      transition: all 0.4s ease;
      border: 2px solid transparent;
      position: relative;
      overflow: hidden;
    }

    .contact-item:nth-child(1) {
      border-image: linear-gradient(135deg, #8bc34a, #66bb6a) 1;
    }

    .contact-item:nth-child(2) {
      border-image: linear-gradient(135deg, #03a9f4, #0288d1) 1;
    }

    .contact-item:nth-child(3) {
      border-image: linear-gradient(135deg, #9c27b0, #7b1fa2) 1;
    }

    .contact-item::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.3), transparent);
      transform: rotate(45deg);
      transition: all 0.6s;
    }

    .contact-item:hover::before {
      top: 100%;
      left: 100%;
    }

    .contact-item:hover {
      transform: translateY(-10px) scale(1.03);
      box-shadow: 0 20px 45px rgba(0, 0, 0, 0.15);
    }

    .contact-item h4 {
      font-size: 1.3rem;
      margin-bottom: 20px;
      font-weight: 600;
    }

    .contact-item:nth-child(1) h4 {
      color: #8bc34a;
    }

    .contact-item:nth-child(2) h4 {
      color: #03a9f4;
    }

    .contact-item:nth-child(3) h4 {
      color: #9c27b0;
    }

    .contact p {
      font-size: 1.1rem;
      color: #555;
      margin: 10px 0;
      line-height: 1.8;
    }

    .contact a {
      color: #03a9f4 !important;
      text-decoration: none !important;
      font-weight: 600;
      transition: all 0.3s ease;
      position: relative;
    }

    .contact a::after {
      content: '';
      position: absolute;
      bottom: -2px;
      left: 0;
      width: 0;
      height: 2px;
      background: linear-gradient(90deg, #8bc34a, #03a9f4);
      transition: width 0.3s ease;
    }

    .contact a:hover::after {
      width: 100%;
    }

    .contact a:hover {
      color: #8bc34a !important;
      transform: translateX(-3px);
    }

    .availability-badge {
      display: inline-block;
      background: linear-gradient(135deg, #4caf50, #8bc34a);
      color: white;
      padding: 12px 30px;
      border-radius: 50px;
      font-weight: 600;
      font-size: 1.2rem;
      margin-top: 30px;
      box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
      animation: pulse 2s ease infinite;
    }

    /* Footer */
    footer {
      background: linear-gradient(135deg, #2c3e50, #34495e);
      color: white;
      text-align: center;
      padding: 40px 30px;
      font-size: 1.05rem;
      margin-top: 60px;
      position: relative;
      z-index: 1;
    }

    footer::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, #8bc34a, #03a9f4, #9c27b0);
    }

    /* Responsive Design */
    @media (max-width: 768px) {
      header {
        padding: 15px 20px;
        flex-direction: column;
        gap: 15px;
      }

      header h1 {
        font-size: 1.5rem;
      }

      header img {
        height: 60px;
      }

      .hero {
        margin: 20px;
        padding: 60px 30px;
      }

      .hero h2 {
        font-size: 2.2rem;
      }

      .hero p {
        font-size: 1.1rem;
      }

      .features {
        margin: 40px 20px;
        gap: 30px;
      }

      .contact {
        margin: 40px 20px 0;
        padding: 50px 25px;
      }

      .contact h3 {
        font-size: 2rem;
      }

      .hero-buttons {
        flex-direction: column;
        align-items: center;
      }
    }

    @media (max-width: 480px) {
      .hero h2 {
        font-size: 1.8rem;
      }

      .company-badge {
        font-size: 0.95rem;
        padding: 8px 20px;
      }

      .feature-box {
        padding: 30px 20px;
      }

      .contact-item {
        padding: 25px 20px;
      }
    }
  </style>
</head>
<body>
  <!-- Floating Background Shapes -->
  <div class="floating-shape shape1"></div>
  <div class="floating-shape shape2"></div>
  <div class="floating-shape shape3"></div>

  <header>
    <img src="/files/match_system_logo.png" alt="Match Systems Logo">
    <h1>Match Systems - حلول الأعمال المتكاملة</h1>
  </header>

  <section class="hero">
    <div class="hero-content">
      <div class="company-badge">🚀 Company Development - Match Systems 2025 Business One</div>
      <h2>حلول تخطيط موارد المؤسسات الذكية</h2>
      <p>
        نقدم أنظمة ERP متطورة لإدارة جميع عمليات مؤسستك بكفاءة وفعالية. من إدارة المخزون والمبيعات إلى الموارد البشرية والمحاسبة، نوفر لك حلولاً شاملة ومتكاملة تساعدك على تحقيق التميز والنمو المستدام في عالم الأعمال الرقمي.
      </p>
      <div class="hero-buttons">
        <a href="/login" class="btn-primary">تسجيل الدخول للنظام</a>
        <a href="https://matchprosys.com/" target="_blank" class="btn-secondary">زيارة موقعنا الإلكتروني</a>
      </div>
    </div>
  </section>

  <section class="features">
    <div class="feature-box">
      <div class="feature-icon">💼</div>
      <h4>إدارة متكاملة للأعمال</h4>
      <p>نظام شامل لإدارة جميع عمليات مؤسستك من المشتريات والمبيعات إلى المحاسبة والموارد البشرية في منصة واحدة موحدة.</p>
    </div>
    <div class="feature-box">
      <div class="feature-icon">📊</div>
      <h4>تقارير تحليلية ذكية</h4>
      <p>احصل على رؤى عميقة وتقارير تفصيلية في الوقت الفعلي لاتخاذ قرارات استراتيجية مبنية على البيانات الدقيقة.</p>
    </div>
    <div class="feature-box">
      <div class="feature-icon">🔒</div>
      <h4>أمان وحماية عالية</h4>
      <p>حماية متقدمة لبياناتك مع أنظمة تشفير قوية وصلاحيات مرنة لضمان سرية وأمان معلومات مؤسستك الحساسة.</p>
    </div>
    <div class="feature-box">
      <div class="feature-icon">☁️</div>
      <h4>سحابي ومرن</h4>
      <p>وصول آمن من أي مكان وفي أي وقت عبر السحابة مع دعم جميع الأجهزة وواجهات استخدام سهلة وبديهية.</p>
    </div>
  </section>

  <section class="contact">
    <h3>📞 تواصل معنا الآن</h3>
    <div class="contact-grid">
      <div class="contact-item">
        <h4>👤 اسم العميل</h4>
        <p><strong>Match Systems</strong></p>
      </div>
      <div class="contact-item">
        <h4>📱 رقم الهاتف</h4>
        <p dir="ltr">00970593081003</p>
      </div>
      <div class="contact-item">
        <h4>🌐 الموقع الإلكتروني</h4>
        <p><a href="https://matchprosys.com/" target="_blank">matchprosys.com</a></p>
      </div>
    </div>
    <div class="availability-badge">⏰ متاحون للخدمة 24/7</div>
  </section>

  <footer>
    <strong>جميع الحقوق محفوظة © 2025 - Match Systems - Company Development Business One</strong>
    <br>
    <small style="margin-top: 10px; display: block; opacity: 0.9;">حلول تخطيط موارد المؤسسات المتطورة</small>
  </footer>

  <!-- Font Awesome CDN -->
  <script src="https://kit.fontawesome.com/5d56b5c1f9.js" crossorigin="anonymous"></script>
</body>
</html>
"""

# Help dropdown items that must be hidden by default in Navbar Settings
HIDDEN_HELP_ITEMS = {
	"documentation",
	"user forum",
	"frappe school",
	"report an issue",
	"about",
	"frappe support",
}

# Fallback match by route/action in case item_label differs across versions
HIDDEN_HELP_ITEM_SIGNATURES = [
	"frappe.io/support",
	"show_about",
]


def after_install():
	"""Apply Match Systems branding and default settings on a fresh site."""
	setup_logo_files()
	setup_navbar_settings()
	setup_system_settings()
	setup_website_settings()
	setup_home_page()
	setup_translations()
	frappe.db.commit()


def _attach_logo_file(target_filename):
	"""Ensure /files/<target_filename> exists, copying the bundled logo if needed."""
	from frappe.utils.file_manager import save_file

	file_url = f"/files/{target_filename}"

	if frappe.db.exists("File", {"file_url": file_url}):
		return file_url

	source_path = os.path.join(
		get_module_path("match_utils"), "data", "match_system_logo.png"
	)

	with open(source_path, "rb") as f:
		content = f.read()

	save_file(target_filename, content, "", "", folder="Home", is_private=0)

	return file_url


def setup_logo_files():
	"""Make the Match Systems logo available under the well-known file name."""
	_attach_logo_file("match_system_logo.png")


def setup_navbar_settings():
	navbar_settings = frappe.get_single("Navbar Settings")
	navbar_settings.app_logo = "/files/match_system_logo.png"

	for item in navbar_settings.help_dropdown:
		label = (item.item_label or "").strip().lower()
		signature = f"{item.route or ''} {item.action or ''}".lower()

		if label in HIDDEN_HELP_ITEMS or any(
			sig in signature for sig in HIDDEN_HELP_ITEM_SIGNATURES
		):
			item.hidden = 1

	navbar_settings.save(ignore_permissions=True)


def setup_system_settings():
	system_settings = frappe.get_single("System Settings")
	system_settings.enable_onboarding = 0
	system_settings.disable_system_update_notification = 1
	system_settings.save(ignore_permissions=True)


def setup_website_settings():
	website_settings = frappe.get_single("Website Settings")

	website_settings.app_name = "Match ERP"
	website_settings.title_prefix = "Match ERP System"
	website_settings.home_page = "home"

	website_settings.banner_image = "/files/match_system_logo.png"
	website_settings.splash_image = "/files/match_system_logo.png"
	website_settings.favicon = "/files/match_system_logo.png"
	website_settings.app_logo = "/files/match_system_logo.png"

	website_settings.brand_html = (
		'<img src="/files/match_system_logo.png" alt="Match ERP" style="height: 30px;">'
	)

	website_settings.address = "Palestine - Ramallah - 📍"
	website_settings.copyright = "Match Systems 2026"
	website_settings.footer_powered = "Match Systems"
	website_settings.footer_logo = "/files/match_system_logo.png"

	website_settings.save(ignore_permissions=True)


def setup_home_page():
	if frappe.db.exists("Web Page", {"route": "home"}):
		web_page = frappe.get_doc("Web Page", {"route": "home"})
	else:
		web_page = frappe.new_doc("Web Page")
		web_page.title = "Home"
		web_page.route = "home"

	web_page.published = 1
	web_page.content_type = "HTML"
	web_page.main_section_html = HOME_PAGE_HTML

	web_page.save(ignore_permissions=True)


# Source text -> Match ERP branded text, applied as Translation overrides
# so the "ERPNext" name never shows up in the UI without touching erpnext itself.
BRAND_TRANSLATIONS = {
	"ERPNext": "Match ERP",
}


def setup_translations():
	"""Override 'ERPNext' with 'Match ERP' for the languages used on the site."""
	languages = {"en", "ar"}
	system_language = frappe.db.get_single_value("System Settings", "language")
	if system_language:
		languages.add(system_language)

	for language in languages:
		for source_text, translated_text in BRAND_TRANSLATIONS.items():
			if frappe.db.exists(
				"Translation",
				{"language": language, "source_text": source_text},
			):
				continue

			frappe.get_doc(
				{
					"doctype": "Translation",
					"language": language,
					"source_text": source_text,
					"translated_text": translated_text,
				}
			).insert(ignore_permissions=True)
