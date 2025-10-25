import requests
import json

# Primeiro fazer login
login_data = {
    "email": "marcosagnes@gmail.com",
    "password": "abc123"
}

response = requests.post(
    "http://localhost:8040/auth/login",
    headers={"Content-Type": "application/json"},
    json=login_data
)

print(f"Login Status Code: {response.status_code}")
print(f"Login Response: {response.text}")

if response.status_code == 200:
    print("✅ Login realizado com sucesso!")
    data = response.json()
    token = data.get('access_token')
    print(f"Token: {token[:50]}...")
    
    # Testar endpoint protegido
    headers = {"Authorization": f"Bearer {token}"}
    profile_response = requests.get(
        "http://localhost:8040/auth/me",
        headers=headers
    )
    
    print(f"\nProfile Status Code: {profile_response.status_code}")
    print(f"Profile Response: {profile_response.text}")
    
    if profile_response.status_code == 200:
        print("✅ Acesso ao perfil funcionando!")
    else:
        print("❌ Erro ao acessar perfil")
        
else:
    print("❌ Erro no login")