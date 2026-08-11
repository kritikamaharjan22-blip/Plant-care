# tutorial_speech.py - Tutorial + Read Out Loud functionality

# ============================================
# TUTORIAL STEPS
# ============================================
TUTORIAL_STEPS = [
    {
        "id": "welcome",
        "highlight": ".lang-toggle",
        "action": "click",
        "en": {
            "title": "👋 Welcome to Plant Care!",
            "desc": "Click the Translation button to switch between English and Nepali.",
            "instruction": "👉 Click the Translation button to continue"
        },
        "ne": {
            "title": "👋 प्लान्ट केयरमा स्वागत छ!",
            "desc": "अनुवाद बटनमा क्लिक गर्नुहोस् अंग्रेजी र नेपाली बीच स्विच गर्न।",
            "instruction": "👉 जारी राख्न अनुवाद बटन क्लिक गर्नुहोस्"
        }
    },
    {
        "id": "upload",
        "highlight": "#dropZone",
        "action": "click_or_ok",
        "en": {
            "title": "📸 Upload a Leaf Photo",
            "desc": "Click here or drag and drop a photo of a leaf from your plant.",
            "instruction": "👉 Click here or press OK to continue"
        },
        "ne": {
            "title": "📸 पातको फोटो अपलोड गर्नुहोस्",
            "desc": "यहाँ क्लिक गर्नुहोस् वा तपाईंको बिरुवाको पातको फोटो तान्नुहोस्।",
            "instruction": "👉 जारी राख्न यहाँ क्लिक गर्नुहोस् वा OK थिच्नुहोस्"
        }
    },
    {
        "id": "diagnose",
        "highlight": "#predictBtn",
        "action": "click_or_ok",
        "en": {
            "title": "🔍 Diagnose Your Plant",
            "desc": "After uploading a photo, click here to detect diseases.",
            "instruction": "👉 Click the Analyze button or press OK"
        },
        "ne": {
            "title": "🔍 आफ्नो बिरुवा निदान गर्नुहोस्",
            "desc": "फोटो अपलोड गरेपछि, रोग पत्ता लगाउन यहाँ क्लिक गर्नुहोस्।",
            "instruction": "👉 विश्लेषण बटन क्लिक गर्नुहोस् वा OK थिच्नुहोस्"
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
            "desc": "Use Read Out Loud to hear instructions. Tutorial replays this guide anytime.",
            "instruction": "👉 Press OK to finish the tutorial"
        },
        "ne": {
            "title": "🔊 अतिरिक्त सुविधाहरू",
            "desc": "पढेर सुनाउनुहोस् प्रयोग गर्नुहोस् निर्देशनहरू सुन्न। ट्यूटोरियलले यो गाइड पुन: चलाउँछ।",
            "instruction": "👉 ट्यूटोरियल समाप्त गर्न OK थिच्नुहोस्"
        }
    }
]

def get_all_tutorial_steps(lang='en'):
    """Get all tutorial steps in a language"""
    return [{
        'id': step['id'],
        'highlight': step['highlight'],
        'action': step['action'],
        **step.get(lang, step['en'])
    } for step in TUTORIAL_STEPS]