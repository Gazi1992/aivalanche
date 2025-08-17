# API Configuration Guide

## Setting up Google Gemini API

### 1. Get your API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

### 2. Configure Environment Variables

#### Method 1: Using .env file (Recommended for development)

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

3. The `.env` file is already in `.gitignore` so it won't be committed

#### Method 2: System Environment Variables (Recommended for production)

**Windows:**
```bash
setx GEMINI_API_KEY "your_actual_api_key_here"
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your_actual_api_key_here"
```

Or add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):
```bash
echo 'export GEMINI_API_KEY="your_actual_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Verify Setup

Start the backend server:
```bash
cd backend
python -m uvicorn api.server:app --reload
```

The server should start without warnings about missing API key.

## Security Best Practices

1. **Never commit API keys to version control**
   - Always use environment variables
   - Add `.env` to `.gitignore`

2. **Rotate keys regularly**
   - Generate new keys periodically
   - Delete old keys from Google AI Studio

3. **Use different keys for different environments**
   - Development key for local testing
   - Production key for deployed application

4. **Set usage limits**
   - Configure quotas in Google Cloud Console
   - Monitor usage regularly

## Troubleshooting

### API Key Not Found
If you see: "AI service is not configured. Please set GEMINI_API_KEY environment variable."

1. Check that `.env` file exists and contains the key
2. Restart the backend server after adding the key
3. Verify the key is valid in Google AI Studio

### Invalid API Key
If you get authentication errors:

1. Verify the key is copied correctly (no extra spaces)
2. Check the key hasn't been deleted or rotated
3. Ensure you have API access enabled in your Google account

### Rate Limiting
If requests are being throttled:

1. Check your usage in Google Cloud Console
2. Consider upgrading to a paid plan
3. Implement caching to reduce API calls