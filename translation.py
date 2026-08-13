# translation.py - Complete with ALL translations (UI + Care Instructions)
import random

# ============================================
# UI TRANSLATIONS - Full Interface
# ============================================
UI_TRANSLATIONS = {
    'en': {
        # App
        'app_title': 'Plant Care',
        'app_subtitle': 'Smart Disease Detection for Your Plants',
        
        # Header
        'read_btn': '🔊 Read',
        'read_btn_stop': '⏹️ Stop',
        'tutorial_btn': '🎓 Tutorial',
        'lang_en': 'EN',
        'lang_ne': 'NE',
        
        # Upload Area
        'upload_title': 'Upload a leaf image',
        'upload_hint': 'Drag & drop or click to browse',
        'browse_btn': '📁 Choose Image',
        'choose_another_btn': '📁 Choose Another Image',
        'analyze_btn': '🔍 Analyze Plant',
        
        # Loading
        'loading_text': 'Analyzing your plant...',
        
        # Results
        'confidence': 'Confidence',
        'resultHealthy': '🌿 Your plant appears healthy!',
        'resultDisease': '⚠️ Disease detected!',
        'care_title': '📋 Post Care Guidance',
        
        # Care Sections
        'what_to_do': 'What to do now',
        'treatment_options': 'Treatment Options',
        'prevention': 'Prevention',
        'safety_warnings': 'Safety warnings',
        'notice': 'Notice',
        'immediate_actions': 'Immediate Actions',
        
        # Plant info
        'diagnosable_plants': 'Currently diagnosable plants:',
        
        # Footer
        'footer': '🌱 Keep your plants healthy with Plant Care',
        
        # Welcome Popup
        'popup_title': 'Welcome to Plant Care!',
        'popup_tagline': 'Your smart companion for healthy plants',
        'popup_subtext': '🌱 Helping you detect and treat plant diseases',
        'popup_btn': '🌿 Get Started',
        
        # Alerts
        'no_disease_alert': 'Please diagnose a plant first!',
        'error_title': 'Error',
        'connection_error': 'Connection Error',
    },
    'ne': {
        # App
        'app_title': 'प्लान्ट केयर',
        'app_subtitle': 'तपाईंको बिरुवाहरूको लागि स्मार्ट रोग पत्ता लगाउने',
        
        # Header
        'read_btn': '🔊 पढ्नुहोस्',
        'read_btn_stop': '⏹️ रोक्नुहोस्',
        'tutorial_btn': '🎓 ट्यूटोरियल',
        'lang_en': 'अं',
        'lang_ne': 'ने',
        
        # Upload Area
        'upload_title': 'पातको फोटो अपलोड गर्नुहोस्',
        'upload_hint': 'तान्नुहोस् र छोड्नुहोस् वा ब्राउज गर्न क्लिक गर्नुहोस्',
        'browse_btn': '📁 फोटो छान्नुहोस्',
        'choose_another_btn': '📁 अर्को फोटो छान्नुहोस्',
        'analyze_btn': '🔍 बिरुवा विश्लेषण गर्नुहोस्',
        
        # Loading
        'loading_text': 'तपाईंको बिरुवा विश्लेषण गर्दै...',
        
        # Results
        'confidence': 'विश्वसनीयता',
        'resultHealthy': '🌿 तपाईंको बिरुवा स्वस्थ देखिन्छ!',
        'resultDisease': '⚠️ रोग पत्ता लाग्यो!',
        'care_title': '📋 पश्चात् सेवा मार्गदर्शन',
        
        # Care Sections
        'what_to_do': 'अब के गर्ने',
        'treatment_options': 'उपचार विकल्पहरू',
        'prevention': 'रोकथाम',
        'safety_warnings': 'सुरक्षा चेतावनीहरू',
        'notice': 'सूचना',
        'immediate_actions': 'तुरुन्त कार्यहरू',
        
        # Plant info
        'diagnosable_plants': 'हाल निदान गर्न सकिने बिरुवाहरू:',
        
        # Footer
        'footer': '🌱 प्लान्ट केयरसँग आफ्नो बिरुवाहरू स्वस्थ राख्नुहोस्',
        
        # Welcome Popup
        'popup_title': '🌿 प्लान्ट केयरमा स्वागत छ!',
        'popup_tagline': 'स्वस्थ बिरुवाहरूको लागि तपाईंको स्मार्ट साथी',
        'popup_subtext': '🌱 बिरुवाका रोगहरू पत्ता लगाउन र उपचार गर्न मद्दत गर्दै',
        'popup_btn': '🌿 सुरु गर्नुहोस्',
        
        # Alerts
        'no_disease_alert': 'कृपया पहिले बिरुवा निदान गर्नुहोस्!',
        'error_title': 'त्रुटि',
        'connection_error': 'जडान त्रुटि',
    }
}

