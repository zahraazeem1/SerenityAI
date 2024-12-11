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
            # If adding the new word exceeds the width, push the current line and start a new one
            wrapped_lines.append(current_line)
            current_line = word
        else:
            current_line = test_line

    # Add the last line if it's not empty
    if current_line:
        wrapped_lines.append(current_line)

    return wrapped_lines

def main():
    st.title("Mindful Companion Chatbot")
    st.markdown("Welcome to **Mindful Companion**, your friendly wellness consultant! 🌟")

    # Initialize persistent state for COLL
    if "COLL" not in st.session_state:
        st.session_state["COLL"] = []

    # Collect user details
    st.sidebar.header("Your Details")
    name = st.sidebar.text_input("Name")
    age = st.sidebar.number_input("Age", min_value=1, max_value=120, step=1)
    gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
    nationality = st.sidebar.text_input("Nationality")
    preferences = st.sidebar.text_area("Anything you'd like us to focus on?")

    # Display a friendly message
    st.markdown("Let's start your journey to clarity and balance! 💖")

    # Chat interface
    st.markdown("---")
    st.markdown("### Chat")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content":
                f"Hi {name if name else 'there'}, I'm your wellness consultant! 🌟"}
        ]

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

            # Integrate user inputs into the chatbot prompt
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

            # Call Groq API
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
            st.session_state["COLL"].append(response)  # Persist response
            st.markdown(response)
            st.session_state["messages"].append({"role": "assistant", "content": response})

    # Generate Prescription Image
    if st.button("Generate Prescription"):
        if name and age and gender:
            # Load the prescription template
            image_path = "detected_text_areas.jpg"  # Replace with a relative path to your template
            image = cv2.imread(image_path)

            if image is None:
                st.error(f"Failed to load image from path: {image_path}. Please check the image path.")
            else:
                # Define title (Mr./Miss.) based on gender
                title = "Mr." if gender == "Male" else "Miss." if gender == "Female" else ""
                formatted_name = f"{title} {name}"

                # Define text properties
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1
                font_color = (0, 0, 0)  # Black text
                thickness = 2

                # Add Name
                name_coords = (170, 420)  # Adjust these based on your template
                cv2.putText(image, formatted_name, name_coords, font, font_scale, font_color, thickness)

                # Add Age
                age_coords = (620, 520)  # Adjust these based on your template
                cv2.putText(image, f"{age}", age_coords, font, font_scale, font_color, thickness)

                # Wrap the response text
                response_text = " ".join(st.session_state["COLL"])  # Join persisted responses
                max_text_width = 600  # Adjust as needed based on the image size and desired text width
                lines = wrap_text(response_text, font, font_scale, thickness, max_text_width)

                # Starting coordinates for the response text
                resp_start_x, resp_start_y = 200, 620  # Adjust these based on your template
                line_height = 30  # Adjust spacing between lines as needed

                # Write each line onto the image
                for i, line in enumerate(lines):
                    y_position = resp_start_y + i * line_height
                    cv2.putText(image, line, (resp_start_x, y_position), font, font_scale, font_color, thickness)

                # Save and display the final image
                output_path = "output_prescription.jpeg"
                cv2.imwrite(output_path, image)

                st.image(image, caption="Processed Image", use_column_width=True)
                st.image(output_path, caption="Generated Prescription")
                st.success("Prescription generated successfully!")
        else:
            st.error("Please provide your Name, Age, and Gender to generate the prescription.")

if __name__ == "__main__":
    main()
