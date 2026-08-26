# app.py - COMPLETE FINAL VERSION WITH PROFESSIONAL VIDEO CONTROLS
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
import base64
import io

# Import Piper TTS
from piper import PiperVoice

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
# LOAD PIPER VOICE MODEL (Google Voice - for Nepali only)
# ============================================
print("\nLoading Piper voice model...")

# Path to the Google Nepali voice model
voice_path = "voices/ne/ne_NP/google/ne_NP-google-medium.onnx"

try:
    voice = PiperVoice.load(voice_path)
    print("Piper voice loaded successfully")
    print("   Voice: Google Nepali Medium (for Nepali TTS)")
except Exception as e:
    print(f"Error loading Piper voice: {e}")
    print("Make sure the voice file exists at:", voice_path)
    voice = None

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
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px;
            position: relative;
            background-image: url('/static/side_panel.jpg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }

        /* Dark overlay for the entire page */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.50);
            z-index: 0;
        }

        /* ===== CONTENT WRAPPER (Vertical block with blur) ===== */
        .content-wrapper {
            position: relative;
            z-index: 1;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            border-radius: 28px;
            padding: 0.5rem 2rem 2rem 2rem;
            max-width: 750px;
            width: 100%;
            box-shadow: 0 25px 70px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.1);
            border: 2px solid rgba(255, 255, 255, 0.15);
        }

        /* ===== HEADER ===== */
        .app-header {
            background: rgba(26, 58, 43, 0.85);
            backdrop-filter: blur(5px);
            -webkit-backdrop-filter: blur(5px);
            padding: 1.2rem 1.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 16px 16px 0 0;
            margin: 0 -2rem 0 -2rem;
            padding-left: 2rem;
            padding-right: 2rem;
            box-shadow: 0 4px 25px rgba(0,0,0,0.25);
            border-bottom: 2px solid rgba(255,255,255,0.08);
        }

        .app-title {
            color: #ffffff;
            font-size: 3.4rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            text-align: center;
            padding: 0.1rem 1.5rem;
            border-radius: 0px;
            border: none;
            background: none;
            backdrop-filter: none;
            -webkit-backdrop-filter: none;
            box-shadow: none;
            -webkit-text-stroke: 1.5px rgba(255, 255, 255, 0.2);
            text-shadow: 0 0 50px rgba(67, 160, 71, 0.5), 0 0 100px rgba(67, 160, 71, 0.25), 0 4px 30px rgba(0,0,0,0.6);
        }

        /* ===== SUBTITLE ===== */
        .main-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #e8f5e9;
            text-align: center;
            margin: 0.8rem 0 0.3rem 0;
            text-shadow: 0 2px 20px rgba(0,0,0,0.5), 0 0 30px rgba(0,0,0,0.3);
            position: relative;
            z-index: 1;
        }
        .main-title .sub {
            font-size: 1rem;
            font-weight: 400;
            color: #d4e8cf;
            display: block;
            letter-spacing: 1px;
            text-shadow: 0 2px 15px rgba(0,0,0,0.5);
        }

        /* ===== BUTTONS BELOW SUBTITLE ===== */
        .header-nav {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            padding: 0.6rem 0 0.9rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            margin: 0 -2rem 1rem -2rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }

        .nav-btn {
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(106, 154, 122, 0.7);
            color: #e8f5e9;
            padding: 0.5rem 1.4rem;
            border-radius: 25px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.25s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.3rem;
            min-width: 100px;
            height: 38px;
            letter-spacing: 0.3px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.2);
            text-shadow: 0 1px 8px rgba(0,0,0,0.3);
        }

        .nav-btn:hover {
            background: rgba(255, 255, 255, 0.18);
            border-color: #8aba8a;
            color: #ffffff;
            transform: scale(1.03);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }

        /* ===== CONTAINER (Brighter - slightly darker than upload area) ===== */
        .container {
            background: rgba(255, 255, 255, 0.80);
            backdrop-filter: blur(6px);
            -webkit-backdrop-filter: blur(6px);
            border-radius: 20px;
            padding: 28px 32px 32px 32px;
            width: 100%;
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
            position: relative;
            z-index: 1;
            border: 1px solid rgba(255,255,255,0.2);
        }

        /* ===== PLANT INFO ===== */
        .plant-info {
            text-align: center;
            margin-bottom: 14px;
        }
        .plant-info .info-label {
            color: #2e5a2e;
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
        .badge-rice { 
            background: #e8d5a8; 
            color: #6a4e1a; 
        }
        .badge-potato { 
            background: #e8c8c0; 
            color: #7a3a2a; 
        }

        /* ===== UPLOAD AREA (Slightly darker than container) ===== */
        #dropZone {
            border: 2px dashed #4a8a4a;
            border-radius: 16px;
            padding: 30px 20px;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
            background: rgba(255, 255, 255, 0.72);
            backdrop-filter: blur(6px);
            -webkit-backdrop-filter: blur(6px);
            position: relative;
            z-index: 1;
        }
        #dropZone:hover { 
            border-color: #2a7a2a; 
            background: rgba(255, 255, 255, 0.80); 
        }
        #dropZone.dragover { 
            border-color: #1a6a1a; 
            background: rgba(255, 255, 255, 0.85); 
        }
        #dropZone.has-image { padding: 12px 20px; }
        .upload-icon { font-size: 48px; margin-bottom: 6px; }
        .hint { color: #4a7a4a; font-size: 14px; margin-top: 4px; }
        .btn-upload {
            display: inline-block;
            padding: 10px 28px;
            background: linear-gradient(135deg, #43a047, #2e7d32);
            color: white;
            border-radius: 10px;
            cursor: pointer;
            margin-top: 10px;
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
            margin-top: 6px;
        }
        #fileInput { display: none; }
        #preview {
            max-width: 100%;
            max-height: 200px;
            margin: 8px auto;
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
            top: -8px;
            right: -8px;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: #c0392b;
            color: white;
            border: none;
            font-size: 16px;
            cursor: pointer;
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 10;
            transition: all 0.3s;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        .remove-image-btn:hover {
            transform: scale(1.1);
            background: #a93226;
        }
        .remove-image-btn.show {
            display: flex;
        }

        .analyze-wrapper { margin-top: 14px; width: 100%; }
        .btn-predict {
            background: linear-gradient(135deg, #43a047, #2e7d32);
            color: white;
            border: none;
            padding: 13px 40px;
            border-radius: 12px;
            font-size: 17px;
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

        #loading { display: none; text-align: center; padding: 20px; }
        .spinner { border: 4px solid #e8f5e9; border-top: 4px solid #43a047; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 10px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .loading-text { color: #558b2f; font-size: 14px; font-weight: 500; }

        #result {
            margin-top: 15px;
            padding: 18px;
            border-radius: 16px;
            display: none;
            animation: slideDown 0.5s ease-out;
            position: relative;
            z-index: 1;
        }
        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-15px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .healthy { background: #e8f5e9; border: 2px solid #43a047; }
        .disease { background: #ffebee; border: 2px solid #e53935; }
        .result-icon { font-size: 40px; text-align: center; }
        .result-name { font-size: 20px; font-weight: 700; text-align: center; margin: 6px 0; color: #1b5e20; }
        .result-confidence { text-align: center; color: #558b2f; font-size: 13px; }
        .progress-bar { width: 100%; height: 8px; background: #e0e0e0; border-radius: 4px; margin-top: 8px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #43a047, #2e7d32); transition: width 0.8s ease-out; border-radius: 4px; }
        .result-status { text-align: center; margin-top: 10px; font-size: 14px; font-weight: 500; }

        /* ===== CARE SECTION (with thicker border and more shadow) ===== */
        .care-section { 
            margin-top: 15px; 
            padding: 14px; 
            background: rgba(245, 245, 245, 0.5); 
            border-radius: 12px; 
            display: none; 
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
            border: 2.5px solid rgba(160, 160, 160, 0.35);
            box-shadow: 0 6px 28px rgba(0, 0, 0, 0.14);
        }
        .care-section.visible { display: block; }

        .care-title {
            font-size: 17px;
            font-weight: 700;
            color: #2e7d32;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }

        .btn-speech-green {
            background: transparent;
            border: none;
            cursor: pointer;
            padding: 4px;
            color: #2E7D32;
            font-size: 22px;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            display: flex;
            align-items: center;
        }

        .btn-speech-green:hover {
            transform: scale(1.1);
        }

        .btn-speech-green.speaking {
            color: transparent;
            -webkit-text-stroke: 2.5px #2E7D32;
            transform: scale(1.2);
        }

        .translation-badge {
            display: inline-block;
            background: #43a047;
            color: white;
            font-size: 10px;
            padding: 2px 10px;
            border-radius: 12px;
            margin-left: auto;
            font-weight: 600;
        }

        /* ===== CARE BLOCKS (with thicker border and more shadow) ===== */
        .care-section-block {
            margin: 6px 0;
            padding: 8px 12px;
            border-radius: 8px;
            background: rgba(249, 249, 249, 0.45);
            border-left: 4px solid #43a047;
            border: 2.5px solid rgba(160, 160, 160, 0.25);
            border-left-width: 4px;
            backdrop-filter: blur(2px);
            -webkit-backdrop-filter: blur(2px);
            box-shadow: 0 3px 14px rgba(0, 0, 0, 0.08);
        }
        .care-section-block h4 { color: #2e5a2e; margin-bottom: 3px; font-size: 13px; font-weight: 600; }
        .care-section-block ul { padding-left: 18px; margin: 0; }
        .care-section-block ul li { margin-bottom: 2px; color: #3a4a3a; font-size: 12.5px; line-height: 1.5; }
        .care-section-block p { margin: 0; color: #3a4a3a; font-size: 12.5px; line-height: 1.5; }
        .care-section-block strong { color: #2e5a2e; }
        .care-section-block.notice { border-left-color: #d4952a; background: rgba(255, 243, 224, 0.35); }

        .footer { 
            text-align: center; 
            margin-top: 14px; 
            color: #3a6a3a; 
            font-size: 12px; 
            font-weight: 500;
        }

        /* ===== TUTORIAL MODAL ===== */
        .tutorial-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.85);
            z-index: 99999;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .tutorial-modal.show { display: flex; }
        .tutorial-modal-content {
            background: #1a1a1a;
            padding: 10px;
            border-radius: 16px;
            max-width: 900px;
            width: 95%;
            position: relative;
            box-shadow: 0 20px 60px rgba(0,0,0,0.6);
        }
        .tutorial-modal-content .close-btn {
            position: absolute;
            top: -18px;
            right: -18px;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #e53935;
            color: white;
            border: none;
            font-size: 22px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10;
            box-shadow: 0 2px 12px rgba(0,0,0,0.3);
            transition: transform 0.2s;
        }
        .tutorial-modal-content .close-btn:hover {
            transform: scale(1.1);
            background: #c62828;
        }
        
        .tutorial-video-container {
            width: 100%;
            position: relative;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
            border-radius: 10px 10px 0 0;
            background: #000;
        }
        .tutorial-video-container video {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }
        
        .tutorial-title {
            color: #ffffff;
            font-size: 1.2rem;
            font-weight: 600;
            text-align: center;
            padding: 12px 0 8px 0;
            letter-spacing: 0.5px;
        }

        /* ===== VIDEO CONTROLS - PROFESSIONAL STYLE ===== */
        .video-controls {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            padding: 10px 16px 8px 16px;
            flex-wrap: wrap;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 0 0 12px 12px;
            margin-top: 2px;
        }

        .video-btn {
            background: transparent;
            border: none;
            color: rgba(255, 255, 255, 0.8);
            padding: 6px 10px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 3px;
            font-size: 13px;
            font-weight: 400;
        }

        .video-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
        }

        .video-btn .btn-label {
            font-size: 11px;
            font-weight: 500;
            opacity: 0.7;
        }

        .video-btn svg {
            flex-shrink: 0;
        }

        .video-time {
            color: rgba(255, 255, 255, 0.8);
            font-size: 13px;
            font-weight: 400;
            min-width: 90px;
            text-align: center;
            font-family: 'Segoe UI', monospace;
            letter-spacing: 0.3px;
        }

        .video-speed-label {
            color: rgba(255, 255, 255, 0.7);
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 4px;
            padding: 4px 6px;
            border-radius: 4px;
            transition: background 0.2s;
        }

        .video-speed-label:hover {
            background: rgba(255, 255, 255, 0.08);
        }

        .video-speed-select {
            background: transparent;
            border: none;
            color: rgba(255, 255, 255, 0.8);
            padding: 2px 4px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: 400;
            cursor: pointer;
            outline: none;
        }

        .video-speed-select:hover {
            background: rgba(255, 255, 255, 0.08);
        }

        .video-speed-select option {
            background: #1a1a1a;
            color: #ffffff;
        }

        @media (max-width: 650px) {
            .content-wrapper {
                padding: 0.5rem 1rem 1rem 1rem;
            }
            .app-header {
                margin: 0 -1rem 0 -1rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .header-nav {
                margin: 0 -1rem 0.5rem -1rem;
                padding-left: 1rem;
                padding-right: 1rem;
                flex-wrap: wrap;
            }
            .app-title {
                font-size: 2.4rem !important;
                padding: 0.1rem 0.8rem !important;
            }
            .nav-btn {
                min-width: 80px;
                font-size: 0.8rem;
                padding: 0.3rem 1rem;
                height: 32px;
            }
            .main-title {
                font-size: 1rem;
            }
            .main-title .sub {
                font-size: 0.85rem;
            }
            .container { padding: 18px; }
            .plant-info .info-label { font-size: 0.85rem; }
            .badge { font-size: 0.85rem; padding: 3px 10px; }
            .tutorial-modal-content .close-btn {
                width: 32px;
                height: 32px;
                font-size: 18px;
                top: -14px;
                right: -14px;
            }
            .video-controls {
                gap: 4px;
                padding: 8px 10px 6px 10px;
            }
            .video-btn {
                padding: 4px 6px;
                font-size: 12px;
            }
            .video-btn .btn-label {
                font-size: 10px;
            }
            .video-btn svg {
                width: 16px;
                height: 16px;
            }
            .video-time {
                font-size: 11px;
                min-width: 70px;
            }
            .video-speed-label {
                font-size: 11px;
            }
            .video-speed-select {
                font-size: 11px;
            }
        }

        @media (max-width: 450px) {
            .app-title { font-size: 1.8rem !important; padding: 0.1rem 0.5rem !important; }
            .nav-btn { font-size: 0.7rem; padding: 0.2rem 0.6rem; min-width: 60px; height: 28px; }
            .container { padding: 12px; }
            .upload-icon { font-size: 36px; }
            .btn-predict { font-size: 15px; padding: 10px 20px; }
        }
    </style>
</head>
<body>
    <!-- ===== CONTENT WRAPPER ===== -->
    <div class="content-wrapper">

        <!-- ===== HEADER ===== -->
        <header class="app-header">
            <span class="app-title" id="appTitle">Plant Care</span>
        </header>

        <!-- ===== SUBTITLE ===== -->
        <div class="main-title">
            <span class="sub" id="mainSubtitle">Smart Disease Detection for Your Plants</span>
        </div>

        <!-- ===== BUTTONS BELOW SUBTITLE ===== -->
        <div class="header-nav">
            <button class="nav-btn" id="tutorialBtn">
                <span id="tutorialLabel">Tutorial</span>
            </button>
            <button class="nav-btn" id="langToggle">
                <span id="langLabel">English ⇄ नेपाली</span>
            </button>
        </div>

        <!-- ===== MAIN CONTAINER ===== -->
        <div class="container">
            <div class="plant-info">
                <span class="info-label" id="plantInfoText">Currently diagnosable plants:</span>
                <span class="badge badge-rice" id="riceBadge">🌾 Rice</span>
                <span class="badge badge-potato" id="potatoBadge">🥔 Potato</span>
            </div>

            <div class="upload-area" id="dropZone">
                <div class="upload-icon" id="uploadIcon">📸</div>
                <p style="color: #2e5a2e; font-weight: 500;" id="uploadText">Upload a leaf image</p>
                <p class="hint" id="hintText">Drag & drop or click to browse</p>
                <label class="btn-upload" for="fileInput" id="browseBtn">Choose Image</label>
                <input type="file" id="fileInput" accept="image/*">
                <div class="image-container">
                    <img id="preview" alt="Preview">
                    <button class="remove-image-btn" id="removeImageBtn">✕</button>
                </div>
                <label class="btn-upload btn-upload-small" for="fileInput" id="chooseAnotherBtn" style="display: none;">Choose Another</label>
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

    </div>

    <!-- ===== TUTORIAL MODAL ===== -->
    <div class="tutorial-modal" id="tutorialModal">
        <div class="tutorial-modal-content">
            <button class="close-btn" id="tutorialCloseBtn">✕</button>
            <div class="tutorial-title" id="tutorialTitle">📖 Plant Care Tutorial</div>
            <div class="tutorial-video-container">
                <video id="tutorialVideo" controls autoplay>
                    <source src="" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            <!-- ===== PROFESSIONAL VIDEO CONTROLS ===== -->
            <div class="video-controls">
                <button class="video-btn" id="rewindBtn" title="Rewind 5 seconds">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="11,19 2,12 11,5 11,19"/>
                        <polygon points="19,19 10,12 19,5 19,19"/>
                    </svg>
                    <span class="btn-label">5</span>
                </button>
                
                <button class="video-btn" id="playPauseBtn" title="Play/Pause">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                        <polygon id="playIcon" points="5,3 19,12 5,21"/>
                        <rect id="pauseIcon" x="6" y="4" width="4" height="16" display="none"/>
                        <rect id="pauseIcon2" x="14" y="4" width="4" height="16" display="none"/>
                    </svg>
                </button>
                
                <button class="video-btn" id="forwardBtn" title="Forward 5 seconds">
                    <span class="btn-label">5</span>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="13,19 22,12 13,5 13,19"/>
                        <polygon points="5,19 14,12 5,5 5,19"/>
                    </svg>
                </button>
                
                <span class="video-time" id="videoTime">00:00 / 00:00</span>
                
                <button class="video-btn" id="downloadBtn" title="Download Tutorial">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="7,10 12,15 17,10"/>
                        <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                </button>
                
                <label class="video-speed-label">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"/>
                        <polyline points="12,6 12,12 16,14"/>
                    </svg>
                    <select class="video-speed-select" id="speedSelect">
                        <option value="0.5">0.5x</option>
                        <option value="0.75">0.75x</option>
                        <option value="1" selected>1x</option>
                        <option value="1.25">1.25x</option>
                        <option value="1.5">1.5x</option>
                        <option value="2">2x</option>
                    </select>
                </label>
            </div>
        </div>
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
        let audioElement = null;
        let isPiperFallback = false;
        let videoControlsInitialized = false;

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
            tutorialVideo: document.getElementById('tutorialVideo'),
            tutorialTitle: document.getElementById('tutorialTitle'),
            speechGreenBtn: document.getElementById('speechGreenBtn')
        };

        // ============================================
        // FORMAT TIME (MM:SS)
        // ============================================
        function formatTime(seconds) {
            if (isNaN(seconds) || !isFinite(seconds)) return '00:00';
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        }

        // ============================================
        // INIT VIDEO CONTROLS
        // ============================================
        function initVideoControls() {
            if (videoControlsInitialized) return;
            
            const video = el.tutorialVideo;
            const rewindBtn = document.getElementById('rewindBtn');
            const forwardBtn = document.getElementById('forwardBtn');
            const playPauseBtn = document.getElementById('playPauseBtn');
            const downloadBtn = document.getElementById('downloadBtn');
            const speedSelect = document.getElementById('speedSelect');
            const timeDisplay = document.getElementById('videoTime');
            const playIcon = document.getElementById('playIcon');
            const pauseIcon = document.getElementById('pauseIcon');
            const pauseIcon2 = document.getElementById('pauseIcon2');

            // Rewind 5 seconds
            rewindBtn.addEventListener('click', function() {
                video.currentTime = Math.max(0, video.currentTime - 5);
            });

            // Forward 5 seconds
            forwardBtn.addEventListener('click', function() {
                video.currentTime = Math.min(video.duration || 0, video.currentTime + 5);
            });

            // Play/Pause with icon toggle
            function updatePlayPauseIcon() {
                if (video.paused) {
                    playIcon.style.display = 'block';
                    pauseIcon.style.display = 'none';
                    pauseIcon2.style.display = 'none';
                } else {
                    playIcon.style.display = 'none';
                    pauseIcon.style.display = 'block';
                    pauseIcon2.style.display = 'block';
                }
            }

            playPauseBtn.addEventListener('click', function() {
                if (video.paused) {
                    video.play();
                } else {
                    video.pause();
                }
                updatePlayPauseIcon();
            });

            // Update icon when video state changes
            video.addEventListener('play', updatePlayPauseIcon);
            video.addEventListener('pause', updatePlayPauseIcon);

            // Update time display
            video.addEventListener('timeupdate', function() {
                const current = formatTime(video.currentTime);
                const total = formatTime(video.duration);
                timeDisplay.textContent = `${current} / ${total}`;
            });

            // Speed control
            speedSelect.addEventListener('change', function() {
                video.playbackRate = parseFloat(this.value);
            });

            // Download video
            downloadBtn.addEventListener('click', function() {
                const link = document.createElement('a');
                link.href = video.src;
                link.download = video.src.split('/').pop();
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            });

            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                if (!el.tutorialModal.classList.contains('show')) return;
                
                if (e.key === 'ArrowLeft') {
                    e.preventDefault();
                    video.currentTime = Math.max(0, video.currentTime - 5);
                }
                else if (e.key === 'ArrowRight') {
                    e.preventDefault();
                    video.currentTime = Math.min(video.duration || 0, video.currentTime + 5);
                }
                else if (e.key === ' ' || e.key === 'Spacebar') {
                    e.preventDefault();
                    if (video.paused) {
                        video.play();
                    } else {
                        video.pause();
                    }
                    updatePlayPauseIcon();
                }
            });
            
            // Initialize icon state
            updatePlayPauseIcon();
            videoControlsInitialized = true;
        }

        // ============================================
        // TUTORIAL
        // ============================================
        function showTutorial() {
            let videoPath = '';
            let titleText = '';
            
            if (currentLang === 'en') {
                videoPath = '{{ url_for("static", filename="Tutorial_Video/English_Tutorial.mp4") }}';
                titleText = '📖 Plant Care Tutorial (English)';
            } else {
                videoPath = '{{ url_for("static", filename="Tutorial_Video/Nepali_Tutorial.mp4") }}';
                titleText = '📖 प्लान्ट केयर ट्यूटोरियल (नेपाली)';
            }
            
            el.tutorialVideo.src = videoPath;
            el.tutorialTitle.textContent = titleText;
            el.tutorialVideo.load();
            el.tutorialModal.classList.add('show');
            
            if (!videoControlsInitialized) {
                initVideoControls();
                videoControlsInitialized = true;
            }
            
            setTimeout(() => {
                el.tutorialVideo.play();
            }, 300);
        }

        function closeTutorial() {
            el.tutorialVideo.pause();
            el.tutorialVideo.src = '';
            el.tutorialModal.classList.remove('show');
            
            const timeDisplay = document.getElementById('videoTime');
            if (timeDisplay) {
                timeDisplay.textContent = '00:00 / 00:00';
            }
        }

        // ============================================
        // PLAY AUDIO FROM BASE64 (Piper version - for Nepali)
        // ============================================
        function playAudioFromBase64(base64Data) {
            if (isSpeaking) {
                stopSpeaking();
                return;
            }
            
            if (audioElement) {
                audioElement.pause();
                audioElement = null;
            }
            
            audioElement = new Audio('data:audio/wav;base64,' + base64Data);
            
            audioElement.onplay = () => {
                isSpeaking = true;
                updateSpeechButton();
            };
            
            audioElement.onended = () => {
                isSpeaking = false;
                updateSpeechButton();
                audioElement = null;
            };
            
            audioElement.onerror = () => {
                isSpeaking = false;
                updateSpeechButton();
                audioElement = null;
            };
            
            audioElement.play();
        }

        // ============================================
        // STOP SPEAKING
        // ============================================
        function stopSpeaking() {
            if (window.speechSynthesis) {
                window.speechSynthesis.cancel();
            }
            
            if (audioElement) {
                audioElement.pause();
                audioElement = null;
            }
            
            isSpeaking = false;
            isPiperFallback = false;
            updateSpeechButton();
        }

        // ============================================
        // UPDATE SPEECH BUTTON
        // ============================================
        function updateSpeechButton() {
            const btn = el.speechGreenBtn;
            if (btn) {
                if (isSpeaking) {
                    btn.classList.add('speaking');
                    btn.textContent = '⏹️';
                } else {
                    btn.classList.remove('speaking');
                    btn.textContent = '🔊';
                }
            }
        }

        // ============================================
        // BUILD ENGLISH SPEECH TEXT
        // ============================================
        function buildEnglishSpeechText() {
            const isHealthy = diseaseData.class.includes('Healthy');
            let displayName = diseaseData.class;
            if (DISEASE_TRANSLATIONS['en'] && DISEASE_TRANSLATIONS['en'][diseaseData.class]) {
                displayName = DISEASE_TRANSLATIONS['en'][diseaseData.class];
            } else {
                displayName = diseaseData.class.replace(/_/g, ' ');
            }
            
            let text = `Diagnosis: ${displayName}. ... `;
            text += `Post Care Guidance. `;
            
            if (diseaseData.care) {
                if (diseaseData.care.immediate_actions && diseaseData.care.immediate_actions.length > 0) {
                    text += `What to do now. Immediate Actions: `;
                    text += diseaseData.care.immediate_actions.join('. ') + '. ';
                }
                if (diseaseData.care.treatment_options && diseaseData.care.treatment_options.length > 0) {
                    text += `Treatment Options: `;
                    text += diseaseData.care.treatment_options.join('. ') + '. ';
                }
                if (diseaseData.care.prevention) {
                    text += `Prevention: ${diseaseData.care.prevention}. `;
                }
                if (diseaseData.care.safety_warnings && diseaseData.care.safety_warnings.length > 0) {
                    text += `Safety warnings: `;
                    text += diseaseData.care.safety_warnings.join('. ') + '. ';
                }
                if (diseaseData.care.notice) {
                    text += `Notice: ${diseaseData.care.notice}. `;
                }
            }
            
            text = text.replace(/[^\w\s.,;:!?()\- ]/g, '');
            return text;
        }

        // ============================================
        // SPEAK ENGLISH USING BROWSER SPEECH SYNTHESIS
        // ============================================
        function speakEnglishWithBrowser() {
            if (window.speechSynthesis) {
                window.speechSynthesis.cancel();
            }
            
            let text = buildEnglishSpeechText();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';
            utterance.rate = 0.9;
            utterance.pitch = 1;
            
            utterance.onstart = () => {
                isSpeaking = true;
                isPiperFallback = false;
                updateSpeechButton();
            };
            
            utterance.onend = () => {
                isSpeaking = false;
                isPiperFallback = false;
                updateSpeechButton();
            };
            
            utterance.onerror = () => {
                if (isSpeaking) {
                    isSpeaking = false;
                    isPiperFallback = true;
                    updateSpeechButton();
                    speakNepaliWithPiper();
                }
            };
            
            window.speechSynthesis.speak(utterance);
        }

        // ============================================
        // SPEAK NEPALI USING PIPER
        // ============================================
        function speakNepaliWithPiper() {
            if (window.speechSynthesis) {
                window.speechSynthesis.cancel();
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

            isPiperFallback = false;

            if (currentLang === 'en') {
                speakEnglishWithBrowser();
                return;
            }

            speakNepaliWithPiper();
        }

        // ============================================
        // REMOVE IMAGE
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
        // TRANSLATION
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
            if (el.chooseAnotherBtn) el.chooseAnotherBtn.textContent = t.choose_another_btn || 'Choose Another';
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
        // FILE UPLOAD
        // ============================================
        el.fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                selectedFile = this.files[0];
                el.predictBtn.disabled = false;
                el.resultDiv.style.display = 'none';
                el.careSection.classList.remove('visible');
                diseaseData = null;
                stopSpeaking();
                
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
                stopSpeaking();
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
            stopSpeaking();
            
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

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeTutorial();
            }
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
    """Generate audio using Piper TTS (for Nepali only)"""
    global voice
    
    try:
        lang = request.args.get('lang', 'en')
        
        if voice is None:
            return jsonify({'success': False, 'error': 'Piper voice not loaded'}), 500
        
        disease_class = session.get('last_disease_class')
        if not disease_class:
            return jsonify({'success': False, 'error': 'No disease data available'}), 400
        
        care = get_care(disease_class, lang)
        disease_data = {'class': disease_class, 'care': care}
        ui_text = get_ui_text(lang)
        
        text = build_speech_text(disease_data, ui_text, lang)
        print(f"Text to speak: {text[:100]}...")
        
        audio_chunks = voice.synthesize(text)
        
        audio_bytes = b''
        for chunk in audio_chunks:
            audio_bytes += chunk.audio_int16_bytes
        
        print(f"Audio bytes length: {len(audio_bytes)}")
        
        wav_buffer = io.BytesIO()
        
        wav_buffer.write(b'RIFF')
        wav_buffer.write((36 + len(audio_bytes)).to_bytes(4, 'little'))
        wav_buffer.write(b'WAVE')
        wav_buffer.write(b'fmt ')
        wav_buffer.write((16).to_bytes(4, 'little'))
        wav_buffer.write((1).to_bytes(2, 'little'))
        wav_buffer.write((1).to_bytes(2, 'little'))
        wav_buffer.write((22050).to_bytes(4, 'little'))
        wav_buffer.write((44100).to_bytes(4, 'little'))
        wav_buffer.write((2).to_bytes(2, 'little'))
        wav_buffer.write((16).to_bytes(2, 'little'))
        wav_buffer.write(b'data')
        wav_buffer.write(len(audio_bytes).to_bytes(4, 'little'))
        wav_buffer.write(audio_bytes)
        
        wav_data = wav_buffer.getvalue()
        audio_base64 = base64.b64encode(wav_data).decode('utf-8')
        
        return jsonify({
            'success': True,
            'audio_base64': audio_base64,
            'language': lang
        })
        
    except Exception as e:
        print(f"Speech error: {e}")
        import traceback
        traceback.print_exc()
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
        'voice_loaded': voice is not None,
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
    print(f"TTS Engine: Browser API (English) + Piper (Nepali)")
    print(f"Voice: Google Nepali Medium (for Nepali)")
    print(f"Tutorials: English & Nepali video tutorials")
    print(f"Server: http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    app.run(debug=True, threaded=True)