import os
import json
from datetime import datetime
import requests
from gtts import gTTS
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# ─── إعداد OpenRouter ───
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
if not client.api_key:
    raise Exception("OPENROUTER_API_KEY not found in secrets")

# ─── التاريخ والمجلدات ───
date_str = datetime.utcnow().strftime("%Y-%m-%d")
archive_dir = "archive"
os.makedirs(archive_dir, exist_ok=True)
lesson_dir = f"{archive_dir}/{date_str}"
os.makedirs(lesson_dir, exist_ok=True)
file_path = f"{lesson_dir}/index.html"

if os.path.exists(file_path):
    print("Lesson already exists.")
    exit(0)

# ─── تحميل الكلمات المستخدمة سابقاً ───
history_file = f"{archive_dir}/history.json"
used_words = []
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as f:
        used_words = json.load(f)

# ─── توليد المحتوى ───
prompt = f"""
You are a language learning assistant. Generate today's daily English lesson.

Previously used phrases (avoid repeating): {used_words[-50:]}

Return ONLY a JSON object (no markdown):
{{
  "phrase": "a common English phrase or expression",
  "phrase_ar": "ترجمة بالعربية",
  "pronunciation": "/phonetic/",
  "explanation": "شرح مبسط بالعربية",
  "usages": [
    "First usage example",
    "Second usage example",
    "Third usage example"
  ],
  "joke": {{
    "en": "A joke related to the phrase",
    "ar": "ترجمة النكتة"
  }},
  "grammar_tip": "نصيحة قواعدية بالعربية",
  "vocabulary": [
    {{"word": "word1", "meaning_ar": "معنى", "example": "example sentence"}},
    {{"word": "word2", "meaning_ar": "معنى", "example": "example sentence"}},
    {{"word": "word3", "meaning_ar": "معنى", "example": "example sentence"}}
  ]
}}
"""

response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.8,
)
text = response.choices[0].message.content.strip()
text = text.replace("```json", "").replace("```", "").strip()
data = json.loads(text)

# ─── تحديث السجل ───
used_words.append(data["phrase"])
with open(history_file, "w", encoding="utf-8") as f:
    json.dump(used_words, f, ensure_ascii=False)

# ─── توليد الصوت ───
# صوت الجملة الرئيسية
tts_phrase = gTTS(data["phrase"], lang='en')
tts_phrase.save(f"{lesson_dir}/phrase.mp3")

# صوت كل كلمة
for i, vocab in enumerate(data["vocabulary"]):
    tts_word = gTTS(vocab["word"], lang='en')
    tts_word.save(f"{lesson_dir}/word_{i}.mp3")

# ─── بناء HTML ───
vocab_cards = ""
for i, vocab in enumerate(data["vocabulary"]):
    vocab_cards += f"""
    <div class="vocab-card">
        <span class="vocab-word">{vocab['word']}</span>
        <span class="vocab-meaning">{vocab['meaning_ar']}</span>
        <p class="vocab-example">"{vocab['example']}"</p>
        <audio controls src="word_{i}.mp3"></audio>
    </div>
    """

usages_html = ""
for usage in data["usages"]:
    usages_html += f'<div class="usage-item">💬 {usage}</div>\n'

