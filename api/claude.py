import random
from anthropic import Anthropic

API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(API_KEY)


BASE_PROMPT = """
I need help guessing the location of an email domain.
The domain is: {domain}

Rules:
- If the domain contains the name of a company, return the location of the company's headquarters.
- If the domain contains the name of a city, return that city.
- Do NOT return obscure towns that coincidentally share the same name.
- If unsure, choose the most globally well-known location that matches the name.
- Output ONLY the city and country. No explanation.
"""

# Exact known domains
EXACT_DOMAINS = {
    "gmail.com":      "Mountain View, USA",
    "outlook.com":    "Seattle, USA",
    "hotmail.com":    "Seattle, USA",
    "icloud.com":     "Cupertino, USA",
    "yahoo.com":      "Sunnyvale, USA",
}

# Suffix-based guesses
DOMAIN_SUFFIXES = {
    ".co.uk": "London, UK",
    ".uk":    "London, UK",
    ".za":    "Cape Town, South Africa",
    ".de":    "Berlin, Germany",
    ".fr":    "Paris, France",
    ".in":    "Mumbai, India",
    ".us":    "Los Angeles, USA",
    ".edu":   "Boston, USA",
    ".gov":   "Washington DC, USA",
    ".com":   "The Moon",
}


def ask_claude(text):
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=30,
        messages=[{"role": "user", "content": text}]
    )
    return response.content[0].text.strip()


def get_location_from_email(email):
    domain = email.split("@")[1]

    # 1. Exact match
    if domain in EXACT_DOMAINS:
        return EXACT_DOMAINS[domain]

    # 2. Suffix match
    for suffix, location in DOMAIN_SUFFIXES.items():
        if domain.endswith(suffix):
            return location

    # 3. Ask Claude for unknown domains
    try:
        ai_guess = ask_claude(BASE_PROMPT.format(domain=domain))
        if ai_guess:
            return ai_guess
    except Exception as e:
        print("Claude ERROR:", e)

    # 4. Fallback
    # 4. Fallback funny locations
    RANDOM_FALLBACKS = [
        "Nowhere, Internet",
        "The Cloud, Everywhere",
        "Area 51, USA",
        "Middle of Nowhere, Earth",
        "Narnia, Fictional",
        "Atlantis, Undersea",
        "Mars Colony, Mars",
        "The Moon, Space",
        "Back of the Fridge, Home",
        "42nd Parallel, Unknown"
    ]
    return random.choice(RANDOM_FALLBACKS)


# TEST

print(get_location_from_email("joan@whoop.go"))
