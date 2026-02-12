import os
import google.generativeai as genai
from datetime import datetime

# إعداد الـ API الخاص بـ Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

date_str = datetime.now().strftime("%Y-%m-%d")

# البرومبت الاحترافي للسيو والتصميم
prompt = f"""
أنت خبير سيو (SEO) ومصمم ويب ومدرس لغة إنجليزية.
أريد إنشاء صفحة HTML كاملة لدرس تاريخ {date_str}.
المتطلبات:
1. اختر كلمة إنجليزية قوية ومفيدة.
2. صمم عنوان Meta جذاب لجوجل يتضمن الكلمة، مثلاً: "تعلم معنى كلمة [الكلمة] وكيفية استخدامها في جملة".
3. أضف وصف Meta فريد (Meta Description).
4. استخدم CSS داخلي لجعل الصفحة تبدو كمدونة احترافية (ألوان هادئة، خطوط واضحة، حواف مستديرة).
5. المحتوى: (الكلمة، النطق، الترجمة العربية، 3 أمثلة، ونكتة أو حقيقة ممتعة).
6. أضف قسم في نهاية المقال بعنوان "دروس قد تهمك" واتركه فارغاً.
7. أضف تعليق HTML في مكان استراتيجي مكتوب فيه لأضع فيه كود إعلاناتي لاحقاً.
ملاحظة: أريد كود الـ HTML فقط في المخرج.
"""

response = model.generate_content(prompt)
html_content = response.text.replace('```html', '').replace('```', '') # تنظيف الكود

# 1. حفظ صفحة الدرس المنفردة للأرشفة
if not os.path.exists('archive'):
    os.makedirs('archive')

file_path = f"archive/{date_str}.html"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

# 2. تحديث الصفحة الرئيسية (index.html) لتكون فهرس للدروس
# سنقوم بقراءة الروابط القديمة وإضافة الجديد في البداية
links = []
if os.path.exists('index.html'):
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
        # محاولة استخراج الروابط القديمة (بسيط جداً)
        if "<ul>" in content:
            links_part = content.split("<ul>")[1].split("</ul>")[0]
            links = links_part.strip().split("\n")

# إضافة الرابط الجديد في أعلى القائمة
new_link = f'<li><a href="{file_path}">درس يوم {date_str} - تعلم كلمة جديدة</a></li>'
links.insert(0, new_link)

# إعادة كتابة الصفحة الرئيسية بتصميم بسيط
index_html = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>مدونة تعلم الإنجليزية اليومية</title>
    <style>
        body {{ font-family: sans-serif; padding: 20px; line-height: 1.6; background: #f4f4f4; }}
        .container {{ max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; }}
        h1 {{ color: #333; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
        a {{ text-decoration: none; color: #007bff; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>أرشيف دروس الإنجليزية</h1>
        <p>دروس يومية متجددة بالذكاء الاصطناعي</p>
        <ul>
            {"".join(links[:50])} </ul>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(index_html)
