# Microservice Social Sweat

This is the backend microservice for the **Social Sweat App**.
**Frontend repository**: [social-sweat-app](https://github.com/miguelgrieder/social-sweat-app)

---

## Table of Contents

1. [Integration with Other Services](#integration-with-other-services)
2. [Getting Started](#getting-started)
3. [Contributing](#contributing)

---

## Integration with Other Services

As the backend for the Social Sweat app, this microservice provides core functionalities such as activity data handling, user profiles, and more.

### MongoDB
A running **MongoDB** instance is required.
For a local Docker setup, replace the `x-` variables with your own values:

```bash
sudo docker run -d \
  --name x-docker_mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=x-name \
  -e MONGO_INITDB_ROOT_PASSWORD=x-pass \
  -v mongo_db:/data/db \
  mongo:latest
```

Then, set these environment variables in your `.env`:

```bash
## - MongoDB Config - ##
MONGO_VARIABLES_HOST=0.0.0.0
MONGO_VARIABLES_PORT=27017
MONGO_VARIABLES_USERNAME=x-name
MONGO_VARIABLES_PASSWORD=x-pass
```

Once configured, you can start your MongoDB container with:
```bash
sudo docker start x-docker_mongodb
```

### Clerk
For user authentication and management, you’ll need a [Clerk](https://clerk.com/) account.
Include these environment variables in your `.env`:
```bash
CLERK_API_URL=https://api.clerk.com/v1
CLERK_API_PUBLIC_KEY=pk_test_XYZ
CLERK_API_SECRET_KEY=sk_test_XYZ
CLERK_JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\nXYZ\n-----END PUBLIC KEY-----"
```

---

## Getting Started

1. **Clone this Repository**
   ```bash
   git clone https://github.com/miguelgrieder/microservice-social-sweat.git
   ```
2. **Set Up Virtual Environment**
   In your terminal:
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   python --version
   pip install --upgrade pip
   pip install pip-tools
   /bin/sh -e scripts/install_requirements_dev.sh
   ```
3. **Set Up Environment Variables**
   - Create a `.env` file from `.env.example`.
   - Add the required MongoDB and Clerk variables (and any others as needed).

4. **Run the App**
   - Ensure your MongoDB instance is running.
   - Run the microservice locally:
     ```bash
     python3.12 bin/run.py
     ```
   - Or run it via Docker Compose:
     ```bash
     sudo docker-compose up
     # or
     sudo docker compose up
     ```

---

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue to report a bug or request a new feature. Before contributing, please make sure you:

- Follow the existing code style and linting rules:
  ```bash
  /usr/bin/env bash scripts/format.sh
  /usr/bin/env bash scripts/lint.sh
  ```
- Test your changes:
  ```bash
  tox
  ```
- Provide a clear description of your changes and the motivation behind them.
- Add or update tests for any new functionality introduced.

---

If you have any questions or need assistance, don’t hesitate to reach out or open an issue.
