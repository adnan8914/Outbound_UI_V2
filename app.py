from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import requests
import re

app = Flask(__name__)
CORS(app)

# Hardcoded agent configuration
AGENT_ID = "agent_2901kjjw7dvbewerjp1csvgpvjz2"
AGENT_PHONE_NUMBER_ID = "phnum_1401kbkjfxxzfgx95b8sdfqczkkf"
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
        if not isinstance(data, dict):
            return jsonify({
                'success': False,
                'error': 'Invalid JSON body'
            }), 400
        
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
        if not isinstance(dynamic_vars, dict):
            return jsonify({
                'success': False,
                'error': 'dynamic_variables must be a JSON object'
            }), 400

        # Required dynamic variables (must be provided by UI)
        required_dynamic_keys = [
            "patient_first_name",
            "patient_last_name",
            "procedure_name",
            "referring_physician_first_name",
            "referring_physician_last_name",
            "patient_gender",
            "patient_appointment_type",
        ]

        processed_vars = {}
        missing_fields = []
        for key in required_dynamic_keys:
            raw_value = dynamic_vars.get(key, "")
            value = raw_value.strip() if isinstance(raw_value, str) else str(raw_value).strip()
            if not value:
                missing_fields.append(key)
            else:
                processed_vars[key] = value

        if missing_fields:
            return jsonify({
                'success': False,
                'error': f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        # Backend-only dynamic variables (always sent as single space)
        backend_only_keys = [
            "patient_appointment_start",
            "patient_id",
            "patient_insurance_member_id",
            "patient_insurance_name",
            "patient_phone",
            "patient_email",
            "patient_dob",
            "mrn",
        ]
        for key in backend_only_keys:
            processed_vars[key] = " "
        
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

