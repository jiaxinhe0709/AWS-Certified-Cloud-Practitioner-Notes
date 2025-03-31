
import os
import re
from pathlib import Path

INPUT_DIR = "practice-exam"
OUTPUT_DIR = "quizzes"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_markdown_to_quiz_html(markdown_text, exam_title="AWS Practice Exam"):
    question_blocks = re.split(r"\n(?=\d+\.\s)", markdown_text.strip())
    questions_html = ""
    score_script = "const answers = {}\n"

    for i, block in enumerate(question_blocks):
        question_match = re.match(r"(\d+)\.\s+(.*?)\n", block)
        if not question_match:
            continue

        q_number = question_match.group(1)
        question_text = question_match.group(2)

        options = re.findall(r"-\s([A-E])\.\s(.+)", block)
        correct = re.search(r"Correct answer: ([A-E](?:,\s?[A-E])*)", block)
        correct_answers = [c.strip() for c in correct.group(1).split(",")] if correct else []

        questions_html += f"<div class='question' id='q{q_number}-container'><p><strong>{q_number}. {question_text}</strong></p>\n"
        for opt in options:
            opt_val, opt_text = opt
            input_type = "checkbox" if len(correct_answers) > 1 else "radio"
            name_attr = f"name='q{q_number}'"
            questions_html += f"<label><input type='{input_type}' {name_attr} value='{opt_val}'> {opt_val}. {opt_text}</label><br>\n"
        questions_html += f"<p id='q{q_number}-feedback' class='feedback'></p>\n"
        questions_html += "</div><br>\n"

        score_script += f"answers['q{q_number}'] = {correct_answers};\n"

    full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{exam_title}</title>
    <style>
        body {{ font-family: Arial; padding: 20px; max-width: 800px; margin: auto; }}
        .question {{ margin-bottom: 20px; }}
        .summary {{ font-weight: bold; font-size: 1.2em; }}
        .correct {{ color: green; }}
        .incorrect {{ color: red; }}
        .feedback {{ font-style: italic; margin-top: 5px; }}
    </style>
</head>
<body>
    <h1>{exam_title}</h1>
    <form id="quizForm">
        {questions_html}
        <button type="button" onclick="submitQuiz()">Submit</button>
    </form>
    <p id="result" class="summary"></p>

    <script>
        {score_script}

        function submitQuiz() {{
            let score = 0;
            let total = Object.keys(answers).length;

            for (let key in answers) {{
                const selected = Array.from(document.querySelectorAll(`input[name='${{key}}']:checked`)).map(el => el.value);
                const correct = answers[key];

                const selectedSorted = selected.slice().sort().join('');
                const correctSorted = correct.slice().sort().join('');
                const isCorrect = selectedSorted === correctSorted;

                const feedbackEl = document.getElementById(`${{key}}-feedback`);
                if (isCorrect) {{
                    score++;
                    feedbackEl.innerText = "✅ Correct";
                    feedbackEl.className = "feedback correct";
                }} else {{
                    feedbackEl.innerText = "❌ Incorrect. Correct answer(s): " + correct.join(", ");
                    feedbackEl.className = "feedback incorrect";
                }}
            }}

            document.getElementById("result").innerText = `Your Score: ${{score}} / ${{total}}`;
        }}
    </script>
</body>
</html>
"""
    return full_html

def convert_all_markdown_files():
    for md_file in Path(INPUT_DIR).glob("*.md"):
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        exam_name = md_file.stem.replace("-", " ").title()
        html = parse_markdown_to_quiz_html(content, exam_title=exam_name)

        output_file = Path(OUTPUT_DIR) / f"{md_file.stem}.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Converted: {md_file.name} -> {output_file.name}")

if __name__ == "__main__":
    convert_all_markdown_files()
