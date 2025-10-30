# Narev

![Narev Banner](./.github/assets/banner.webp)

**Convert any billing into FOCUS format**

[![GitHub last commit](https://img.shields.io/github/last-commit/narevai/narev)](https://github.com/narevai/narev/commits)
[![Latest tag](https://img.shields.io/github/v/tag/narevai/narev?label=latest)](https://github.com/narevai/narev/tags)
[![Code Size](https://img.shields.io/github/languages/code-size/narevai/narev)](https://github.com/narevai/narev)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

Narev is an open source, self-hosted FinOps platform. It allows translating SaaS data into a FOCUS 1.2 format, and exporting it.

**Sources we support**:
- AWS
- Azure
- GCP
- OpenAI

**Exports we support**:
- Snowflake
- CSV
- Excel

We ship with lightweight FOCUS-compliant analytics.

![Narev Dashboard](./.github/assets/screenshot.png)

## Quick Start

### Demo Mode (with sample data)
```bash
docker run -d \
  --name narev \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e DEMO="true" \
  ghcr.io/narevai/narev:latest
```

### Production
First, generate an encryption key:
```bash
python -c "from cryptography.fernet import Fernet; \
print(Fernet.generate_key().decode())"
```
Then run the container with your generated key:
```bash
docker run -d \
  --name narev-prod \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e ENCRYPTION_KEY="gAAAAABhZ_your_actual_generated_key_here" \
  -e ENVIRONMENT="production" \
  ghcr.io/narevai/narev:latest
```
- Full production setup in the [Deployment Guide](https://www.narev.ai/docs/opensource/getting-started/deployment).

## License

Apache 2.0

---

## Acknowledgments

Thanks to [@satnaing](https://github.com/satnaing) for the excellent [front end starter](https://github.com/satnaing/shadcn-admin/tree/main)
