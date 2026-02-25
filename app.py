from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import requests
import re

app = Flask(__name__)
CORS(app)

# Hardcoded agent configuration
AGENT_ID = "agent_1901kj0npeb1ensaya8ax8kthrdw"
AGENT_PHONE_NUMBER_ID = "phnum_2601kdtetwm8ekms2wakxxvpxyvy"
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/convai/twilio/outbound-call"

def validate_phone_number(phone):
    """
    Validate phone number for Indian and US formats
    Indian: +91 followed by 10 digits, or 0 followed by 10 digits
    US: +1 followed by 10 digits, or 10 digits starting with area code
    """
    # Remove spaces, dashes, and parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Indian number patterns
    indian_patterns = [
        r'^\+91[6-9]\d{9}$',  # +91 followed by 10 digits starting with 6-9
        r'^91[6-9]\d{9}$',     # 91 followed by 10 digits starting with 6-9
        r'^0[6-9]\d{9}$',      # 0 followed by 10 digits starting with 6-9
    ]
    
    # US number patterns
    us_patterns = [
        r'^\+1[2-9]\d{2}[2-9]\d{2}\d{4}$',  # +1 followed by valid area code and number
        r'^1[2-9]\d{2}[2-9]\d{2}\d{4}$',    # 1 followed by valid area code and number
        r'^[2-9]\d{2}[2-9]\d{2}\d{4}$',     # Direct 10-digit number with valid area code
    ]
    
    # Check Indian patterns
    for pattern in indian_patterns:
        if re.match(pattern, cleaned):
            # Format as +91XXXXXXXXXX
            if cleaned.startswith('0'):
                return f"+91{cleaned[1:]}"
            elif cleaned.startswith('91'):
                return f"+{cleaned}"
            elif cleaned.startswith('+91'):
                return cleaned
            else:
                return f"+91{cleaned}"
    
    # Check US patterns
    for pattern in us_patterns:
        if re.match(pattern, cleaned):
            # Format as +1XXXXXXXXXX
            if cleaned.startswith('+1'):
                return cleaned
            elif cleaned.startswith('1'):
                return f"+{cleaned}"
            else:
                return f"+1{cleaned}"
    
    return None

@app.route('/')
def index():
    return render_template('index.html'), 200

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/make-call', methods=['POST'])
def make_call():
    try:
        data = request.json
        
        # Get API key from environment variable
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'ELEVENLABS_API_KEY environment variable is not set'
            }), 500
        
        # Validate phone number
        to_number = data.get('to_number', '').strip()
        validated_phone = validate_phone_number(to_number)
        if not validated_phone:
            return jsonify({
                'success': False,
                'error': 'Invalid phone number. Please enter a valid Indian (+91) or US (+1) number.'
            }), 400
        
        # Get dynamic variables from request
        dynamic_vars = data.get('dynamic_variables', {})
        
        # Process dynamic variables: replace empty strings with space
        processed_vars = {}
        for key, value in dynamic_vars.items():
            if value is None or value.strip() == '':
                processed_vars[key] = " "
            else:
                processed_vars[key] = value.strip()
        
        # Always send single space for removed fields
        processed_vars['patient_email'] = " "
        processed_vars['patient_dob'] = " "
        processed_vars['patient_address'] = " "
        processed_vars['patient_insurance_member_id'] = " "
        
        # Ensure required dynamic variables exist, defaulting to single space
        required_keys = [
            "patient_appointment_type",
            "procedure_name",
            "order_number",
            "patient_first_name",
            "patient_last_name",
            "referring_physician_first_name",
            "referring_physician_last_name",
            "patient_insurance_name",
            "procedure_code",
            "medical_record_number",
            "order_date",
        ]
        for key in required_keys:
            if key not in processed_vars:
                processed_vars[key] = " "

        # Explicitly remove patient_id if present; it should not be sent
        processed_vars.pop("patient_id", None)
        
        # Handle CT_Type based on appointment type
        appointment_type = processed_vars.get('patient_appointment_type', '').strip()
        if appointment_type == 'CT Scan':
            processed_vars['CT_Type'] = 'CT_Scan_Contrast'
        else:
            processed_vars['CT_Type'] = " "
        
        # Prepare request payload
        payload = {
            "agent_id": AGENT_ID,
            "agent_phone_number_id": AGENT_PHONE_NUMBER_ID,
            "to_number": validated_phone,
            "conversation_initiation_client_data": {
                "dynamic_variables": processed_vars
            }
        }
        
        # Make API call to ElevenLabs
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(ELEVENLABS_API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'message': result.get('message', 'Call initiated successfully'),
                'conversation_id': result.get('conversation_id'),
                'callSid': result.get('callSid')
            })
        else:
            error_data = response.json() if response.content else {}
            return jsonify({
                'success': False,
                'error': error_data.get('detail', {}).get('message', f'API Error: {response.status_code}'),
                'status_code': response.status_code
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

