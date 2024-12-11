import streamlit as st
from groq import Groq
import cv2
import numpy as np

# Set page configuration
st.set_page_config(page_title="Mindful Companion", page_icon="🌱", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    /* Hide the default Streamlit header and footer */
    header, footer {visibility: hidden;}

    /* Set a subtle background gradient */
    body {
        background: linear-gradient(to bottom right, #f0f4f9, #cfe0f2);
        font-family: "Helvetica Neue", Arial, sans-serif;
    }

    /* Style main title */
    .main > div:nth-child(1) h1 {
        color: #1f3c88;
        font-size: 2.5em;
        font-weight: 600;
        margin-bottom: 0.5em;
    }

    /* Subtle styling for sidebar */
    .css-1d391kg, .css-18e3th9 {
        background-color: #e8ebf0 !important;
    }

    /* Chat messages styling */
    .markdown-text-container {
        font-size: 1.1em;
        line-height: 1.5em;
    }

    /* Make the button more modern */
    button[kind="primary"] {
        background-color: #1f3c88 !important;
        color: #ffffff !important;
        border-radius: 0.5em !important;
        font-weight: 600 !important;
        border: none !important;
    }

    /* Footer text */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        font-size: 0.9em;
        color: #333;
        padding: 0.5em;
    }
    </style>
""", unsafe_allow_html=True)

client = Groq(api_key=st.secrets["api_key"])

def wrap_text(text, font, font_scale, thickness, max_width):
    words = text.split(' ')
    wrapped_lines = []
    current_line = ""

    for word in words:
        test_line = word if not current_line else f"{current_line} {word}"
        (w, _), _ = cv2.getTextSize(test_line, font, font_scale, thickness)
        if w > max_width and current_line:
            wrapped_lines.append(current_line)
            current_line = word
        else:
            current_line = test_line

    if current_line:
        wrapped_lines.append(current_line)

    return wrapped_lines

def main():
    st.markdown("<h1>Serenity AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.2em; color:#333;'>Welcome to <b>Mindful Companion Chatbot</b>, your friendly guide to mental wellness and clarity.🌟</p>", unsafe_allow_html=True)

    if "COLL" not in st.session_state:
        st.session_state["COLL"] = []
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Hello! I'm here to listen and help you find balance and peace."}
        ]
    if "prescription_generated" not in st.session_state:
        st.session_state["prescription_generated"] = False

    # Sidebar for user details
    with st.sidebar:
        st.header("Your Details")
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=1, max_value=120, step=1)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        nationality = st.text_input("Nationality")
        preferences = st.text_area("Focus Areas")

    # Main content
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### Chat")
    for message in st.session_state["messages"]:
        if message["role"] == "assistant":
            st.markdown(f"**Mindful Companion:** {message['content']}")
        else:
            st.markdown(f"**You:** {message['content']}")

    user_input = st.text_input("Your Message", "")
    col1, col2 = st.columns([1,0.3])
    with col1:
        if st.button("Send"):
            if user_input:
                st.session_state["messages"].append({"role": "user", "content": user_input})
                sup = {m['role']: m['content'] for m in st.session_state['messages']}

                prompt = (
                    f"User Details:\n"
                    f"Name: {name}\n"
                    f"Age: {age}\n"
                    f"Gender: {gender}\n"
                    f"Nationality: {nationality}\n"
                    f"Preferences: {preferences}\n\n"
                    f"Chatbot Interaction:\n"
                    f"{''.join(sup)}"
                )

                completion = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "system", "content": prompt}],
                    temperature=1,
                    max_tokens=150,
                    top_p=1,
                    stream=False,
                    stop=None,
                )

                response = completion.choices[0].message.content
                st.session_state["COLL"].append(response)
                st.session_state["messages"].append({"role": "assistant", "content": response})
                st.markdown(response)
    with col2:
        if st.button("Get Collective Advice"):
            if st.session_state["COLL"]:
                summary_prompt = (
                    "You are a helpful assistant. The following are multiple responses you've given:\n\n"
                    + "\n".join(st.session_state["COLL"]) +
                    "\n\nPlease summarize these and give a collective, empathetic piece of advice on how to overcome the user's challenges."
                )
                summary_completion = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "system", "content": summary_prompt}],
                    temperature=1,
                    max_tokens=200,
                    top_p=1,
                    stream=False,
                    stop=None,
                )
                final_advice = summary_completion.choices[0].message.content
                st.markdown("**Collective Advice:**")
                st.markdown(final_advice)

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("Generate Prescription"):
        if not st.session_state["prescription_generated"]:
            if name and age and gender:
                image_path = "detected_text_areas.jpg"
                image = cv2.imread(image_path)

                if image is None:
                    st.error(f"Failed to load image from path: {image_path}. Please check the image path.")
                else:
                    title = "Mr." if gender == "Male" else "Miss." if gender == "Female" else ""
                    formatted_name = f"{title} {name}"

                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.7
                    font_color = (0, 0, 0)
                    thickness = 1

                    # Name
                    name_coords = (170, 420)
                    cv2.putText(image, formatted_name, name_coords, font, font_scale, font_color, thickness)

                    # Age
                    age_coords = (620, 520)
                    cv2.putText(image, f"{age}", age_coords, font, font_scale, font_color, thickness)

                    # Responses
                    response_text = " ".join(st.session_state["COLL"])
                    max_text_width = 500
                    lines = wrap_text(response_text, font, font_scale, thickness, max_text_width)

                    resp_start_x, resp_start_y = 200, 620
                    line_height = 25
                    for i, line in enumerate(lines):
                        y_position = resp_start_y + i * line_height
                        cv2.putText(image, line, (resp_start_x, y_position), font, font_scale, font_color, thickness)

                    output_path = "output_prescription.jpeg"
                    cv2.imwrite(output_path, image)

                    st.image(image, caption="Your Personalized Prescription", use_column_width=True)
                    st.success("Prescription generated successfully!")
                    st.session_state["prescription_generated"] = True
            else:
                st.error("Please provide your Name, Age, and Gender to generate the prescription.")
    
    # Footer
    st.markdown("<div class='footer'>© Team CodeCore</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
