# agent-test

FastAPI Agent 示例服务，Python 3.13，输出 JSON 日志到 stdout，并通过 OpenTelemetry OTLP HTTP 接入 Collector。

## 功能

- `GET /health` 健康检查
- `GET /api/data` 返回 Agent 服务数据
- `POST /api/process` 供 Node/Java 调用，返回处理结果
- `POST /api/java-agent-java` 供 Java 调用，内部回调 Java `/api/agent/data`，形成 `java -> agent -> java`
- 每秒输出 heartbeat 日志

## 本地启动

```bash
python3.13 -m venv .venv
. .venv/bin/activate
pip install -e ".[test]"
python -m unittest tests/test_api_contract.py
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Kubernetes

```bash
kubectl apply -f k8s/test
kubectl get pods -n test -l app.kubernetes.io/name=agent-test
```

## CI/CD

当前使用 GitHub self-hosted runner 构建镜像并推送 Harbor，Argo CD 负责同步部署。测试环境 push `main` 自动发布，生产环境通过手动 workflow 发布。先按 [docs/github-runner-setup.md](docs/github-runner-setup.md) 配置 runner，再看 [docs/cicd-local-k3s.md](docs/cicd-local-k3s.md)。
