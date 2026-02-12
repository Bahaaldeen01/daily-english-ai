import os
from google import genai
from datetime import datetime

# إعداد العميل باستخدام المكتبة الجديدة
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

date_str = datetime.now().strftime("%Y-%m-%d")

# الطلب المحدث
prompt = f"""
أنت خبير سيو ومدرس لغة إنجليزية. صمم صفحة HTML كاملة لدرس تاريخ {date_str}.
اختر كلمة إنجليزية مفيدة، وقدم: (العنوان، وصف Meta، المعنى، النطق، 3 أمثلة، ونكتة).
أضف تنسيق CSS عصري وجذاب.
أريد كود HTML فقط.
"""

# تشغيل الموديل (تأكد من استخدام الاسم الصحيح للموديل)
response = client.models.generate_content(
    model="gemini-2.0-flash", # نستخدم أحدث إصدار متاح حالياً
    contents=prompt
)

html_content = response.text

# 1. حفظ صفحة الدرس المنفردة للأرشفة
if not os.path.exists('archive'):
    os.makedirs('archive')

file_path = f"archive/{date_str}.html"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

# 2. تحديث الفهرس في الصفحة الرئيسية (index.html)
new_link = f'<li><a href="{file_path}">درس يوم {date_str} - تعلم كلمة جديدة</a></li>'

# قراءة الروابط الحالية إذا وجدت
links = []
if os.path.exists('index.html'):
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
        if "<ul>" in content and "</ul>" in content:
            links_part = content.split("<ul>")[1].split("</ul>")[0]
            links = [l.strip() for l in links_part.strip().split("\n") if l.strip()]

# إضافة الرابط الجديد في البداية
links.insert(0, new_link)

# بناء صفحة الـ Index بتصميم بسيط
index_html = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>أرشيف دروس الإنجليزية</title>
    <style>
        body {{ font-family: sans-serif; background: #f0f2f5; padding: 40px; }}
        .card {{ background: white; max-width: 700px; margin: auto; padding: 25px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a73e8; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ padding: 12px; border-bottom: 1px solid #fafafa; }}
        a {{ text-decoration: none; color: #444; font-weight: 500; }}
        a:hover {{ color: #1a73e8; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>موسوعة الكلمات اليومية</h1>
        <ul>
            {"".join(links[:50])}
        </ul>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(index_html)
