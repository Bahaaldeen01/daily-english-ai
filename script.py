import os
import json
from datetime import datetime
import google.generativeai as genai

# إعداد API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# تاريخ اليوم
date_str = datetime.utcnow().strftime("%Y-%m-%d")

# اسم الملف
file_path = f"archive/{date_str}.html"

# منع التكرار
if os.path.exists(file_path):
    print("Lesson already exists.")
    exit(0)

# البرومبت
prompt = """
Create 5 English words for beginners.

Return ONLY JSON array:
[
{"word":"","meaning":"","example":"","pronunciation":""}
]

Rules:
- Arabic meaning
- short example
- no markdown
"""

try:
    response = model.generate_content(prompt)
    text = response.text.strip()

    # تنظيف النص
    text = text.replace("```json", "").replace("```", "").strip()

    data = json.loads(text)

    if not isinstance(data, list) or len(data) == 0:
        raise Exception("Invalid AI response")

    # إنشاء كروت الكلمات
    cards = ""
    for item in data:
        cards += f"""
        <div class="card">
            <div class="word">{item['word']} – 🔊 {item['pronunciation']}</div>
            <div class="meaning">Meaning: {item['meaning']}</div>
            <div class="example">Example: {item['example']}</div>
        </div>
        """

    # قراءة القالب
    with open("template.html", encoding="utf-8") as f:
        template = f.read()

    final_html = template.replace("{{date}}", date_str).replace("{{content}}", cards)

    # إنشاء مجلد archive
    os.makedirs("archive", exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print("Lesson page created.")

    # ----- تحديث index -----
    links = []
    for name in sorted(os.listdir("archive"), reverse=True)[:30]:
        links.append(f'<li><a href="archive/{name}">{name}</a></li>')

    with open("index_template.html", encoding="utf-8") as f:
        index_template = f.read()

    index_html = index_template.replace("{{links}}", "\n".join(links))

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    print("Index updated.")

except Exception as e:
    print("ERROR:", e)
    exit(1)
