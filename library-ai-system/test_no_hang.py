import requests
import json
import time

print("🧪 Testando upload SEM processamento automático de embeddings...")

# Login
login_data = {"email": "marcosagnes@gmail.com", "password": "abc123"}
response = requests.post("http://localhost:8040/auth/login", json=login_data)

if response.status_code == 200:
    token = response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    # PDF de teste simples
    test_pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Teste sem travamento!) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
299
%%EOF"""

    params = {
        "title": "Teste Sem Travamento Final",
        "isbn": f"978-{int(time.time())}", # ISBN único baseado no timestamp
        "publication_year": 2024,
        "publisher": "Publisher Teste",
        "language": "Portuguese",
        "genre": "test",
        "description": "PDF de teste para verificar que não trava mais",
        "author_names": '["Autor Teste"]'
    }
    
    files = {'file': ('test_no_hang.pdf', test_pdf_content, 'application/pdf')}
    
    print("📚 Fazendo upload...")
    start_time = time.time()
    
    upload_response = requests.post(
        "http://localhost:8040/books/upload",
        headers=headers,
        files=files,
        params=params,
        timeout=15
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"⏱️ Upload completado em {duration:.2f} segundos")
    print(f"Status: {upload_response.status_code}")
    
    if upload_response.status_code == 200:
        response_data = upload_response.json()
        print("✅ Upload bem-sucedido!")
        print(f"Book ID: {response_data.get('book_id')}")
        print(f"Message: {response_data.get('message')}")
        
        # Testar imediatamente se API ainda responde
        print("\n🔍 Testando responsividade IMEDIATA...")
        health1 = requests.get("http://localhost:8040/health", timeout=5)
        print(f"Health 1: {health1.status_code}")
        
        # Testar novamente após 1 segundo
        time.sleep(1)
        print("🔍 Testando após 1 segundo...")
        health2 = requests.get("http://localhost:8040/health", timeout=5)
        print(f"Health 2: {health2.status_code}")
        
        # Testar listagem de livros
        print("📚 Testando listagem...")
        books = requests.get("http://localhost:8040/books/", headers=headers, timeout=5)
        print(f"Books: {books.status_code}")
        
        if books.status_code == 200:
            total = books.json().get('total', 0)
            print(f"✅ Sistema totalmente responsivo! Total de livros: {total}")
        
    else:
        print("❌ Erro no upload")
        print(upload_response.text)
        
else:
    print("❌ Erro no login")