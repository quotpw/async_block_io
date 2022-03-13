import asyncio

import block_io


async def main():
    obj = block_io.Client('0362-2eb8-7375-3132')
    print(await obj.get_new_address())


if __name__ == '__main__':
    asyncio.run(main())
