# app.py - COMPLETE FINAL VERSION
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
            margin-bottom: 10px;
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

        .plant-info {
            text-align: center;
            margin-bottom: 12px;
        }
        .plant-info .info-label {
            color: #558b2f;
            font-size: 13px;
            font-weight: 500;
            margin-right: 8px;
        }
        .badge { 
            padding: 4px 16px; 
            border-radius: 20px; 
            font-size: 12px; 
            font-weight: 600; 
            display: inline-block;
            margin: 0 4px;
        }
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
        <span class="leaf">🌿</span> <span id="appTitle">Plant Care</span> <span class="leaf">🌿</span>
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
        <div class="header">
            <button class="btn-sm btn-tutorial" id="tutorialBtn">
                <span class="emoji">🎓</span> <span id="tutorialLabel">Tutorial</span>
            </button>
            <button class="lang-toggle" id="langToggle">
                <span class="lang-icon" id="langIcon">🇬🇧</span>
                <span id="langLabel">EN</span>
            </button>
        </div>

        <div class="plant-info">
            <span class="info-label" id="plantInfoText">Currently diagnosable plants:</span>
            <span class="badge badge-rice" id="riceBadge">🌾 Rice</span>
            <span class="badge badge-potato" id="potatoBadge">🥔 Potato</span>
        </div>

        <div class="upload-area" id="dropZone">
            <div class="upload-icon" id="uploadIcon">📸</div>
            <p style="color: #2e7d32; font-weight: 500;" id="uploadText">Upload a leaf image</p>
            <p class="hint" id="hintText">Drag &amp; drop or click to browse</p>
            <label class="btn-upload" for="fileInput" id="browseBtn">📁 Choose Image</label>
            <input type="file" id="fileInput" accept="image/*">
            <div class="image-container">
                <img id="preview" alt="Preview">
            </div>
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
        // UI TRANSLATIONS FROM BACKEND
        // ============================================
        const UI_TEXT = {{ ui_text | tojson | default('{}') }};
        const TUTORIAL_STEPS = {{ tutorial_steps | tojson | default('[]') }};
        const DISEASE_TRANSLATIONS = {{ disease_translations | tojson | default('{}') }};

        console.log('🔍 UI_TEXT loaded:', UI_TEXT);
        console.log('🔍 DISEASE_TRANSLATIONS loaded:', DISEASE_TRANSLATIONS);

        // ============================================
        // STATE
        // ============================================
        let currentLang = 'en';
        let selectedFile = null;
        let diseaseData = null;

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
        // TRANSLATION FUNCTION
        // ============================================
        function translatePage(lang) {
            // Fetch the right translations from backend
            fetch(`/api/get_ui_text?lang=${lang}`)
                .then(res => res.json())
                .then(uiText => {
                    // Update UI_TEXT with new translations
                    Object.assign(UI_TEXT, uiText);
                    applyTranslations(lang);
                })
                .catch(() => {
                    // Fallback: use existing UI_TEXT
                    applyTranslations(lang);
                });
        }

        function applyTranslations(lang) {
            const t = UI_TEXT;
            
            if (!t || typeof t !== 'object') {
                console.error('❌ UI_TEXT not available');
                return;
            }
            
            console.log('🔄 Applying translations for:', lang);
            
            // App title
            if (el.appTitle) el.appTitle.textContent = t.app_title || 'Plant Care';
            if (el.mainSubtitle) el.mainSubtitle.textContent = t.app_subtitle || 'Smart Disease Detection for Your Plants';
            
            // Plant info
            if (el.plantInfoText) el.plantInfoText.textContent = t.diagnosable_plants || 'Currently diagnosable plants:';
            
            // Badges - Rice and Potato translations
            if (el.riceBadge) {
                el.riceBadge.textContent = lang === 'en' ? '🌾 Rice' : '🌾 चामल';
            }
            if (el.potatoBadge) {
                el.potatoBadge.textContent = lang === 'en' ? '🥔 Potato' : '🥔 आलु';
            }
            
            // Upload area
            if (el.uploadText) el.uploadText.textContent = t.upload_title || 'Upload a leaf image';
            if (el.hintText) el.hintText.textContent = t.upload_hint || 'Drag & drop or click to browse';
            if (el.browseBtn) el.browseBtn.textContent = t.browse_btn || '📁 Choose Image';
            if (el.chooseAnotherBtn) el.chooseAnotherBtn.textContent = t.choose_another_btn || '📁 Choose Another Image';
            if (el.predictBtn) el.predictBtn.textContent = t.analyze_btn || '🔍 Analyze Plant';
            if (el.loadingText) el.loadingText.textContent = t.loading_text || 'Analyzing your plant...';
            if (el.footerText) el.footerText.textContent = t.footer || '🌱 Keep your plants healthy with Plant Care';
            
            // Tutorial button - single emoji
            if (el.tutorialLabel) el.tutorialLabel.textContent = t.tutorial_btn || 'Tutorial';
            
            // Translation button - swapping symbol
            if (el.langLabel) {
                el.langLabel.textContent = lang === 'en' ? '⇄ नेपाली' : '⇄ English';
            }
            if (el.langIcon) {
                el.langIcon.textContent = lang === 'en' ? '🇳🇵' : '🇬🇧';
            }
            
            // Update result if exists
            if (diseaseData) {
                displayResult(diseaseData);
            }
            
            // Update care title
            if (el.careTitle) {
                const titleText = lang === 'en' ? (t.care_title || '📋 Post Care Guidance') : (t.care_title || '📋 पश्चात् सेवा मार्गदर्शन');
                const badge = lang === 'en' ? 'EN' : 'ने';
                el.careTitle.innerHTML = titleText + ' <span class="translation-badge" id="langBadge">' + badge + '</span>';
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
            
            // Get translated disease name
            let displayName = data.class;
            if (DISEASE_TRANSLATIONS[currentLang] && DISEASE_TRANSLATIONS[currentLang][data.class]) {
                displayName = DISEASE_TRANSLATIONS[currentLang][data.class];
            } else {
                // Replace underscores with spaces as fallback
                displayName = data.class.replace(/_/g, ' ');
            }
            
            el.resultDiv.className = isHealthy ? 'healthy' : 'disease';
            
            let emoji = isHealthy ? '✅' : '⚠️';
            let statusText = isHealthy ? (t.resultHealthy || '🌿 Your plant appears healthy!') : (t.resultDisease || '⚠️ Disease detected!');
            
            el.resultIcon.textContent = emoji;
            el.resultName.textContent = displayName;
            el.resultConfidence.textContent = `${currentLang === 'en' ? 'Confidence' : 'विश्वसनीयता'}: ${data.confidence.toFixed(2)}%`;
            el.progressFill.style.width = `${data.confidence}%`;
            el.resultStatus.textContent = statusText;
            el.resultStatus.style.color = isHealthy ? '#2e7d32' : '#c62828';
            
            if (data.care) {
                el.careSection.classList.add('visible');
                
                // Update care title
                const titleText = currentLang === 'en' ? (t.care_title || '📋 Post Care Guidance') : (t.care_title || '📋 पश्चात् सेवा मार्गदर्शन');
                const badge = currentLang === 'en' ? 'EN' : 'ने';
                el.careTitle.innerHTML = titleText + ' <span class="translation-badge" id="langBadge">' + badge + '</span>';
                
                let html = '';
                
                if (data.care.immediate_actions && data.care.immediate_actions.length > 0) {
                    html += `
                        <div class="care-section-block">
                            <h4>${t.what_to_do || 'What to do now'}</h4>
                            <ul>
                                ${data.care.immediate_actions.map(a => `<li>${a}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }
                
                if (data.care.treatment_options && data.care.treatment_options.length > 0) {
                    html += `
                        <div class="care-section-block">
                            <h4>${t.treatment_options || 'Treatment options'}</h4>
                            <ul>
                                ${data.care.treatment_options.map(a => `<li>${a}</li>`).join('')}
                            </ul>
                        </div>
                    `;
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
    tutorial_steps = get_tutorial_steps('en')
    return render_template_string(
        HTML_TEMPLATE,
        ui_text=ui_text,
        tutorial_steps=tutorial_steps,
        current_lang='en',
        disease_translations=DISEASE_TRANSLATIONS
    )

@app.route('/api/get_ui_text')
def get_ui_text_api():
    """Get UI translations for a specific language"""
    lang = request.args.get('lang', 'en')
    ui_text = get_ui_text(lang)
    return jsonify(ui_text)

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
        print(f"❌ Prediction error: {e}")
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
    print("🌿 PLANT CARE - COMPLETE FINAL VERSION")
    print("=" * 50)
    print(f"📊 Detects: {len(class_names)} plant conditions")
    print(f"🗣️  Languages: English + Nepali (FULL TRANSLATION)")
    print(f"🚀 Server: http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    app.run(debug=True, threaded=True)