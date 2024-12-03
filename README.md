# Raft Consensus Algorithm Simulation

## Descrição do Projeto
Este projeto implementa uma simulação do algoritmo de consenso Raft em um ambiente distribuído. Ele inclui um nó coordenador e nós participantes que se comunicam entre si para alcançar o consenso.

## Algoritmo Implementado
O algoritmo Raft é utilizado para garantir que múltiplos nós em um sistema distribuído concordem sobre um único estado, mesmo na presença de falhas de nó e comunicação.

## Configuração do Ambiente
1. Clone o repositório:
   ```bash
   git clone https://github.com/herva2003/Algoritmos-de-Consenso.git
   ```

2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Execução do Código
### Iniciar o Coordenador
Para iniciar a simulação, primeiro execute o script `coordinator.py`:
```bash
python src/coordinator.py
```

### Iniciar os Nós
Em diferentes terminais ou janelas de terminal, execute os seguintes comandos para iniciar cada nó:
```bash
python src/raft.py http://localhost:5001
python src/raft.py http://localhost:5002
python src/raft.py http://localhost:5003
```

### Simular Falha de Nó
Para simular uma falha de nó, você pode usar o seguinte comando:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"node": "http://localhost:5001", "duration": 10}' http://localhost:5000/simulate_failure
```
Esse comando simulará uma falha no nó `http://localhost:5001` por 10 segundos.

### Verificar o Status dos Nós
Para verificar o status dos nós, você pode acessar:
```bash
curl http://localhost:5000/status
```

## Explicação das Fases do Algoritmo
1. **Eleição de Líder**: Os nós elegem um líder quando o sistema inicia ou quando o líder atual falha.
2. **Replicação de Log**: O líder recebe comandos dos clientes e os replica nos logs dos seguidores.
3. **Segurança**: O sistema garante que apenas entradas comprometidas sejam aplicadas ao estado.

## Falhas Simuladas
- **Falha de Nó**: Nós podem falhar aleatoriamente durante a simulação.
- **Recuperação**: Nós tentam se recuperar e retomar a comunicação com o líder.

## Logs
Os logs detalhados de cada fase do consenso são armazenados em `logs/log.txt`.
