import os
print("ENV KEYS:", list(os.environ.keys()))

import os
import json
from datetime import datetime
from openai import OpenAI

# الاتصال بـ OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

# التاريخ
date_str = datetime.utcnow().strftime("%Y-%m-%d")

file_path = f"archive/{date_str}.html"

# منع التكرار
if os.path.exists(file_path):
    print("Lesson already exists.")
    exit(0)

prompt = """
Create 5 English words for beginners.

Return ONLY JSON array:
[
{"word":"","meaning":"","example":"","pronunciation":""}
]

Rules:
- meaning in Arabic
- short example
- no markdown
"""

try:
    completion = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    text = completion.choices[0].message.content.strip()

    # تنظيف
    text = text.replace("```json", "").replace("```", "").strip()

    data = json.loads(text)

    if not isinstance(data, list) or len(data) == 0:
        raise Exception("Invalid AI response")

    # إنشاء الكروت
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

    os.makedirs("archive", exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print("Lesson page created.")

    # تحديث index
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
