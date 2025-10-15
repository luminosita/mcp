-- =============================================================================
-- Database Initialization Script for AI Agent MCP Server
-- =============================================================================
-- Purpose: Initialize PostgreSQL database with pgvector extension
-- Executed automatically on first container startup via /docker-entrypoint-initdb.d/
-- =============================================================================

-- Enable pgvector extension for vector embeddings storage
-- Required for RAG (Retrieval-Augmented Generation) capabilities
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify pgvector extension is enabled
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- Log initialization completion
DO $$
BEGIN
    RAISE NOTICE '✅ Database initialization complete';
    RAISE NOTICE '✅ pgvector extension enabled';
    RAISE NOTICE '✅ Ready for Alembic migrations';
END $$;
