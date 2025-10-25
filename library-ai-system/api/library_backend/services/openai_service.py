from openai import OpenAI
import os
import logging
from typing import List, Dict, Any
import tiktoken

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = "text-embedding-ada-002"
        self.chat_model = "gpt-4o"
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        
    async def generate_embedding(self, text: str) -> List[float]:
        """Gerar embedding para texto usando OpenAI"""
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            return []
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Gerar embeddings para múltiplos textos"""
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.embedding_model
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings em lote: {e}")
            return []
    
    async def chat_with_context(self, messages: List[Dict[str, str]], context_chunks: List[Dict[str, Any]]) -> str:
        """Gerar resposta do chat usando contexto dos livros"""
        try:
            # Construir contexto a partir dos chunks
            context_text = ""
            books_mentioned = set()
            
            for chunk in context_chunks:
                context_text += f"\n--- Trecho do livro '{chunk['book_title']}' (Página {chunk.get('page_number', 'N/A')}) ---\n"
                context_text += chunk['text']
                context_text += "\n"
                books_mentioned.add(chunk['book_title'])
            
            # Criar mensagem do sistema com contexto
            system_message = f"""Você é uma bibliotecária virtual especializada em ajudar usuários a encontrar informações em livros.

CONTEXTO DOS LIVROS:
{context_text}

INSTRUÇÕES:
1. Use APENAS as informações fornecidas no contexto acima para responder
2. Seja precisa e cite os livros específicos quando relevante
3. Se a informação não estiver no contexto, diga que não encontrou nos livros disponíveis
4. Seja conversacional e útil, como uma bibliotecária experiente
5. Quando citar trechos, mencione o livro e a página se disponível

LIVROS CONSULTADOS: {', '.join(books_mentioned)}"""

            # Preparar mensagens para a API
            api_messages = [{"role": "system", "content": system_message}]
            api_messages.extend(messages)
            
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=api_messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta do chat: {e}")
            return "Desculpe, ocorreu um erro ao processar sua pergunta. Tente novamente."
    
    def count_tokens(self, text: str) -> int:
        """Contar tokens em um texto"""
        return len(self.encoding.encode(text))
    
    def split_text_by_tokens(self, text: str, max_tokens: int = 1000, overlap: int = 100) -> List[str]:
        """Dividir texto em chunks baseado no número de tokens"""
        tokens = self.encoding.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = min(start + max_tokens, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            # Mover o início com overlap
            start = end - overlap
            if start >= len(tokens):
                break
                
        return chunks