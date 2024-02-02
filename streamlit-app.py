import streamlit as st
import requests

st.title("PyScript Runner")

# Create two columns for the layout
col1, col2 = st.columns(2)

# Left column for user inputs and submit button
with col1:
    st.subheader("Input")
    prompt = st.text_area("Prompt", "list all pipelines")
    service = st.text_input("Service", "seqera")
    token = st.text_input("Token", "token")

    # Submit button
    submitted = st.button("Submit")
    if submitted:
        # Make a POST request to the server
        response = requests.post(
            "http://127.0.0.1:5000/gen-script",  # Replace with your actual endpoint
            json={"service": service, "token": token, "prompt": prompt},
        )

        if response.status_code == 200:
            code = response.json().get("code", "")
        else:
            st.error("Error generating code.")

# ... rest of your code ...

# Right column for code display, run button, and output
with col2:
    st.subheader("Generated Code")
    code_display = st.empty()  # Placeholder for code display

    # Only display the run button if the code is available
    run_button = None
    if "code" in locals():
        run_button = st.button("Run Code")  # Run code button

    output_display = st.empty()  # Placeholder for output display

# Outside of the columns, after the placeholders have been created
if "submitted" in locals() and submitted and response.status_code == 200:
    # Update the code display
    code_display.code(code, language="python")

    # Display the PyScript HTML with the returned code
    html = f"""
    <html>
      <head>
        <link rel="stylesheet" href="https://pyscript.net/latest/pyscript.css" />
        <script defer src="https://pyscript.net/latest/pyscript.js"></script>
      </head>
      <body>
        <py-script>{code}</py-script>
      </body>
    </html>
    """
    # Correctly use st.components to render HTML content
    st.components.v1.html(html, height=300, scrolling=True)

# You can use the run_button to execute some action if needed
# but remember that Streamlit apps rerun from the top upon interaction
if run_button and run_button:
    # Logic to execute the Python code and display the output
    # This will need backend support to run the Python code safely
    pass
