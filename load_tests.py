import uuid
import random
import aiohttp
import asyncio
import aiofiles


fixture_1 = {
    "r_type": 1,
    "r_format": "xlsx",
    "user_id": 2
}


fixture_2 = {
    "r_type": 1,
    "r_format": "xlsx",
    "user_id": 4
}


fixture_3 = {
    "r_type": 1,
    "r_format": "xlsx",
    "user_id": 5
}


async def test_load_requests(session, data):

    for _ in range(random.randint(10, 20)):
        response = await session.post("http://127.0.0.1:8088/report/", json=data)

        if response.status == 200:
            content = await response.read()
            async with aiofiles.open(f"report_{uuid.uuid4()}.xlsx", "wb") as file:
                await file.write(content)
            print(f"Отчет успешно создан: report_{_}.xlsx")
        else:
            print(f"Ошибка при создании отчета: {response.status}")


async def main():
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            test_load_requests(session, fixture_1),
            test_load_requests(session, fixture_2),
            test_load_requests(session, fixture_3)
        )


if __name__ == '__main__':

    asyncio.run(main())
