# Project Architecture: Reflexive Self Assistant

The system is built as a modular multi-agent architecture with recursive symbolic reflection. Core components include:

- `CodeAgent`, `TestAgent`, `DocumentationAgent`: Perform task-oriented generation
- `ReflectionAgent`: Performs feedback-based symbolic reflection
- `SymbolicEvaluator`: Extracts and updates identity patterns
- `SymbolicMemory`: Tracks long-term symbolic consistency and evolution
- `SupervisorAgent`: Oversees collective agent behavior and issues meta-diagnoses
- `StrategyPlanner` and `Simulator`: Predictively plan task variation
- `SymbolicSelfNarrator`: Generates self-reflective narratives
- `SupervisorSelfEvaluator`: Allows meta-reflection on supervision logic

Information is stored and cycled through YAML-based memory and decision logs. Neo4j (optional) supports symbolic graph persistence.