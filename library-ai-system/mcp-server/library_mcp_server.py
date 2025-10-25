import pandas as pd
import psycopg2
from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
import os
import logging
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar servidor MCP
mcp = FastMCP("LibraryAnalyst")

# Configurações do banco de dados
DATABASE_URI = os.getenv("DATABASE_URI", "postgresql+psycopg2://postgres:lib_pass_2024@library-pg:5432/library_db")

# --------------------------------------------------------------------------
# MODELOS PYDANTIC PARA PARÂMETROS
# --------------------------------------------------------------------------
class AnalysisRequest(BaseModel):
    """Modelo para solicitações de análise"""
    period_days: int = Field(default=30, description="Período em dias para análise")

class BookSearchRequest(BaseModel):
    """Modelo para busca de livros"""
    query: str = Field(..., description="Termo de busca")
    limit: int = Field(default=10, description="Limite de resultados")

class UserAnalysisRequest(BaseModel):
    """Modelo para análise de usuário"""
    user_id: int = Field(..., description="ID do usuário")

# --------------------------------------------------------------------------
# FUNÇÃO AUXILIAR PARA CONEXÃO COM BANCO
# --------------------------------------------------------------------------
def get_db_connection():
    """Criar conexão com PostgreSQL"""
    try:
        # Extrair parâmetros da URI
        uri_parts = DATABASE_URI.replace("postgresql+psycopg2://", "").split("@")
        user_pass = uri_parts[0].split(":")
        host_db = uri_parts[1].split("/")
        host_port = host_db[0].split(":")
        
        connection = psycopg2.connect(
            host=host_port[0],
            port=host_port[1] if len(host_port) > 1 else 5432,
            database=host_db[1],
            user=user_pass[0],
            password=user_pass[1]
        )
        return connection
    except Exception as e:
        logger.error(f"Erro ao conectar com banco de dados: {e}")
        return None

# --------------------------------------------------------------------------
# FERRAMENTAS MCP
# --------------------------------------------------------------------------

