#!/usr/bin/env python3
"""
Teste e correção do ChromaDB
"""

import requests
import subprocess
import json

def test_chromadb_endpoints():
    """Testa diferentes endpoints do ChromaDB"""
    
    print("🔍 Testando endpoints do ChromaDB...")
    
    endpoints = [
        ("GET", "http://localhost:8000", "Root endpoint"),
        ("GET", "http://localhost:8000/api/v1/heartbeat", "Heartbeat"),
        ("GET", "http://localhost:8000/api/v1/version", "Version"),
        ("GET", "http://localhost:8000/api/v1/collections", "Collections"),
        ("POST", "http://localhost:8000/api/v1/collections", "Create collection")
    ]
    
    working_endpoints = []
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(endpoint, timeout=5)
            else:
                # POST para testar criação de collection
                data = {"name": "test_collection"}
                response = requests.post(endpoint, json=data, timeout=5)
            
            status = "✅" if response.status_code in [200, 201] else "⚠️"
            print(f"{status} {description}: {response.status_code}")
            
            if response.status_code in [200, 201]:
                working_endpoints.append(endpoint)
                try:
                    data = response.json()
                    print(f"   📝 Resposta: {json.dumps(data, indent=2)[:100]}...")
                except:
                    print(f"   📝 Resposta texto: {response.text[:100]}...")
            elif response.status_code == 410:
                print(f"   💡 Status 410 pode ser normal para este endpoint")
                    
        except Exception as e:
            print(f"❌ {description}: {str(e)[:50]}")
    
    return working_endpoints

def test_chromadb_via_docker():
    """Testa ChromaDB diretamente no container"""
    
    print("\n🐳 Testando ChromaDB via Docker...")
    
    try:
        # Testar se container está rodando
        result = subprocess.run([
            'docker', 'exec', 'rsca-chromadb', 'echo', 'Container funcionando'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Container ChromaDB está acessível")
        else:
            print("❌ Problema de acesso ao container")
            return False
        
        # Testar curl interno
        result = subprocess.run([
            'docker', 'exec', 'rsca-chromadb', 
            'curl', '-s', 'http://localhost:8000/api/v1/heartbeat'
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ ChromaDB respondendo internamente")
            print(f"📝 Resposta: {result.stdout}")
            return True
        else:
            print("❌ ChromaDB não está respondendo internamente")
            print(f"❌ Stderr: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar via Docker: {e}")
        return False

def fix_chromadb_config():
    """Sugere correções para ChromaDB"""
    
    print("\n🔧 Sugestões de correção para ChromaDB...")
    
    print("""
💡 ChromaDB Status 410 - Possíveis soluções:

1. **Restart do container**:
   docker restart rsca-chromadb

2. **Verificar logs**:
   docker logs rsca-chromadb

3. **Atualizar docker-compose.yml** com configuração mais específica:
   ```yaml
   chromadb:
     image: chromadb/chroma:latest
     environment:
       - CHROMA_SERVER_HOST=0.0.0.0
       - CHROMA_SERVER_PORT=8000
       - CHROMA_SERVER_CORS_ALLOW_ORIGINS=["*"]
   ```

4. **Para desenvolvimento, ChromaDB é opcional**:
   - Sistema funciona sem ChromaDB por enquanto
   - Será usado apenas para GraphRAG (próxima fase)
   - Neo4j é mais importante para sistema simbólico atual

5. **Teste alternativo**:
   docker exec rsca-chromadb chroma --help
""")

def main():
    print("🔍 DIAGNÓSTICO CHROMADB")
    print("="*40)
    
    # Testar endpoints externos
    working_endpoints = test_chromadb_endpoints()
    
    # Testar via Docker
    docker_ok = test_chromadb_via_docker()
    
    # Resumo
    print(f"\n📊 RESUMO:")
    print(f"   Endpoints funcionando: {len(working_endpoints)}")
    print(f"   Acesso via Docker: {'✅' if docker_ok else '❌'}")
    
    if not working_endpoints and not docker_ok:
        print(f"\n⚠️ ChromaDB não está totalmente funcional")
        print(f"   Mas isso não impede o sistema de funcionar!")
        print(f"   ChromaDB será usado apenas para GraphRAG mais tarde")
        fix_chromadb_config()
    else:
        print(f"\n✅ ChromaDB está parcialmente funcional")
    
    return len(working_endpoints) > 0 or docker_ok

if __name__ == "__main__":
    main()