import asyncio

async def greet(name:str)->str:
    await asyncio.sleep(1)
    return f"salom,{name}"

async def main():
    coro=greet("Mamur")
    print(f"Type:{type(coro)}")
    print(f"object:{coro}")

    result=await coro
    print(f"Type {type(coro)}")
    print(f"result:{result}")


    result2= await greet("Mahmud")
    print(f"Result:{result2}")

if __name__=="__main__":
    asyncio.run( main())