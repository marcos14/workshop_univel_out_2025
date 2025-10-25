import requests
import json
import time

# Primeiro fazer login
login_data = {
    "email": "marcosagnes@gmail.com",
    "password": "abc123"
}

print("🔐 Fazendo login...")
response = requests.post(
    "http://localhost:8040/auth/login",
    headers={"Content-Type": "application/json"},
    json=login_data
)

if response.status_code == 200:
    token = response.json().get('access_token')
    print("✅ Login realizado com sucesso!")
    
    # Criar um PDF simples em texto para teste
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
(Hello World!) Tj
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

    # Testar upload
    headers = {"Authorization": f"Bearer {token}"}
    
    # Dados do livro
    book_data = {
        "title": "Teste de Upload",
        "isbn": "978-0000000000",
        "publication_year": 2024,
        "publisher": "Teste Publisher",
        "language": "Portuguese",
        "genre": "test",
        "description": "Livro de teste para verificar upload",
        "author_names": ["Autor Teste"]
    }
    
    files = {
        'file': ('test_book.pdf', test_pdf_content, 'application/pdf')
    }
    
    print("📚 Fazendo upload do livro...")
    start_time = time.time()
    
    try:
        upload_response = requests.post(
            "http://localhost:8040/books/upload",
            headers=headers,
            files=files,
            data=book_data,
            timeout=30  # Timeout de 30 segundos
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️ Upload completado em {duration:.2f} segundos")
        print(f"Status Code: {upload_response.status_code}")
        print(f"Response: {upload_response.text}")
        
        if upload_response.status_code == 200:
            print("✅ Upload realizado com sucesso!")
            
            # Testar se a API ainda está responsiva
            print("🔍 Testando se a API ainda está responsiva...")
            health_response = requests.get("http://localhost:8040/health", timeout=5)
            if health_response.status_code == 200:
                print("✅ API ainda está responsiva!")
            else:
                print("❌ API não está mais responsiva")
                
        else:
            print("❌ Erro no upload")
            
    except requests.exceptions.Timeout:
        print("⏰ Upload travou (timeout)")
    except Exception as e:
        print(f"❌ Erro durante upload: {e}")
        
else:
    print("❌ Erro no login")
    print(response.text)