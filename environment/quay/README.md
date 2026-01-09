# 🐳 Quay Registry — Local Docker Compose Setup

Run your own **local Quay Container Registry** with Docker Compose — including PostgreSQL and Redis for full Quay
functionality.  
Perfect for local testing, development, or experimenting with Quay API and configuration.

---

## 🚀 Usage

1. **Create environment file**
   ```bash
   cp .env.example .env
   ```

2. **Start the registry**
   ```bash
   make install
   ```

3. **Access Quay**  
   Open [http://127.0.0.1:9080](http://127.0.0.1:9080) and log in using your admin credentials.

## 🧩 Notes

- 💾 All data is persisted in Docker volumes.
- ⚙️ The default admin user must be created manually as described below.

## 🛠️ Makefile Commands

| **Command**           | **Description**                             |
|-----------------------|---------------------------------------------|
| `make install`        | Start Quay Registry using Docker Compose    |
| `make logs`           | Show live logs from Quay container          |
| `make restart`        | Restart Quay container                      |
| `make uninstall`      | Stop and remove all Quay containers         |
| `make status`         | Show status of running containers           |
| `make shell`          | Open shell inside Quay container            |
| `make db-shell`       | Open PostgreSQL shell                       |
| `make rebuild`        | Rebuild Quay without cache                  |
| `make clean-logs`     | Save logs to file `quay_logs.txt`           |
| `make inspect-config` | Inspect Quay configuration inside container |

## 🔍 API Testing

To test the Quay API, you’ll need a valid **Bearer Token**:

1. Create an **Organization**
2. Create an **Application** within it
3. Generate an **Access Token**

You can use tools like [Requestly](https://requestly.com) to send API requests.  
A folder with example API requests is included — simply add the `Playground` folder to Requestly for quick testing.  
Don’t forget to update your **Bearer Token** and environment variables under the *Authentication* section before sending
requests.

📚
Reference: [Red Hat Quay API Documentation](https://docs.redhat.com/en/documentation/red_hat_quay/3.15/html/red_hat_quay_api_reference/index)
