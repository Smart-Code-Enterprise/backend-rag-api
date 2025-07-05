job "smartcodes-rag-backend" {
  datacenters = ["dc1"]
  type = "service"
  node_pool = "all"
  namespace = "smartcodes"

  group "smartcodes-rag-backend-dev" {
    count = 1

    constraint {
      attribute = "${meta.support_smartcodes_rag_backend}"
      operator  = "="
      value    = "true"
    }

    network {
      port "api" {
        to = 8000
        static = 18000
      }
    }

    task "smartcodes-rag-backend-dev" {
      driver = "docker"

      config {
        image = "docker-registry.imutably.com/v2/firecrawl-api:latest"
        command = "/bin/sh"
        args = ["-c", "pnpm run start:production" ]
        ports = ["api"]

        mount {
          type   = "bind"
          target = "/app/logs"
          source = "${meta.home_path}/workspace/smartcodes/backend-rag-api/logs"
          readonly = false
        }

        mount {
          type   = "bind"
          target = "/app/chroma_db_claude_NBC_2020"
          source = "${meta.home_path}/workspace/smartcodes/backend-rag-api/chroma_db_claude_NBC_2020"
          readonly = false
        }

        mount {
          type   = "bind"
          target = "/app/data"
          source = "${meta.home_path}/workspace/smartcodes/backend-rag-api/data"
          readonly = false
        }
      }

      env {
        LOG_LEVEL = "INFO"
        OPENAI_API_KEY = "sk-proj-1234567890"
        HOST = "0.0.0.0"
        PORT = "8000"
      }

      resources {
        cpu    = 1000
        memory = 2048
      }

      service {
        name = "smartcodes-rag-backend-dev"
        port = "api"
        provider = "nomad"

        tags = [
          "traefik.enable=true",
          "traefik.http.routers.smartcodes-rag-backend-dev.rule=Host(`smartcodes-dev.imutably.com`)",
          "traefik.http.routers.smartcodes-rag-backend-dev.tls=true",
          "traefik.http.routers.smartcodes-rag-backend-dev.entrypoints=web,websecure",
          "traefik.http.routers.smartcodes-rag-backend-dev.tls.certresolver=mytlschallenge",
          "traefik.http.middlewares.smartcodes-rag-backend-dev.headers.SSLRedirect=true",
          "traefik.http.middlewares.smartcodes-rag-backend-dev.headers.STSSeconds=315360000",
          "traefik.http.middlewares.smartcodes-rag-backend-dev.headers.browserXSSFilter=true",
          "traefik.http.middlewares.smartcodes-rag-backend-dev.headers.contentTypeNosniff=true",
          "traefik.http.middlewares.smartcodes-rag-backend-dev.headers.forceSTSHeader=true",
          "traefik.http.middlewares.smartcodes-rag-backend-dev.headers.SSLHost=imutably.com",
          "traefik.http.middlewares.smartcodes-rag-backend-dev.headers.STSIncludeSubdomains=true",
          "traefik.http.middlewares.smartcodes-rag-backend-dev.headers.STSPreload=true",
          "traefik.http.routers.smartcodes-rag-backend-dev.middlewares=smartcodes-rag-backend-dev@nomad"
        ]
      }
    }
  }
}