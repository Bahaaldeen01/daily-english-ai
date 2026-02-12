import os
import json
from datetime import datetime
from gtts import gTTS
from openai import OpenAI

# ═══════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
if not client.api_key:
    raise Exception("OPENROUTER_API_KEY not found")

date_str = datetime.utcnow().strftime("%Y-%m-%d")
archive_dir = "archive"
os.makedirs(archive_dir, exist_ok=True)
lesson_dir = f"{archive_dir}/{date_str}"
os.makedirs(lesson_dir, exist_ok=True)
file_path = f"{lesson_dir}/index.html"

if os.path.exists(file_path):
    print("Lesson already exists.")
    exit(0)

# ═══════════════════════════════════════
#  LOAD HISTORY
# ═══════════════════════════════════════
history_file = f"{archive_dir}/history.json"
used_phrases = []
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as f:
        used_phrases = json.load(f)

# ═══════════════════════════════════════
#  GENERATE CONTENT
# ═══════════════════════════════════════
prompt = f"""
You are a language learning assistant. Generate today's daily English lesson.

Previously used phrases (DO NOT repeat): {used_phrases[-60:]}

Return ONLY a valid JSON object with NO markdown:
{{
  "phrase": "a common English phrase, idiom, or expression",
  "phrase_ar": "ترجمة بالعربية",
  "pronunciation": "/phonetic pronunciation/",
  "explanation": "شرح مبسط وواضح بالعربية لمعنى الجملة ومتى تُستخدم",
  "usages": [
    "First example sentence using the phrase",
    "Second example sentence",
    "Third example sentence"
  ],
  "joke": {{
    "en": "A short funny joke related to the phrase",
    "ar": "ترجمة النكتة بالعربية"
  }},
  "grammar_tip": "نصيحة قواعدية قصيرة بالعربية مرتبطة بالجملة",
  "vocabulary": [
    {{"word": "word1", "meaning_ar": "المعنى", "example": "Example sentence"}},
    {{"word": "word2", "meaning_ar": "المعنى", "example": "Example sentence"}},
    {{"word": "word3", "meaning_ar": "المعنى", "example": "Example sentence"}}
  ],
  "quiz": [
    {{
      "question": "سؤال اختيار من متعدد بالعربية عن معنى الجملة",
      "options": ["خيار 1", "خيار 2", "خيار 3"],
      "correct": 0
    }},
    {{
      "question": "سؤال آخر عن استخدام الجملة أو إحدى المفردات",
      "options": ["خيار 1", "خيار 2", "خيار 3"],
      "correct": 1
    }}
  ]
}}

Rules:
- Target beginner to intermediate Arabic-speaking learners
- The phrase should be useful in daily life
- Arabic explanations must be clear and simple
- The joke MUST be related to the phrase
- Quiz questions in Arabic, options in Arabic
- Return valid JSON only, no extra text
"""

response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.8,
)

text = response.choices[0].message.content.strip()
text = text.replace("```json", "").replace("```", "").strip()
data = json.loads(text)

# ═══════════════════════════════════════
#  UPDATE HISTORY
# ═══════════════════════════════════════
used_phrases.append(data["phrase"])
with open(history_file, "w", encoding="utf-8") as f:
    json.dump(used_phrases, f, ensure_ascii=False)

# ═══════════════════════════════════════
#  GENERATE AUDIO
# ═══════════════════════════════════════
tts = gTTS(data["phrase"], lang='en')
tts.save(f"{lesson_dir}/phrase.mp3")

for i, vocab in enumerate(data["vocabulary"]):
    tts_w = gTTS(vocab["word"], lang='en')
    tts_w.save(f"{lesson_dir}/word_{i}.mp3")

# ═══════════════════════════════════════
#  BUILD LESSON HTML
# ═══════════════════════════════════════

# Usages HTML
usages_html = ""
for usage in data["usages"]:
    usages_html += f'<div class="usage-item">{usage}</div>\n'

# Vocabulary cards HTML
vocab_html = ""
for i, v in enumerate(data["vocabulary"]):
    vocab_html += f"""
    <div class="vocab-card">
      <button class="vocab-sound-btn" data-audio="word_{i}.mp3">🔊</button>
      <div>
        <div class="vocab-word-text">{v['word']}</div>
        <div class="vocab-meaning">{v['meaning_ar']}</div>
        <div class="vocab-example">"{v['example']}"</div>
      </div>
    </div>
    """

# Quiz HTML
quiz_html = ""
for qi, q in enumerate(data["quiz"]):
    opts = ""
    for oi, opt in enumerate(q["options"]):
        opts += f'<button class="quiz-option">{opt}</button>\n'
    quiz_html += f"""
    <div class="quiz-block" data-correct="{q['correct']}" style="margin-bottom:20px;">
      <div class="quiz-question">{qi + 1}. {q['question']}</div>
      <div class="quiz-options">
        {opts}
      </div>
      <div class="quiz-result"></div>
    </div>
    """

# Load template and replace
with open("lesson_template.html", "r", encoding="utf-8") as f:
    template = f.read()

replacements = {
    "{{date}}": date_str,
    "{{phrase}}": data["phrase"],
    "{{phrase_ar}}": data["phrase_ar"],
    "{{pronunciation}}": data["pronunciation"],
    "{{explanation}}": data["explanation"],
    "{{usages}}": usages_html,
    "{{vocab_cards}}": vocab_html,
    "{{joke_en}}": data["joke"]["en"],
    "{{joke_ar}}": data["joke"]["ar"],
    "{{grammar_tip}}": data["grammar_tip"],
    "{{quiz_html}}": quiz_html,
}

lesson_html = template
for key, value in replacements.items():
    lesson_html = lesson_html.replace(key, value)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(lesson_html)
print(f"Lesson created: {file_path}")

# ═══════════════════════════════════════
#  UPDATE SEARCH INDEX
# ═══════════════════════════════════════
search_index_file = f"{archive_dir}/lessons-data.json"
search_data = []
if os.path.exists(search_index_file):
    with open(search_index_file, "r", encoding="utf-8") as f:
        search_data = json.load(f)

search_data.append({
    "date": date_str,
    "phrase": data["phrase"],
    "phrase_ar": data["phrase_ar"],
    "vocabulary": [v["word"] for v in data["vocabulary"]]
})

with open(search_index_file, "w", encoding="utf-8") as f:
    json.dump(search_data, f, ensure_ascii=False, indent=2)

# ═══════════════════════════════════════
#  UPDATE INDEX.HTML
# ═══════════════════════════════════════
lesson_dirs = sorted(
    [d for d in os.listdir(archive_dir)
     if os.path.isdir(f"{archive_dir}/{d}") and d[0].isdigit()],
    reverse=True
)

links = ""
for d in lesson_dirs[:90]:
    # Load phrase for preview
    preview = ""
    lesson_data_path = f"{archive_dir}/lessons-data.json"
    if os.path.exists(lesson_data_path):
        with open(lesson_data_path, "r", encoding="utf-8") as f:
            all_data = json.load(f)
            match = [x for x in all_data if x["date"] == d]
            if match:
                preview = match[0]["phrase"]

    links += f"""
    <li class="lesson-item" data-date="{d}">
      <a href="archive/{d}/index.html">
        <div>
          <div class="lesson-date">{d}</div>
          <div class="lesson-preview">{preview}</div>
        </div>
        <span class="check-icon">✅</span>
      </a>
    </li>
    """

with open("index_template.html", "r", encoding="utf-8") as f:
    index_template = f.read()

index_html = index_template.replace("{{links}}", links)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(index_html)
print("Index updated.")
