import requests

# Testar acesso à documentação da API
response = requests.get("http://localhost:8040/docs")
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    print("✅ API está respondendo!")
    
    # Testar endpoint de healthcheck se existir
    try:
        health_response = requests.get("http://localhost:8040/health")
        print(f"Health Status: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"Health Response: {health_response.text}")
    except:
        print("Endpoint /health não existe")
    
    # Testar endpoint de livros (sem autenticação primeiro)
    try:
        books_response = requests.get("http://localhost:8040/books/")
        print(f"Books Status: {books_response.status_code}")
        print(f"Books Response: {books_response.text}")
    except Exception as e:
        print(f"Erro ao testar books: {e}")
        
else:
    print("❌ API não está respondendo")