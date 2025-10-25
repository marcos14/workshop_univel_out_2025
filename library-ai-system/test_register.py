import requests
import json

# Dados para teste de registro
user_data = {
    "name": "Marcos Agnes",
    "email": "marcosagnes@gmail.com",
    "password": "abc123"
}

# Fazer request de registro
response = requests.post(
    "http://localhost:8040/auth/register",
    headers={"Content-Type": "application/json"},
    json=user_data
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print("✅ Registro realizado com sucesso!")
    data = response.json()
    print(f"ID do usuário: {data.get('id')}")
    print(f"Nome: {data.get('name')}")
    print(f"Email: {data.get('email')}")
else:
    print("❌ Erro no registro")