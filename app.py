# app.py - COMPLETE FINAL VERSION WITH gTTS (No credit card needed)
from flask import Flask, request, jsonify, render_template_string, session
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os
import json
import gc
import tensorflow as tf
from werkzeug.utils import secure_filename

# NEW IMPORTS FOR gTTS (Audio generation without saving files)
import io
import base64
from gtts import gTTS

# Import our modules
from garbage_collection import clear_memory, print_memory, cleanup_variables
from translation import get_care, get_language_name, CARE_DATA, get_ui_text
from speech import build_speech_text, clean_text_for_speech, get_speech_language

app = Flask(__name__)
app.secret_key = 'plant_care_secret'
CORS(app)

# ============================================
# CONFIGURATION
# ============================================
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# ============================================
# LOAD MODEL
# ============================================
print("\nLoading Plant Care...")
print_memory()

model = None
class_names = []

try:
    model = load_model('model/plant_care_model.h5')
    print("Model loaded")
except:
    try:
        model = load_model('plant_care_model.h5')
        print("Model loaded from root")
    except:
        print("Model not found! Run train_model.py first")
        exit()

try:
    with open('model/class_names.json', 'r') as f:
        class_names = json.load(f)
    print(f"{len(class_names)} classes loaded")
except:
    try:
        with open('class_names.json', 'r') as f:
            class_names = json.load(f)
        print(f"{len(class_names)} classes loaded from root")
    except:
        print("Class names not found")
        exit()

# Disease name translations
DISEASE_TRANSLATIONS = {
    'en': {
        'Rice___Brown_Spot': 'Rice Brown Spot',
        'Rice___Healthy': 'Rice Healthy',
        'Rice___Leaf_Blast': 'Rice Leaf Blast',
        'Rice___Neck_Blast': 'Rice Neck Blast',
        'Potato___Early_Blight': 'Potato Early Blight',
        'Potato___Healthy': 'Potato Healthy',
        'Potato___Late_Blight': 'Potato Late Blight'
    },
    'ne': {
        'Rice___Brown_Spot': 'धानको खैरो थोप्ले रोग',
        'Rice___Healthy': 'स्वस्थ धान',
        'Rice___Leaf_Blast': 'धानको पात मरुवा रोग',
        'Rice___Neck_Blast': 'धानको बोट मरुवा रोग',
        'Potato___Early_Blight': 'आलुको जल्द पाला रोग',
        'Potato___Healthy': 'स्वस्थ आलु',
        'Potato___Late_Blight': 'आलुको पछौटे डढुवा रोग'
    }
}

