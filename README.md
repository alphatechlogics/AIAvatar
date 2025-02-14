# LightX AI Services 🚀

Welcome to the **LightX AI Services** app! This Streamlit application lets you transform your personal photo into either a personalized AI Avatar or a professional full-body cartoon character using the LightX APIs.

---

## Overview 📖

**LightX AI Avatar**  
Generate realistic, high-quality avatars that preserve your unique facial features—perfect for gaming, social media, or digital identity.  
[LightX AI Avatar API Docs](https://docs.lightxeditor.com/api/ai-avatar)

**LightX AI Cartoon**  
Transform your photo into a stylized, full-body cartoon character with bold outlines, exaggerated features, and vibrant colors—ideal for creative projects and marketing materials.  
[LightX AI Cartoon API Docs](https://docs.lightxeditor.com/api/ai-caricature-generator)

The app workflow includes:

- **Image Upload:** Upload your image (JPG/JPEG/PNG under 2MB).
- **Presigned URL Request:** Retrieve a presigned URL from LightX for image upload.
- **Image Upload to S3:** Upload your image using the presigned URL.
- **Generation Request:** Call the appropriate LightX endpoint (Avatar or Cartoon) with your image URL and text prompt.
- **Order Status Polling:** Poll the status (up to 5 retries, every 3 seconds) until the output is ready.
- **Display Output:** Show the final generated image.

---

## Features ✨

- **Two Service Options:**
  - **AI Avatar:** Generate a realistic, personalized avatar.
  - **AI Cartoon:** Transform your photo into a full-body cartoon character.
- **Simple Image Upload:** Easy-to-use interface to upload your photo.
- **Custom Text Prompt:** Provide a prompt to guide the style of the output.
- **Automated Polling:** Automatically checks for order completion.
- **User-Friendly UI:** Built with Streamlit for an interactive experience.

---

## Requirements 📋

- Python 3.8+
- [Streamlit](https://streamlit.io/)
- [Requests](https://pypi.org/project/requests/)
- [Pillow](https://pillow.readthedocs.io/)
- A valid LightX API key (get one from the LightX API portal)

---

## Installation 🛠️

1. **Clone the repository or download `main.py`:**

   ```bash
   git clone https://github.com/alphatechlogics/AIAvatar.git
   cd AIAvatar
   ```

2. **Create and activate a virtual environment:**

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. **Install required packages:**

```bash
pip install -r requirements.txt
```

## Usage ▶️

1. **Run the app:**

```bash
streamlit run main.py
```

2. **In the app:**

- Enter your LightX API Key.
- Upload your image (must be under 2MB).
- Select the service:
  - AI Avatar for a realistic, personalized avatar.
  - AI Cartoon for a professional full-body cartoon.
- Enter a text prompt to customize your output (e.g., "Turn my photo into a superhero avatar" or "Transform my photo into a cartoon character with bold outlines").
- Click Generate.

The app will upload your image, request generation, poll for status, and finally display your output image.
