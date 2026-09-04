import json
import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
_model = genai.GenerativeModel("gemini-3.6-flash")


PROMPT_TEMPLATE = """You are helping a beginner programmer understand an open source GitHub repo and find a good first contribution.

Repo name: {name}
Description: {description}
Languages used: {languages}
Stars: {stars}

README (partial):
{readme}

CONTRIBUTING guide (if present):
{contributing}

Open issues:
{issues}

User's known languages / skill level: {user_profile}

Return ONLY valid JSON, no markdown fences, no extra text, in exactly this shape:
{{
  "summary": "2-3 sentence plain-language summary of what this project does",
  "tech_stack": ["list", "of", "detected", "technologies"],
  "suggestions": [
    {{
      "title": "short title of the contribution idea",
      "difficulty": "easy | medium | hard",
      "reason": "1-2 sentences on why this is a good starting point for this user",
      "issue_url": "link to the issue if it maps to one, else empty string"
    }}
  ]
}}

Give exactly 5 suggestions, ranked easiest first. Base at least 2-3 of them on the actual open issues listed above when possible. If few issues are useful, suggest doc fixes, test additions, or small code improvements you can infer are needed.
"""


def analyze_repo(repo_data, user_profile="Beginner, comfortable with Python and JavaScript"):
    issues_text = "\n".join(
        f"- #{i['number']}: {i['title']} (labels: {', '.join(i['labels']) or 'none'})"
        for i in repo_data["issues"]
    ) or "No open issues found."

    prompt = PROMPT_TEMPLATE.format(
        name=repo_data["name"],
        description=repo_data["description"] or "No description provided",
        languages=", ".join(repo_data["languages"]) or "Unknown",
        stars=repo_data["stars"],
        readme=repo_data["readme"] or "No README found",
        contributing=repo_data["contributing"] or "No CONTRIBUTING.md found",
        issues=issues_text,
        user_profile=user_profile,
    )

    response = _model.generate_content(prompt)
    text = response.text.strip()

    # Strip markdown code fences if Gemini adds them anyway
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ValueError(f"Could not parse AI response as JSON:\n{text}")