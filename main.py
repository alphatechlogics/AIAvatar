import streamlit as st
import requests
import time
import json
from io import BytesIO
from PIL import Image

# ------------------------------
# Helper Functions
# ------------------------------


def get_presigned_url(api_key: str, file_size: int, content_type: str) -> dict:
    """
    Call LightX's uploadImageUrl endpoint to get a presigned URL for uploading the image.
    """
    url = "https://api.lightxeditor.com/external/api/v2/uploadImageUrl"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }
    data = {
        # Options: "maskedImageUrl", "imageUrl", "styleImageUrl"
        "uploadType": "maskedImageUrl",
        "size": file_size,
        "contentType": content_type
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()


def upload_file_to_s3(presigned_url: str, file_bytes: bytes, content_type: str) -> bool:
    """
    Upload the image file to the provided presigned S3 URL.
    """
    headers = {"Content-Type": content_type}
    response = requests.put(presigned_url, headers=headers, data=file_bytes)
    return response.status_code == 200


def request_generation(api_key: str, endpoint: str, image_url: str, text_prompt: str) -> dict:
    """
    Request AI generation (Avatar or Cartoon) from LightX.
    """
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }
    data = {
        "imageUrl": image_url,
        # Using same URL for style; adjust if needed.
        "styleImageUrl": image_url,
        "textPrompt": text_prompt
    }
    response = requests.post(endpoint, headers=headers, json=data)
    return response.json()


def check_order_status(api_key: str, order_id: str) -> dict:
    """
    Check the status of the generation order.
    """
    url = "https://api.lightxeditor.com/external/api/v1/order-status"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }
    data = {"orderId": order_id}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

# ------------------------------
# Main App
# ------------------------------


def main():
    st.set_page_config(page_title="LightX AI Services", layout="wide")
    st.title("LightX AI Services")
    st.markdown("### Generate Your Personalized AI Output")
    st.write(
        "Upload your photo and choose one of the options below to transform it using LightX APIs."
    )

    # Sidebar instructions with documentation links
    st.sidebar.header("Instructions")
    st.sidebar.markdown(
        """
        **Step 1:** Enter your LightX API Key.  
        **Step 2:** Upload your image (JPG/JPEG/PNG, under 2MB).  
        **Step 3:** Select a service:
        - **AI Avatar:** Generates a realistic, personalized avatar.  
          [API Docs](https://docs.lightxeditor.com/api/ai-avatar)
        - **AI Cartoon:** Transforms your photo into a professional full-body cartoon character with bold outlines.  
          [API Docs](https://docs.lightxeditor.com/api/ai-caricature-generator)
        **Step 4:** Enter a text prompt to guide the style.  
        **Step 5:** Click **Generate** to start the process.  
        The app will upload your image, request generation, poll for status, and display the final output.
        """
    )

    # User inputs
    api_key = st.text_input("Enter your LightX API Key", type="password")

    # Service selection: AI Avatar or AI Cartoon
    service_option = st.radio("Select Service", options=[
                              "AI Avatar", "AI Cartoon"])

    # Set default text prompt based on selection
    if service_option == "AI Avatar":
        default_prompt = "Turn my photo into a superhero avatar with realistic details"
    else:
        default_prompt = "Transform my photo into a full-body cartoon character with bold outlines, exaggerated features, and vibrant colors"

    text_prompt = st.text_input("Enter your text prompt", default_prompt)

    # Image uploader
    uploaded_file = st.file_uploader(
        "Upload your image (under 2MB)", type=["jpg", "jpeg", "png"])

    if st.button("Generate"):
        if not api_key:
            st.error("Please enter your LightX API Key.")
            return
        if not uploaded_file:
            st.error("Please upload an image.")
            return

        # Read image bytes and check file size
        file_bytes = uploaded_file.read()
        file_size = len(file_bytes)
        if file_size > 2_097_152:
            st.error("Image exceeds the 2MB limit. Please upload a smaller image.")
            return

        # Determine content type from extension
        filename = uploaded_file.name.lower()
        content_type = "image/png" if filename.endswith(
            ".png") else "image/jpeg"

        # Display the uploaded image
        image = Image.open(BytesIO(file_bytes)).convert("RGB")
        st.subheader("Uploaded Image")
        st.image(image, use_column_width=True)

        # 1) Request presigned URL from LightX
        st.write("Requesting presigned upload URL from LightX...")
        presigned_response = get_presigned_url(
            api_key, file_size, content_type)
        if presigned_response.get("statusCode") != 2000:
            st.error(
                f"Failed to get presigned URL. Response: {presigned_response}")
            return

        body = presigned_response.get("body", {})
        presigned_url = body.get("uploadImage")
        final_image_url = body.get("imageUrl") or body.get("maskedImageUrl")
        if not presigned_url or not final_image_url:
            st.error("Missing upload URL or final image URL in the response.")
            return

        # 2) Upload image to S3 using the presigned URL
        st.write("Uploading image to S3...")
        if not upload_file_to_s3(presigned_url, file_bytes, content_type):
            st.error("Image upload failed.")
            return
        st.success("Image uploaded successfully!")

        # 3) Determine endpoint based on service selection
        if service_option == "AI Avatar":
            endpoint = "https://api.lightxeditor.com/external/api/v1/avatar"
        else:
            endpoint = "https://api.lightxeditor.com/external/api/v1/cartoon"

        st.write(f"Requesting {service_option} generation from LightX...")
        gen_response = request_generation(
            api_key, endpoint, final_image_url, text_prompt)
        if gen_response.get("statusCode") != 2000:
            st.error(
                f"{service_option} request failed. Response: {gen_response}")
            return

        order_id = gen_response.get("body", {}).get("orderId")
        if not order_id:
            st.error("No orderId received from the generation request.")
            return

        st.write(f"{service_option} generation started. Order ID: {order_id}")

        # 4) Poll for order status (up to 5 retries, every 3 seconds)
        poll_count = 0
        max_retries = 5
        output_url = None
        st.write("Polling for order status...")
        while poll_count < max_retries:
            poll_count += 1
            time.sleep(3)
            status_response = check_order_status(api_key, order_id)
            if status_response.get("statusCode") != 2000:
                st.warning(f"Status check failed on attempt {poll_count}.")
                continue
            status = status_response.get("body", {}).get("status")
            st.write(f"Attempt {poll_count}: status = {status}")
            if status == "active":
                output_url = status_response.get("body", {}).get("output")
                break
            elif status == "failed":
                st.error(f"{service_option} generation failed.")
                return

        if not output_url:
            st.error("Generation timed out. Please try again.")
            return

        # 5) Display final output image
        st.subheader(f"Your {service_option} Output")
        st.image(output_url, use_column_width=True)


if __name__ == "__main__":
    main()
