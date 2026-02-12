import os
import google.generativeai as genai
from datetime import datetime

# 1. إعداد الاتصال
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

date_str = datetime.now().strftime("%Y-%m-%d")

# 2. البرومبت (طلب الكود بوضوح)
prompt = f"Write a complete HTML page for an English lesson about a new word for {date_str}. Include the word, meaning, and an example sentence. Use simple internal CSS for a nice look. Return ONLY the HTML code."

try:
    # 3. طلب المحتوى وتنظيفه
    response = model.generate_content(prompt)
    raw_html = response.text.strip()
    
    # تنظيف الكود من علامات markdown إذا وجدت
    clean_html = raw_html.replace('```html', '').replace('```', '').strip()

    # تأمين المجلد
    if not os.path.exists('archive'):
        os.makedirs('archive')

    # 4. حفظ ملف الدرس
    file_path = f"archive/{date_str}.html"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(clean_html)

    # 5. تحديث الصفحة الرئيسية (بناء كامل وجديد لضمان عدم الفراغ)
    # سنقوم بجلب الملفات الموجودة في الأرشيف لإنشاء القائمة
    archive_files = os.listdir('archive')
    archive_files.sort(reverse=True) # الأحدث أولاً
    
    links_html = ""
    for file in archive_files:
        links_html += f'<li><a href="archive/{file}">درس يوم {file.replace(".html", "")}</a></li>\n'

    index_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>تعلم الإنجليزية يومياً</title>
        <style>
            body {{ font-family: Arial; background: #f4f4f9; padding: 20px; text-align: center; }}
            .container {{ background: white; max-width: 600px; margin: auto; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ margin: 10px 0; padding: 10px; border-bottom: 1px solid #eee; }}
            a {{ text-decoration: none; color: #3498db; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>أرشيف الدروس الذكي</h1>
            <ul>
                {links_html}
            </ul>
        </div>
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_content)
        
    print(f"Done! Created {file_path} and updated index.html")

except Exception as e:
    print(f"Error: {e}")
    # في حالة الخطأ، لا تترك الملف فارغاً
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("<h1>تحت الصيانة - يرجى العودة لاحقاً</h1>")
