import re
import streamlit as st


# ============================================================
# OPTIONAL ANTHROPIC API
# ============================================================

try:
    import anthropic
except ImportError:
    anthropic = None


API_MODEL = "claude-haiku-4-5-20251001"


# ============================================================
# API KEY
# ============================================================

def _api_key():

    try:
        return st.secrets["ANTHROPIC_API_KEY"]

    except Exception:
        return None


def using_api():

    return (
        bool(_api_key())
        and anthropic is not None
    )


# ============================================================
# API CLIENT
# ============================================================

@st.cache_resource
def _client(key):

    return anthropic.Anthropic(
        api_key=key
    )


# ============================================================
# API CONVERSION
# ============================================================

def _ask_api(option, text):

    instructions = {

        "Simple English":
            """
            Rewrite the text in very simple English.
            Use easy words and short sentences.
            Keep the original meaning.
            Do not add new information.
            Return only the rewritten text.
            """,

        "Professional English":
            """
            Rewrite the text in formal and professional English.
            Fix grammar and spelling.
            Keep the original meaning.
            Do not add new information.
            Return only the rewritten text.
            """,

        "Shorten Text":
            """
            Shorten the text while keeping the most important information.
            Remove unnecessary details.
            Return only the shortened text.
            """,

        "Bullet Points":
            """
            Convert the text into clear bullet points.
            Put one idea on each line.
            Return only the bullet points.
            """,

        "Email Mode":
            """
            Convert the text into a professional email.
            Include a subject, greeting, body and closing.
            Do not invent information.
            Return only the email.
            """
    }

    client = _client(
        _api_key()
    )

    response = client.messages.create(

        model=API_MODEL,

        max_tokens=1000,

        system=instructions[option],

        messages=[
            {
                "role": "user",
                "content": text
            }
        ]
    )

    return "".join(

        block.text
        for block in response.content
        if block.type == "text"

    ).strip()


# ============================================================
# TEXT UTILITIES
# ============================================================

def _sentences(text):

    text = text.strip()

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+|\n+",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# ============================================================
# CLEAN COMMON CASUAL WORDS
# ============================================================

CASUAL_WORDS = {

    "u": "you",
    "ur": "your",
    "pls": "please",
    "plz": "please",

    "tmrw": "tomorrow",
    "tommorow": "tomorrow",
    "tommorrow": "tomorrow",
    "tomorow": "tomorrow",

    "clg": "college",

    "dont": "don't",
    "cant": "can't",
    "wont": "won't",
    "didnt": "didn't",
    "isnt": "isn't",
    "wasnt": "wasn't",

    "im": "I am",
    "ive": "I have",
    "id": "I would",

    "msg": "message",
    "asap": "as soon as possible"
}


def clean_casual_text(text):

    for wrong, correct in CASUAL_WORDS.items():

        text = re.sub(
            rf"\b{re.escape(wrong)}\b",
            correct,
            text,
            flags=re.IGNORECASE
        )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    if text:

        text = (
            text[0].upper()
            + text[1:]
        )

    return text


# ============================================================
# SIMPLE ENGLISH
# ============================================================

def simple_english_local(text):

    text = clean_casual_text(text)

    replacements = {

        "approximately": "about",
        "utilize": "use",
        "utilizes": "uses",
        "numerous": "many",
        "individuals": "people",
        "purchase": "buy",
        "purchased": "bought",
        "assist": "help",
        "assistance": "help",
        "commence": "start",
        "terminate": "end",
        "demonstrate": "show",
        "require": "need",
        "requirements": "needs",
        "obtain": "get",
        "subsequently": "later",
        "therefore": "so",
        "however": "but",
        "additional": "extra",
        "difficult": "hard",
        "immediately": "right away",
        "information": "details",
        "individual": "person",
        "regarding": "about",
        "frequently": "often",
        "approximately": "about"
    }

    for difficult, simple in replacements.items():

        text = re.sub(
            rf"\b{re.escape(difficult)}\b",
            simple,
            text,
            flags=re.IGNORECASE
        )

    # Shorten some common sentence structures
    text = re.sub(
        r"\bin order to\b",
        "to",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\bdue to the fact that\b",
        "because",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\bat this point in time\b",
        "now",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\bhas the ability to\b",
        "can",
        text,
        flags=re.IGNORECASE
    )

    return text.strip()


# ============================================================
# PROFESSIONAL ENGLISH
# ============================================================

def professional_english_local(text):

    text = clean_casual_text(text)

    # Common casual replacements

    replacements = {

        r"\bI want\b":
            "I would like",

        r"\bi need\b":
            "I would like",

        r"\bI need some\b":
            "I would appreciate some",

        r"\bI can't\b":
            "I will not be able to",

        r"\bI cant\b":
            "I will not be able to",

        r"\bI don't\b":
            "I do not",

        r"\bdon't\b":
            "do not",

        r"\bcan you\b":
            "Could you please",

        r"\bCan you\b":
            "Could you please",

        r"\bsend me\b":
            "please send me",

        r"\btell me\b":
            "please let me know",

        r"\bASAP\b":
            "at your earliest convenience",

        r"\bfast\b":
            "at your earliest convenience"
    }

    for pattern, replacement in replacements.items():

        text = re.sub(
            pattern,
            replacement,
            text,
            flags=re.IGNORECASE
        )

    # Remove unnecessary repeated spaces

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    # Capitalize first letter

    if text:

        text = (
            text[0].upper()
            + text[1:]
        )

    # Add professional punctuation

    if text and text[-1] not in ".!?":

        text += "."

    return text


