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

# ============================================
# TUTORIAL DATA - COMPLETE WITH BOTH LANGUAGES
# ============================================
TUTORIAL_STEPS = [
    {
        "id": "welcome",
        "highlight": ".lang-toggle",
        "action": "click",
        "en": {
            "title": "👋 Welcome to Plant Care!",
            "desc": "First, click the Translation button to switch between English and Nepali.",
            "instruction": "👉 Click the Translation button"
        },
        "ne": {
            "title": "👋 प्लान्ट केयरमा स्वागत छ!",
            "desc": "पहिले, अनुवाद बटनमा क्लिक गर्नुहोस् अंग्रेजी र नेपाली बीच स्विच गर्न।",
            "instruction": "👉 अनुवाद बटन क्लिक गर्नुहोस्"
        }
    },
    {
        "id": "upload",
        "highlight": "#dropZone",
        "action": "click_or_ok",
        "en": {
            "title": "📸 Upload a Leaf Photo",
            "desc": "This is the Upload Area. Click here or drag and drop a leaf photo.",
            "instruction": "👉 Click here or press OK"
        },
        "ne": {
            "title": "📸 पातको फोटो अपलोड गर्नुहोस्",
            "desc": "यो अपलोड क्षेत्र हो। यहाँ क्लिक गर्नुहोस् वा पातको फोटो तान्नुहोस्।",
            "instruction": "👉 यहाँ क्लिक गर्नुहोस् वा OK थिच्नुहोस्"
        }
    },
    {
        "id": "diagnose",
        "highlight": "#predictBtn",
        "action": "click_or_ok",
        "en": {
            "title": "🔍 Diagnose Your Plant",
            "desc": "After uploading a photo, click this button to detect diseases.",
            "instruction": "👉 Click Analyze or press OK"
        },
        "ne": {
            "title": "🔍 आफ्नो बिरुवा निदान गर्नुहोस्",
            "desc": "फोटो अपलोड गरेपछि, रोग पत्ता लगाउन यो बटन क्लिक गर्नुहोस्।",
            "instruction": "👉 विश्लेषण क्लिक गर्नुहोस् वा OK थिच्नुहोस्"
        }
    },
    {
        "id": "results",
        "highlight": "#result",
        "action": "ok_only",
        "en": {
            "title": "📋 Results & Care Instructions",
            "desc": "You'll see the disease name, confidence score, and care instructions.",
            "instruction": "👉 Press OK to continue"
        },
        "ne": {
            "title": "📋 नतिजा र हेरचाह निर्देशनहरू",
            "desc": "तपाईंले रोगको नाम, विश्वसनीयता स्कोर, र हेरचाह निर्देशनहरू देख्नुहुनेछ।",
            "instruction": "👉 जारी राख्न OK थिच्नुहोस्"
        }
    },
    {
        "id": "features",
        "highlight": ".extra-buttons",
        "action": "ok_only",
        "en": {
            "title": "🔊 Extra Features",
            "desc": "Use Read Out Loud to hear instructions. The Tutorial button replays this guide.",
            "instruction": "👉 Press OK to finish"
        },
        "ne": {
            "title": "🔊 अतिरिक्त सुविधाहरू",
            "desc": "पढेर सुनाउनुहोस् प्रयोग गर्नुहोस् निर्देशनहरू सुन्न। ट्यूटोरियल बटनले यो गाइड पुन: चलाउछ।",
            "instruction": "👉 समाप्त गर्न OK थिच्नुहोस्"
        }
    }
]

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
        
        /* ============================================
           MAIN TITLE - CENTERED OUTSIDE BOX
           ============================================ */
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
        .main-title .leaf {
            font-size: 48px;
        }
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

        /* ============================================
           HEADER - 3 BUTTONS CLEAN ALIGNMENT
           ============================================ */
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
        
        .btn-speech { background: #2196F3; color: white; }
        .btn-speech.speaking { background: #f44336; }
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

        /* ============================================
           SUBTITLE
           ============================================ */
        .subtitle { 
            text-align: center; 
            color: #558b2f; 
            font-size: 14px; 
            margin-bottom: 15px; 
            font-weight: 500;
        }

        /* ============================================
           BADGES
           ============================================ */
        .badges { display: flex; justify-content: center; gap: 10px; margin-bottom: 15px; }
        .badge { padding: 4px 16px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .badge-rice { background: #fef3c7; color: #92400e; }
        .badge-potato { background: #fde8e8; color: #9b2c2c; }

        /* ============================================
           UPLOAD AREA (Drag & Drop ONLY)
           ============================================ */
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
        #fileInput { display: none; }
        #preview { max-width: 100%; max-height: 180px; margin: 10px 0; border-radius: 12px; display: none; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }

        /* ============================================
           ANALYZE PLANT BUTTON - OUTSIDE DOTTED BOX
           ============================================ */
        .analyze-wrapper {
            margin-top: 16px;
            width: 100%;
        }
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

        /* ============================================
           LOADING
           ============================================ */
        #loading { display: none; text-align: center; padding: 25px; }
        .spinner { border: 4px solid #e8f5e9; border-top: 4px solid #43a047; border-radius: 50%; width: 45px; height: 45px; animation: spin 1s linear infinite; margin: 0 auto 12px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .loading-text { color: #558b2f; font-size: 15px; font-weight: 500; }

        /* ============================================
           RESULTS
           ============================================ */
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

        /* ============================================
           POST CARE GUIDANCE
           ============================================ */
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
        .care-section-block h4 {
            color: #2e7d32;
            margin-bottom: 6px;
            font-size: 14px;
            font-weight: 600;
        }
        .care-section-block ul {
            padding-left: 20px;
            margin: 0;
        }
        .care-section-block ul li {
            margin-bottom: 4px;
            color: #333;
            font-size: 14px;
            line-height: 1.5;
        }
        .care-section-block p {
            margin: 0;
            color: #333;
            font-size: 14px;
            line-height: 1.5;
        }
        .doctor-advice { border-left-color: #f44336; background: #ffebee; }
        .safety-warnings { border-left-color: #ff9800; background: #fff3e0; }
        .prevention { border-left-color: #2196f3; background: #e3f2fd; }
        .success-rate { border-left-color: #9c27b0; background: #f3e5f5; }

        .footer { text-align: center; margin-top: 18px; color: #a5d6a7; font-size: 12px; }

        /* ============================================
           LEAF WELCOME POPUP
           ============================================ */
        .leaf-popup-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.5);
            z-index: 9999;
            display: none;
            justify-content: center;
            align-items: center;
            backdrop-filter: blur(4px);
        }
        .leaf-popup-overlay.show { display: flex; }
        
        .leaf-popup {
            position: relative;
            background: linear-gradient(145deg, #2e7d32, #388e3c, #43a047);
            border-radius: 60% 60% 60% 60% / 60% 60% 60% 60%;
            padding: 50px 60px 60px 60px;
            max-width: 450px;
            width: 90%;
            text-align: center;
            color: white;
            box-shadow: 0 30px 80px rgba(0,0,0,0.4), inset 0 -10px 30px rgba(0,0,0,0.1);
            animation: leafPulse 3s ease-in-out infinite, leafFloat 4s ease-in-out infinite;
            transform-origin: center;
            border: 2px solid rgba(255,255,255,0.1);
        }
        .leaf-popup::before {
            content: '';
            position: absolute;
            top: 15%;
            left: 50%;
            transform: translateX(-50%);
            width: 2px;
            height: 70%;
            background: rgba(255,255,255,0.08);
            border-radius: 2px;
        }
        .leaf-popup::after {
            content: '';
            position: absolute;
            top: 30%;
            left: 20%;
            width: 60%;
            height: 1px;
            background: rgba(255,255,255,0.05);
            border-radius: 2px;
            transform: rotate(15deg);
        }
        @keyframes leafPulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.02); } }
        @keyframes leafFloat { 0%, 100% { transform: translateY(0px) rotate(-1deg); } 50% { transform: translateY(-8px) rotate(1deg); } }
        .leaf-popup .leaf-icon { font-size: 72px; display: block; margin-bottom: 8px; filter: drop-shadow(0 4px 20px rgba(0,0,0,0.2)); animation: leafSpin 8s linear infinite; }
        @keyframes leafSpin { 0% { transform: rotate(-5deg); } 50% { transform: rotate(5deg); } 100% { transform: rotate(-5deg); } }
        .leaf-popup h2 { font-size: 32px; font-weight: 700; margin-bottom: 6px; text-shadow: 0 2px 20px rgba(0,0,0,0.1); letter-spacing: -0.5px; }
        .leaf-popup .tagline { font-size: 16px; opacity: 0.9; margin-bottom: 4px; font-weight: 300; }
        .leaf-popup .sub-text { font-size: 13px; opacity: 0.7; margin-bottom: 16px; font-weight: 300; }
        .leaf-popup .progress-dots { display: flex; justify-content: center; gap: 6px; margin: 10px 0 16px 0; }
        .leaf-popup .progress-dots span { display: block; width: 8px; height: 8px; border-radius: 50%; background: rgba(255,255,255,0.2); transition: all 0.5s; }
        .leaf-popup .progress-dots span.active { background: white; width: 24px; border-radius: 4px; }
        .leaf-popup .btn-leaf { background: white; color: #2e7d32; border: none; padding: 12px 40px; border-radius: 30px; font-size: 16px; font-weight: 700; cursor: pointer; transition: all 0.3s; box-shadow: 0 4px 20px rgba(0,0,0,0.15); }
        .leaf-popup .btn-leaf:hover { transform: scale(1.05); box-shadow: 0 8px 30px rgba(0,0,0,0.25); }
        .leaf-popup .leaf-deco { position: absolute; font-size: 24px; opacity: 0.2; animation: leafFloat 6s ease-in-out infinite; }
        .leaf-popup .leaf-deco:nth-child(1) { top: -10px; left: -10px; animation-delay: 0s; }
        .leaf-popup .leaf-deco:nth-child(2) { bottom: -10px; right: -10px; animation-delay: 2s; }
        .leaf-popup .leaf-deco:nth-child(3) { top: 10%; right: -15px; animation-delay: 4s; font-size: 18px; }
        .leaf-popup .leaf-deco:nth-child(4) { bottom: 20%; left: -15px; animation-delay: 1s; font-size: 18px; }

        /* ============================================
           TUTORIAL OVERLAY
           ============================================ */
        .tutorial-dim {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.75);
            z-index: 9998;
            opacity: 0;
            transition: opacity 0.6s ease;
            pointer-events: none;
        }
        .tutorial-dim.active { opacity: 1; pointer-events: all; }

        .tutorial-spotlight {
            position: fixed;
            z-index: 9999;
            border-radius: 16px;
            box-shadow: 0 0 0 4px #43a047, 0 0 0 12px rgba(67, 160, 71, 0.25), 0 0 60px rgba(67, 160, 71, 0.15);
            background: transparent;
            transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            opacity: 0;
            transform: scale(0.95);
            pointer-events: none;
        }
        .tutorial-spotlight.active { opacity: 1; transform: scale(1); pointer-events: auto; }
        .tutorial-spotlight .pulse-ring {
            position: absolute;
            top: -12px;
            left: -12px;
            right: -12px;
            bottom: -12px;
            border-radius: 20px;
            border: 2px solid rgba(67, 160, 71, 0.3);
            animation: pulse-ring 2s ease-out infinite;
        }
        @keyframes pulse-ring { 0% { transform: scale(1); opacity: 1; } 100% { transform: scale(1.15); opacity: 0; } }

        .tutorial-tooltip {
            position: fixed;
            z-index: 10000;
            max-width: 420px;
            background: linear-gradient(135deg, #1b5e20, #2e7d32);
            color: white;
            padding: 24px 28px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            opacity: 0;
            transform: translateY(20px) scale(0.95);
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            pointer-events: all;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .tutorial-tooltip.active { opacity: 1; transform: translateY(0) scale(1); }
        .tutorial-tooltip .title { font-size: 20px; font-weight: 700; margin-bottom: 6px; }
        .tutorial-tooltip .description { font-size: 15px; line-height: 1.6; opacity: 0.95; margin-bottom: 10px; }
        .tutorial-tooltip .instruction { font-size: 14px; font-weight: 600; opacity: 0.9; padding: 8px 16px; background: rgba(255,255,255,0.12); border-radius: 10px; display: inline-block; margin-bottom: 14px; border: 1px solid rgba(255,255,255,0.08); }
        .tutorial-tooltip .buttons { display: flex; gap: 10px; margin-top: 4px; }
        .tutorial-tooltip .btn-ok { background: white; color: #1b5e20; border: none; padding: 10px 32px; border-radius: 10px; font-size: 15px; font-weight: 700; cursor: pointer; transition: all 0.2s; }
        .tutorial-tooltip .btn-ok:hover { transform: scale(1.05); box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        .tutorial-tooltip .btn-skip { background: transparent; color: rgba(255,255,255,0.6); border: 1px solid rgba(255,255,255,0.2); padding: 10px 20px; border-radius: 10px; font-size: 13px; cursor: pointer; transition: all 0.2s; }
        .tutorial-tooltip .btn-skip:hover { background: rgba(255,255,255,0.08); color: white; }

        .tutorial-arrow {
            position: fixed;
            z-index: 10001;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.5s ease;
        }
        .tutorial-arrow.active { opacity: 1; }
        .tutorial-arrow svg { display: block; filter: drop-shadow(0 4px 12px rgba(0,0,0,0.4)); animation: bounce-arrow 1.5s ease-in-out infinite; }
        @keyframes bounce-arrow { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
        .tutorial-arrow.direction-down { transform: rotate(0deg); }
        .tutorial-arrow.direction-up { transform: rotate(180deg); }
        .tutorial-arrow.direction-left { transform: rotate(270deg); }
        .tutorial-arrow.direction-right { transform: rotate(90deg); }

        .tutorial-progress {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 10001;
            display: flex;
            gap: 10px;
            align-items: center;
            background: rgba(0,0,0,0.7);
            padding: 8px 20px;
            border-radius: 30px;
            backdrop-filter: blur(8px);
            pointer-events: none;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .tutorial-progress .dot { width: 10px; height: 10px; border-radius: 50%; background: rgba(255,255,255,0.2); transition: all 0.3s; }
        .tutorial-progress .dot.active { background: #43a047; transform: scale(1.3); }
        .tutorial-progress .dot.completed { background: #a5d6a7; }
        .tutorial-progress .step-text { color: rgba(255,255,255,0.7); font-size: 12px; margin-left: 8px; font-weight: 500; }

        .tutorial-voice-indicator {
            position: fixed;
            bottom: 80px;
            right: 30px;
            z-index: 10001;
            background: rgba(0,0,0,0.85);
            color: white;
            padding: 10px 18px;
            border-radius: 30px;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 10px;
            opacity: 0;
            transition: opacity 0.5s;
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255,255,255,0.05);
        }
        .tutorial-voice-indicator.active { opacity: 1; }
        .tutorial-voice-indicator .wave { display: flex; gap: 3px; align-items: center; height: 20px; }
        .tutorial-voice-indicator .wave span { display: block; width: 3px; height: 100%; background: #43a047; border-radius: 2px; animation: wave 0.8s ease-in-out infinite alternate; }
        .tutorial-voice-indicator .wave span:nth-child(2) { animation-delay: 0.2s; }
        .tutorial-voice-indicator .wave span:nth-child(3) { animation-delay: 0.4s; }
        .tutorial-voice-indicator .wave span:nth-child(4) { animation-delay: 0.6s; }
        .tutorial-voice-indicator .wave span:nth-child(5) { animation-delay: 0.8s; }
        @keyframes wave { 0% { height: 4px; } 100% { height: 20px; } }

        @media (max-width: 600px) {
            .main-title { font-size: 32px; }
            .main-title .leaf { font-size: 30px; }
            .main-title .sub { font-size: 14px; }
            .container { padding: 20px; }
            .header { gap: 8px; }
            .header .btn-sm { font-size: 12px; padding: 6px 12px; }
            .header .btn-sm .emoji { font-size: 16px; }
            .lang-toggle { font-size: 12px; padding: 6px 12px; }
            .leaf-popup { padding: 30px 25px 40px 25px; border-radius: 40% 40% 40% 40% / 40% 40% 40% 40%; }
            .leaf-popup .leaf-icon { font-size: 50px; }
            .leaf-popup h2 { font-size: 24px; }
            .tutorial-tooltip { max-width: 90vw; padding: 16px 18px; left: 5% !important; right: 5% !important; bottom: 100px !important; top: auto !important; }
            .tutorial-tooltip .title { font-size: 18px; }
            .tutorial-tooltip .description { font-size: 14px; }
            .tutorial-arrow { display: none; }
            .tutorial-progress { bottom: 20px; padding: 6px 14px; }
            .tutorial-voice-indicator { bottom: 70px; right: 15px; padding: 6px 12px; font-size: 11px; }
        }
    </style>
</head>
<body>
    <!-- ============================================
    MAIN TITLE - CENTERED OUTSIDE BOX
    ============================================ -->
    <div class="main-title">
        <span class="leaf">🌿</span> PLANT CARE
        <span class="sub" id="mainSubtitle">Smart Disease Detection for Your Plants</span>
    </div>

    <!-- ============================================
    LEAF WELCOME POPUP
    ============================================ -->
    <div class="leaf-popup-overlay" id="leafPopup">
        <div class="leaf-popup">
            <span class="leaf-deco">🌿</span>
            <span class="leaf-deco">🍃</span>
            <span class="leaf-deco">🌱</span>
            <span class="leaf-deco">☘️</span>
            <span class="leaf-icon">🌿</span>
            <h2 id="popupTitle">Welcome to Plant Care!</h2>
            <p class="tagline" id="popupTagline">Your smart companion for healthy plants</p>
            <p class="sub-text" id="popupSubtext">🌱 Helping you detect and treat plant diseases</p>
            <div class="progress-dots" id="popupDots">
                <span class="active"></span>
                <span></span>
                <span></span>
                <span></span>
            </div>
            <button class="btn-leaf" id="popupBtn">🌿 Get Started</button>
        </div>
    </div>

    <!-- ============================================
    TUTORIAL OVERLAY
    ============================================ -->
    <div class="tutorial-dim" id="tutorialDim"></div>
    <div class="tutorial-spotlight" id="tutorialSpotlight"><div class="pulse-ring"></div></div>
    <div class="tutorial-arrow" id="tutorialArrow">
        <svg width="56" height="56" viewBox="0 0 56 56">
            <defs>
                <linearGradient id="arrowGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#43a047;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#2e7d32;stop-opacity:1" />
                </linearGradient>
            </defs>
            <path d="M28 4 L28 40 M14 26 L28 40 L42 26" stroke="url(#arrowGrad)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            <circle cx="28" cy="4" r="8" fill="url(#arrowGrad)"/>
            <circle cx="28" cy="4" r="3" fill="white" opacity="0.3"/>
        </svg>
    </div>
    <div class="tutorial-tooltip" id="tutorialTooltip">
        <div class="title"></div>
        <div class="description"></div>
        <div class="instruction"></div>
        <div class="buttons">
            <button class="btn-ok" id="tutorialOk">✅ OK</button>
            <button class="btn-skip" id="tutorialSkip">⏭️ Skip</button>
        </div>
    </div>
    <div class="tutorial-progress" id="tutorialProgress"></div>
    <div class="tutorial-voice-indicator" id="tutorialVoice">
        <span>🔊</span> Speaking...
        <div class="wave"><span></span><span></span><span></span><span></span><span></span></div>
    </div>

    <!-- ============================================
    MAIN APP CONTAINER
    ============================================ -->
    <div class="container" id="mainContainer">
        <!-- Header with 3 Buttons -->
        <div class="header">
            <button class="btn-sm btn-speech" id="speechBtn">
                <span class="emoji">🔊</span> <span id="speechLabel">Read</span>
            </button>
            <button class="btn-sm btn-tutorial" id="tutorialBtn">
                <span class="emoji">🎓</span> <span id="tutorialLabel">Tutorial</span>
            </button>
            <button class="lang-toggle" id="langToggle">
                <span class="lang-icon" id="langIcon">🇬🇧</span>
                <span id="langLabel">EN</span>
            </button>
        </div>

        <!-- Badges -->
        <div class="badges">
            <span class="badge badge-rice">🌾 Rice</span>
            <span class="badge badge-potato">🥔 Potato</span>
        </div>

        <!-- Upload Area (Drag & Drop ONLY) -->
        <div class="upload-area" id="dropZone">
            <div class="upload-icon">📸</div>
            <p style="color: #2e7d32; font-weight: 500;" id="uploadText">Upload a leaf image</p>
            <p class="hint" id="hintText">Drag &amp; drop or click to browse</p>
            <label class="btn-upload" for="fileInput" id="browseBtn">📁 Choose Image</label>
            <input type="file" id="fileInput" accept="image/*">
            <img id="preview" alt="Preview">
        </div>

        <!-- Analyze Plant Button - OUTSIDE dotted box -->
        <div class="analyze-wrapper">
            <button class="btn-predict" id="predictBtn" disabled>🔍 Analyze Plant</button>
        </div>

        <!-- Loading -->
        <div id="loading">
            <div class="spinner"></div>
            <p class="loading-text" id="loadingText">Analyzing your plant...</p>
        </div>

        <!-- Results -->
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
        const UI_TEXT = {{ ui_text | tojson }};
        const TUTORIAL_STEPS = {{ tutorial_steps | tojson }};

        // ============================================
        // STATE
        // ============================================
        let currentLang = 'en';
        let selectedFile = null;
        let diseaseData = null;
        let isTutorialActive = false;
        let currentTutorialStepIndex = 0;
        let isSpeaking = false;
        let speechSynth = window.speechSynthesis;
        let tutorialCompleted = localStorage.getItem('plant_care_tutorial_completed') === 'true';

        // ============================================
        // DOM REFERENCES
        // ============================================
        const elements = {
            mainSubtitle: document.getElementById('mainSubtitle'),
            uploadText: document.getElementById('uploadText'),
            hintText: document.getElementById('hintText'),
            browseBtn: document.getElementById('browseBtn'),
            predictBtn: document.getElementById('predictBtn'),
            loadingText: document.getElementById('loadingText'),
            footerText: document.getElementById('footerText'),
            speechLabel: document.getElementById('speechLabel'),
            tutorialLabel: document.getElementById('tutorialLabel'),
            langLabel: document.getElementById('langLabel'),
            langIcon: document.getElementById('langIcon'),
            langToggle: document.getElementById('langToggle'),
            popupTitle: document.getElementById('popupTitle'),
            popupTagline: document.getElementById('popupTagline'),
            popupSubtext: document.getElementById('popupSubtext'),
            popupBtn: document.getElementById('popupBtn'),
            popupOverlay: document.getElementById('leafPopup'),
            popupDots: document.getElementById('popupDots'),
            tutorialDim: document.getElementById('tutorialDim'),
            tutorialSpotlight: document.getElementById('tutorialSpotlight'),
            tutorialArrow: document.getElementById('tutorialArrow'),
            tutorialTooltip: document.getElementById('tutorialTooltip'),
            tutorialProgress: document.getElementById('tutorialProgress'),
            tutorialVoice: document.getElementById('tutorialVoice'),
            tutorialOk: document.getElementById('tutorialOk'),
            tutorialSkip: document.getElementById('tutorialSkip'),
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
            speechBtn: document.getElementById('speechBtn'),
            tutorialBtn: document.getElementById('tutorialBtn')
        };

        // ============================================
        // TRANSLATION FUNCTION - FULL PAGE
        // ============================================
        function translatePage(lang) {
            const t = UI_TEXT[lang] || UI_TEXT['en'];
            
            // Update main title subtitle
            if (elements.mainSubtitle) elements.mainSubtitle.textContent = t.app_subtitle;
            
            // Update upload area
            if (elements.uploadText) elements.uploadText.textContent = t.upload_title;
            if (elements.hintText) elements.hintText.textContent = t.upload_hint;
            if (elements.browseBtn) elements.browseBtn.textContent = t.browse_btn;
            if (elements.predictBtn) elements.predictBtn.textContent = t.analyze_btn;
            if (elements.loadingText) elements.loadingText.textContent = t.loading_text;
            if (elements.footerText) elements.footerText.textContent = t.footer;
            
            // Update buttons
            if (elements.speechLabel) elements.speechLabel.textContent = t.read_btn;
            if (elements.tutorialLabel) elements.tutorialLabel.textContent = t.tutorial_btn;
            
            // Update language toggle
            if (elements.langLabel) {
                elements.langLabel.textContent = lang === 'en' ? 'EN' : 'ने';
            }
            if (elements.langIcon) {
                elements.langIcon.textContent = lang === 'en' ? '🇬🇧' : '🇳🇵';
            }
            
            // Update popup
            if (elements.popupTitle) elements.popupTitle.textContent = t.popup_title;
            if (elements.popupTagline) elements.popupTagline.textContent = t.popup_tagline;
            if (elements.popupSubtext) elements.popupSubtext.textContent = t.popup_subtext;
            if (elements.popupBtn) elements.popupBtn.textContent = t.popup_btn;
            
            // Update care title
            if (elements.careTitle) {
                const titleText = lang === 'en' ? '📋 Post Care Guidance' : '📋 पोस्ट केयर गाइडेन्स';
                elements.careTitle.innerHTML = titleText + ' <span class="translation-badge" id="langBadge">' + lang.toUpperCase() + '</span>';
            }
            
            // Update lang badge
            if (elements.langBadge) elements.langBadge.textContent = lang.toUpperCase();
            
            // Update result status if exists
            if (diseaseData) {
                displayResult(diseaseData);
            }
            
            // Update tutorial if active
            if (isTutorialActive && elements.tutorialTooltip.classList.contains('active')) {
                const step = TUTORIAL_STEPS[currentTutorialStepIndex];
                const content = step[lang] || step.en;
                elements.tutorialTooltip.querySelector('.title').textContent = content.title;
                elements.tutorialTooltip.querySelector('.description').textContent = content.desc;
                elements.tutorialTooltip.querySelector('.instruction').textContent = content.instruction;
            }
            
            // Store current language
            currentLang = lang;
        }

        // ============================================
        // SPEECH SYNTHESIS
        // ============================================
        function speakText(text, lang, callback) {
            if (!speechSynth) {
                if (callback) callback();
                return;
            }
            try { speechSynth.cancel(); } catch(e) {}
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = lang === 'ne' ? 'ne-NP' : 'en-US';
            utterance.rate = 0.85;
            utterance.pitch = 1;
            utterance.volume = 1;
            
            let speaking = true;
            utterance.onstart = () => {
                isSpeaking = true;
                if (elements.speechBtn) {
                    elements.speechLabel.textContent = UI_TEXT[currentLang].read_btn_stop || '⏹️ Stop';
                    elements.speechBtn.classList.add('speaking');
                }
                if (elements.tutorialVoice) elements.tutorialVoice.classList.add('active');
            };
            
            utterance.onend = () => {
                speaking = false;
                isSpeaking = false;
                if (elements.speechBtn) {
                    elements.speechLabel.textContent = UI_TEXT[currentLang].read_btn;
                    elements.speechBtn.classList.remove('speaking');
                }
                if (elements.tutorialVoice) elements.tutorialVoice.classList.remove('active');
                if (callback) callback();
            };
            
            utterance.onerror = () => {
                speaking = false;
                isSpeaking = false;
                if (elements.speechBtn) {
                    elements.speechLabel.textContent = UI_TEXT[currentLang].read_btn;
                    elements.speechBtn.classList.remove('speaking');
                }
                if (elements.tutorialVoice) elements.tutorialVoice.classList.remove('active');
                if (callback) callback();
            };
            
            speechSynth.speak(utterance);
            
            setTimeout(() => {
                if (speaking) {
                    try { speechSynth.cancel(); } catch(e) {}
                    isSpeaking = false;
                    if (elements.speechBtn) {
                        elements.speechLabel.textContent = UI_TEXT[currentLang].read_btn;
                        elements.speechBtn.classList.remove('speaking');
                    }
                    if (elements.tutorialVoice) elements.tutorialVoice.classList.remove('active');
                    if (callback) callback();
                }
            }, 20000);
        }

        function stopSpeaking() {
            try { if (speechSynth) speechSynth.cancel(); } catch(e) {}
            isSpeaking = false;
            if (elements.speechBtn) {
                elements.speechLabel.textContent = UI_TEXT[currentLang].read_btn;
                elements.speechBtn.classList.remove('speaking');
            }
            if (elements.tutorialVoice) elements.tutorialVoice.classList.remove('active');
        }

        // ============================================
        // LEAF WELCOME POPUP
        // ============================================
        function showLeafPopup() {
            const overlay = elements.popupOverlay;
            if (!overlay) return;
            overlay.classList.add('show');
            
            const dots = elements.popupDots.querySelectorAll('span');
            let dotIndex = 0;
            const dotInterval = setInterval(() => {
                dots.forEach(d => d.classList.remove('active'));
                dots[dotIndex].classList.add('active');
                dotIndex = (dotIndex + 1) % dots.length;
            }, 600);
            
            elements.popupBtn.onclick = function() {
                clearInterval(dotInterval);
                overlay.classList.remove('show');
                if (!tutorialCompleted) {
                    setTimeout(startTutorial, 800);
                }
            };
        }

        // ============================================
        // TUTORIAL
        // ============================================
        function startTutorial() {
            if (isTutorialActive || !TUTORIAL_STEPS || TUTORIAL_STEPS.length === 0) return;
            isTutorialActive = true;
            currentTutorialStepIndex = 0;
            showTutorialStep(0);
        }

        function showTutorialStep(index) {
            if (index >= TUTORIAL_STEPS.length) {
                endTutorial();
                return;
            }

            const step = TUTORIAL_STEPS[index];
            const content = step[currentLang] || step.en;
            const highlight = step.highlight;
            const action = step.action;

            const titleEl = elements.tutorialTooltip.querySelector('.title');
            const descEl = elements.tutorialTooltip.querySelector('.description');
            const instEl = elements.tutorialTooltip.querySelector('.instruction');
            if (titleEl) titleEl.textContent = content.title;
            if (descEl) descEl.textContent = content.desc;
            if (instEl) instEl.textContent = content.instruction;
            elements.tutorialTooltip.classList.add('active');

            elements.tutorialDim.classList.add('active');

            const element = document.querySelector(highlight);
            if (element) {
                const rect = element.getBoundingClientRect();
                const padding = 20;
                const spot = elements.tutorialSpotlight;
                spot.style.left = (rect.left - padding) + 'px';
                spot.style.top = (rect.top - padding) + 'px';
                spot.style.width = (rect.width + padding * 2) + 'px';
                spot.style.height = (rect.height + padding * 2) + 'px';
                spot.classList.add('active');

                positionTooltip(rect);
                showArrow(rect);

                if (action === 'click') {
                    elements.tutorialOk.style.display = 'none';
                    const clickHandler = () => {
                        element.removeEventListener('click', clickHandler);
                        nextTutorialStep();
                    };
                    element.addEventListener('click', clickHandler);
                } else {
                    elements.tutorialOk.style.display = 'inline-block';
                }
            } else {
                elements.tutorialOk.style.display = 'inline-block';
            }

            updateTutorialProgress(index);
            if (content.desc) {
                speakText(content.desc, currentLang, () => {});
            }
        }

        function positionTooltip(rect) {
            const tooltip = elements.tutorialTooltip;
            const tw = tooltip.offsetWidth || 400;
            const th = tooltip.offsetHeight || 300;
            let top, left;
            if (rect.top - th - 80 > 0) {
                top = rect.top - th - 80;
                left = Math.max(20, Math.min(rect.left + rect.width/2 - tw/2, window.innerWidth - tw - 20));
            } else if (rect.bottom + th + 80 < window.innerHeight) {
                top = rect.bottom + 80;
                left = Math.max(20, Math.min(rect.left + rect.width/2 - tw/2, window.innerWidth - tw - 20));
            } else {
                top = window.innerHeight/2 - th/2;
                left = window.innerWidth/2 - tw/2;
            }
            tooltip.style.top = top + 'px';
            tooltip.style.left = left + 'px';
        }

        function showArrow(rect) {
            const centerX = rect.left + rect.width/2;
            const centerY = rect.top + rect.height/2;
            const vh = window.innerHeight;
            let direction, x, y;
            if (centerY < vh * 0.4) {
                direction = 'down';
                x = centerX - 28;
                y = rect.bottom + 20;
            } else if (centerY > vh * 0.6) {
                direction = 'up';
                x = centerX - 28;
                y = rect.top - 70;
            } else if (rect.left < window.innerWidth * 0.4) {
                direction = 'right';
                x = rect.right + 20;
                y = centerY - 28;
            } else {
                direction = 'left';
                x = rect.left - 70;
                y = centerY - 28;
            }
            elements.tutorialArrow.style.left = x + 'px';
            elements.tutorialArrow.style.top = y + 'px';
            elements.tutorialArrow.className = 'tutorial-arrow direction-' + direction + ' active';
        }

        function updateTutorialProgress(index) {
            const total = TUTORIAL_STEPS.length;
            elements.tutorialProgress.innerHTML = '';
            for (let i = 0; i < total; i++) {
                const dot = document.createElement('div');
                dot.className = 'dot';
                if (i < index) dot.classList.add('completed');
                if (i === index) dot.classList.add('active');
                elements.tutorialProgress.appendChild(dot);
            }
            const text = document.createElement('span');
            text.className = 'step-text';
            text.textContent = `Step ${index + 1} of ${total}`;
            elements.tutorialProgress.appendChild(text);
        }

        function nextTutorialStep() {
            currentTutorialStepIndex++;
            if (currentTutorialStepIndex < TUTORIAL_STEPS.length) {
                showTutorialStep(currentTutorialStepIndex);
            } else {
                endTutorial();
            }
        }

        function endTutorial() {
            isTutorialActive = false;
            elements.tutorialDim.classList.remove('active');
            elements.tutorialSpotlight.classList.remove('active');
            elements.tutorialArrow.classList.remove('active');
            elements.tutorialTooltip.classList.remove('active');
            elements.tutorialProgress.innerHTML = '';
            elements.tutorialVoice.classList.remove('active');
            stopSpeaking();
            localStorage.setItem('plant_care_tutorial_completed', 'true');
            tutorialCompleted = true;
        }

        elements.tutorialOk.addEventListener('click', nextTutorialStep);
        elements.tutorialSkip.addEventListener('click', endTutorial);

        // ============================================
        // LANGUAGE TOGGLE - TRANSLATE EVERYTHING
        // ============================================
        elements.langToggle.addEventListener('click', function() {
            const newLang = currentLang === 'en' ? 'ne' : 'en';
            translatePage(newLang);
        });

        // ============================================
        // SPEECH BUTTON
        // ============================================
        elements.speechBtn.addEventListener('click', function() {
            if (!diseaseData) {
                alert(currentLang === 'en' ? 'Please diagnose a plant first!' : 'कृपया पहिले बिरुवा निदान गर्नुहोस्!');
                return;
            }

            if (isSpeaking) {
                stopSpeaking();
                return;
            }

            const care = diseaseData.care || { immediate_actions: [], treatment_options: [], prevention: '' };
            let text = '';
            
            if (currentLang === 'en') {
                text = `Disease detected: ${diseaseData.class}. Confidence: ${diseaseData.confidence.toFixed(2)} percent. `;
                if (care.immediate_actions && care.immediate_actions.length > 0) {
                    text += `What to do now: ${care.immediate_actions.join('. ')}. `;
                }
                if (care.treatment_options && care.treatment_options.length > 0) {
                    text += `Treatment options: ${care.treatment_options.join('. ')}. `;
                }
                if (care.consult_doctor) {
                    text += `When to consult a doctor: ${care.consult_doctor}. `;
                }
                if (care.safety_warnings && care.safety_warnings.length > 0) {
                    text += `Safety warnings: ${care.safety_warnings.join('. ')}. `;
                }
                if (care.prevention) {
                    text += `Prevention: ${care.prevention}.`;
                }
            } else {
                text = `रोग पत्ता लाग्यो: ${diseaseData.class}. विश्वसनीयता: ${diseaseData.confidence.toFixed(2)} प्रतिशत. `;
                if (care.immediate_actions && care.immediate_actions.length > 0) {
                    text += `अब के गर्ने: ${care.immediate_actions.join('. ')}. `;
                }
                if (care.treatment_options && care.treatment_options.length > 0) {
                    text += `उपचार विकल्पहरू: ${care.treatment_options.join('. ')}. `;
                }
                if (care.consult_doctor) {
                    text += `डाक्टरलाई कहिले सोध्ने: ${care.consult_doctor}. `;
                }
                if (care.safety_warnings && care.safety_warnings.length > 0) {
                    text += `सुरक्षा चेतावनीहरू: ${care.safety_warnings.join('. ')}. `;
                }
                if (care.prevention) {
                    text += `रोकथाम: ${care.prevention}.`;
                }
            }

            speakText(text, currentLang, () => {});
        });

        // ============================================
        // TUTORIAL BUTTON
        // ============================================
        elements.tutorialBtn.addEventListener('click', function() {
            localStorage.removeItem('plant_care_tutorial_completed');
            tutorialCompleted = false;
            startTutorial();
        });

        // ============================================
        // FILE UPLOAD
        // ============================================
        elements.fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                selectedFile = this.files[0];
                elements.predictBtn.disabled = false;
                elements.resultDiv.style.display = 'none';
                elements.careSection.classList.remove('visible');
                diseaseData = null;
                const reader = new FileReader();
                reader.onload = (e) => { elements.preview.src = e.target.result; elements.preview.style.display = 'block'; };
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
                elements.predictBtn.disabled = false;
                elements.resultDiv.style.display = 'none';
                elements.careSection.classList.remove('visible');
                diseaseData = null;
                elements.fileInput.files = e.dataTransfer.files;
                const reader = new FileReader();
                reader.onload = (e) => { elements.preview.src = e.target.result; elements.preview.style.display = 'block'; };
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
            elements.preview.style.display = 'none';

            try {
                const response = await fetch('/api/predict', { method: 'POST', body: formData });
                const data = await response.json();

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
                elements.loadingDiv.style.display = 'none';
                elements.resultDiv.style.display = 'block';
                elements.resultDiv.className = 'disease';
                elements.resultIcon.textContent = '❌';
                elements.resultName.textContent = 'Connection Error';
                elements.resultStatus.textContent = error.message;
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

        function displayResult(data) {
            const isHealthy = data.class.includes('Healthy');
            const lang = currentLang;
            const t = UI_TEXT[lang] || UI_TEXT['en'];

            elements.resultDiv.className = isHealthy ? 'healthy' : 'disease';

            let emoji = isHealthy ? '✅' : '⚠️';
            let statusText = isHealthy ? t.resultHealthy : t.resultDisease;

            elements.resultIcon.textContent = emoji;
            elements.resultName.textContent = data.class;
            elements.resultConfidence.textContent = `${lang === 'en' ? 'Confidence' : 'विश्वसनीयता'}: ${data.confidence.toFixed(2)}%`;
            elements.progressFill.style.width = `${data.confidence}%`;
            elements.resultStatus.textContent = statusText;
            elements.resultStatus.style.color = isHealthy ? '#2e7d32' : '#c62828';

            if (data.care) {
                elements.careSection.classList.add('visible');
                const care = data.care;
                const titleText = lang === 'en' ? '📋 Post Care Guidance' : '📋 पोस्ट केयर गाइडेन्स';
                elements.careTitle.innerHTML = titleText + ' <span class="translation-badge">' + lang.toUpperCase() + '</span>';

                let html = '';

                // Immediate Actions
                if (care.immediate_actions && care.immediate_actions.length > 0) {
                    html += `
                        <div class="care-section-block">
                            <h4>${t.what_to_do}</h4>
                            <ul>
                                ${care.immediate_actions.map(a => `<li>${a}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }

                // Treatment Options
                if (care.treatment_options && care.treatment_options.length > 0) {
                    html += `
                        <div class="care-section-block">
                            <h4>${t.treatment_options}</h4>
                            <ul>
                                ${care.treatment_options.map(a => `<li>${a}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }

                // Consult Doctor
                if (care.consult_doctor) {
                    html += `
                        <div class="care-section-block doctor-advice">
                            <h4>${t.consult_doctor}</h4>
                            <p>${care.consult_doctor}</p>
                        </div>
                    `;
                }

                // Safety Warnings
                if (care.safety_warnings && care.safety_warnings.length > 0) {
                    html += `
                        <div class="care-section-block safety-warnings">
                            <h4>${t.safety_warnings}</h4>
                            <ul>
                                ${care.safety_warnings.map(a => `<li>${a}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }

                // Prevention
                if (care.prevention) {
                    html += `
                        <div class="care-section-block prevention">
                            <h4>${t.prevention}</h4>
                            <p>${care.prevention}</p>
                        </div>
                    `;
                }

                // Success Rate
                if (care.success_rate) {
                    html += `
                        <div class="care-section-block success-rate">
                            <strong>${t.success_rate}</strong> ${care.success_rate}
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
        // INITIALIZATION
        // ============================================
        window.addEventListener('load', function() {
            // Translate page to English by default
            translatePage('en');
            
            // Show popup
            showLeafPopup();
            
            // Preload speech voices
            if (speechSynth) {
                speechSynth.getVoices();
            }
        });

        window.addEventListener('beforeunload', function() {
            localStorage.removeItem('plant_care_tutorial_completed');
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
    ui_text = get_ui_text('en')
    tutorial_steps = get_tutorial_steps('en')
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
            return jsonify({'success': False, 'error': 'No file uploaded'})

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})

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
        clear_memory()
        return jsonify({'success': False, 'error': str(e)})

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

@app.route('/api/set_language/<lang>', methods=['POST'])
def set_language(lang):
    if lang in ['en', 'ne']:
        session['language'] = lang
        return jsonify({'success': True, 'language': lang})
    return jsonify({'success': False, 'error': 'Invalid language'})

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
    print(f"🎓 Tutorial: Leaf popup + auto-start with voice")
    print(f"🔊 Read Out Loud: Supported in both languages")
    print(f"✨ Spotlight + Arrow: Interactive tutorial")
    print(f"🍃 Leaf Popup: Beautiful welcome notice")
    print(f"🚀 Server: http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    app.run(debug=True, threaded=True)