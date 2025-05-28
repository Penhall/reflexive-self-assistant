#!/usr/bin/env python3
"""
Teste para encontrar endpoint correto do ChromaDB
"""

import requests

def test_chromadb_endpoints():
    """Testa diferentes endpoints do ChromaDB"""
    
    endpoints = [
        "http://localhost:8000/api/v1/heartbeat",
        "http://localhost:8000/api/v1/version", 
        "http://localhost:8000/api/v1",
        "http://localhost:8000/heartbeat",
        "http://localhost:8000/version",
        "http://localhost:8000/api/v1/collections",
        "http://localhost:8000"
    ]
    
    print("🔍 Testando endpoints do ChromaDB...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            print(f"✅ {endpoint} - Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   📝 Resposta: {data}")
                except:
                    print(f"   📝 Resposta: {response.text[:100]}")
        except Exception as e:
            print(f"❌ {endpoint} - Erro: {str(e)[:50]}")
    
    # Testar se ChromaDB está funcionando via Docker
    print(f"\n🐳 Testando via Docker...")
    import subprocess
    try:
        result = subprocess.run([
            'docker', 'exec', 'rsca-chromadb', 
            'curl', '-s', 'http://localhost:8000/api/v1/heartbeat'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ ChromaDB está respondendo internamente no container")
            print(f"📝 Resposta: {result.stdout}")
        else:
            print("❌ ChromaDB não está respondendo no container")
            print(f"❌ Erro: {result.stderr}")
    except Exception as e:
        print(f"❌ Erro ao testar via Docker: {e}")

if __name__ == "__main__":
    test_chromadb_endpoints()