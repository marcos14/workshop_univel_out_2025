import requests
import json
import time

print("🧪 Testando processamento MANUAL de embeddings...")

# Login
login_data = {"email": "marcosagnes@gmail.com", "password": "abc123"}
response = requests.post("http://localhost:8040/auth/login", json=login_data)

if response.status_code == 200:
    token = response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    # Listar livros para pegar um ID
    books_response = requests.get("http://localhost:8040/books/", headers=headers)
    
    if books_response.status_code == 200:
        books = books_response.json().get('books', [])
        
        if books:
            book_id = books[0]['id']  # Pegar o primeiro livro
            print(f"📖 Processando embeddings para livro ID: {book_id}")
            print(f"Título: {books[0]['title']}")
            
            # Testar processamento manual
            print("⚙️ Iniciando processamento manual...")
            start_time = time.time()
            
            try:
                process_response = requests.post(
                    f"http://localhost:8040/books/{book_id}/process-embeddings",
                    headers=headers,
                    timeout=30  # Timeout maior para processamento
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"⏱️ Processamento completado em {duration:.2f} segundos")
                print(f"Status: {process_response.status_code}")
                print(f"Response: {process_response.text}")
                
                # Testar responsividade durante e após processamento
                print("\n🔍 Testando responsividade após processamento...")
                
                for i in range(3):
                    health = requests.get("http://localhost:8040/health", timeout=5)
                    print(f"Health check {i+1}: {health.status_code}")
                    time.sleep(1)
                
                print("✅ Teste de processamento manual concluído!")
                
            except requests.exceptions.Timeout:
                print("⏰ Processamento manual travou (timeout)")
            except Exception as e:
                print(f"❌ Erro no processamento manual: {e}")
                
        else:
            print("❌ Nenhum livro encontrado para testar")
    else:
        print("❌ Erro ao listar livros")
        
else:
    print("❌ Erro no login")