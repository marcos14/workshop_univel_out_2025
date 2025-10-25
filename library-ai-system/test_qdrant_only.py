import requests
import json

print("🧪 Testando apenas a conexão com Qdrant...")

# Login
login_data = {"email": "marcosagnes@gmail.com", "password": "abc123"}
response = requests.post("http://localhost:8040/auth/login", json=login_data)

if response.status_code == 200:
    token = response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    # Testar endpoint de teste do Qdrant
    print("🔍 Testando Qdrant...")
    qdrant_test = requests.get("http://localhost:8040/books/test-qdrant", headers=headers, timeout=10)
    
    print(f"Status: {qdrant_test.status_code}")
    if qdrant_test.status_code == 200:
        print("✅ Qdrant funcionando!")
        print(qdrant_test.json())
    else:
        print("❌ Erro no Qdrant")
        print(qdrant_test.text)
        
else:
    print("❌ Erro no login")