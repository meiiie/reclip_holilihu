import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


EXPECTED_TOOLS = {
    'get_video_info',
    'download_video',
    'download_many',
    'get_download_status',
    'get_runtime_status',
    'list_recent_downloads',
}


async def main():
    params = StdioServerParameters(command=sys.executable, args=['-m', 'mcp_server'])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = {tool.name for tool in tools.tools}
            missing = EXPECTED_TOOLS - names
            assert not missing, f'Missing MCP tools: {sorted(missing)}'
            print('smoke_mcp ok')


if __name__ == '__main__':
    asyncio.run(main())
