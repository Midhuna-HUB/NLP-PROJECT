import streamlit as st

from text_converter import convert_text, using_api


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Text Converter",
    page_icon="📝",
    layout="centered"
)


# ============================================================
# TITLE
# ============================================================

st.title("📝 AI Text Converter & Simplifier")

st.write(
    "Convert any text into simple, professional, shorter, "
    "bullet-point format, or a complete email using NLP."
)


# ============================================================
# INPUT
# ============================================================

text = st.text_area(
    "Enter your text",
    placeholder="Paste your text here...",
    height=250
)


# ============================================================
# CONVERSION OPTION
# ============================================================

option = st.selectbox(
    "Choose conversion type",
    [
        "Email Mode",
        "Professional English",
        "Simple English",
        "Shorten Text",
        "Bullet Points"
    ]
)


# ============================================================
# CONVERT BUTTON
# ============================================================

if st.button("✨ Convert Text"):

    if not text.strip():

        st.warning("Please enter some text.")

    else:

        try:

            with st.spinner("Processing your text..."):

                result = convert_text(
                    text,
                    option
                )

            # Always convert result into a string
            output_text = str(result)

            # Save result
            st.session_state["output_text"] = output_text
            st.session_state["input_words"] = len(
                text.split()
            )

        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )

            st.stop()


# ============================================================
# OUTPUT
# ============================================================

if "output_text" in st.session_state:

    output_text = st.session_state["output_text"]

    st.subheader("Converted Text")

    # Display result
    st.markdown(
        output_text.replace(
            "\n",
            "  \n"
        )
    )

    # Word count
    input_words = st.session_state["input_words"]
    output_words = len(output_text.split())

    engine = (
        "AI model (API)"
        if using_api()
        else "Free local NLP"
    )

    st.caption(
        f"Words: {input_words} → {output_words} | "
        f"Engine: {engine}"
    )

    # Download
    st.download_button(
        "⬇️ Download result",
        data=output_text,
        file_name="converted_text.txt",
        mime="text/plain"
    )

    # Copy
    with st.expander("📋 Copy text"):

        st.code(
            output_text,
            language=None
        )