# ============================================
# DISEASE NAME MAPPING
# ============================================
# Maps model output names to CARE_DATA keys
DISEASE_NAME_MAPPING = {
    'Rice___Brown_Spot': 'Rice - Brown Spot',
    'Rice___Healthy': 'Rice - Healthy',
    'Rice___Leaf_Blast': 'Rice - Leaf Blast',
    'Rice___Neck_Blast': 'Rice - Neck Blast',
    'Potato___Early_Blight': 'Potato - Early Blight',
    'Potato___Healthy': 'Potato - Healthy',
    'Potato___Late_Blight': 'Potato - Late Blight'
}

# ============================================
# CARE INSTRUCTIONS (English + Nepali)
# ============================================
CARE_DATA = {
    "Rice - Brown Spot": {
        "en": {
            "title": "🌾 Rice - Brown Spot",
            "immediate_actions": [
                "🔴 Remove infected leaves immediately - dispose in sealed bag",
                "💧 Apply recommended fungicide (Mancozeb or Copper Oxychloride)",
                "🌱 Ensure proper spacing between plants (at least 20cm apart)",
                "💦 Water at base of plants - avoid overhead watering"
            ],
            "treatment_options": [
                "🌿 Apply neem oil spray (2ml/L water) every 5 days",
                "🧪 Use Trichoderma bio-fungicide as preventive measure",
                "🌾 Apply potassium-rich fertilizer to boost resistance"
            ],
            "prevention": "🛡️ Use resistant varieties and maintain proper drainage",
            "safety_warnings": [
                "⚠️ DO NOT water in the evening (increases fungal growth)",
                "⚠️ DO NOT use same fungicide repeatedly (can cause resistance)",
                "⚠️ Wear protective gear when applying chemicals"
            ],
            "notice": "📢 If leaves develop large dark spots (>1cm) or spread rapidly, consult an agricultural officer immediately"
        },
        "ne": {
            "title": "🌾 धान - खैरो धब्बा",
            "immediate_actions": [
                "🔴 संक्रमित पातहरू तुरुन्त हटाउनुहोस् - बन्द झोलामा फाल्नुहोस्",
                "💧 सिफारिस गरिएको फंगिसाइड (म्यान्कोजेब वा कपर अक्सिक्लोराइड) प्रयोग गर्नुहोस्",
                "🌱 बिरुवाहरू बीच उचित दूरी (कम्तिमा २० सेमी) राख्नुहोस्",
                "💦 बिरुवाको फेदमा पानी दिनुहोस् - माथिबाट पानी हाल्नु हुँदैन"
            ],
            "treatment_options": [
                "🌿 नीमको तेल स्प्रे (२ मिली/लिटर पानी) हरेक ५ दिनमा लगाउनुहोस्",
                "🧪 ट्राइकोडर्मा जैविक फंगिसाइड रोकथामको लागि प्रयोग गर्नुहोस्",
                "🌾 पोटासियम युक्त मल प्रतिरोध बढाउन प्रयोग गर्नुहोस्"
            ],
            "prevention": "🛡️ प्रतिरोधी प्रजातिहरू प्रयोग गर्नुहोस् र राम्रो जल निकासी कायम राख्नुहोस्",
            "safety_warnings": [
                "⚠️ साँझमा पानी नहाल्नुहोस् (फंगस बढ्न सक्छ)",
                "⚠️ एउटै फंगिसाइड बारम्बार प्रयोग नगर्नुहोस् (प्रतिरोध हुन सक्छ)",
                "⚠️ रसायन लगाउँदा सुरक्षा गियर लगाउनुहोस्"
            ],
            "notice": "📢 यदि पातहरूमा ठूला कालो धब्बा (>१ सेमी) देखिन्छ वा छिटो फैलिन्छ भने तुरुन्त कृषि अधिकारीसँग सम्पर्क गर्नुहोस्"
        }
    },
    "Rice - Leaf Blast": {
        "en": {
            "title": "🌾 Rice - Leaf Blast",
            "immediate_actions": [
                "🔴 Remove and destroy all infected leaves immediately",
                "💧 Apply silicon-based fertilizer (foliar spray)",
                "💦 Reduce nitrogen fertilizer - apply balanced NPK",
                "🌱 Maintain proper water levels (shallow, intermittent irrigation)"
            ],
            "treatment_options": [
                "🌿 Apply Tricyclazole fungicide (0.6g/L water)",
                "🧪 Use Pseudomonas fluorescens bio-control",
                "🌾 Apply potassium silicate for resistance"
            ],
            "prevention": "🛡️ Use resistant varieties, proper spacing, and balanced fertilization",
            "safety_warnings": [
                "⚠️ DO NOT apply excess nitrogen fertilizer",
                "⚠️ DO NOT overcrowd plants",
                "⚠️ DO NOT use infected seeds"
            ],
            "notice": "🚨 URGENT: If >30% of leaves are infected, stop using nitrogen fertilizer and consult agricultural officer immediately"
        },
        "ne": {
            "title": "🌾 धान - पात विस्फोट",
            "immediate_actions": [
                "🔴 सबै संक्रमित पातहरू तुरुन्त हटाउनुहोस् र नष्ट गर्नुहोस्",
                "💧 सिलिकन-आधारित मल (पाते स्प्रे) प्रयोग गर्नुहोस्",
                "💦 नाइट्रोजन मल घटाउनुहोस् - सन्तुलित NPK प्रयोग गर्नुहोस्",
                "🌱 उचित पानीको स्तर कायम राख्नुहोस् (उथले, अन्तराल सिँचाइ)"
            ],
            "treatment_options": [
                "🌿 ट्राइसाइक्लाजोल फंगिसाइड (०.६ ग्राम/लिटर पानी) प्रयोग गर्नुहोस्",
                "🧪 स्यूडोमोनास फ्लोरेसेन्स जैविक नियन्त्रण प्रयोग गर्नुहोस्",
                "🌾 प्रतिरोधको लागि पोटासियम सिलिकेट प्रयोग गर्नुहोस्"
            ],
            "prevention": "🛡️ प्रतिरोधी प्रजातिहरू, उचित दूरी, र सन्तुलित मल प्रयोग गर्नुहोस्",
            "safety_warnings": [
                "⚠️ अत्यधिक नाइट्रोजन मल नलगाउनुहोस्",
                "⚠️ बिरुवाहरू धेरै नजिक नरोप्नुहोस्",
                "⚠️ संक्रमित बीउहरू प्रयोग नगर्नुहोस्"
            ],
            "notice": "🚨 अत्यावश्यक: यदि ३०% भन्दा बढी पातहरू संक्रमित छन् भने, नाइट्रोजन मल प्रयोग बन्द गर्नुहोस् र तुरुन्त कृषि अधिकारीसँग सम्पर्क गर्नुहोस्"
        }
    },
    "Rice - Neck Blast": {
        "en": {
            "title": "🌾 Rice - Neck Blast",
            "immediate_actions": [
                "🔴 Remove infected panicles immediately",
                "💧 Apply fungicide at booting stage (Edifenphos or Iprodione)",
                "🌱 Practice crop rotation - do not plant rice in same field for 2 years",
                "💦 Maintain proper water levels during panicle initiation"
            ],
            "treatment_options": [
                "🌿 Apply Kasugamycin (2ml/L water) as foliar spray",
                "🧪 Use Trichoderma viride in soil application",
                "🌾 Apply balanced fertilizer with extra potassium"
            ],
            "prevention": "🛡️ Use resistant varieties, practice crop rotation, and use disease-free seeds",
            "safety_warnings": [
                "⚠️ DO NOT plant rice in same field consecutively",
                "⚠️ DO NOT use infected seeds",
                "⚠️ DO NOT over-fertilize with nitrogen"
            ],
            "notice": "🚨 CRITICAL: If panicle neck turns brown and grains are empty, consult agricultural officer immediately - this can spread to entire field within 5-7 days"
        },
        "ne": {
            "title": "🌾 धान - घाँटी विस्फोट",
            "immediate_actions": [
                "🔴 संक्रमित बालाहरू तुरुन्त हटाउनुहोस्",
                "💧 बुटिंग अवस्थामा फंगिसाइड (एडिफेनफोस वा आइप्रोडियोन) लगाउनुहोस्",
                "🌱 बाली चक्रण अभ्यास गर्नुहोस् - २ वर्षसम्म एउटै खेतमा धान नरोप्नुहोस्",
                "💦 बाला सुरु हुने अवस्थामा उचित पानीको स्तर कायम राख्नुहोस्"
            ],
            "treatment_options": [
                "🌿 कासुगामाइसिन (२ मिली/लिटर पानी) पाते स्प्रेको रूपमा लगाउनुहोस्",
                "🧪 ट्राइकोडर्मा भिराइड माटोमा प्रयोग गर्नुहोस्",
                "🌾 अतिरिक्त पोटासियमसहित सन्तुलित मल प्रयोग गर्नुहोस्"
            ],
            "prevention": "🛡️ प्रतिरोधी प्रजातिहरू, बाली चक्रण, र रोग-मुक्त बीउहरू प्रयोग गर्नुहोस्",
            "safety_warnings": [
                "⚠️ एउटै खेतमा लगातार धान नरोप्नुहोस्",
                "⚠️ संक्रमित बीउहरू प्रयोग नगर्नुहोस्",
                "⚠️ नाइट्रोजनको अत्यधिक मल नलगाउनुहोस्"
            ],
            "notice": "🚨 महत्वपूर्ण: यदि बालाको घाँटी खैरो हुन्छ र अन्नहरू खाली छन् भने, तुरुन्त कृषि अधिकारीसँग सम्पर्क गर्नुहोस् - यो ५-७ दिनमा पूरै खेतमा फैलिन सक्छ"
        }
    },
    "Rice - Healthy": {
        "en": {
            "title": "🌾 Rice - Healthy",
            "immediate_actions": [
                "✅ Continue regular watering schedule",
                "🌱 Apply balanced fertilizer (NPK 4:2:3 ratio) monthly",
                "🔍 Monitor for pests weekly (look for leaf damage)",
                "🌿 Remove weeds regularly"
            ],
            "treatment_options": [
                "🌾 Apply compost or organic matter every 3 months",
                "💧 Maintain 5-8cm standing water during vegetative stage",
                "🌱 Practice integrated pest management (IPM)"
            ],
            "prevention": "🛡️ Continue good agricultural practices and regular monitoring",
            "safety_warnings": [
                "✅ Maintain good field hygiene",
                "✅ Use certified disease-free seeds for next season",
                "✅ Practice crop rotation to maintain soil health"
            ],
            "notice": "✅ Your crop appears healthy! Continue regular monitoring and consult if you notice any unusual leaf spots or wilting"
        },
        "ne": {
            "title": "🌾 धान - स्वस्थ",
            "immediate_actions": [
                "✅ नियमित पानीको तालिका जारी राख्नुहोस्",
                "🌱 मासिक सन्तुलित मल (NPK ४:२:३ अनुपात) लगाउनुहोस्",
                "🔍 साप्ताहिक कीटहरूको निगरानी गर्नुहोस् (पात क्षति हेर्नुहोस्)",
                "🌿 नियमित झारपात हटाउनुहोस्"
            ],
            "treatment_options": [
                "🌾 हरेक ३ महिनामा कम्पोस्ट वा जैविक मल लगाउनुहोस्",
                "💧 बिरुवा बढ्ने अवस्थामा ५-८ सेमी पानी कायम राख्नुहोस्",
                "🌱 एकीकृत कीट व्यवस्थापन (IPM) अभ्यास गर्नुहोस्"
            ],
            "prevention": "🛡️ राम्रो कृषि अभ्यास र नियमित निगरानी जारी राख्नुहोस्",
            "safety_warnings": [
                "✅ राम्रो खेत सरसफाई कायम राख्नुहोस्",
                "✅ अर्को सिजनको लागि प्रमाणित रोग-मुक्त बीउ प्रयोग गर्नुहोस्",
                "✅ माटोको स्वास्थ्य कायम राख्न बाली चक्रण अभ्यास गर्नुहोस्"
            ],
            "notice": "✅ तपाईंको बाली स्वस्थ देखिन्छ! नियमित निगरानी जारी राख्नुहोस् र कुनै असामान्य पात धब्बा वा सुख्खापन देखिएमा सल्लाह लिनुहोस्"
        }
    },
    "Potato - Early Blight": {
        "en": {
            "title": "🥔 Potato - Early Blight",
            "immediate_actions": [
                "🔴 Remove and destroy infected leaves - bag and burn",
                "💧 Apply copper-based fungicide (Copper Oxychloride 3g/L)",
                "🌱 Improve air circulation by proper spacing",
                "💦 Water at base - avoid wetting leaves"
            ],
            "treatment_options": [
                "🌿 Apply Azoxystrobin (1ml/L) every 7-10 days",
                "🧪 Use Bacillus subtilis as bio-control",
                "🌾 Apply potassium-rich fertilizer for resistance"
            ],
            "prevention": "🛡️ Use certified disease-free seed potatoes, practice crop rotation (3-4 years), and maintain proper drainage",
            "safety_warnings": [
                "⚠️ DO NOT compost infected plant material",
                "⚠️ DO NOT over-water",
                "⚠️ DO NOT work in field when wet"
            ],
            "notice": "⚠️ If stem lesions appear or >50% leaves affected, consult plant pathologist immediately - may spread to tubers"
        },
        "ne": {
            "title": "🥔 आलु - प्रारम्भिक झुसा",
            "immediate_actions": [
                "🔴 संक्रमित पातहरू हटाउनुहोस् र नष्ट गर्नुहोस् - झोलामा बन्द गरी जलाउनुहोस्",
                "💧 तामा-आधारित फंगिसाइड (कपर अक्सिक्लोराइड ३ ग्राम/लिटर) लगाउनुहोस्",
                "🌱 उचित दूरीले हावा संचार सुधार गर्नुहोस्",
                "💦 फेदमा पानी दिनुहोस् - पात भिजाउनु हुँदैन"
            ],
            "treatment_options": [
                "🌿 एजोक्सिस्ट्रोबिन (१ मिली/लिटर) हरेक ७-१० दिनमा लगाउनुहोस्",
                "🧪 ब्यासिलस सबटिलिस जैविक नियन्त्रणको रूपमा प्रयोग गर्नुहोस्",
                "🌾 प्रतिरोधको लागि पोटासियम युक्त मल लगाउनुहोस्"
            ],
            "prevention": "🛡️ प्रमाणित रोग-मुक्त बीउ आलु प्रयोग गर्नुहोस्, बाली चक्रण (३-४ वर्ष) अभ्यास गर्नुहोस्, र राम्रो जल निकासी कायम राख्नुहोस्",
            "safety_warnings": [
                "⚠️ संक्रमित बिरुवाको कम्पोस्ट नबनाउनुहोस्",
                "⚠️ अत्यधिक पानी नदिनुहोस्",
                "⚠️ खेत भिजेको बेला काम नगर्नुहोस्"
            ],
            "notice": "⚠️ यदि डाँठमा घाउ देखिन्छ वा ५०% भन्दा बढी पातहरू प्रभावित छन् भने, तुरुन्त बिरुवा रोग विशेषज्ञसँग सम्पर्क गर्नुहोस् - आलुसम्म फैलिन सक्छ"
        }
    },
    "Potato - Late Blight": {
        "en": {
            "title": "🥔 Potato - Late Blight",
            "immediate_actions": [
                "🚨 STOP all irrigation immediately",
                "🔴 Remove and destroy ALL infected plants - burn them",
                "💧 Apply emergency fungicide (Metalaxyl-M + Mancozeb)",
                "🌱 Quarantine area - prevent spreading to healthy plants"
            ],
            "treatment_options": [
                "🌿 Apply Cymoxanil + Famoxadone for severe cases",
                "🧪 Use copper-based spray as preventive on healthy plants",
                "🌾 Apply potash fertilizer to boost plant immunity"
            ],
            "prevention": "🛡️ Use resistant varieties, practice strict field hygiene, apply preventive fungicides before rainy season",
            "safety_warnings": [
                "⚠️ DO NOT touch infected plants without gloves",
                "⚠️ DO NOT compost infected plant material",
                "⚠️ DO NOT work in wet fields - spreads through water"
            ],
            "notice": "🚨 URGENT: Late blight is highly contagious and can destroy entire crop in 7 days. CONTACT AGRICULTURAL OFFICER IMMEDIATELY if you see water-soaked lesions"
        },
        "ne": {
            "title": "🥔 आलु - ढिलो झुसा",
            "immediate_actions": [
                "🚨 सबै सिँचाइ तुरुन्त बन्द गर्नुहोस्",
                "🔴 सबै संक्रमित बिरुवाहरू हटाउनुहोस् र नष्ट गर्नुहोस् - जलाउनुहोस्",
                "💧 आपातकालीन फंगिसाइड (मेटालाक्सिल-एम + म्यान्कोजेब) लगाउनुहोस्",
                "🌱 क्षेत्र क्वारेन्टाइन गर्नुहोस् - स्वस्थ बिरुवाहरूमा फैलिन नदिनुहोस्"
            ],
            "treatment_options": [
                "🌿 गम्भीर अवस्थाको लागि साइमोक्सानिल + फामोक्साडोन लगाउनुहोस्",
                "🧪 स्वस्थ बिरुवाहरूमा रोकथामको लागि तामा-आधारित स्प्रे प्रयोग गर्नुहोस्",
                "🌾 बिरुवाको प्रतिरोध क्षमता बढाउन पोटास मल लगाउनुहोस्"
            ],
            "prevention": "🛡️ प्रतिरोधी प्रजातिहरू प्रयोग गर्नुहोस्, कडा खेत सरसफाई अभ्यास गर्नुहोस्, वर्षायाम अघि रोकथाम फंगिसाइड लगाउनुहोस्",
            "safety_warnings": [
                "⚠️ पन्जा बिना संक्रमित बिरुवाहरू नछुनुहोस्",
                "⚠️ संक्रमित बिरुवाको कम्पोस्ट नबनाउनुहोस्",
                "⚠️ भिजेको खेतमा काम नगर्नुहोस् - पानीबाट फैलिन्छ"
            ],
            "notice": "🚨 अत्यावश्यक: ढिलो झुसा अत्यन्त संक्रामक छ र ७ दिनमा पूरै बाली नष्ट गर्न सक्छ। यदि पानीले भिजेको घाउ देख्नुभयो भने तुरुन्त कृषि अधिकारीसँग सम्पर्क गर्नुहोस्"
        }
    },
    "Potato - Healthy": {
        "en": {
            "title": "🥔 Potato - Healthy",
            "immediate_actions": [
                "✅ Continue regular watering schedule",
                "🌱 Apply balanced fertilizer (NPK 3:2:4 ratio) every 2 weeks",
                "🔍 Monitor for pests weekly - check under leaves",
                "🌿 Practice proper hilling (earthing up) for tuber protection"
            ],
            "treatment_options": [
                "🌾 Apply compost every 3 months for soil health",
                "💧 Maintain consistent moisture - don't let soil dry out",
                "🌱 Rotate crops annually to prevent soil-borne diseases"
            ],
            "prevention": "🛡️ Continue good agricultural practices and regular monitoring",
            "safety_warnings": [
                "✅ Use disease-free seed tubers",
                "✅ Practice crop rotation (avoid planting potatoes in same field for 3-4 years)",
                "✅ Maintain proper drainage to prevent waterlogging"
            ],
            "notice": "✅ Your crop appears healthy! Continue regular monitoring and consult if you notice any unusual spots or wilting"
        },
        "ne": {
            "title": "🥔 आलु - स्वस्थ",
            "immediate_actions": [
                "✅ नियमित पानीको तालिका जारी राख्नुहोस्",
                "🌱 हरेक २ हप्तामा सन्तुलित मल (NPK ३:२:४ अनुपात) लगाउनुहोस्",
                "🔍 साप्ताहिक कीटहरूको निगरानी गर्नुहोस् - पातको फेदमा हेर्नुहोस्",
                "🌿 आलुको सुरक्षाको लागि उचित माटो चढाउने अभ्यास गर्नुहोस्"
            ],
            "treatment_options": [
                "🌾 माटोको स्वास्थ्यको लागि हरेक ३ महिनामा कम्पोस्ट लगाउनुहोस्",
                "💧 लगातार चिस्यान कायम राख्नुहोस् - माटो सुख्खा हुन नदिनुहोस्",
                "🌱 माटोबाट हुने रोगहरू रोक्न वार्षिक बाली चक्रण गर्नुहोस्"
            ],
            "prevention": "🛡️ राम्रो कृषि अभ्यास र नियमित निगरानी जारी राख्नुहोस्",
            "safety_warnings": [
                "✅ रोग-मुक्त बीउ आलु प्रयोग गर्नुहोस्",
                "✅ बाली चक्रण अभ्यास गर्नुहोस् (एउटै खेतमा ३-४ वर्षसम्म आलु नरोप्नुहोस्)",
                "✅ पानी जम्न नदिन उचित जल निकासी कायम राख्नुहोस्"
            ],
            "notice": "✅ तपाईंको बाली स्वस्थ देखिन्छ! नियमित निगरानी जारी राख्नुहोस् र कुनै असामान्य धब्बा वा सुख्खापन देखिएमा सल्लाह लिनुहोस्"
        }
    }
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_ui_text(lang='en'):
    """Get all UI translations for a language"""
    if lang not in UI_TRANSLATIONS:
        lang = 'en'
    return UI_TRANSLATIONS[lang]

def get_care(disease_name, lang='en'):
    """Get dynamic care instructions for a disease"""
    # First try direct mapping
    mapped_key = DISEASE_NAME_MAPPING.get(disease_name)
    
    if mapped_key and mapped_key in CARE_DATA:
        disease_key = mapped_key
    else:
        # Try to find by partial match
        disease_key = None
        for key in CARE_DATA.keys():
            if disease_name in key or key in disease_name:
                disease_key = key
                break
    
    if not disease_key:
        return {
            'title': 'Care Instructions Not Found' if lang == 'en' else 'हेरचाह निर्देशनहरू फेला परेन',
            'immediate_actions': ['Please consult a plant expert for guidance'] if lang == 'en' else ['कृपया बिरुवा विशेषज्ञसँग सल्लाह लिनुहोस्'],
            'treatment_options': [],
            'prevention': 'Regular monitoring is recommended' if lang == 'en' else 'नियमित निगरानी सिफारिस गरिन्छ',
            'safety_warnings': ['Seek professional advice'] if lang == 'en' else ['पेशागत सल्लाह लिनुहोस्'],
            'notice': 'Contact your local agricultural extension office' if lang == 'en' else 'आफ्नो स्थानीय कृषि कार्यालयलाई सम्पर्क गर्नुहोस्'
        }
    
    data = CARE_DATA[disease_key]
    
    # Get language-specific content
    if lang not in data:
        lang = 'en'
    
    content = data[lang]
    
    # Add some dynamic variation to keep it fresh
    if 'treatment_options' in content and len(content['treatment_options']) > 1:
        random.seed(disease_name)
        options = content['treatment_options'][:]
        random.shuffle(options)
        content['treatment_options'] = options[:3]
        random.seed()
    
    return content

def get_language_name(lang_code):
    """Get full language name"""
    names = {'en': 'English', 'ne': 'Nepali'}
    return names.get(lang_code, 'Unknown')