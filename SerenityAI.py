import streamlit as st
from groq import Groq
import cv2
import numpy as np

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
    st.title("Serenity AI")
    st.markdown("Welcome to **Serenity AI - Mindful Companion Chatbot**, your friendly wellness consultant! 🌟")

    if "COLL" not in st.session_state:
        st.session_state["COLL"] = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Hi there, I'm your wellness consultant! 🌟"}
        ]

    if "prescription_generated" not in st.session_state:
        st.session_state["prescription_generated"] = False

    st.sidebar.header("Your Details")
    name = st.sidebar.text_input("Name")
    age = st.sidebar.number_input("Age", min_value=1, max_value=120, step=1)
    gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
    nationality = st.sidebar.text_input("Nationality")
    preferences = st.sidebar.text_area("Anything you'd like us to focus on?")

    st.markdown("Let's start your journey to clarity and balance! 💖")

    st.markdown("---")
    st.markdown("### Chat")

    for message in st.session_state["messages"]:
        if message["role"] == "assistant":
            st.markdown(f"**Mindful Companion:** {message['content']}")
        else:
            st.markdown(f"**You:** {message['content']}")

    user_input = st.text_input("Your Message", "")
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

    # New button to get collective advice
    if st.button("Get Collective Advice"):
        if st.session_state["COLL"]:
            summary_prompt = (
                "You are a helpful assistant. The following are multiple responses you've given to a user:\n\n"
                + "\n".join(st.session_state["COLL"]) +
                "\n\nPlease summarize all these responses and give a collective, generous piece of advice on how they can overcome their problems."
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

    if st.button("Generate Prescription"):
        if not st.session_state["prescription_generated"]:
            if name and age and gender:
                image_path = "detected_text_areas.jpg"  # Adjust if needed
                image = cv2.imread(image_path)

                if image is None:
                    st.error(f"Failed to load image from path: {image_path}. Please check the image path.")
                else:
                    title = "Mr." if gender == "Male" else "Miss." if gender == "Female" else ""
                    formatted_name = f"{title} {name}"

                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.7  # Reduced text size
                    font_color = (0, 0, 0)  
                    thickness = 1

                    # Name
                    name_coords = (170, 420)
                    cv2.putText(image, formatted_name, name_coords, font, font_scale, font_color, thickness)

                    # Age
                    age_coords = (620, 520)
                    cv2.putText(image, f"{age}", age_coords, font, font_scale, font_color, thickness)

                    # Wrap and add responses
                    response_text = " ".join(st.session_state["COLL"])
                    max_text_width = 500  # Slightly narrower for better wrapping
                    lines = wrap_text(response_text, font, font_scale, thickness, max_text_width)

                    resp_start_x, resp_start_y = 100, 620
                    line_height = 25
                    for i, line in enumerate(lines):
                        y_position = resp_start_y + i * line_height
                        cv2.putText(image, line, (resp_start_x, y_position), font, font_scale, font_color, thickness)

                    output_path = "output_prescription.jpeg"
                    cv2.imwrite(output_path, image)

                    st.image(image, caption="Processed Image", use_column_width=True)
                    st.image(output_path, caption="Generated Prescription")
                    st.success("Prescription generated successfully!")
                    st.session_state["prescription_generated"] = True
            else:
                st.error("Please provide your Name, Age, and Gender to generate the prescription.")

if __name__ == "__main__":
    main()
