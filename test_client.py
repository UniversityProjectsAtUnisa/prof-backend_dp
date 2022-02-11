import httpx
import asyncio

data = {
  "q":"jaguar",
  "provider": "wikipedia"
}
provider = "wikipedia"

async def run():
  async with httpx.AsyncClient() as client:
    res = await client.get(f"http://localhost:8000/search", timeout=1000, params=data)
    print(res.json())

async def main():
  await run()

asyncio.get_event_loop().run_until_complete(main())