@mcp.tool()
def get_library_stats(request: AnalysisRequest) -> Dict[str, Any]:
    """
    Fornece estatísticas gerais da biblioteca digital. Mostra total de livros, usuários ativos, 
    conversas recentes e livros mais populares.
    """
    try:
        conn = get_db_connection()
        if not conn:
            return {"error": "Erro de conexão com banco de dados"}
        
        cursor = conn.cursor()
        
        # Total de livros
        cursor.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]
        
        # Livros processados
        cursor.execute("SELECT COUNT(*) FROM books WHERE processed = true")
        processed_books = cursor.fetchone()[0]
        
        # Total de usuários
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = true")
        total_users = cursor.fetchone()[0]
        
        # Conversas nos últimos dias
        cursor.execute("""
            SELECT COUNT(*) FROM conversations 
            WHERE created_at >= %s
        """, (datetime.now() - timedelta(days=request.period_days),))
        recent_conversations = cursor.fetchone()[0]
        
        # Mensagens nos últimos dias
        cursor.execute("""
            SELECT COUNT(*) FROM messages 
            WHERE created_at >= %s AND role = 'user'
        """, (datetime.now() - timedelta(days=request.period_days),))
        recent_messages = cursor.fetchone()[0]
        
        # Top 5 livros mais referenciados
        cursor.execute("""
            SELECT b.title, COUNT(i.id) as references
            FROM books b
            LEFT JOIN user_book_interactions i ON b.id = i.book_id
            WHERE i.interaction_type = 'chat_reference'
            AND i.created_at >= %s
            GROUP BY b.id, b.title
            ORDER BY references DESC
            LIMIT 5
        """, (datetime.now() - timedelta(days=request.period_days),))
        top_books = cursor.fetchall()
        
        conn.close()
        
        return {
            "biblioteca_stats": {
                "total_livros": total_books,
                "livros_processados": processed_books,
                "usuarios_ativos": total_users,
                "conversas_recentes": recent_conversations,
                "mensagens_periodo": recent_messages,
                "periodo_analise_dias": request.period_days
            },
            "livros_mais_populares": [
                {"titulo": title, "referencias": count} 
                for title, count in top_books
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return {"error": f"Erro ao processar estatísticas: {str(e)}"}

@mcp.tool()
def search_books_by_content(request: BookSearchRequest) -> Dict[str, Any]:
    """
    Busca livros por conteúdo, título ou autor. Útil para encontrar livros específicos
    ou descobrir quais livros tratam de determinado assunto.
    """
    try:
        conn = get_db_connection()
        if not conn:
            return {"error": "Erro de conexão com banco de dados"}
        
        cursor = conn.cursor()
        
        # Buscar por título, descrição e autores
        cursor.execute("""
            SELECT DISTINCT b.id, b.title, b.genre, b.description, b.pages, b.processed,
                   array_agg(a.name) as authors
            FROM books b
            LEFT JOIN book_authors ba ON b.id = ba.book_id
            LEFT JOIN authors a ON ba.author_id = a.id
            WHERE b.title ILIKE %s 
               OR b.description ILIKE %s
               OR a.name ILIKE %s
               OR b.genre ILIKE %s
            GROUP BY b.id, b.title, b.genre, b.description, b.pages, b.processed
            ORDER BY b.title
            LIMIT %s
        """, (f"%{request.query}%", f"%{request.query}%", f"%{request.query}%", 
              f"%{request.query}%", request.limit))
        
        books = cursor.fetchall()
        
        # Buscar também em chunks de texto para livros processados
        cursor.execute("""
            SELECT DISTINCT b.id, b.title, COUNT(bc.id) as chunk_matches
            FROM books b
            JOIN book_chunks bc ON b.id = bc.book_id
            WHERE bc.chunk_text ILIKE %s
            GROUP BY b.id, b.title
            ORDER BY chunk_matches DESC
            LIMIT %s
        """, (f"%{request.query}%", request.limit))
        
        content_matches = cursor.fetchall()
        
        conn.close()
        
        result_books = []
        for book in books:
            result_books.append({
                "id": book[0],
                "titulo": book[1],
                "genero": book[2],
                "descricao": book[3],
                "paginas": book[4],
                "processado": book[5],
                "autores": [author for author in book[6] if author]
            })
        
        content_results = []
        for match in content_matches:
            content_results.append({
                "id": match[0],
                "titulo": match[1],
                "trechos_encontrados": match[2]
            })
        
        return {
            "busca_realizada": request.query,
            "livros_encontrados_metadata": result_books,
            "livros_por_conteudo": content_results,
            "total_resultados": len(result_books) + len(content_results)
        }
        
    except Exception as e:
        logger.error(f"Erro na busca de livros: {e}")
        return {"error": f"Erro na busca: {str(e)}"}

@mcp.tool()
def analyze_user_behavior(request: UserAnalysisRequest) -> Dict[str, Any]:
    """
    Analisa o comportamento de um usuário específico, incluindo livros favoritos,
    padrões de leitura e temas de interesse.
    """
    try:
        conn = get_db_connection()
        if not conn:
            return {"error": "Erro de conexão com banco de dados"}
        
        cursor = conn.cursor()
        
        # Verificar se usuário existe
        cursor.execute("SELECT name, email FROM users WHERE id = %s", (request.user_id,))
        user_info = cursor.fetchone()
        
        if not user_info:
            return {"error": "Usuário não encontrado"}
        
        # Conversas do usuário
        cursor.execute("""
            SELECT COUNT(*) as total_conversas,
                   COUNT(CASE WHEN created_at >= %s THEN 1 END) as conversas_recentes
            FROM conversations WHERE user_id = %s
        """, (datetime.now() - timedelta(days=30), request.user_id))
        conv_stats = cursor.fetchone()
        
        # Mensagens do usuário
        cursor.execute("""
            SELECT COUNT(*) FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            WHERE c.user_id = %s AND m.role = 'user'
        """, (request.user_id,))
        total_messages = cursor.fetchone()[0]
        
        # Livros mais consultados pelo usuário
        cursor.execute("""
            SELECT b.title, COUNT(i.id) as interactions
            FROM books b
            JOIN user_book_interactions i ON b.id = i.book_id
            WHERE i.user_id = %s
            GROUP BY b.id, b.title
            ORDER BY interactions DESC
            LIMIT 10
        """, (request.user_id,))
        favorite_books = cursor.fetchall()
        
        # Gêneros de interesse
        cursor.execute("""
            SELECT b.genre, COUNT(i.id) as interest_count
            FROM books b
            JOIN user_book_interactions i ON b.id = i.book_id
            WHERE i.user_id = %s AND b.genre IS NOT NULL
            GROUP BY b.genre
            ORDER BY interest_count DESC
        """, (request.user_id,))
        genre_interests = cursor.fetchall()
        
        # Atividade por tipo de interação
        cursor.execute("""
            SELECT interaction_type, COUNT(*) as count
            FROM user_book_interactions
            WHERE user_id = %s
            GROUP BY interaction_type
        """, (request.user_id,))
        interaction_types = cursor.fetchall()
        
        conn.close()
        
        return {
            "usuario": {
                "id": request.user_id,
                "nome": user_info[0],
                "email": user_info[1]
            },
            "atividade": {
                "total_conversas": conv_stats[0],
                "conversas_ultimo_mes": conv_stats[1],
                "total_mensagens": total_messages
            },
            "livros_favoritos": [
                {"titulo": title, "interacoes": count}
                for title, count in favorite_books
            ],
            "generos_interesse": [
                {"genero": genre, "nivel_interesse": count}
                for genre, count in genre_interests
            ],
            "tipos_interacao": [
                {"tipo": int_type, "quantidade": count}
                for int_type, count in interaction_types
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro na análise de usuário: {e}")
        return {"error": f"Erro na análise: {str(e)}"}

@mcp.tool()
def get_popular_topics(request: AnalysisRequest) -> Dict[str, Any]:
    """
    Identifica os tópicos mais populares baseado nas perguntas dos usuários e
    livros mais consultados no período especificado.
    """
    try:
        conn = get_db_connection()
        if not conn:
            return {"error": "Erro de conexão com banco de dados"}
        
        cursor = conn.cursor()
        
        # Gêneros mais populares
        cursor.execute("""
            SELECT b.genre, COUNT(i.id) as popularity
            FROM books b
            JOIN user_book_interactions i ON b.id = i.book_id
            WHERE i.created_at >= %s AND b.genre IS NOT NULL
            GROUP BY b.genre
            ORDER BY popularity DESC
            LIMIT 10
        """, (datetime.now() - timedelta(days=request.period_days),))
        popular_genres = cursor.fetchall()
        
        # Livros mais ativos (com mais interações)
        cursor.execute("""
            SELECT b.title, b.genre, COUNT(i.id) as activity_score
            FROM books b
            JOIN user_book_interactions i ON b.id = i.book_id
            WHERE i.created_at >= %s
            GROUP BY b.id, b.title, b.genre
            ORDER BY activity_score DESC
            LIMIT 15
        """, (datetime.now() - timedelta(days=request.period_days),))
        active_books = cursor.fetchall()
        
        # Análise de palavras-chave nas mensagens (simplificada)
        cursor.execute("""
            SELECT COUNT(*) as total_user_messages
            FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            WHERE m.role = 'user' AND m.created_at >= %s
        """, (datetime.now() - timedelta(days=request.period_days),))
        total_user_messages = cursor.fetchone()[0]
        
        # Usuários mais ativos
        cursor.execute("""
            SELECT u.name, COUNT(i.id) as activity_level
            FROM users u
            JOIN user_book_interactions i ON u.id = i.user_id
            WHERE i.created_at >= %s
            GROUP BY u.id, u.name
            ORDER BY activity_level DESC
            LIMIT 10
        """, (datetime.now() - timedelta(days=request.period_days),))
        active_users = cursor.fetchall()
        
        conn.close()
        
        return {
            "periodo_analise": f"{request.period_days} dias",
            "generos_populares": [
                {"genero": genre, "score_popularidade": count}
                for genre, count in popular_genres
            ],
            "livros_mais_ativos": [
                {"titulo": title, "genero": genre, "score_atividade": score}
                for title, genre, score in active_books
            ],
            "engajamento": {
                "total_mensagens_usuarios": total_user_messages,
                "media_mensagens_por_dia": round(total_user_messages / request.period_days, 2)
            },
            "usuarios_mais_ativos": [
                {"nome": name, "nivel_atividade": level}
                for name, level in active_users
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro na análise de tópicos populares: {e}")
        return {"error": f"Erro na análise: {str(e)}"}

@mcp.tool()
def get_recommendation_insights(request: UserAnalysisRequest) -> Dict[str, Any]:
    """
    Gera insights para recomendações de livros baseado no histórico e preferências
    do usuário, utilizando padrões de interação e similaridades.
    """
    try:
        conn = get_db_connection()
        if not conn:
            return {"error": "Erro de conexão com banco de dados"}
        
        cursor = conn.cursor()
        
        # Verificar se usuário existe
        cursor.execute("SELECT name FROM users WHERE id = %s", (request.user_id,))
        user_info = cursor.fetchone()
        
        if not user_info:
            return {"error": "Usuário não encontrado"}
        
        # Gêneros preferidos do usuário
        cursor.execute("""
            SELECT b.genre, COUNT(i.id) as preference_score
            FROM books b
            JOIN user_book_interactions i ON b.id = i.book_id
            WHERE i.user_id = %s AND b.genre IS NOT NULL
            GROUP BY b.genre
            ORDER BY preference_score DESC
            LIMIT 5
        """, (request.user_id,))
        preferred_genres = cursor.fetchall()
        
        # Livros similares aos que o usuário já interagiu (mesmo gênero)
        if preferred_genres:
            top_genre = preferred_genres[0][0]
            cursor.execute("""
                SELECT b.id, b.title, b.description
                FROM books b
                WHERE b.genre = %s 
                AND b.processed = true
                AND b.id NOT IN (
                    SELECT DISTINCT book_id 
                    FROM user_book_interactions 
                    WHERE user_id = %s
                )
                ORDER BY b.created_at DESC
                LIMIT 10
            """, (top_genre, request.user_id))
            similar_books = cursor.fetchall()
        else:
            similar_books = []
        
        # Livros populares que o usuário ainda não interagiu
        cursor.execute("""
            SELECT b.id, b.title, b.genre, COUNT(i.id) as popularity
            FROM books b
            JOIN user_book_interactions i ON b.id = i.book_id
            WHERE b.id NOT IN (
                SELECT DISTINCT book_id 
                FROM user_book_interactions 
                WHERE user_id = %s
            )
            AND b.processed = true
            GROUP BY b.id, b.title, b.genre
            ORDER BY popularity DESC
            LIMIT 8
        """, (request.user_id,))
        popular_unread = cursor.fetchall()
        
        # Autores que o usuário ainda não explorou mas que são populares
        cursor.execute("""
            SELECT a.name, COUNT(i.id) as author_popularity
            FROM authors a
            JOIN book_authors ba ON a.id = ba.author_id
            JOIN books b ON ba.book_id = b.id
            JOIN user_book_interactions i ON b.id = i.book_id
            WHERE a.id NOT IN (
                SELECT DISTINCT ba2.author_id
                FROM book_authors ba2
                JOIN user_book_interactions i2 ON ba2.book_id = i2.book_id
                WHERE i2.user_id = %s
            )
            GROUP BY a.id, a.name
            ORDER BY author_popularity DESC
            LIMIT 5
        """, (request.user_id,))
        unexplored_authors = cursor.fetchall()
        
        conn.close()
        
        return {
            "usuario": user_info[0],
            "preferencias_identificadas": {
                "generos_favoritos": [
                    {"genero": genre, "score": score}
                    for genre, score in preferred_genres
                ]
            },
            "recomendacoes": {
                "livros_genero_similar": [
                    {"id": book_id, "titulo": title, "descricao": desc}
                    for book_id, title, desc in similar_books
                ],
                "livros_populares_nao_lidos": [
                    {"id": book_id, "titulo": title, "genero": genre, "popularidade": pop}
                    for book_id, title, genre, pop in popular_unread
                ],
                "autores_para_explorar": [
                    {"nome": name, "nivel_popularidade": pop}
                    for name, pop in unexplored_authors
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Erro nos insights de recomendação: {e}")
        return {"error": f"Erro na análise: {str(e)}"}

# --------------------------------------------------------------------------
# INICIALIZAR SERVIDOR
# --------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando Library MCP Server...")
    logger.info("📊 Ferramentas disponíveis:")
    logger.info("  - get_library_stats: Estatísticas gerais da biblioteca")
    logger.info("  - search_books_by_content: Busca livros por conteúdo")
    logger.info("  - analyze_user_behavior: Análise comportamental de usuários")
    logger.info("  - get_popular_topics: Tópicos e tendências populares")
    logger.info("  - get_recommendation_insights: Insights para recomendações")
    
    # Executar servidor
    uvicorn.run("__main__:mcp", host="0.0.0.0", port=8001)