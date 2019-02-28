from aiohttp.web import middleware, Response


@middleware
async def check_group_middleware(request, handler):
    data = await request.json()
    if data['group_id'] != request.dict_config.owner.cfg['group_id']:
        return Response(status=400)  # Bad Request for invalid group id
    return await handler(request)
