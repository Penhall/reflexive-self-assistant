from infrastructure.llm_bridge import LLMBridge

bridge = LLMBridge()
response = bridge.send("Crie uma função Python que some dois números")
print(response)
