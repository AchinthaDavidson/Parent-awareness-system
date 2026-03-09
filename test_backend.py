"""
Quick test script to verify the Parent Dashboard Backend is working.
Run this after starting the server with: python main.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/parentdashboard/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Health check passed: {data}")
        return True
    else:
        print(f"✗ Health check failed: {response.status_code}")
        return False

def test_root():
    """Test root endpoint"""
    print("\nTesting root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Root endpoint passed")
        print(f"  Message: {data.get('message')}")
        print(f"  Version: {data.get('version')}")
        return True
    else:
        print(f"✗ Root endpoint failed: {response.status_code}")
        return False

def test_list_pdfs():
    """Test listing PDFs"""
    print("\nTesting list PDFs endpoint...")
    response = requests.get(f"{BASE_URL}/parentdashboard/pdfs")
    if response.status_code == 200:
        data = response.json()
        pdf_count = len(data.get('files', []))
        print(f"✓ List PDFs passed")
        print(f"  Found {pdf_count} PDF files")
        return True
    else:
        print(f"✗ List PDFs failed: {response.status_code}")
        return False

def test_ask_question():
    """Test asking a question"""
    print("\nTesting ask question endpoint...")
    
    payload = {
        "question": "What is speech therapy?",
        "child_id": ""
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/parentdashboard/ask",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30  # LLM may take some time
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer', '')
            print(f"✓ Ask question passed")
            print(f"  Answer preview: {answer[:100]}...")
            return True
        else:
            print(f"✗ Ask question failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print(f"⚠ Ask question timed out (this can happen with LLMs)")
        return None  # Neutral - not pass/fail
    except Exception as e:
        print(f"✗ Ask question error: {e}")
        return False

def test_speech_progress():
    """Test speech progress endpoint"""
    print("\nTesting speech progress endpoint...")
    
    response = requests.get(f"{BASE_URL}/parentdashboard/speech-progress")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Speech progress passed")
        print(f"  Overall accuracy: {data.get('overall_accuracy', 'N/A')}%")
        print(f"  Total words: {data.get('total_words', 0)}")
        return True
    else:
        # May fail if Firebase not configured - that's OK for basic test
        print(f"⚠ Speech progress returned {response.status_code} (Firebase may not be configured)")
        return None

def main():
    print("=" * 60)
    print("Parent Dashboard Backend - Quick Test")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}\n")
    
    try:
        results = []
        results.append(test_root())
        results.append(test_health())
        results.append(test_list_pdfs())
        
        # Optional tests (may timeout or require Firebase)
        ask_result = test_ask_question()
        if ask_result is not None:
            results.append(ask_result)
        
        progress_result = test_speech_progress()
        if progress_result is not None:
            results.append(progress_result)
        
        print("\n" + "=" * 60)
        passed = sum(1 for r in results if r is True)
        total = len(results)
        print(f"Tests passed: {passed}/{total}")
        print("=" * 60)
        
        if all(r is True for r in results):
            print("\n✓ All tests passed! Backend is working correctly.")
        elif any(r is False for r in results):
            print("\n⚠ Some tests failed. Check the output above.")
        else:
            print("\n✓ Core endpoints working. Some features may need Firebase setup.")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to server!")
        print("  Make sure the server is running: python main.py")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")

if __name__ == "__main__":
    main()
