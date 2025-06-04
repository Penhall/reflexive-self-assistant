#!/usr/bin/env python3
"""
Script para configurar Neo4j automaticamente
Resolve o problema de autenticação
"""

import subprocess
import time
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def check_docker():
    """Verifica se Docker está instalado e rodando"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Docker instalado")
            return True
        else:
            print("❌ Docker não funcionando")
            return False
    except Exception as e:
        print(f"❌ Docker não encontrado: {e}")
        return False

def stop_existing_neo4j():
    """Para e remove containers Neo4j existentes"""
    containers = ['neo4j', 'rsca-neo4j']
    
    for container in containers:
        try:
            # Parar container
            subprocess.run(['docker', 'stop', container], 
                          capture_output=True, timeout=10)
            print(f"🛑 Container {container} parado")
            
            # Remover container
            subprocess.run(['docker', 'rm', container], 
                          capture_output=True, timeout=10)
            print(f"🗑️ Container {container} removido")
            
        except:
            pass  # Container pode não existir

def start_neo4j():
    """Inicia Neo4j com configurações corretas"""
    print("🚀 Iniciando Neo4j...")
    
    cmd = [
        'docker', 'run', '-d',
        '--name', 'rsca-neo4j',
        '-p', '7474:7474',
        '-p', '7687:7687',
        '-e', 'NEO4J_AUTH=neo4j/reflexive123',
        '-e', 'NEO4J_PLUGINS=["apoc"]',
        '--restart', 'unless-stopped',
        'neo4j:latest'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Neo4j iniciado com sucesso")
            print(f"🆔 Container ID: {result.stdout.strip()[:12]}")
            return True
        else:
            print(f"❌ Erro ao iniciar Neo4j: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar Docker: {e}")
        return False

def wait_for_neo4j():
    """Aguarda Neo4j ficar disponível"""
    print("⏳ Aguardando Neo4j ficar disponível...")
    
    max_attempts = 12  # 60 segundos
    for attempt in range(max_attempts):
        try:
            # Verificar se container está rodando
            result = subprocess.run(['docker', 'logs', 'rsca-neo4j'], 
                                  capture_output=True, text=True, timeout=5)
            
            if 'Started.' in result.stdout:
                print("✅ Neo4j iniciado completamente")
                return True
            elif 'ERROR' in result.stdout:
                print("❌ Erro detectado nos logs do Neo4j")
                print(result.stdout[-500:])  # Últimas 500 chars
                return False
            
            print(f"⏳ Tentativa {attempt + 1}/{max_attempts}...")
            time.sleep(5)
            
        except Exception as e:
            print(f"⚠️ Erro ao verificar status: {e}")
            time.sleep(5)
    
    print("❌ Timeout aguardando Neo4j")
    return False

def test_connection():
    """Testa conexão com Neo4j"""
    print("🧪 Testando conexão...")
    
    try:
        sys.path.append(str(PROJECT_ROOT))
        from memory.graph_rag.graph_interface import GraphMemory
        
        graph = GraphMemory()
        categories = graph.get_categories_and_counts()
        graph.close()
        
        print("✅ Conexão com Neo4j funcionando!")
        print(f"📊 Categorias encontradas: {len(categories)}")
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def create_env_file():
    """Cria arquivo .env com configurações Neo4j"""
    env_file = PROJECT_ROOT / ".env"
    
    env_content = """# Configurações do Neo4j para RSCA
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=reflexive123

# Configurações Ollama (se necessário)
OLLAMA_HOST=http://localhost:11434

# Configurações ChromaDB (se necessário)
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
"""
    
    if env_file.exists():
        print("ℹ️ Arquivo .env já existe - não sobrescrevendo")
    else:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"✅ Arquivo .env criado: {env_file}")

def show_neo4j_info():
    """Mostra informações sobre o Neo4j"""
    print("\n📋 INFORMAÇÕES DO NEO4J:")
    print("• URL Web: http://localhost:7474")
    print("• Usuário: neo4j")
    print("• Senha: reflexive123")
    print("• URI Bolt: bolt://localhost:7687")
    
    print("\n🔧 COMANDOS ÚTEIS:")
    print("• Ver logs: docker logs rsca-neo4j")
    print("• Parar: docker stop rsca-neo4j")
    print("• Iniciar: docker start rsca-neo4j")
    print("• Remover: docker rm rsca-neo4j")

def main():
    """Função principal"""
    print("🐳 Configurando Neo4j para RSCA")
    print("=" * 40)
    
    # 1. Verificar Docker
    if not check_docker():
        print("❌ Instale Docker primeiro: https://docker.com/get-started")
        return False
    
    # 2. Parar Neo4j existente
    stop_existing_neo4j()
    
    # 3. Iniciar novo Neo4j
    if not start_neo4j():
        return False
    
    # 4. Aguardar inicialização
    if not wait_for_neo4j():
        print("⚠️ Neo4j pode não estar totalmente pronto")
        print("💡 Aguarde mais alguns minutos e teste novamente")
    
    # 5. Testar conexão
    connection_ok = test_connection()
    
    # 6. Criar arquivo .env
    create_env_file()
    
    # 7. Mostrar informações
    show_neo4j_info()
    
    print("\n" + "=" * 40)
    
    if connection_ok:
        print("✅ NEO4J CONFIGURADO COM SUCESSO!")
        print("\n🎯 Próximos passos:")
        print("1. Execute: python core/main.py")
        print("2. Verifique GraphRAG funcionando")
        print("3. Acesse interface web: http://localhost:7474")
    else:
        print("⚠️ NEO4J INICIADO MAS CONEXÃO FALHOU")
        print("\n🔧 Troubleshooting:")
        print("1. Aguarde 2-3 minutos para inicialização completa")
        print("2. Verifique logs: docker logs rsca-neo4j")
        print("3. Teste conexão: python scripts/test_neo4j.py")
    
    return connection_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)