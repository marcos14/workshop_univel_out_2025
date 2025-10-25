import requests
import json
import time

print("🔧 Testando sistema com PDF mais robusto...")

# Login
login_data = {"email": "marcosagnes@gmail.com", "password": "abc123"}
response = requests.post("http://localhost:8040/auth/login", json=login_data)

if response.status_code == 200:
    token = response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    # Criar um arquivo de texto simples para teste
    test_content = """
Este é um texto de teste mais longo para verificar o processamento de embeddings.

O sistema de biblioteca inteligente utiliza tecnologias avançadas como:
- FastAPI para a API REST
- PostgreSQL para armazenamento de dados estruturados
- Qdrant para armazenamento de embeddings vetoriais
- OpenAI para geração de embeddings
- LangChain para processamento de linguagem natural

O objetivo é permitir que usuários façam perguntas sobre o conteúdo dos livros
e recebam respostas inteligentes baseadas no texto extraído dos PDFs.

Este é um exemplo de como a tecnologia pode revolucionar a forma como 
interagimos com documentos e bibliotecas digitais.
""".strip()
    
    params = {
        "title": "Teste PDF Texto Completo",
        "isbn": "978-0000000002", 
        "publication_year": 2024,
        "publisher": "Publisher Teste",
        "language": "Portuguese",
        "genre": "technology",
        "description": "PDF de teste com texto mais completo para embeddings",
        "author_names": '["Autor Teste"]'
    }
    
    # Simular upload de arquivo de texto como se fosse PDF
    files = {'file': ('test_content.txt', test_content.encode('utf-8'), 'text/plain')}
    
    print("📚 Testando upload...")
    upload_response = requests.post(
        "http://localhost:8040/books/upload",
        headers=headers,
        files=files,
        params=params,
        timeout=30
    )
    
    print(f"Status: {upload_response.status_code}")
    if upload_response.status_code == 200:
        print("✅ Upload bem-sucedido")
        print(upload_response.json())
    else:
        print("❌ Erro no upload")
        print(upload_response.text)
    
    # Aguardar processamento
    print("⏳ Aguardando processamento...")
    time.sleep(5)
    
    # Verificar logs do processamento
    print("🔍 Verificando se API ainda responde...")
    health = requests.get("http://localhost:8040/health", timeout=5)
    print(f"Health status: {health.status_code}")
    
else:
    print("❌ Erro no login")