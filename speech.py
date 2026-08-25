# speech.py - Read Out Loud functionality
import re

def build_speech_text(disease_data, ui_text, lang='en'):
    """
    Build text for speech synthesis based on disease data and language
    
    Args:
        disease_data: Dictionary containing disease info and care instructions
        ui_text: UI translations dictionary
        lang: Language code ('en' or 'ne')
    
    Returns:
        String containing formatted text for speech
    """
    if not disease_data:
        return None
    
    # Get the disease class name
    disease_class = disease_data.get('class', '')
    care = disease_data.get('care', {})
    text = ''
    
    # Get display name - from care title or class name
    if disease_class:
        disease_display = care.get('title', disease_class.replace('_', ' '))
        disease_display = clean_text_for_speech(disease_display)
    else:
        disease_display = 'Unknown'
    
    # Get translations based on language
    if lang == 'en':
        # FIRST: Read the disease/health status
        text += f"Diagnosis: {disease_display}. "
        
        # Add a 3-second pause (three periods creates a longer pause)
        text += "... "
        
        # THEN: Care guidance
        # Care title
        text += f"{ui_text.get('care_title', 'Post Care Guidance')}. "
        
        # What to do now - Immediate Actions
        if care.get('immediate_actions') and len(care['immediate_actions']) > 0:
            text += f"{ui_text.get('what_to_do', 'What to do now')}. "
            text += f"{ui_text.get('immediate_actions', 'Immediate Actions')}: "
            clean_actions = [clean_text_for_speech(a) for a in care['immediate_actions']]
            text += '. '.join(clean_actions) + '. '
        
        # Treatment Options
        if care.get('treatment_options') and len(care['treatment_options']) > 0:
            text += f"{ui_text.get('treatment_options', 'Treatment Options')}: "
            clean_options = [clean_text_for_speech(a) for a in care['treatment_options']]
            text += '. '.join(clean_options) + '. '
        
        # Prevention
        if care.get('prevention'):
            text += f"{ui_text.get('prevention', 'Prevention')}: {clean_text_for_speech(care['prevention'])}. "
        
        # Safety warnings
        if care.get('safety_warnings') and len(care['safety_warnings']) > 0:
            text += f"{ui_text.get('safety_warnings', 'Safety warnings')}: "
            clean_warnings = [clean_text_for_speech(a) for a in care['safety_warnings']]
            text += '. '.join(clean_warnings) + '. '
        
        # Notice
        if care.get('notice'):
            text += f"{ui_text.get('notice', 'Notice')}: {clean_text_for_speech(care['notice'])}. "
    
    else:  # Nepali
        # FIRST: Read the disease/health status
        text += f"निदान: {disease_display}. "
        
        # Add a 3-second pause
        text += "... "
        
        # THEN: Care guidance
        # Care title
        text += f"{ui_text.get('care_title', 'पश्चात् सेवा मार्गदर्शन')}. "
        
        # What to do now - Immediate Actions
        if care.get('immediate_actions') and len(care['immediate_actions']) > 0:
            text += f"{ui_text.get('what_to_do', 'अब के गर्ने')}. "
            text += f"{ui_text.get('immediate_actions', 'तुरुन्त कार्यहरू')}: "
            clean_actions = [clean_text_for_speech(a) for a in care['immediate_actions']]
            text += '. '.join(clean_actions) + '. '
        
        # Treatment Options
        if care.get('treatment_options') and len(care['treatment_options']) > 0:
            text += f"{ui_text.get('treatment_options', 'उपचार विकल्पहरू')}: "
            clean_options = [clean_text_for_speech(a) for a in care['treatment_options']]
            text += '. '.join(clean_options) + '. '
        
        # Prevention
        if care.get('prevention'):
            text += f"{ui_text.get('prevention', 'रोकथाम')}: {clean_text_for_speech(care['prevention'])}. "
        
        # Safety warnings
        if care.get('safety_warnings') and len(care['safety_warnings']) > 0:
            text += f"{ui_text.get('safety_warnings', 'सुरक्षा चेतावनीहरू')}: "
            clean_warnings = [clean_text_for_speech(a) for a in care['safety_warnings']]
            text += '. '.join(clean_warnings) + '. '
        
        # Notice
        if care.get('notice'):
            text += f"{ui_text.get('notice', 'सूचना')}: {clean_text_for_speech(care['notice'])}. "
    
    return text


def clean_text_for_speech(text):
    """
    Remove emojis and special characters that don't read well in speech synthesis
    
    Args:
        text: String to clean
    
    Returns:
        Cleaned string
    """
    # Remove emojis and special symbols
    # Keep letters, numbers, punctuation, and spaces
    cleaned = re.sub(r'[^\w\s.,;:!?()\-]', '', text)
    # Remove extra spaces
    cleaned = ' '.join(cleaned.split())
    return cleaned


def get_speech_language(lang_code):
    """
    Get the speech synthesis language code
    
    Args:
        lang_code: 'en' or 'ne'
    
    Returns:
        Language code for speech synthesis
    """
    return 'ne-NP' if lang_code == 'ne' else 'en-US'