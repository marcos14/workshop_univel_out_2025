import requests
import json

# Primeiro fazer login para obter token
login_data = {
    "email": "marcosagnes@gmail.com",
    "password": "abc123"
}

response = requests.post(
    "http://localhost:8040/auth/login",
    headers={"Content-Type": "application/json"},
    json=login_data
)

if response.status_code == 200:
    token = response.json().get('access_token')
    print("✅ Login realizado com sucesso!")
    
    # Testar listagem de livros
    headers = {"Authorization": f"Bearer {token}"}
    books_response = requests.get(
        "http://localhost:8040/books/",
        headers=headers
    )
    
    print(f"Livros Status: {books_response.status_code}")
    if books_response.status_code == 200:
        books_data = books_response.json()
        print(f"✅ Total de livros: {books_data.get('total', 0)}")
        print(f"Livros na página: {len(books_data.get('books', []))}")
    else:
        print(f"❌ Erro ao listar livros: {books_response.text}")
        
else:
    print("❌ Erro no login")
    print(response.text)