# ============================================================
# SHORTEN TEXT
# ============================================================

def shorten_text_local(text):

    sentences = _sentences(text)

    words = text.split()

    # Very short text
    if len(words) <= 12:

        return text

    # One sentence
    if len(sentences) == 1:

        # Remove common unnecessary phrases

        result = text

        unnecessary = [

            "very ",
            "really ",
            "basically ",
            "actually ",
            "in order to ",
            "at this point in time ",
            "due to the fact that "
        ]

        for phrase in unnecessary:

            result = re.sub(
                re.escape(phrase),
                "",
                result,
                flags=re.IGNORECASE
            )

        if len(result.split()) < len(words):

            return result.strip()

        # Keep approximately 70%
        target = max(
            10,
            int(len(words) * 0.7)
        )

        return (
            " ".join(words[:target])
            + "..."
        )

    # ========================================================
    # Multiple sentences
    # ========================================================

    # 2 sentences -> keep 1
    if len(sentences) == 2:

        return sentences[0]

    # 3 sentences -> keep 2
    elif len(sentences) == 3:

        selected = sentences[:2]

    # 4+ sentences -> keep about 60%
    else:

        keep_count = max(
            2,
            round(len(sentences) * 0.6)
        )

        selected = sentences[:keep_count]

    result = " ".join(
        selected
    )

    # Remove unnecessary phrases

    result = re.sub(
        r"\bvery\s+",
        "",
        result,
        flags=re.IGNORECASE
    )

    result = re.sub(
        r"\breally\s+",
        "",
        result,
        flags=re.IGNORECASE
    )

    result = re.sub(
        r"\bbasically\s+",
        "",
        result,
        flags=re.IGNORECASE
    )

    result = re.sub(
        r"\bin order to\b",
        "to",
        result,
        flags=re.IGNORECASE
    )

    return result.strip()


# ============================================================
# BULLET POINTS
# ============================================================

def bullet_points_local(text):

    sentences = _sentences(text)

    points = []

    # --------------------------------------------------------
    # Convert each sentence into one bullet
    # --------------------------------------------------------

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        # Remove existing bullet symbols

        sentence = re.sub(
            r"^[\-\*\•\●\▪\◦]+\s*",
            "",
            sentence
        )

        # Remove final punctuation

        sentence = sentence.rstrip(
            ".!?"
        )

        # Make sure first letter is capitalized

        if sentence:

            sentence = (
                sentence[0].upper()
                + sentence[1:]
            )

            points.append(
                "• " + sentence
            )

    # --------------------------------------------------------
    # If sentence detection failed
    # --------------------------------------------------------

    if not points:

        return "• " + text.strip()

    return "\n".join(
        points
    )


# ============================================================
# EMAIL MODE
# ============================================================

def email_mode_local(text):

    cleaned = clean_casual_text(text)

    # Remove existing casual greeting

    cleaned = re.sub(
        r"^(hi|hello|hey)"
        r"(\s+(sir|madam|mam|ma'am))?"
        r"[,!\s]*",
        "",
        cleaned,
        flags=re.IGNORECASE
    ).strip()

    # Professionalize the message

    body = professional_english_local(
        cleaned
    )

    # --------------------------------------------------------
    # Generate simple subject
    # --------------------------------------------------------

    lower_text = cleaned.lower()

    if (
        "meeting" in lower_text
        and (
            "cannot" in lower_text
            or "can't" in lower_text
            or "cant" in lower_text
            or "attend" in lower_text
        )
    ):

        subject = "Request to Reschedule Meeting"

    elif "leave" in lower_text:

        subject = "Leave Request"

    elif "project" in lower_text:

        subject = "Project Update"

    elif "exam" in lower_text:

        subject = "Request Regarding Exam"

    elif "report" in lower_text:

        subject = "Report Request"

    else:

        subject = "Request"

    # --------------------------------------------------------
    # Complete email
    # --------------------------------------------------------

    email = (
        f"Subject: {subject}\n\n"
        f"Dear Sir/Madam,\n\n"
        f"{body}\n\n"
        f"Thank you for your time and consideration.\n\n"
        f"Yours sincerely,\n"
        f"[Your Name]"
    )

    return email


# ============================================================
# MAIN CONVERSION FUNCTION
# ============================================================

def convert_text(text, option):

    text = text.strip()

    # --------------------------------------------------------
    # Use API if available
    # --------------------------------------------------------

    if using_api():

        try:

            return _ask_api(
                option,
                text
            )

        except Exception as e:

            st.warning(
                "API conversion failed. "
                "Using free local NLP instead."
            )

    # --------------------------------------------------------
    # FREE LOCAL NLP
    # --------------------------------------------------------

    if option == "Simple English":

        return simple_english_local(
            text
        )

    elif option == "Professional English":

        return professional_english_local(
            text
        )

    elif option == "Shorten Text":

        return shorten_text_local(
            text
        )

    elif option == "Bullet Points":

        return bullet_points_local(
            text
        )

    elif option == "Email Mode":

        return email_mode_local(
            text
        )

    return text