# ============================================
# HTML - COMPLETE FINAL VERSION
# ============================================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="{{ current_lang }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plant Care</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }

        /* ===== HEADER ===== */
        .app-header {
            background: #1a3a2b;
            padding: 1rem 2.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            border-radius: 16px;
            max-width: 900px;
            width: 100%;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            position: relative;
        }

        .logo-area {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding-left: 0.5rem;
        }

        .logo-icon {
            font-size: 1.8rem;
            color: #a8d5a2;
        }

        .app-title {
            color: #f0f7ec;
            font-size: 1.8rem;
            font-weight: 700;
            letter-spacing: -0.5px;
        }

        .header-nav {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            padding-right: 0.5rem;
        }

        .nav-btn {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid #4a7a5a;
            color: #d4e8cf;
            padding: 0.4rem 1.2rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.25s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.3rem;
            min-width: 80px;
            height: 34px;
        }

        .nav-btn:hover {
            background: rgba(255, 255, 255, 0.16);
            border-color: #6a9a7a;
            color: #ffffff;
            transform: scale(1.03);
        }

        .nav-btn i {
            font-size: 0.9rem;
            color: #a8d5a2;
        }

        .nav-btn-tutorial {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid #4a7a5a;
            color: #d4e8cf;
        }

        .nav-btn-tutorial:hover {
            background: rgba(255, 255, 255, 0.16);
            border-color: #6a9a7a;
            color: #ffffff;
        }

        .nav-btn-lang {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid #4a7a5a;
            color: #d4e8cf;
        }

        .nav-btn-lang:hover {
            background: rgba(255, 255, 255, 0.16);
            border-color: #6a9a7a;
            color: #ffffff;
        }

        /* ===== MAIN TITLE ===== */
        .main-title {
            font-size: 2.8rem;
            font-weight: 800;
            color: #1b5e20;
            text-align: center;
            margin-bottom: 4px;
            letter-spacing: -1px;
            text-shadow: 0 4px 20px rgba(27, 94, 32, 0.12);
        }
        .main-title .sub {
            font-size: 1rem;
            font-weight: 400;
            color: #43a047;
            display: block;
            margin-top: 2px;
            letter-spacing: 1.5px;
        }

        /* ===== CONTAINER ===== */
        .container {
            background: white;
            border-radius: 24px;
            padding: 30px 35px 35px 35px;
            max-width: 700px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.08);
        }

        /* ===== PLANT INFO ===== */
        .plant-info {
            text-align: center;
            margin-bottom: 14px;
        }
        .plant-info .info-label {
            color: #558b2f;
            font-size: 0.95rem;
            font-weight: 500;
            margin-right: 6px;
        }
        .badge {
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.95rem;
            font-weight: 600;
            display: inline-block;
            margin: 0 3px;
        }
        .badge-rice { background: #fef3c7; color: #92400e; }
        .badge-potato { background: #fde8e8; color: #9b2c2c; }

        /* ===== UPLOAD AREA ===== */
        #dropZone {
            border: 2px dashed #a5d6a7;
            border-radius: 16px;
            padding: 35px 20px;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
            background: #f1f8e9;
            position: relative;
            z-index: 1;
        }
        #dropZone:hover { border-color: #43a047; background: #e8f5e9; }
        #dropZone.dragover { border-color: #2e7d32; background: #c8e6c9; }
        #dropZone.has-image { padding: 15px 20px; }
        .upload-icon { font-size: 56px; margin-bottom: 8px; }
        .hint { color: #81c784; font-size: 14px; margin-top: 4px; }
        .btn-upload {
            display: inline-block;
            padding: 10px 28px;
            background: linear-gradient(135deg, #43a047, #2e7d32);
            color: white;
            border-radius: 10px;
            cursor: pointer;
            margin-top: 12px;
            font-size: 14px;
            font-weight: 600;
            transition: transform 0.2s;
            border: none;
            position: relative;
            z-index: 1;
        }
        .btn-upload:hover { transform: scale(1.05); }
        .btn-upload-small {
            padding: 8px 20px;
            font-size: 13px;
            margin-top: 8px;
        }
        #fileInput { display: none; }
        #preview {
            max-width: 100%;
            max-height: 250px;
            margin: 10px auto;
            border-radius: 12px;
            display: none;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        #preview.show { display: block; }

        .image-container {
            text-align: center;
            width: 100%;
            position: relative;
        }

        .remove-image-btn {
            position: absolute;
            top: 0px;
            right: 0px;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: #f44336;
            color: white;
            border: none;
            font-size: 18px;
            cursor: pointer;
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 10;
            transition: all 0.3s;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        .remove-image-btn:hover {
            transform: scale(1.1);
            background: #d32f2f;
        }
        .remove-image-btn.show {
            display: flex;
        }

        .analyze-wrapper { margin-top: 16px; width: 100%; }
        .btn-predict {
            background: linear-gradient(135deg, #43a047, #2e7d32);
            color: white;
            border: none;
            padding: 14px 40px;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
            position: relative;
            z-index: 1;
            box-shadow: 0 4px 15px rgba(46, 125, 50, 0.3);
        }
        .btn-predict:hover:not(:disabled) {
            transform: scale(1.02);
            box-shadow: 0 6px 25px rgba(46,125,50,0.4);
        }
        .btn-predict:disabled { opacity: 0.5; cursor: not-allowed; box-shadow: none; }

        #loading { display: none; text-align: center; padding: 25px; }
        .spinner { border: 4px solid #e8f5e9; border-top: 4px solid #43a047; border-radius: 50%; width: 45px; height: 45px; animation: spin 1s linear infinite; margin: 0 auto 12px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .loading-text { color: #558b2f; font-size: 15px; font-weight: 500; }

        #result {
            margin-top: 18px;
            padding: 20px;
            border-radius: 16px;
            display: none;
            animation: slideDown 0.5s ease-out;
            position: relative;
            z-index: 1;
        }
        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .healthy { background: #e8f5e9; border: 2px solid #43a047; }
        .disease { background: #ffebee; border: 2px solid #e53935; }
        .result-icon { font-size: 48px; text-align: center; }
        .result-name { font-size: 22px; font-weight: 700; text-align: center; margin: 8px 0; color: #1b5e20; }
        .result-confidence { text-align: center; color: #558b2f; font-size: 14px; }
        .progress-bar { width: 100%; height: 10px; background: #e0e0e0; border-radius: 5px; margin-top: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #43a047, #2e7d32); transition: width 0.8s ease-out; border-radius: 5px; }
        .result-status { text-align: center; margin-top: 12px; font-size: 14px; font-weight: 500; }

        .care-section { margin-top: 18px; padding: 16px; background: #f5f5f5; border-radius: 12px; display: none; }
        .care-section.visible { display: block; }

        .care-title {
            font-size: 18px;
            font-weight: 700;
            color: #2e7d32;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .btn-speech-green {
            background: transparent;
            border: none;
            cursor: pointer;
            padding: 4px;
            color: #2E7D32;
            font-size: 24px;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            display: flex;
            align-items: center;
            margin-left: 4px;
        }

        .btn-speech-green:hover {
            transform: scale(1.1);
        }

        .btn-speech-green.speaking {
            color: transparent;
            -webkit-text-stroke: 2.5px #2E7D32;
            transform: scale(1.25);
        }

        .translation-badge { display: inline-block; background: #43a047; color: white; font-size: 10px; padding: 2px 10px; border-radius: 12px; margin-left: 4px; font-weight: 600; }

        .care-section-block {
            margin: 10px 0;
            padding: 12px 14px;
            border-radius: 10px;
            background: #f9f9f9;
            border-left: 4px solid #43a047;
        }
        .care-section-block h4 { color: #2e7d32; margin-bottom: 6px; font-size: 14px; font-weight: 600; }
        .care-section-block ul { padding-left: 20px; margin: 0; }
        .care-section-block ul li { margin-bottom: 4px; color: #333; font-size: 14px; line-height: 1.5; }
        .care-section-block p { margin: 0; color: #333; font-size: 14px; line-height: 1.5; }
        .care-section-block strong { color: #2e7d32; }
        .care-section-block.notice { border-left-color: #ff9800; background: #fff3e0; }

        .footer { text-align: center; margin-top: 18px; color: #a5d6a7; font-size: 12px; }

        /* Tutorial Modal */
        .tutorial-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 99999;
            justify-content: center;
            align-items: center;
        }
        .tutorial-modal.show { display: flex; }
        .tutorial-modal-content {
            background: white;
            padding: 20px;
            border-radius: 20px;
            max-width: 800px;
            width: 90%;
            position: relative;
        }
        .tutorial-modal-content .close-btn {
            position: absolute;
            top: -15px;
            right: -15px;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #f44336;
            color: white;
            border: none;
            font-size: 24px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .tutorial-modal-content .close-btn:hover { background: #d32f2f; }
        .tutorial-modal-content .dummy-video {
            width: 100%;
            height: 400px;
            background: linear-gradient(135deg, #2e7d32, #43a047);
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
        }
        .tutorial-modal-content .dummy-video .big-icon { font-size: 100px; margin-bottom: 20px; }
        .tutorial-modal-content .dummy-video .lang-label { font-size: 16px; opacity: 0.8; margin-top: 10px; }

        @media (max-width: 650px) {
            .app-header {
                flex-direction: column;
                align-items: stretch;
                gap: 0.8rem;
                padding: 1rem 1.2rem;
            }
            .logo-area {
                justify-content: center;
                padding-left: 0;
            }
            .header-nav {
                justify-content: center;
                padding-right: 0;
            }
            .nav-btn {
                min-width: 60px;
                font-size: 0.75rem;
                padding: 0.3rem 0.8rem;
                height: 30px;
            }
            .app-title {
                font-size: 1.4rem;
            }
            .main-title {
                font-size: 2rem;
            }
            .container { padding: 20px; }
            .plant-info .info-label { font-size: 0.85rem; }
            .badge { font-size: 0.85rem; padding: 3px 10px; }
        }

        @media (max-width: 450px) {
            .app-title { font-size: 1.2rem; }
            .nav-btn { font-size: 0.7rem; padding: 0.2rem 0.6rem; min-width: 50px; height: 26px; }
            .header-nav { gap: 0.4rem; }
            .main-title { font-size: 1.6rem; }
            .main-title .sub { font-size: 0.8rem; }
            .container { padding: 14px; }
        }
    </style>
</head>
<body>
    <!-- ===== HEADER ===== -->
    <header class="app-header">
        <div class="logo-area">
            <span class="logo-icon">🌿</span>
            <span class="app-title" id="appTitle">Plant Care</span>
        </div>
        <div class="header-nav">
            <button class="nav-btn nav-btn-tutorial" id="tutorialBtn">
                <span id="tutorialLabel">Tutorial</span>
            </button>
            <button class="nav-btn nav-btn-lang" id="langToggle">
                <span id="langLabel">English ⇄ नेपाली</span>
            </button>
        </div>
    </header>

    <!-- MAIN TITLE -->
    <div class="main-title">
        <span class="sub" id="mainSubtitle">Smart Disease Detection for Your Plants</span>
    </div>

    <!-- TUTORIAL MODAL -->
    <div class="tutorial-modal" id="tutorialModal">
        <div class="tutorial-modal-content">
            <button class="close-btn" id="tutorialCloseBtn">✕</button>
            <div id="tutorialVideoContainer"></div>
        </div>
    </div>

    <!-- MAIN CONTAINER -->
    <div class="container">
        <div class="plant-info">
            <span class="info-label" id="plantInfoText">Currently diagnosable plants:</span>
            <span class="badge badge-rice" id="riceBadge">🌾 Rice</span>
            <span class="badge badge-potato" id="potatoBadge">🥔 Potato</span>
        </div>

        <div class="upload-area" id="dropZone">
            <div class="upload-icon" id="uploadIcon">📸</div>
            <p style="color: #2e7d32; font-weight: 500;" id="uploadText">Upload a leaf image</p>
            <p class="hint" id="hintText">Drag & drop or click to browse</p>
            <label class="btn-upload" for="fileInput" id="browseBtn">Choose Image</label>
            <input type="file" id="fileInput" accept="image/*">
            <div class="image-container">
                <img id="preview" alt="Preview">
                <button class="remove-image-btn" id="removeImageBtn">✕</button>
            </div>
            <label class="btn-upload btn-upload-small" for="fileInput" id="chooseAnotherBtn" style="display: none;">Choose Another Image</label>
        </div>

        <div class="analyze-wrapper">
            <button class="btn-predict" id="predictBtn" disabled>Analyze Plant</button>
        </div>

        <div id="loading">
            <div class="spinner"></div>
            <p class="loading-text" id="loadingText">Analyzing your plant...</p>
        </div>

        <div id="result">
            <div class="result-icon" id="resultIcon">✅</div>
            <div class="result-name" id="resultName">Healthy Plant</div>
            <div class="result-confidence" id="resultConfidence">Confidence: 95.0%</div>
            <div class="progress-bar"><div class="progress-fill" id="progressFill" style="width: 95%"></div></div>
            <div class="result-status" id="resultStatus">Your plant appears healthy!</div>

            <div class="care-section" id="careSection">
                <div class="care-title" id="careTitle">
                    <span id="careTitleText">Post Care Guidance</span>
                    <button class="btn-speech-green" id="speechGreenBtn" title="Listen to guidance">🔊</button>
                    <span class="translation-badge" id="langBadge">EN</span>
                </div>
                <div id="careSteps"></div>
            </div>
        </div>

        <div class="footer" id="footerText">Keep your plants healthy with Plant Care</div>
    </div>

    <script>
        // ============================================
        // UI TRANSLATIONS FROM BACKEND
        // ============================================
        const UI_TEXT = {{ ui_text | tojson | default('{}') }};
        const DISEASE_TRANSLATIONS = {{ disease_translations | tojson | default('{}') }};

        // ============================================
        // STATE
        // ============================================
        let currentLang = 'en';
        let selectedFile = null;
        let diseaseData = null;
        let isSpeaking = false;

        // ============================================
        // CONVERT ENGLISH NUMBER TO NEPALI
        // ============================================
        function toNepaliNumber(num) {
            const nepaliDigits = ['०', '१', '२', '३', '४', '५', '६', '७', '८', '९'];
            return num.toString().replace(/\d/g, d => nepaliDigits[parseInt(d)]);
        }

        // ============================================
        // DOM ELEMENTS
        // ============================================
        const el = {
            appTitle: document.getElementById('appTitle'),
            mainSubtitle: document.getElementById('mainSubtitle'),
            plantInfoText: document.getElementById('plantInfoText'),
            riceBadge: document.getElementById('riceBadge'),
            potatoBadge: document.getElementById('potatoBadge'),
            uploadText: document.getElementById('uploadText'),
            uploadIcon: document.getElementById('uploadIcon'),
            hintText: document.getElementById('hintText'),
            browseBtn: document.getElementById('browseBtn'),
            chooseAnotherBtn: document.getElementById('chooseAnotherBtn'),
            predictBtn: document.getElementById('predictBtn'),
            loadingText: document.getElementById('loadingText'),
            footerText: document.getElementById('footerText'),
            tutorialLabel: document.getElementById('tutorialLabel'),
            langLabel: document.getElementById('langLabel'),
            langToggle: document.getElementById('langToggle'),
            resultDiv: document.getElementById('result'),
            resultIcon: document.getElementById('resultIcon'),
            resultName: document.getElementById('resultName'),
            resultConfidence: document.getElementById('resultConfidence'),
            progressFill: document.getElementById('progressFill'),
            resultStatus: document.getElementById('resultStatus'),
            careSection: document.getElementById('careSection'),
            careTitle: document.getElementById('careTitle'),
            careTitleText: document.getElementById('careTitleText'),
            careSteps: document.getElementById('careSteps'),
            langBadge: document.getElementById('langBadge'),
            fileInput: document.getElementById('fileInput'),
            loadingDiv: document.getElementById('loading'),
            dropZone: document.getElementById('dropZone'),
            preview: document.getElementById('preview'),
            removeImageBtn: document.getElementById('removeImageBtn'),
            tutorialBtn: document.getElementById('tutorialBtn'),
            tutorialModal: document.getElementById('tutorialModal'),
            tutorialCloseBtn: document.getElementById('tutorialCloseBtn'),
            tutorialVideoContainer: document.getElementById('tutorialVideoContainer'),
            speechGreenBtn: document.getElementById('speechGreenBtn')
        };

        // ============================================
        // PLAY AUDIO FROM BASE64 (gTTS version)
        // ============================================
        function playAudioFromBase64(base64Data) {
            if (isSpeaking) {
                stopSpeaking();
                return;
            }

            const audio = new Audio('data:audio/mp3;base64,' + base64Data);

            audio.onplay = () => {
                isSpeaking = true;
                if (el.speechGreenBtn) {
                    el.speechGreenBtn.classList.add('speaking');
                }
            };

            audio.onended = () => {
                isSpeaking = false;
                if (el.speechGreenBtn) {
                    el.speechGreenBtn.classList.remove('speaking');
                }
            };

            audio.play();
        }

        // ============================================
        // READ CARE INSTRUCTIONS
        // ============================================
        function readCareInstructions() {
            if (!diseaseData) {
                alert(currentLang === 'en' ? 'Please diagnose a plant first!' : 'कृपया पहिले बिरुवा निदान गर्नुहोस्!');
                return;
            }

            if (isSpeaking) {
                stopSpeaking();
                return;
            }

            fetch(`/api/speech_text?lang=${currentLang}`)
                .then(res => res.json())
                .then(data => {
                    if (data.success && data.audio_base64) {
                        playAudioFromBase64(data.audio_base64);
                    } else {
                        alert(currentLang === 'en' ? 'Error generating audio' : 'अडियो उत्पन्न गर्न त्रुटि');
                    }
                })
                .catch(() => {
                    alert(currentLang === 'en' ? 'Network error. Check your internet!' : 'नेटवर्क त्रुटि। आफ्नो इन्टरनेट जाँच गर्नुहोस्!');
                });
        }

        // ============================================
        // STOP SPEAKING
        // ============================================
        function stopSpeaking() {
            document.querySelectorAll('audio').forEach(audio => audio.pause());
            isSpeaking = false;
            if (el.speechGreenBtn) {
                el.speechGreenBtn.classList.remove('speaking');
            }
        }

        // ============================================
        // REMOVE IMAGE FUNCTION
        // ============================================
        function removeImage() {
            selectedFile = null;
            diseaseData = null;
            el.preview.src = '';
            el.preview.classList.remove('show');
            el.removeImageBtn.classList.remove('show');
            el.predictBtn.disabled = true;
            el.resultDiv.style.display = 'none';
            el.careSection.classList.remove('visible');
            stopSpeaking();

            el.uploadIcon.style.display = 'block';
            el.uploadText.style.display = 'block';
            el.hintText.style.display = 'block';
            el.browseBtn.style.display = 'inline-block';
            el.chooseAnotherBtn.style.display = 'none';
            el.dropZone.classList.remove('has-image');
            el.fileInput.value = '';
        }

        // ============================================
        // TRANSLATION FUNCTION
        // ============================================
        function translatePage(lang) {
            fetch(`/api/get_ui_text?lang=${lang}`)
                .then(res => res.json())
                .then(uiText => {
                    Object.assign(UI_TEXT, uiText);
                    applyTranslations(lang);
                })
                .catch(() => {
                    applyTranslations(lang);
                });
        }

        function applyTranslations(lang) {
            const t = UI_TEXT;

            if (!t || typeof t !== 'object') {
                console.error('UI_TEXT not available');
                return;
            }

            console.log('Applying translations for:', lang);

            if (el.appTitle) {
                el.appTitle.textContent = lang === 'en' ? 'Plant Care' : 'प्लान्ट केयर';
            }
            if (el.mainSubtitle) {
                el.mainSubtitle.textContent = t.app_subtitle || 'Smart Disease Detection for Your Plants';
            }

            if (el.plantInfoText) el.plantInfoText.textContent = t.diagnosable_plants || 'Currently diagnosable plants:';

            if (el.riceBadge) {
                el.riceBadge.textContent = lang === 'en' ? '🌾 Rice' : '🌾 चामल';
            }
            if (el.potatoBadge) {
                el.potatoBadge.textContent = lang === 'en' ? '🥔 Potato' : '🥔 आलु';
            }

            if (el.uploadText) el.uploadText.textContent = t.upload_title || 'Upload a leaf image';
            if (el.hintText) el.hintText.textContent = t.upload_hint || 'Drag & drop or click to browse';
            if (el.browseBtn) el.browseBtn.textContent = t.browse_btn || 'Choose Image';
            if (el.chooseAnotherBtn) el.chooseAnotherBtn.textContent = t.choose_another_btn || 'Choose Another Image';
            if (el.predictBtn) el.predictBtn.textContent = t.analyze_btn || 'Analyze Plant';
            if (el.loadingText) el.loadingText.textContent = t.loading_text || 'Analyzing your plant...';
            if (el.footerText) el.footerText.textContent = t.footer || 'Keep your plants healthy with Plant Care';

            if (el.tutorialLabel) {
                let tutorialText = t.tutorial_btn || 'Tutorial';
                tutorialText = tutorialText.replace(/[🎓]/g, '').trim();
                el.tutorialLabel.textContent = tutorialText || 'Tutorial';
            }

            if (el.langLabel) {
                el.langLabel.textContent = lang === 'en' ? 'English ⇄ नेपाली' : 'नेपाली ⇄ अंग्रेजी';
            }

            if (diseaseData) {
                fetch(`/api/care/${encodeURIComponent(diseaseData.class)}?lang=${lang}`)
                    .then(res => res.json())
                    .then(careData => {
                        if (careData.success) {
                            diseaseData.care = careData.care;
                        }
                        displayResult(diseaseData);
                    })
                    .catch(() => {
                        displayResult(diseaseData);
                    });
            }

            if (el.careTitleText) {
                const titleText = lang === 'en' ? (t.care_title || 'Post Care Guidance') : (t.care_title || 'पश्चात् सेवा मार्गदर्शन');
                el.careTitleText.textContent = titleText;
            }
            if (el.langBadge) {
                el.langBadge.textContent = lang === 'en' ? 'EN' : 'ने';
            }

            currentLang = lang;
        }

        // ============================================
        // DISPLAY RESULT
        // ============================================
        function displayResult(data) {
            const isHealthy = data.class.includes('Healthy');
            const t = UI_TEXT;
            const lang = currentLang;

            let displayName = data.class;
            if (DISEASE_TRANSLATIONS[lang] && DISEASE_TRANSLATIONS[lang][data.class]) {
                displayName = DISEASE_TRANSLATIONS[lang][data.class];
            } else {
                displayName = data.class.replace(/_/g, ' ');
            }

            el.resultDiv.className = isHealthy ? 'healthy' : 'disease';

            let emoji = isHealthy ? '✅' : '⚠️';
            let statusText = isHealthy ? (t.resultHealthy || 'Your plant appears healthy!') : (t.resultDisease || 'Disease detected!');

            el.resultIcon.textContent = emoji;
            el.resultName.textContent = displayName;

            let confidenceText = data.confidence.toFixed(2);
            let confidenceLabel = lang === 'en' ? 'Confidence' : 'विश्वसनीयता';
            if (lang === 'ne') {
                confidenceText = toNepaliNumber(data.confidence.toFixed(2));
                el.resultConfidence.textContent = `${confidenceLabel}: ${confidenceText}%`;
            } else {
                el.resultConfidence.textContent = `${confidenceLabel}: ${confidenceText}%`;
            }

            el.progressFill.style.width = `${data.confidence}%`;
            el.resultStatus.textContent = statusText;
            el.resultStatus.style.color = isHealthy ? '#2e7d32' : '#c62828';

            if (data.care) {
                el.careSection.classList.add('visible');

                const titleText = lang === 'en' ? (t.care_title || 'Post Care Guidance') : (t.care_title || 'पश्चात् सेवा मार्गदर्शन');
                el.careTitleText.textContent = titleText;
                const badge = lang === 'en' ? 'EN' : 'ने';
                el.langBadge.textContent = badge;

                let html = '';

                let hasImmediateActions = data.care.immediate_actions && data.care.immediate_actions.length > 0;
                let hasTreatmentOptions = data.care.treatment_options && data.care.treatment_options.length > 0;

                if (hasImmediateActions || hasTreatmentOptions) {
                    html += `<div class="care-section-block"><h4>${t.what_to_do || 'What to do now'}</h4>`;

                    if (hasImmediateActions) {
                        html += `<p><strong>${t.immediate_actions || 'Immediate Actions'}:</strong></p>
                                 <ul>`;
                        data.care.immediate_actions.forEach(action => {
                            html += `<li>${action}</li>`;
                        });
                        html += `</ul>`;
                    }

                    if (hasTreatmentOptions) {
                        html += `<p><strong>${t.treatment_options || 'Treatment Options'}:</strong></p>
                                 <ul>`;
                        data.care.treatment_options.forEach(option => {
                            html += `<li>${option}</li>`;
                        });
                        html += `</ul>`;
                    }

                    html += `</div>`;
                }

                if (data.care.prevention) {
                    html += `
                        <div class="care-section-block">
                            <h4>${t.prevention || 'Prevention'}</h4>
                            <p>${data.care.prevention}</p>
                        </div>
                    `;
                }

                if (data.care.safety_warnings && data.care.safety_warnings.length > 0) {
                    html += `
                        <div class="care-section-block">
                            <h4>${t.safety_warnings || 'Safety warnings'}</h4>
                            <ul>
                                ${data.care.safety_warnings.map(a => `<li>${a}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }

                if (data.care.notice) {
                    html += `
                        <div class="care-section-block notice">
                            <h4>${t.notice || 'Notice'}</h4>
                            <p>${data.care.notice}</p>
                        </div>
                    `;
                }

                el.careSteps.innerHTML = html;
            } else {
                el.careSection.classList.remove('visible');
            }

            el.resultDiv.style.display = 'block';
        }

        // ============================================
        // TUTORIAL
        // ============================================
        function showTutorial() {
            const container = el.tutorialVideoContainer;
            if (currentLang === 'en') {
                container.innerHTML = `
                    <div class="dummy-video">
                        <div class="big-icon">🎓</div>
                        <div>Plant Care Tutorial</div>
                        <div style="font-size:18px; margin-top:10px;">How to diagnose your plant diseases</div>
                        <div class="lang-label">English Tutorial</div>
                        <div style="font-size:14px; margin-top:20px; opacity:0.7;">
                            Step 1: Upload leaf image<br>
                            Step 2: Click Analyze<br>
                            Step 3: View results & care
                        </div>
                    </div>
                `;
            } else {
                container.innerHTML = `
                    <div class="dummy-video">
                        <div class="big-icon">🎓</div>
                        <div>प्लान्ट केयर ट्यूटोरियल</div>
                        <div style="font-size:18px; margin-top:10px;">आफ्नो बिरुवाको रोग कसरी पत्ता लगाउने</div>
                        <div class="lang-label">नेपाली ट्यूटोरियल</div>
                        <div style="font-size:14px; margin-top:20px; opacity:0.7;">
                            चरण १: पातको फोटो अपलोड गर्नुहोस्<br>
                            चरण २: विश्लेषण क्लिक गर्नुहोस्<br>
                            चरण ३: नतिजा र हेरचाह हेर्नुहोस्
                        </div>
                    </div>
                `;
            }
            el.tutorialModal.classList.add('show');
        }

        function closeTutorial() {
            el.tutorialModal.classList.remove('show');
        }

        // ============================================
        // FILE UPLOAD
        // ============================================
        el.fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                selectedFile = this.files[0];
                el.predictBtn.disabled = false;
                el.resultDiv.style.display = 'none';
                el.careSection.classList.remove('visible');
                diseaseData = null;

                const reader = new FileReader();
                reader.onload = (e) => {
                    el.preview.src = e.target.result;
                    el.preview.classList.add('show');
                    el.removeImageBtn.classList.add('show');
                    el.uploadIcon.style.display = 'none';
                    el.uploadText.style.display = 'none';
                    el.hintText.style.display = 'none';
                    el.browseBtn.style.display = 'none';
                    el.chooseAnotherBtn.style.display = 'inline-block';
                    el.dropZone.classList.add('has-image');
                };
                reader.readAsDataURL(selectedFile);
            }
        });

        el.dropZone.addEventListener('dragover', (e) => { e.preventDefault(); el.dropZone.classList.add('dragover'); });
        el.dropZone.addEventListener('dragleave', () => el.dropZone.classList.remove('dragover'));
        el.dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                selectedFile = e.dataTransfer.files[0];
                el.predictBtn.disabled = false;
                el.resultDiv.style.display = 'none';
                el.careSection.classList.remove('visible');
                diseaseData = null;
                el.fileInput.files = e.dataTransfer.files;
                const reader = new FileReader();
                reader.onload = (e) => {
                    el.preview.src = e.target.result;
                    el.preview.classList.add('show');
                    el.removeImageBtn.classList.add('show');
                    el.uploadIcon.style.display = 'none';
                    el.uploadText.style.display = 'none';
                    el.hintText.style.display = 'none';
                    el.browseBtn.style.display = 'none';
                    el.chooseAnotherBtn.style.display = 'inline-block';
                    el.dropZone.classList.add('has-image');
                };
                reader.readAsDataURL(selectedFile);
            }
        });

        el.removeImageBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            removeImage();
        });

        // ============================================
        // PREDICT
        // ============================================
        el.predictBtn.addEventListener('click', async function() {
            if (!selectedFile) return;

            const formData = new FormData();
            formData.append('file', selectedFile);

            this.disabled = true;
            el.loadingDiv.style.display = 'block';
            el.resultDiv.style.display = 'none';
            el.careSection.classList.remove('visible');

            try {
                const response = await fetch('/api/predict', { method: 'POST', body: formData });
                const data = await response.json();
                el.loadingDiv.style.display = 'none';

                if (data.success) {
                    diseaseData = data;
                    const careResponse = await fetch(`/api/care/${encodeURIComponent(data.class)}?lang=${currentLang}`);
                    const careData = await careResponse.json();
                    if (careData.success) {
                        diseaseData.care = careData.care;
                    }
                    displayResult(diseaseData);
                } else {
                    el.resultDiv.style.display = 'block';
                    el.resultDiv.className = 'disease';
                    el.resultIcon.textContent = '❌';
                    el.resultName.textContent = 'Error';
                    el.resultStatus.textContent = data.error || 'Unknown error';
                }
            } catch (error) {
                el.loadingDiv.style.display = 'none';
                el.resultDiv.style.display = 'block';
                el.resultDiv.className = 'disease';
                el.resultIcon.textContent = '❌';
                el.resultName.textContent = 'Connection Error';
                el.resultStatus.textContent = error.message;
            }

            this.disabled = false;
        });

        // ============================================
        // EVENT LISTENERS
        // ============================================
        el.langToggle.addEventListener('click', function() {
            const newLang = currentLang === 'en' ? 'ne' : 'en';
            translatePage(newLang);
        });

        el.speechGreenBtn.addEventListener('click', readCareInstructions);

        el.tutorialBtn.addEventListener('click', showTutorial);
        el.tutorialCloseBtn.addEventListener('click', closeTutorial);
        el.tutorialModal.addEventListener('click', function(e) {
            if (e.target === this) closeTutorial();
        });

        // ============================================
        // INITIALIZATION
        // ============================================
        window.addEventListener('load', function() {
            translatePage('en');
        });
    </script>
</body>
</html>
'''

# ============================================
# API ROUTES
# ============================================

@app.route('/')
def index():
    """Serve the main page with all translations"""
    ui_text = get_ui_text('en')
    return render_template_string(
        HTML_TEMPLATE,
        ui_text=ui_text,
        current_lang='en',
        disease_translations=DISEASE_TRANSLATIONS
    )

@app.route('/api/get_ui_text')
def get_ui_text_api():
    """Get UI translations for a specific language"""
    lang = request.args.get('lang', 'en')
    ui_text = get_ui_text(lang)
    return jsonify(ui_text)

@app.route('/api/speech_text', methods=['GET'])
def get_speech_text():
    """Generate audio using gTTS (No credit card, no storage needed!)"""
    try:
        lang = request.args.get('lang', 'en')
        
        # Get the disease class from the session (saved when you analyzed the image)
        disease_class = session.get('last_disease_class')
        if not disease_class:
            return jsonify({'success': False, 'error': 'No disease data available'}), 400
        
        # Get care instructions from your translation.py
        care = get_care(disease_class, lang)
        disease_data = {'class': disease_class, 'care': care}
        ui_text = get_ui_text(lang)
        
        # Build the clean text using your speech.py (removes emojis)
        text = build_speech_text(disease_data, ui_text, lang)
        
        # ============================================
        # gTTS GENERATION CODE (Happens in RAM, no file saved)
        # ============================================
        # Google needs 'ne' for Nepali, or 'en' for English
        tts_lang = 'ne' if lang == 'ne' else 'en'
        
        # Create the audio file IN MEMORY (doesn't touch your hard drive)
        tts = gTTS(text=text, lang=tts_lang, slow=False) 
        
        # Save it to a temporary RAM buffer
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0) # Rewind the buffer back to the start
        
        # Convert the audio bytes to Base64 text so we can send it over the internet to the browser
        audio_base64 = base64.b64encode(audio_bytes.read()).decode('utf-8')
        # ============================================
        
        return jsonify({
            'success': True,
            'audio_base64': audio_base64, # Send audio to browser
            'language': lang
        })
        
    except Exception as e:
        print(f"Speech error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        img = image.load_img(filepath, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0

        predictions = model.predict(img_array, verbose=0)
        predicted_idx = np.argmax(predictions)
        predicted_class = class_names[predicted_idx]
        confidence = np.max(predictions) * 100

        os.remove(filepath)
        cleanup_variables(img, img_array, predictions)

        # Save to session for speech feature
        session['last_disease_class'] = predicted_class

        lang = request.args.get('lang', 'en')
        care = get_care(predicted_class, lang)

        return jsonify({
            'success': True,
            'class': predicted_class,
            'confidence': float(confidence),
            'care': care,
            'language': lang
        })

    except Exception as e:
        print(f"Prediction error: {e}")
        import traceback
        traceback.print_exc()
        clear_memory()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/care/<path:disease>', methods=['GET'])
def get_care_api(disease):
    lang = request.args.get('lang', 'en')
    care = get_care(disease, lang)
    return jsonify({
        'success': True,
        'care': care,
        'language': lang
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'app': 'Plant Care',
        'model_loaded': model is not None,
        'classes': len(class_names),
        'memory_mb': print_memory()
    })

@app.teardown_appcontext
def cleanup(error):
    clear_memory()

# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("PLANT CARE - COMPLETE FINAL VERSION")
    print("=" * 50)
    print(f"Detects: {len(class_names)} plant conditions")
    print(f"Languages: English + Nepali (FULL TRANSLATION)")
    print(f"Read Out Loud: Google gTTS (No credit card needed!)")
    print(f"Server: http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    app.run(debug=True, threaded=True)