// infrastructure/neo4j/init/01_schema.cypher
// Schema para RSCA GraphRAG - Design híbrido com sistema YAML atual

// =====================================
// CONSTRAINTS E ÍNDICES
// =====================================

// Experiências de Codificação
CREATE CONSTRAINT experience_id FOR (e:Experience) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT task_id FOR (t:Task) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT code_hash FOR (c:Code) REQUIRE c.hash IS UNIQUE;
CREATE CONSTRAINT pattern_name FOR (p:Pattern) REQUIRE p.name IS UNIQUE;
CREATE CONSTRAINT agent_name FOR (a:Agent) REQUIRE a.name IS UNIQUE;

// Índices de Performance
CREATE INDEX experience_quality FOR (e:Experience) ON (e.quality_score);
CREATE INDEX experience_timestamp FOR (e:Experience) ON (e.timestamp);
CREATE INDEX task_domain FOR (t:Task) ON (t.domain);
CREATE INDEX code_language FOR (c:Code) ON (c.language);
CREATE INDEX pattern_success_rate FOR (p:Pattern) ON (p.success_rate);

// =====================================
// SCHEMA DE NÓS
// =====================================

// Experiência de Codificação (centro do grafo)
CALL db.schema.nodeTypeProperties();

// Criar exemplos de nós para estabelecer schema
CREATE (exp:Experience {
    id: "exp_example_001",
    task_description: "Implementar função de login",
    quality_score: 8.5,
    execution_success: true,
    timestamp: datetime(),
    agent_name: "CodeAgent",
    llm_model: "qwen2:1.5b",
    context_tokens: 1024,
    response_tokens: 256,
    generation_time: 2.3,
    // Conexão com sistema YAML atual
    yaml_cycle: 1,
    yaml_identity_backup: "reflection/state/identity/identity_state.yaml"
});

CREATE (task:Task {
    id: "task_example_001", 
    description: "Implementar função de login",
    domain: "authentication",
    complexity: "medium",
    requirements: ["validation", "security", "error_handling"],
    context_size: 512
});

CREATE (code:Code {
    id: "code_example_001",
    hash: "sha256_abc123...",
    content: "def login(username, password):\n    # código aqui\n    return True",
    language: "python",
    lines_count: 15,
    functions_count: 1,
    classes_count: 0,
    complexity_score: 3,
    syntax_valid: true
});

CREATE (pattern:Pattern {
    id: "pattern_example_001",
    name: "input_validation_pattern",
    template: "if not input or len(input.strip()) == 0: raise ValueError(...)",
    success_rate: 0.89,
    usage_count: 47,
    discovery_date: datetime(),
    contexts: ["login", "user_input", "api_endpoints"]
});

CREATE (agent:Agent {
    id: "agent_codeagent_v1",
    name: "CodeAgent",
    version: "1.0",
    specialization: "code_generation",
    current_llm: "qwen2:1.5b",
    total_experiences: 0,
    avg_quality_score: 0.0,
    consistency_level: "Alta",
    // Ponte com sistema simbólico atual
    yaml_identity_path: "reflection/state/identity/identity_state.yaml",
    symbolic_traits: ["Consistente", "Objetivo"]
});

// =====================================
// RELAÇÕES
// =====================================

// Conexões principais
CREATE (exp)-[:EXECUTED_TASK]->(task);
CREATE (exp)-[:GENERATED_CODE]->(code);
CREATE (exp)-[:USED_PATTERN]->(pattern);
CREATE (exp)-[:PERFORMED_BY]->(agent);

// Relações de similaridade e evolução
CREATE (exp)-[:SIMILAR_TO {similarity_score: 0.85}]->(exp);
CREATE (code)-[:EVOLVED_FROM {improvements: ["added_validation", "better_error_handling"]}]->(code);
CREATE (pattern)-[:DERIVED_FROM]->(pattern);
CREATE (agent)-[:LEARNED_FROM]->(exp);

// Remover exemplos
MATCH (n) WHERE n.id CONTAINS "example_001" DELETE n;

// =====================================
// FUNÇÕES UTILITÁRIAS
// =====================================

// Função para calcular similaridade de tarefas
CALL gds.graph.project(
    'task_similarity',
    'Task',
    'SIMILAR_TO'
);

// Função para encontrar padrões emergentes
CREATE OR REPLACE FUNCTION rsca.find_emerging_patterns() 
RETURNS LIST<MAP<STRING, ANY>> AS
$$
    MATCH (e:Experience)-[:USED_PATTERN]->(p:Pattern)
    WHERE e.timestamp > datetime() - duration("P30D")
    WITH p, COUNT(e) as recent_usage
    WHERE recent_usage > 5
    RETURN collect({
        pattern: p.name,
        recent_usage: recent_usage,
        success_rate: p.success_rate
    })
$$;