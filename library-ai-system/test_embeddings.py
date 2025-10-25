import requests
import json
import time

print("🔧 Testando sistema completo com embeddings e Qdrant...")

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
    
    # Criar um PDF com mais conteúdo para testar embeddings
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
/Length 200
>>
stream
BT
/F1 12 Tf
72 720 Td
(Este e um teste de PDF com mais conteudo para gerar embeddings.) Tj
0 -20 Td
(O processamento de embeddings agora esta ativo novamente.) Tj
0 -20 Td
(Vamos verificar se o sistema funciona sem travamento.) Tj
0 -20 Td
(Esta e uma demonstracao da funcionalidade completa.) Tj
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
450
%%EOF"""

    # Testar upload
    headers = {"Authorization": f"Bearer {token}"}
    
    # Dados do livro
    book_data = {
        "title": "Teste Embeddings Completo",
        "isbn": "978-0000000001",
        "publication_year": 2024,
        "publisher": "Teste Publisher AI",
        "language": "Portuguese",
        "genre": "test",
        "description": "Livro de teste para verificar processamento completo com embeddings e Qdrant",
        "author_names": ["Autor IA", "Coautor Sistema"]
    }
    
    files = {
        'file': ('test_embeddings.pdf', test_pdf_content, 'application/pdf')
    }
    
    print("📚 Fazendo upload do livro com processamento completo...")
    start_time = time.time()
    
    try:
        # Preparar query parameters
        params = {
            "title": "Teste Embeddings Completo",
            "isbn": "978-0000000001",
            "publication_year": 2024,
            "publisher": "Teste Publisher AI",
            "language": "Portuguese",
            "genre": "test",
            "description": "Livro de teste para verificar processamento completo com embeddings e Qdrant",
            "author_names": '["Autor IA", "Coautor Sistema"]'
        }
        
        files = {
            'file': ('test_embeddings.pdf', test_pdf_content, 'application/pdf')
        }
        
        upload_response = requests.post(
            "http://localhost:8040/books/upload",
            headers=headers,
            files=files,
            params=params,
            timeout=60  # Timeout maior para processamento
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️ Upload completado em {duration:.2f} segundos")
        print(f"Status Code: {upload_response.status_code}")
        
        if upload_response.status_code == 200:
            response_data = upload_response.json()
            print("✅ Upload realizado com sucesso!")
            print(f"📖 Book ID: {response_data.get('book_id')}")
            print(f"📝 Status: {response_data.get('processing_status')}")
            print(f"💬 Mensagem: {response_data.get('message')}")
            
            # Aguardar um pouco para processamento em background
            print("⏳ Aguardando processamento em background...")
            time.sleep(3)
            
            # Testar se a API ainda está responsiva
            print("🔍 Testando responsividade da API...")
            health_response = requests.get("http://localhost:8040/health", timeout=10)
            if health_response.status_code == 200:
                print("✅ API ainda está responsiva!")
            else:
                print("❌ API não está mais responsiva")
            
            # Testar listagem de livros
            print("📚 Testando listagem de livros...")
            books_response = requests.get("http://localhost:8040/books/", headers=headers, timeout=10)
            if books_response.status_code == 200:
                books_data = books_response.json()
                print(f"✅ Listagem funcionando! Total: {books_data.get('total', 0)} livros")
            else:
                print("❌ Erro na listagem de livros")
                
        else:
            print("❌ Erro no upload")
            print(f"Response: {upload_response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Upload travou (timeout)")
    except Exception as e:
        print(f"❌ Erro durante upload: {e}")
        
else:
    print("❌ Erro no login")
    print(response.text)

print("\n🏁 Teste concluído!")