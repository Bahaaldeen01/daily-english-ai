import os
import google.generativeai as genai
from datetime import datetime

# إعداد المفتاح
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# استخدام الموديل المستقر (flash)
model = genai.GenerativeModel('gemini-1.5-flash')

date_str = datetime.now().strftime("%Y-%m-%d")

prompt = f"Create a simple HTML English lesson for {date_str}. Word, Meaning, Example. Use basic CSS. Return ONLY HTML."

try:
    # طلب المحتوى
    response = model.generate_content(prompt)
    html_content = response.text.replace('```html', '').replace('```', '')

    # حفظ الملف للأرشيف
    if not os.path.exists('archive'):
        os.makedirs('archive')
    
    file_path = f"archive/{date_str}.html"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # تحديث الصفحة الرئيسية (Index)
    new_link = f'<li><a href="{file_path}">Lesson: {date_str}</a></li>'
    
    links = []
    if os.path.exists('index.html'):
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
            if "<ul>" in content:
                links_part = content.split("<ul>")[1].split("</ul>")[0]
                links = [l.strip() for l in links_part.split("\n") if l.strip()]

    links.insert(0, new_link)
    
    index_html = f"<html><head><meta charset='UTF-8'></head><body><h1>English Archive</h1><ul>{''.join(links[:30])}</ul></body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    print("Success! Lesson generated.")

except Exception as e:
    print(f"Error occurred: {e}")
