import uvicorn
import uvicorn.config

from microservice_social_sweat import config

settings = config.get_settings()

fmt = '[%(asctime)s] [%(levelno)s] [%(status_code)s] %(client_addr)s - "%(request_line)s"'
log_config = uvicorn.config.LOGGING_CONFIG
log_config["formatters"]["access"]["fmt"] = fmt

if __name__ == "__main__":
    uvicorn.run(
        "microservice_social_sweat.main:app",
        host=settings.app_host,
        port=settings.app_port,
        workers=settings.app_workers,
        reload=settings.dev_uvicorn_reload,
    )
