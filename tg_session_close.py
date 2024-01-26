import asyncio

import aiohttp


async def list_open_sessions():
    open_sessions = []
    for session in aiohttp.ClientSession._instances:
        open_sessions.append(session)
    return open_sessions


# Запускаем функцию для получения списка незакрытых сессий
async def main():
    open_sessions = await list_open_sessions()

    if open_sessions:
        print("Незакрытые сессии:")
        for session in open_sessions:
            print(session)
    else:
        print("Нет незакрытых сессий.")


if __name__ == "__main__":
    # Запускаем асинхронный код
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())