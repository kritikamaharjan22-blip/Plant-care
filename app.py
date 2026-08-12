# app.py - COMPLETE UPDATED VERSION
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

# Import our modules
from garbage_collection import clear_memory, print_memory, cleanup_variables
from translation import get_care, get_language_name, CARE_DATA, get_ui_text, get_tutorial_steps

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
print("\n🌿 Loading Plant Care...")
print_memory()

model = None
class_names = []

try:
    model = load_model('model/plant_care_model.h5')
    print("✅ Model loaded")
except:
    try:
        model = load_model('plant_care_model.h5')
        print("✅ Model loaded from root")
    except:
        print("❌ Model not found! Run train_model.py first")
        exit()

try:
    with open('model/class_names.json', 'r') as f:
        class_names = json.load(f)
    print(f"✅ {len(class_names)} classes loaded")
except:
    try:
        with open('class_names.json', 'r') as f:
            class_names = json.load(f)
        print(f"✅ {len(class_names)} classes loaded from root")
    except:
        print("❌ Class names not found")
        exit()

# ============================================
# HTML - COMPLETE UPDATED VERSION
# ============================================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="{{ current_lang }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌿 Plant Care</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px;
            position: relative;
        }
        
        .main-title {
            font-size: 56px;
            font-weight: 800;
            color: #1b5e20;
            text-align: center;
            margin-bottom: 20px;
            letter-spacing: -1px;
            text-shadow: 0 4px 20px rgba(27, 94, 32, 0.15);
            position: relative;
            z-index: 1;
        }
        .main-title .leaf { font-size: 48px; }
        .main-title .sub {
            font-size: 18px;
            font-weight: 400;
            color: #43a047;
            display: block;
            margin-top: 4px;
            letter-spacing: 2px;
        }

        .container {
            background: white;
            border-radius: 24px;
            padding: 35px 40px 40px 40px;
            max-width: 700px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            position: relative;
            z-index: 1;
        }

        .header {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        .header .btn-sm {
            padding: 8px 18px;
            border: none;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
            z-index: 100;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .header .btn-sm:hover { transform: scale(1.05); }
        .header .btn-sm .emoji { font-size: 20px; }
        
        .btn-tutorial { background: #ff9800; color: white; }
        
        .lang-toggle {
            background: #e8f5e9;
            padding: 8px 16px;
            border-radius: 25px;
            border: 2px solid #a5d6a7;
            cursor: pointer;
            font-size: 14px;
            font-weight: 700;
            color: #2e7d32;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
            position: relative;
            z-index: 100;
        }
        .lang-toggle:hover { background: #c8e6c9; transform: scale(1.05); }
        .lang-toggle .lang-icon { font-size: 20px; }

        .badges { display: flex; justify-content: center; gap: 10px; margin-bottom: 15px; }
        .badge { padding: 4px 16px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .badge-rice { background: #fef3c7; color: #92400e; }
        .badge-potato { background: #fde8e8; color: #9b2c2c; }

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
        .care-title { font-size: 18px; font-weight: 700; color: #2e7d32; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }
        .translation-badge { display: inline-block; background: #43a047; color: white; font-size: 10px; padding: 2px 10px; border-radius: 12px; margin-left: 8px; font-weight: 600; }
        
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
        .care-section-block.note { border-left-color: #ff9800; background: #fff3e0; }

        .footer { text-align: center; margin-top: 18px; color: #a5d6a7; font-size: 12px; }

        /* Tutorial Modal - Video Popup */
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
        .tutorial-modal-content .video-container {
            position: relative;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
        }
        .tutorial-modal-content .video-container iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
            border-radius: 10px;
        }
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

        @media (max-width: 600px) {
            .main-title { font-size: 32px; }
            .main-title .leaf { font-size: 30px; }
            .main-title .sub { font-size: 14px; }
            .container { padding: 20px; }
            .header { gap: 8px; }
            .header .btn-sm { font-size: 12px; padding: 6px 12px; }
            .header .btn-sm .emoji { font-size: 16px; }
            .lang-toggle { font-size: 12px; padding: 6px 12px; }
            .tutorial-modal-content .dummy-video { height: 250px; font-size: 18px; }
            .tutorial-modal-content .dummy-video .big-icon { font-size: 60px; }
        }
    </style>
</head>
<body>
    <!-- MAIN TITLE -->
    <div class="main-title">
        <span class="leaf">🌿</span> <span id="appTitle">PLANT CARE</span>
        <span class="sub" id="mainSubtitle">Smart Disease Detection for Your Plants</span>
    </div>

    <!-- TUTORIAL MODAL -->
    <div class="tutorial-modal" id="tutorialModal">
        <div class="tutorial-modal-content">
            <button class="close-btn" id="tutorialCloseBtn">✕</button>
            <div id="tutorialVideoContainer">
                <!-- Dummy video/placeholder - will be replaced by JS -->
            </div>
        </div>
    </div>

    <!-- MAIN CONTAINER -->
    <div class="container" id="mainContainer">
        <div class="header">
            <button class="btn-sm btn-tutorial" id="tutorialBtn">
                <span class="emoji">🎓</span> <span id="tutorialLabel">Tutorial</span>
            </button>
            <button class="lang-toggle" id="langToggle">
                <span class="lang-icon" id="langIcon">🇬🇧</span>
                <span id="langLabel">EN</span>
            </button>
        </div>

        <div class="badges">
            <span class="badge badge-rice">🌾 Rice</span>
            <span class="badge badge-potato">🥔 Potato</span>
        </div>

        <!-- Upload Area -->
        <div class="upload-area" id="dropZone">
            <div class="upload-icon" id="uploadIcon">📸</div>
            <p style="color: #2e7d32; font-weight: 500;" id="uploadText">Upload a leaf image</p>
            <p class="hint" id="hintText">Drag &amp; drop or click to browse</p>
            <label class="btn-upload" for="fileInput" id="browseBtn">📁 Choose Image</label>
            <input type="file" id="fileInput" accept="image/*">
            
            <!-- Image preview container -->
            <div class="image-container">
                <img id="preview" alt="Preview">
            </div>
            
            <!-- Choose Another Image button (hidden by default) -->
            <label class="btn-upload btn-upload-small" for="fileInput" id="chooseAnotherBtn" style="display: none;">📁 Choose Another Image</label>
        </div>

        <div class="analyze-wrapper">
            <button class="btn-predict" id="predictBtn" disabled>🔍 Analyze Plant</button>
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
            <div class="result-status" id="resultStatus">🌿 Your plant appears healthy!</div>

            <div class="care-section" id="careSection">
                <div class="care-title" id="careTitle">📋 Post Care Guidance <span class="translation-badge" id="langBadge">EN</span></div>
                <div id="careSteps"></div>
            </div>
        </div>

        <div class="footer" id="footerText">🌱 Keep your plants healthy with Plant Care</div>
    </div>

    <script>
        // ============================================
        // UI TRANSLATIONS - Convert flat to nested if needed
        // ============================================
        const rawUI_TEXT = {{ ui_text | tojson | default('{}') }};
        const TUTORIAL_STEPS = {{ tutorial_steps | tojson | default('[]') }};

        // Build UI_TEXT with proper nested structure
        let UI_TEXT = {};

        // Check if rawUI_TEXT is already nested
        if (rawUI_TEXT.en && typeof rawUI_TEXT.en === 'object' && rawUI_TEXT.en.app_subtitle) {
            UI_TEXT = rawUI_TEXT;
        } else {
            // Flat format - wrap it
            UI_TEXT = {
                'en': rawUI_TEXT,
                'ne': rawUI_TEXT
            };
            // If we have both translations, use them
            if (rawUI_TEXT.ne && typeof rawUI_TEXT.ne === 'object') {
                UI_TEXT.ne = rawUI_TEXT.ne;
            }
        }

        console.log('🔍 UI_TEXT loaded:', Object.keys(UI_TEXT));
        console.log('🔍 TUTORIAL_STEPS loaded:', TUTORIAL_STEPS.length);

        // ============================================
        // STATE
        // ============================================
        let currentLang = 'en';
        let selectedFile = null;
        let diseaseData = null;
        let isSpeaking = false;
        let speechSynth = window.speechSynthesis;
        let hasImage = false;

        // ============================================
        // DOM REFERENCES
        // ============================================
        const elements = {
            appTitle: document.getElementById('appTitle'),
            mainSubtitle: document.getElementById('mainSubtitle'),
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
            langIcon: document.getElementById('langIcon'),
            langToggle: document.getElementById('langToggle'),
            resultDiv: document.getElementById('result'),
            resultIcon: document.getElementById('resultIcon'),
            resultName: document.getElementById('resultName'),
            resultConfidence: document.getElementById('resultConfidence'),
            progressFill: document.getElementById('progressFill'),
            resultStatus: document.getElementById('resultStatus'),
            careSection: document.getElementById('careSection'),
            careTitle: document.getElementById('careTitle'),
            careSteps: document.getElementById('careSteps'),
            langBadge: document.getElementById('langBadge'),
            fileInput: document.getElementById('fileInput'),
            loadingDiv: document.getElementById('loading'),
            dropZone: document.getElementById('dropZone'),
            preview: document.getElementById('preview'),
            tutorialBtn: document.getElementById('tutorialBtn'),
            tutorialModal: document.getElementById('tutorialModal'),
            tutorialCloseBtn: document.getElementById('tutorialCloseBtn'),
            tutorialVideoContainer: document.getElementById('tutorialVideoContainer')
        };

        // ============================================
        // TRANSLATION FUNCTION - FULL PAGE TRANSLATION
        // ============================================
        function translatePage(lang) {
            // Get translations for the requested language
            let t = UI_TEXT[lang] || UI_TEXT['en'];
            
            if (!t || typeof t !== 'object') {
                console.error('❌ Translations not available for:', lang);
                t = UI_TEXT['en'] || {};
            }
            
            // Update app title
            if (elements.appTitle) {
                elements.appTitle.textContent = t.app_title || 'PLANT CARE';
            }
            
            // Update main title subtitle
            if (elements.mainSubtitle) {
                elements.mainSubtitle.textContent = t.app_subtitle || 'Smart Disease Detection for Your Plants';
            }
            
            // Update upload area - ALL TEXT
            if (elements.uploadText) elements.uploadText.textContent = t.upload_title || 'Upload a leaf image';
            if (elements.hintText) elements.hintText.textContent = t.upload_hint || 'Drag & drop or click to browse';
            if (elements.browseBtn) elements.browseBtn.textContent = t.browse_btn || '📁 Choose Image';
            if (elements.chooseAnotherBtn) elements.chooseAnotherBtn.textContent = t.choose_another_btn || '📁 Choose Another Image';
            if (elements.predictBtn) elements.predictBtn.textContent = t.analyze_btn || '🔍 Analyze Plant';
            if (elements.loadingText) elements.loadingText.textContent = t.loading_text || 'Analyzing your plant...';
            if (elements.footerText) elements.footerText.textContent = t.footer || '🌱 Keep your plants healthy with Plant Care';
            
            // Update tutorial button
            if (elements.tutorialLabel) elements.tutorialLabel.textContent = t.tutorial_btn || '🎓 Tutorial';
            
            // Update language toggle - show OPPOSITE language name
            if (elements.langLabel) {
                elements.langLabel.textContent = lang === 'en' ? 'नेपाली' : 'English';
            }
            if (elements.langIcon) {
                elements.langIcon.textContent = lang === 'en' ? '🇳🇵' : '🇬🇧';
            }
            
            // Update result status if exists
            if (diseaseData) {
                displayResult(diseaseData);
            }
            
            // Update care section title
            updateCareSectionTitle();
            
            currentLang = lang;
        }

        function updateCareSectionTitle() {
            if (elements.careTitle) {
                const titleText = currentLang === 'en' ? '📋 Post Care Guidance' : '📋 पोस्ट केयर गाइडेन्स';
                const badge = currentLang === 'en' ? 'EN' : 'ने';
                elements.careTitle.innerHTML = titleText + ' <span class="translation-badge" id="langBadge">' + badge + '</span>';
            }
            if (elements.langBadge) {
                elements.langBadge.textContent = currentLang === 'en' ? 'EN' : 'ने';
            }
        }

        // ============================================
        // TUTORIAL - Video Popup
        // ============================================
        function showTutorial() {
            const modal = elements.tutorialModal;
            const container = elements.tutorialVideoContainer;
            
            if (currentLang === 'en') {
                container.innerHTML = `
                    <div class="dummy-video">
                        <div class="big-icon">🎓</div>
                        <div>🌿 Plant Care Tutorial</div>
                        <div style="font-size:18px; margin-top:10px;">How to diagnose your plant diseases</div>
                        <div class="lang-label">🔊 English Tutorial</div>
                        <div style="font-size:14px; margin-top:20px; opacity:0.7;">
                            📸 Step 1: Upload leaf image<br>
                            🔍 Step 2: Click Analyze<br>
                            📋 Step 3: View results & care
                        </div>
                    </div>
                `;
            } else {
                container.innerHTML = `
                    <div class="dummy-video">
                        <div class="big-icon">🎓</div>
                        <div>🌿 प्लान्ट केयर ट्यूटोरियल</div>
                        <div style="font-size:18px; margin-top:10px;">आफ्नो बिरुवाको रोग कसरी पत्ता लगाउने</div>
                        <div class="lang-label">🔊 नेपाली ट्यूटोरियल</div>
                        <div style="font-size:14px; margin-top:20px; opacity:0.7;">
                            📸 चरण १: पातको फोटो अपलोड गर्नुहोस्<br>
                            🔍 चरण २: विश्लेषण क्लिक गर्नुहोस्<br>
                            📋 चरण ३: नतिजा र हेरचाह हेर्नुहोस्
                        </div>
                    </div>
                `;
            }
            
            modal.classList.add('show');
        }

        function closeTutorial() {
            elements.tutorialModal.classList.remove('show');
        }

        // ============================================
        // FILE UPLOAD - UPDATED
        // ============================================
        elements.fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                selectedFile = this.files[0];
                hasImage = true;
                elements.predictBtn.disabled = false;
                elements.resultDiv.style.display = 'none';
                elements.careSection.classList.remove('visible');
                diseaseData = null;
                
                const reader = new FileReader();
                reader.onload = (e) => {
                    elements.preview.src = e.target.result;
                    elements.preview.classList.add('show');
                    // Hide upload icon and text, show the image
                    elements.uploadIcon.style.display = 'none';
                    elements.uploadText.style.display = 'none';
                    elements.hintText.style.display = 'none';
                    elements.browseBtn.style.display = 'none';
                    // Show "Choose Another Image" button
                    elements.chooseAnotherBtn.style.display = 'inline-block';
                    elements.dropZone.classList.add('has-image');
                };
                reader.readAsDataURL(selectedFile);
            }
        });

        elements.dropZone.addEventListener('dragover', (e) => { e.preventDefault(); elements.dropZone.classList.add('dragover'); });
        elements.dropZone.addEventListener('dragleave', () => elements.dropZone.classList.remove('dragover'));
        elements.dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                selectedFile = e.dataTransfer.files[0];
                hasImage = true;
                elements.predictBtn.disabled = false;
                elements.resultDiv.style.display = 'none';
                elements.careSection.classList.remove('visible');
                diseaseData = null;
                elements.fileInput.files = e.dataTransfer.files;
                const reader = new FileReader();
                reader.onload = (e) => {
                    elements.preview.src = e.target.result;
                    elements.preview.classList.add('show');
                    elements.uploadIcon.style.display = 'none';
                    elements.uploadText.style.display = 'none';
                    elements.hintText.style.display = 'none';
                    elements.browseBtn.style.display = 'none';
                    elements.chooseAnotherBtn.style.display = 'inline-block';
                    elements.dropZone.classList.add('has-image');
                };
                reader.readAsDataURL(selectedFile);
            }
        });

        // ============================================
        // PREDICT
        // ============================================
        elements.predictBtn.addEventListener('click', async function() {
            if (!selectedFile) return;

            const formData = new FormData();
            formData.append('file', selectedFile);

            this.disabled = true;
            elements.loadingDiv.style.display = 'block';
            elements.resultDiv.style.display = 'none';
            elements.careSection.classList.remove('visible');

            try {
                console.log('📤 Sending prediction request...');
                const response = await fetch('/api/predict', { 
                    method: 'POST', 
                    body: formData 
                });
                
                console.log('📥 Response status:', response.status);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('📦 Response data:', data);

                elements.loadingDiv.style.display = 'none';

                if (data.success) {
                    diseaseData = data;
                    await fetchAndDisplayResults(data.class, data.confidence);
                } else {
                    elements.resultDiv.style.display = 'block';
                    elements.resultDiv.className = 'disease';
                    elements.resultIcon.textContent = '❌';
                    elements.resultName.textContent = 'Error';
                    elements.resultStatus.textContent = data.error || 'Unknown error';
                }
            } catch (error) {
                console.error('❌ Error:', error);
                elements.loadingDiv.style.display = 'none';
                elements.resultDiv.style.display = 'block';
                elements.resultDiv.className = 'disease';
                elements.resultIcon.textContent = '❌';
                elements.resultName.textContent = 'Connection Error';
                elements.resultStatus.textContent = error.message || 'Failed to connect to server';
            }

            this.disabled = false;
        });

        async function fetchAndDisplayResults(className, confidence) {
            const lang = currentLang;
            const response = await fetch(`/api/care/${encodeURIComponent(className)}?lang=${lang}`);
            const data = await response.json();

            if (data.success) {
                diseaseData = { class: className, confidence: confidence, care: data.care };
                displayResult(diseaseData);
            } else {
                displayResult({ class: className, confidence: confidence, care: null });
            }
        }

        // ============================================
        // DISPLAY RESULT - UPDATED with simplified care
        // ============================================
        function displayResult(data) {
            const isHealthy = data.class.includes('Healthy');
            const lang = currentLang;
            
            // Get translations for current language
            let t = UI_TEXT[lang] || UI_TEXT['en'];
            if (!t || typeof t !== 'object') {
                t = UI_TEXT['en'] || {};
            }

            elements.resultDiv.className = isHealthy ? 'healthy' : 'disease';

            let emoji = isHealthy ? '✅' : '⚠️';
            let statusText = isHealthy ? (t.resultHealthy || '🌿 Your plant appears healthy!') : (t.resultDisease || '⚠️ Disease detected!');

            elements.resultIcon.textContent = emoji;
            elements.resultName.textContent = data.class;
            elements.resultConfidence.textContent = `${lang === 'en' ? 'Confidence' : 'विश्वसनीयता'}: ${data.confidence.toFixed(2)}%`;
            elements.progressFill.style.width = `${data.confidence}%`;
            elements.resultStatus.textContent = statusText;
            elements.resultStatus.style.color = isHealthy ? '#2e7d32' : '#c62828';

            // Simplified Care Section - Only "What to do now" and "Note"
            if (data.care) {
                elements.careSection.classList.add('visible');
                updateCareSectionTitle();

                let html = '';

                // What to do now - immediate actions and treatment options combined
                const actions = [];
                if (data.care.immediate_actions && data.care.immediate_actions.length > 0) {
                    actions.push(...data.care.immediate_actions);
                }
                if (data.care.treatment_options && data.care.treatment_options.length > 0) {
                    actions.push(...data.care.treatment_options);
                }

                if (actions.length > 0) {
                    html += `
                        <div class="care-section-block">
                            <h4>${t.what_to_do || 'What to do now'}</h4>
                            <ul>
                                ${actions.map(a => `<li>${a}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }

                // Note - combines consult_doctor, safety_warnings, prevention, success_rate
                const notes = [];
                if (data.care.consult_doctor) notes.push(data.care.consult_doctor);
                if (data.care.safety_warnings && data.care.safety_warnings.length > 0) {
                    notes.push(...data.care.safety_warnings);
                }
                if (data.care.prevention) notes.push(data.care.prevention);
                if (data.care.success_rate) notes.push(data.care.success_rate);

                if (notes.length > 0) {
                    html += `
                        <div class="care-section-block note">
                            <h4>${t.note || 'Note'}</h4>
                            <ul>
                                ${notes.map(n => `<li>${n}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }

                elements.careSteps.innerHTML = html;
            } else {
                elements.careSection.classList.remove('visible');
            }

            elements.resultDiv.style.display = 'block';
        }

        // ============================================
        // EVENT LISTENERS
        // ============================================
        
        // Language toggle
        elements.langToggle.addEventListener('click', function() {
            const newLang = currentLang === 'en' ? 'ne' : 'en';
            translatePage(newLang);
        });

        // Tutorial button
        elements.tutorialBtn.addEventListener('click', showTutorial);
        elements.tutorialCloseBtn.addEventListener('click', closeTutorial);
        elements.tutorialModal.addEventListener('click', function(e) {
            if (e.target === this) closeTutorial();
        });

        // ============================================
        // INITIALIZATION
        // ============================================
        window.addEventListener('load', function() {
            translatePage('en');
            
            // Preload speech voices
            if (speechSynth) {
                speechSynth.getVoices();
            }
        });
    </script>
</body>
</html>
'''

# ============================================
# FLASK ROUTES
# ============================================

@app.route('/')
def index():
    """Serve the main page with all translations"""
    from translation import get_ui_text, get_tutorial_steps
    
    # Get translations
    ui_text = get_ui_text('en')
    tutorial_steps = get_tutorial_steps('en')
    
    # Debug: Check if data exists
    print(f"📝 UI Text keys: {list(ui_text.keys()) if ui_text else 'None'}")
    print(f"📝 Tutorial steps: {len(tutorial_steps) if tutorial_steps else 0}")
    
    return render_template_string(
        HTML_TEMPLATE,
        ui_text=ui_text,
        tutorial_steps=tutorial_steps,
        current_lang='en'
    )

@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict disease from uploaded image"""
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

        lang = session.get('language', 'en')
        care = get_care(predicted_class, lang)

        return jsonify({
            'success': True,
            'class': predicted_class,
            'confidence': float(confidence),
            'care': care,
            'language': lang
        })

    except Exception as e:
        print(f"❌ Prediction error: {e}")
        import traceback
        traceback.print_exc()
        clear_memory()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/care/<path:disease>', methods=['GET'])
def get_care_api(disease):
    """Get care instructions for a disease"""
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
        'language': session.get('language', 'en'),
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
    print("🌿 PLANT CARE - COMPLETE APP")
    print("=" * 50)
    print(f"📊 Detects: {len(class_names)} plant conditions")
    print(f"🗣️  Languages: English + Nepali (FULL TRANSLATION)")
    print(f"🚀 Server: http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    app.run(debug=True, threaded=True)