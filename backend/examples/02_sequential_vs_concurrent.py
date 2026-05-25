"""
Mashq 2: Ketma-ket va parallel ishlatish
- Bir xil ish, 3 baravar farq
"""
import asyncio
import time


async def fetch_user(user_id: int) -> dict:
    """DB so'rovni taqlid qilamiz — 1 sekund kutamiz"""
    print(f"  [{time.strftime('%H:%M:%S')}] User {user_id} so'ralmoqda...")
    await asyncio.sleep(1)
    print(f"  [{time.strftime('%H:%M:%S')}] User {user_id} keldi")
    return {"id": user_id, "name": f"User-{user_id}"}


async def sequential():
    print("=== KETMA-KET ===")
    start = time.perf_counter()

    users = []
    for user_id in [1, 2, 3]:
        user = await fetch_user(user_id)
        users.append(user)

    elapsed = time.perf_counter() - start
    print(f"Jami: {elapsed:.2f}s, foydalanuvchilar: {len(users)}")
    return elapsed


async def concurrent_gather():
    print("\n=== PARALLEL (gather) ===")
    start = time.perf_counter()

    users = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3),
    )

    elapsed = time.perf_counter() - start
    print(f"Jami: {elapsed:.2f}s, foydalanuvchilar: {len(users)}")
    return elapsed


async def concurrent_tasks():
    print("\n=== PARALLEL (create_task) ===")
    start = time.perf_counter()

    tasks = [asyncio.create_task(fetch_user(i)) for i in [1, 2, 3]]
    users = [await t for t in tasks]

    elapsed = time.perf_counter() - start
    print(f"Jami: {elapsed:.2f}s, foydalanuvchilar: {len(users)}")
    return elapsed


async def main():
    seq = await sequential()
    gat = await concurrent_gather()
    tsk = await concurrent_tasks()

    print(f"\n📊 Natija:")
    print(f"  Sequential:  {seq:.2f}s")
    print(f"  Gather:      {gat:.2f}s  ({seq/gat:.1f}x tez)")
    print(f"  Tasks:       {tsk:.2f}s  ({seq/tsk:.1f}x tez)")


if __name__ == "__main__":
    asyncio.run(main())