lesson_html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Daily Phrase – {date_str}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Segoe UI', Tahoma, sans-serif;
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: #f0f0f0;
    min-height: 100vh;
    padding: 20px;
  }}
  .container {{ max-width: 700px; margin: 0 auto; }}
  h1 {{
    text-align: center;
    font-size: 1.8em;
    margin-bottom: 25px;
    color: #4fc3f7;
  }}
  .main-card {{
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 25px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.1);
  }}
  .phrase {{
    font-size: 1.8em;
    color: #4fc3f7;
    font-weight: bold;
    text-align: center;
    direction: ltr;
  }}
  .pronunciation {{
    text-align: center;
    color: #aaa;
    font-style: italic;
    margin: 8px 0;
    direction: ltr;
  }}
  .phrase-ar {{
    text-align: center;
    font-size: 1.3em;
    color: #e0e0e0;
    margin: 10px 0;
  }}
  .section-title {{
    font-size: 1.2em;
    color: #4fc3f7;
    margin: 20px 0 10px;
    padding-bottom: 5px;
    border-bottom: 1px solid rgba(79,195,247,0.3);
  }}
  .explanation {{ line-height: 1.8; font-size: 1.05em; }}
  .usage-item {{
    background: rgba(255,255,255,0.05);
    padding: 10px 15px;
    border-radius: 8px;
    margin: 8px 0;
    direction: ltr;
    text-align: left;
  }}
  .joke-box {{
    background: rgba(255,193,7,0.1);
    border-right: 4px solid #ffc107;
    padding: 15px;
    border-radius: 8px;
    margin: 15px 0;
  }}
  .joke-en {{ direction: ltr; text-align: left; font-style: italic; }}
  .joke-ar {{ margin-top: 8px; color: #ccc; }}
  .grammar-tip {{
    background: rgba(76,175,80,0.1);
    border-right: 4px solid #4caf50;
    padding: 15px;
    border-radius: 8px;
  }}
  .vocab-card {{
    background: rgba(255,255,255,0.06);
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
  }}
  .vocab-word {{
    font-weight: bold;
    color: #4fc3f7;
    font-size: 1.1em;
    direction: ltr;
  }}
  .vocab-meaning {{ color: #ccc; }}
  .vocab-example {{
    width: 100%;
    color: #aaa;
    font-style: italic;
    direction: ltr;
    text-align: left;
  }}
  audio {{ height: 30px; }}
  .nav {{
    text-align: center;
    margin-top: 30px;
  }}
  .nav a {{
    color: #4fc3f7;
    text-decoration: none;
    padding: 8px 20px;
    border: 1px solid #4fc3f7;
    border-radius: 20px;
    transition: 0.3s;
  }}
  .nav a:hover {{
    background: #4fc3f7;
    color: #1e1e2f;
  }}
</style>
</head>
<body>
<div class="container">
  <h1>📘 Daily Phrase – {date_str}</h1>

  <div class="main-card">
    <div class="phrase">{data['phrase']}</div>
    <div class="pronunciation">{data['pronunciation']}</div>
    <div class="phrase-ar">{data['phrase_ar']}</div>
    <div style="text-align:center; margin-top:10px;">
      <audio controls src="phrase.mp3"></audio>
    </div>
  </div>

  <div class="main-card">
    <div class="section-title">📖 الشرح</div>
    <div class="explanation">{data['explanation']}</div>
  </div>

  <div class="main-card">
    <div class="section-title">💬 أمثلة على الاستخدام</div>
    {usages_html}
  </div>

  <div class="main-card">
    <div class="section-title">📝 مفردات الدرس</div>
    {vocab_cards}
  </div>

  <div class="main-card joke-box">
    <div class="section-title">😄 نكتة اليوم</div>
    <div class="joke-en">{data['joke']['en']}</div>
    <div class="joke-ar">{data['joke']['ar']}</div>
  </div>

  <div class="main-card grammar-tip">
    <div class="section-title">💡 نصيحة قواعدية</div>
    <p>{data['grammar_tip']}</p>
  </div>

  <div class="nav">
    <a href="../../index.html">📚 العودة للأرشيف</a>
  </div>
</div>
</body>
</html>"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(lesson_html)
print(f"Lesson created: {file_path}")

# ─── تحديث index.html ───
lesson_dirs = sorted(
    [d for d in os.listdir(archive_dir)
     if os.path.isdir(f"{archive_dir}/{d}") and d[0].isdigit()],
    reverse=True
)

links = ""
for d in lesson_dirs[:60]:
    links += f'<li><a href="archive/{d}/index.html">📘 {d}</a></li>\n'

with open("index_template.html", encoding="utf-8") as f:
    index_template = f.read()
index_html = index_template.replace("{{links}}", links)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(index_html)
print("Index updated.")
