"""
Mashq 5: asyncio.TaskGroup — structured concurrency
- gather'ning zamonaviy alternativi
- Birortasida xato bo'lsa — boshqalari avtomatik bekor qilinadi
"""
import asyncio


async def task(name: str, seconds: float, fail: bool = False):
    print(f"  {name} boshlandi")
    await asyncio.sleep(seconds)
    if fail:
        raise ValueError(f"{name} fail bo'ldi!")
    print(f"  {name} tugadi")
    return name


async def main_success():
    print("=== Hammasi muvaffaqiyatli ===")
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(task("A", 1))
        t2 = tg.create_task(task("B", 2))
        t3 = tg.create_task(task("C", 1.5))

    # TaskGroup tugagandan keyin natijalarni olamiz
    print(f"Natijalar: {t1.result()}, {t2.result()}, {t3.result()}")


async def main_with_error():
    print("\n=== Bittasi fail bo'lsa ===")
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(task("A", 3))
            tg.create_task(task("B", 1, fail=True))  # 1s da fail
            tg.create_task(task("C", 5))
    except* ValueError as eg:
        # ExceptionGroup — TaskGroup ning yangi xususiyati
        for exc in eg.exceptions:
            print(f"Tutildi: {exc}")


async def main():
    await main_success()
    await main_with_error()


if __name__ == "__main__":
    asyncio.run(main())