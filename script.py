import os
import json
from datetime import datetime
import requests
from gtts import gTTS
from openai import OpenAI
from PIL import Image
from io import BytesIO

# إعداد OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
if not client.api_key:
    raise Exception("OPENROUTER_API_KEY not found in secrets")

# التاريخ
date_str = datetime.utcnow().strftime("%Y-%m-%d")
archive_dir = "archive"
os.makedirs(archive_dir, exist_ok=True)
file_path = f"{archive_dir}/{date_str}.html"

# منع التكرار
if os.path.exists(file_path):
    print("Lesson already exists.")
    exit(0)

# توليد الكلمات
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

response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
)
text = response.choices[0].message.content.strip()
text = text.replace("```json","").replace("```","").strip()
data = json.loads(text)

cards = ""
for item in data:
    word = item["word"]
    pronunciation = item.get("pronunciation", "")
    meaning = item["meaning"]
    example = item["example"]

    # توليد صوت MP3
    tts = gTTS(word, lang='en')
    audio_path = f"{archive_dir}/{word}_{date_str}.mp3"
    tts.save(audio_path)

    # توليد صورة بسيطة (كلمة على خلفية ملونة)
    img = Image.new('RGB', (200,100), color=(40,40,64))
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((10,40), word, font=font, fill=(79,195,247))
    img_path = f"{archive_dir}/{word}_{date_str}.png"
    img.save(img_path)

    # إضافة الكارت للدرس
    cards += f"""
    <div class="card">
        <div class="word">{word} – 🔊 {pronunciation}</div>
        <div class="meaning">Meaning: {meaning}</div>
        <div class="example">Example: {example}</div>
        <img class="word-image" src="{img_path}" alt="{word}">
        <audio controls>
            <source src="{audio_path}" type="audio/mpeg">
        </audio>
    </div>
    """

# حفظ الدرس النهائي
with open("template.html", encoding="utf-8") as f:
    template = f.read()
final_html = template.replace("{{date}}", date_str).replace("{{content}}", cards)
with open(file_path, "w", encoding="utf-8") as f:
    f.write(final_html)
print("Lesson created.")

# تحديث index.html
links = [f'<li><a href="{archive_dir}/{name}">{name}</a></li>' for name in sorted(os.listdir(archive_dir), reverse=True)[:30]]
with open("index_template.html", encoding="utf-8") as f:
    index_template = f.read()
index_html = index_template.replace("{{links}}", "\n".join(links))
with open("index.html", "w", encoding="utf-8") as f:
    f.write(index_html)
print("Index updated.")
