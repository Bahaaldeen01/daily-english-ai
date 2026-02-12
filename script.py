import os
from google import genai
from datetime import datetime

# إعداد العميل باستخدام المكتبة الجديدة
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

date_str = datetime.now().strftime("%Y-%m-%d")

prompt = f"""
أنت خبير سيو ومدرس لغة إنجليزية. صمم صفحة HTML كاملة لدرس تاريخ {date_str}.
اختر كلمة إنجليزية مفيدة، وقدم: (العنوان، وصف Meta، المعنى، النطق، 3 أمثلة، ونكتة).
أضف تنسيق CSS عصري وجذاب.
أريد كود HTML فقط.
"""

# التعديل الجوهري هنا: حذف كلمة "models/" وكتابة اسم الموديل مباشرة
response = client.models.generate_content(
    model="gemini-1.5-flash", 
    contents=prompt
)

# التأكد من استخراج النص بشكل صحيح
html_content = response.text

# 1. حفظ صفحة الدرس المنفردة للأرشفة
if not os.path.exists('archive'):
    os.makedirs('archive')

file_path = f"archive/{date_str}.html"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

# 2. تحديث الفهرس (index.html)
new_link = f'<li><a href="{file_path}">درس يوم {date_str} - تعلم كلمة جديدة</a></li>'

links = []
if os.path.exists('index.html'):
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
        if "<ul>" in content:
            parts = content.split("<ul>")
            if len(parts) > 1:
                links_part = parts[1].split("</ul>")[0]
                links = [l.strip() for l in links_part.strip().split("\n") if l.strip()]

links.insert(0, new_link)

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
