# Numberplate Machine Learning

A school project for detecting license plates in images using machine learning, extracting the text, and fetching public vehicle data through an API.

---

## 🚀 Features
- Detects number plates in uploaded images  
- Reads text using OCR (EasyOCR)  
- Sends results to an API for retrieving vehicle data  
- Web interface built with Flask + HTML/CSS templates  
- Android app source code included  

---

## 📂 Project Structure
```
.
├── android_app_sourcecode/   # Android client app
├── static/                   # CSS, JS, assets
├── templates/                # HTML templates for Flask
├── app.py                    # Flask web server
├── config.py                 # Configuration settings
├── fetch_api.py              # API request logic
├── main.py                   # Main script entrypoint
├── read_plate.py             # Plate detection & OCR
├── requirements.txt          # Python dependencies
```

---

## 🛠️ Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/Actevitus/Numberplate-Machine-Learning.git
   cd Numberplate-Machine-Learning
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Linux/Mac
   venv\Scripts\activate      # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:
   ```bash
   python app.py
   ```

---

## 📱 Android App
The `android_app_sourcecode/` folder contains the mobile client code, which interacts with the backend to upload images and display results.

---

## ⚙️ Tech Stack
- **Backend:** Python, Flask  
- **ML & OCR:** OpenCV, EasyOCR, Pillow  
- **Frontend:** HTML, CSS  
- **Mobile:** Java (Android)  

---

## 📖 Usage
1. Start the Flask app.  
2. Open `http://127.0.0.1:5000` in a browser.  
3. Upload an image of a number plate.  
4. View extracted text and vehicle info.  

---

## 📌 Notes
- This is a school project; not production-ready.  
- Requires internet access for vehicle data API calls.  

- We already host an instance of the app, so if you're having trouble running it or downloading it yourself, you can navigate to: `http://209.38.197.151:5000`


---

## 📝 License
MIT License
