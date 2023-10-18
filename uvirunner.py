import signal
import uvicorn

from reports import graceful_exit, cleanup_directory


async def main():

    signal.signal(signal.SIGINT, graceful_exit)

    try:
        config = uvicorn.Config(app="app:app", host="0.0.0.0", port=8000, log_level="info", reload=True)
        server = uvicorn.Server(config)
        await server.serve()
    except KeyboardInterrupt:
        pass
    finally:
        await cleanup_directory()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
