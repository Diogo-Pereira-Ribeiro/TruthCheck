# TruthCheck

Sistema distribuído de análise da credibilidade de notícias.

## Arranque no Windows 11

1. Instala Git e Docker Desktop.
2. No Docker Desktop, confirma que o motor WSL 2 está ativo.
3. Extrai a pasta `truthcheck` e abre-a no VS Code.
4. Copia `.env.example` para `.env`.
5. Abre o terminal PowerShell do VS Code e executa:

```powershell
docker compose up --build
```

## Endereços
- Website: http://localhost:3000
- API: http://localhost:8000
- Documentação da API: http://localhost:8000/docs
- RabbitMQ: http://localhost:15672

Credenciais iniciais RabbitMQ: `truthcheck` / `change_me_local`, depois de copiares o `.env.example` para `.env`.

## Testar a API

```powershell
$body = @{
  title = "Exemplo de título de notícia"
  content = "Este texto de exemplo tem mais de vinte caracteres para testar o envio."
  url = "https://example.com/noticia"
  language = "pt"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/analyses -ContentType "application/json" -Body $body
```

O backend guarda a análise no PostgreSQL e publica uma mensagem em cada uma das três filas. Os Workers recebem e confirmam as mensagens.

## Comandos úteis

```powershell
docker compose ps
docker compose logs -f
docker compose logs -f worker1 worker2 worker3
docker compose down
```

Para apagar também os dados da base de dados, executa `docker compose down -v`. Este comando elimina o volume PostgreSQL.

## Nesta etapa
- Docker Compose com frontend, backend, RabbitMQ e PostgreSQL.
- API FastAPI com endpoint de saúde e submissão de análises.
- Três filas RabbitMQ duráveis.
- Três Workers de teste.
- Tabela inicial no PostgreSQL.

Os Workers ainda não analisam notícias. Nesta etapa validamos a infraestrutura e a comunicação.
