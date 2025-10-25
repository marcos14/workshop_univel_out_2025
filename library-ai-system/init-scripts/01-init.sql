-- Banco de dados para sistema de biblioteca inteligente
-- Combina PostgreSQL + pgvector para dados estruturados e embeddings

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabela de usuários
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de autores
CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    biography TEXT,
    birth_date DATE,
    death_date DATE,
    nationality VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de livros
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    publication_year INTEGER,
    publisher VARCHAR(255),
    language VARCHAR(50) DEFAULT 'Portuguese',
    pages INTEGER,
    genre VARCHAR(100),
    description TEXT,
    file_path VARCHAR(500),
    file_size BIGINT,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de relação muitos-para-muitos entre livros e autores
CREATE TABLE book_authors (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES authors(id) ON DELETE CASCADE,
    UNIQUE(book_id, author_id)
);

-- Tabela de chunks de texto dos livros para embeddings
CREATE TABLE book_chunks (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER,
    qdrant_point_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de conversas entre usuários e a bibliotecária virtual
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de mensagens individuais nas conversas
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    books_referenced INTEGER[], -- Array de IDs de livros referenciados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de interações dos usuários com livros (views, downloads, etc.)
CREATE TABLE user_book_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL, -- 'view', 'download', 'search', 'chat_reference'
    metadata JSONB, -- Dados adicionais sobre a interação
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de recomendações geradas pela IA
CREATE TABLE book_recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    reason TEXT, -- Motivo da recomendação
    confidence_score FLOAT, -- Score de confiança da recomendação (0-1)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    clicked BOOLEAN DEFAULT FALSE,
    clicked_at TIMESTAMP
);

-- Índices para otimização
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_genre ON books(genre);
CREATE INDEX idx_books_processed ON books(processed);
CREATE INDEX idx_book_chunks_book_id ON book_chunks(book_id);
CREATE INDEX idx_book_chunks_qdrant_id ON book_chunks(qdrant_point_id);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_user_interactions_user_id ON user_book_interactions(user_id);
CREATE INDEX idx_user_interactions_book_id ON user_book_interactions(book_id);
CREATE INDEX idx_user_interactions_type ON user_book_interactions(interaction_type);
CREATE INDEX idx_recommendations_user_id ON book_recommendations(user_id);
CREATE INDEX idx_recommendations_book_id ON book_recommendations(book_id);

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para atualizar updated_at
CREATE TRIGGER update_books_updated_at BEFORE UPDATE ON books
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Inserir usuário padrão para testes
INSERT INTO users (name, email, password_hash) VALUES 
('Library Admin', 'admin@library.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY8Y8lZB8YCBaXG');

-- Inserir alguns autores de exemplo
INSERT INTO authors (name, biography, nationality) VALUES 
('Machado de Assis', 'Joaquim Maria Machado de Assis foi um escritor brasileiro, considerado um dos maiores nomes da literatura brasileira.', 'Brasileira'),
('Clarice Lispector', 'Clarice Lispector foi uma escritora e jornalista brasileira nascida na Ucrânia.', 'Brasileira'),
('Jorge Luis Borges', 'Jorge Francisco Isidoro Luis Borges Acevedo foi um escritor, poeta, tradutor, crítico literário e ensaísta argentino.', 'Argentina'),
('Gabriel García Márquez', 'Gabriel José de la Concordia García Márquez foi um escritor, jornalista, editor, ativista e político colombiano.', 'Colombiana');

-- Comentários explicativos
COMMENT ON TABLE books IS 'Armazena metadados dos livros em PDF processados pelo sistema';
COMMENT ON TABLE book_chunks IS 'Fragmentos de texto dos livros para busca semântica, com referência ao Qdrant';
COMMENT ON TABLE conversations IS 'Conversas entre usuários e a bibliotecária virtual com IA';
COMMENT ON TABLE messages IS 'Mensagens individuais nas conversas, incluindo referências a livros';
COMMENT ON TABLE user_book_interactions IS 'Rastreia interações dos usuários com livros para analytics e recomendações';
COMMENT ON TABLE book_recommendations IS 'Recomendações de livros geradas pela IA baseadas no comportamento do usuário';