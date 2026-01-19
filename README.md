# ElevenLabs Outbound Call UI

A Replit-deployable web application for initiating outbound calls through ElevenLabs Conversational AI with dynamic variables.

## Features

- 📞 Initiate outbound calls via ElevenLabs API
- ✅ Phone number validation for Indian (+91) and US (+1) numbers
- 📋 Dynamic variable form with all required fields
- 🔄 Auto-fill CT_Type when "CT Scan" is selected
- 🎨 Modern, responsive UI
- 🔒 Secure API key handling via environment variables

## Setup Instructions

### 1. Clone/Import to Replit

1. Import this project into Replit
2. Or create a new Repl and upload all files

### 2. Set Environment Variable

1. In Replit, click on the "Secrets" tab (lock icon) in the left sidebar
2. Add a new secret:
   - **Key**: `ELEVENLABS_API_KEY`
   - **Value**: Your ElevenLabs API key

### 3. Install Dependencies

The dependencies will be automatically installed when you run the project. If needed, you can manually run:

```bash
pip install -r requirements.txt
```

### 4. Run the Application

Click the "Run" button in Replit, or the application will start automatically.

The app will be available at the URL provided by Replit (usually something like `https://your-repl-name.username.repl.co`)

## Usage

1. **Enter Phone Number**: Enter the recipient's phone number in Indian (+91) or US (+1) format
2. **Fill Dynamic Variables**: Fill in the patient and appointment information
   - All fields are optional except "Appointment Type"
   - If "CT Scan" is selected, CT_Type will be automatically filled with "CT_Scan_Contrast"
   - Empty fields will be sent as a space character " " to the API
3. **Initiate Call**: Click "Initiate Outbound Call" button
4. **View Results**: Success/error messages will be displayed with conversation ID and call SID

## Phone Number Formats Supported

### Indian Numbers:
- `+919876543210`
- `919876543210`
- `09876543210`

### US Numbers:
- `+14155552671`
- `14155552671`
- `4155552671`

## Dynamic Variables

The following dynamic variables are supported:

- `patient_name`
- `procedure_name`
- `patient_id`
- `patient_insurance_member_id`
- `patient_email`
- `patient_appointment_type` (dropdown: MRI, Open MRI, CT Scan, Ultrasound, Digital X-Ray)
- `patient_address`
- `patient_dob`
- `CT_Type` (auto-filled when CT Scan is selected)
- `referring_physician_first_name`
- `referring_physician_last_name`
- `patient_insurance_name`

## Configuration

The following values are hardcoded in `app.py`:

- **Agent ID**: `agent_7401kf8xm2bafp8awsgfcs9ab96p`
- **Agent Phone Number ID**: `phnum_2601kdtetwm8ekms2wakxxvpxyvy`

To change these, edit the constants at the top of `app.py`.

## API Endpoints

### `GET /`
Serves the main UI form.

### `POST /api/make-call`
Initiates an outbound call.

**Request Body:**
```json
{
  "to_number": "+14155552671",
  "dynamic_variables": {
    "patient_name": "John Doe",
    "patient_appointment_type": "CT Scan",
    ...
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Outbound call initiated successfully.",
  "conversation_id": "conv_98765",
  "callSid": "CA1234567890abcdef1234567890abcdef"
}
```

## Error Handling

- Invalid phone numbers will return a validation error
- Missing API key will return an error message
- API errors from ElevenLabs will be displayed to the user

## Notes

- Empty dynamic variables are automatically converted to a space character " " before sending to the API
- The application validates and formats phone numbers automatically
- All API calls are made server-side to keep the API key secure

## Troubleshooting

1. **API Key Error**: Make sure `ELEVENLABS_API_KEY` is set in Replit Secrets
2. **Phone Validation Error**: Ensure the phone number follows Indian or US format
3. **Connection Error**: Check your internet connection and ElevenLabs API status

## License

This project is provided as-is for use with ElevenLabs API.

