# Windows SSL Certificate Fix Guide

## Problem
On Windows machines, especially in corporate environments, you may encounter this error:
```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate
```

## Solutions

### Solution 1: Disable SSL Verification (Quick Fix - Development Only)

**⚠️ WARNING: Only use this in trusted/internal networks!**

Add to your `.env` file:
```bash
ELI_SSL_VERIFY=false
```

This will disable SSL certificate verification for the LLM connection.

### Solution 2: Install Python Certificates (Recommended)

#### Option A: Using pip (Easiest)
```cmd
pip install --upgrade certifi
python -m pip install --upgrade certifi
```

#### Option B: Install Certificates Manually
1. Download certificates from: https://curl.se/ca/cacert.pem
2. Save to a location like: `C:\Python313\Lib\site-packages\certifi\cacert.pem`
3. Or set environment variable:
   ```cmd
   set SSL_CERT_FILE=C:\path\to\cacert.pem
   ```

#### Option C: Use Python's Certificate Installer
```cmd
python -m pip install --upgrade pip
python -m pip install --upgrade certifi
python -c "import certifi; print(certifi.where())"
```

### Solution 3: Install Corporate CA Certificate (Corporate Networks)

If you're behind a corporate proxy/firewall:

1. **Export the corporate CA certificate:**
   - Open Internet Explorer/Edge
   - Go to Internet Options → Content → Certificates
   - Export the root CA certificate
   - Save as `.cer` or `.pem` file

2. **Add to Python's certificate store:**
   ```cmd
   # Find certifi location
   python -c "import certifi; print(certifi.where())"
   
   # Copy your corporate certificate to that location
   # Or append to the existing certificate file
   ```

3. **Or set environment variable:**
   ```cmd
   set REQUESTS_CA_BUNDLE=C:\path\to\corporate-ca.pem
   set SSL_CERT_FILE=C:\path\to\corporate-ca.pem
   ```

### Solution 4: Use System Certificate Store (Windows)

Some Python installations can use Windows certificate store:

```python
# This is handled automatically by httpx in newer versions
# But you may need to ensure certifi is installed
pip install certifi
```

## Verification

After applying a fix, test the connection:

```python
import httpx
import os

# Test with your base URL
base_url = os.getenv("ELI_BASE_URL", "https://gateway.eli.gaia.gic.ericsson.se/api/openai/v1")
verify = os.getenv("ELI_SSL_VERIFY", "true").lower() not in ("false", "0")

try:
    response = httpx.get(base_url, verify=verify, timeout=5)
    print("✅ SSL connection successful!")
except Exception as e:
    print(f"❌ SSL connection failed: {e}")
```

## Environment Variables Summary

Add to `.env` file:

```bash
# Required
ELI_API_KEY=your-api-key
ELI_BASE_URL=https://your-gateway-url/v1

# Optional - SSL Certificate Fix
ELI_SSL_VERIFY=false  # Set to false to disable SSL verification (development only)
```

## Best Practices

1. **Development/Internal Networks**: Use `ELI_SSL_VERIFY=false` if certificates are causing issues
2. **Production**: Always use proper certificates (`ELI_SSL_VERIFY=true` or omit)
3. **Corporate Networks**: Install corporate CA certificates properly
4. **Public Networks**: Never disable SSL verification

## Troubleshooting

### Still getting errors?

1. Check if you're behind a proxy:
   ```cmd
   echo %HTTP_PROXY%
   echo %HTTPS_PROXY%
   ```

2. If using a proxy, configure it:
   ```bash
   # In .env file
   HTTP_PROXY=http://proxy.company.com:8080
   HTTPS_PROXY=http://proxy.company.com:8080
   ```

3. Check Python version and certifi:
   ```cmd
   python --version
   pip show certifi
   ```

4. Update all packages:
   ```cmd
   pip install --upgrade pip certifi httpx openai
   ```

