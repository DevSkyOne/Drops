from __future__ import annotations

from typing import (
    Coroutine,
    TypeVar,
    Optional,
    Union,
    Dict,
    Any,
    Callable
)

import json
import asyncio
import logging
from aiohttp import web

from data.config import *
from color_pprint import cprint


REQ = TypeVar('REQ', bound=web.Request)
RSP = TypeVar('RSP', bound=web.Response)


def error_body(code, message, errors: Optional[Dict[str, Any]] = None) -> str:
    """Creates the body for an error response"""
    base = {'code': code, 'message': message}
    if errors:
        base['errors'] = errors
    return json.dumps(base)


async def handle_404(request: web.Request) -> web.Response:
    return web.HTTPNotFound(body=error_body(0, "404: Not Found"), content_type='application/json')


async def handle_500(request: web.Request) -> web.Response:
    return web.HTTPNotFound(
        body=error_body(
            0,
            "500: Internal Server Error."
            "The server might be overloaded. It this keeps happening please open a ticket on https://discord.gg/devsky"
        ),
        content_type='application/json'
    )


def create_error_middleware(overrides):

    @web.middleware
    async def error_middleware(request: REQ, handler: Callable[[REQ], Coroutine]) -> RSP:
        if DEBUG:
            cprint(
                f'---->>>> Incoming request (HOST: {request.host}) (REMOTE: {request.remote}) ---->>>>',
                highlight='---->>>>',
                highlight_color_bg='',
                highlight_color_fg='\033[31m'
            )
            cprint(
                {
                    'scheme': request.scheme,
                    'method': request.method,
                    'url': request.url,
                    'headers': request.headers,
                    'forwarded': request.forwarded,
                    'query-params': request.query,
                    'has-body': request.body_exists
                },
                end='\n\n'
            )
        result: Optional[RSP] = None
        try:
            result = await handler(request)
        except web.HTTPException as ex:
            # if 'discord' in request.headers['user-agent']:
            #     ...
            override = overrides.get(ex.status)
            if override:
                result = await override(request)
            else:
                raise
        except Exception:
            request.protocol.logger.exception("Error handling request")
            return await overrides[500](request)
        if DEBUG and result:
            cprint(
                f'<<<<---- Outgoing response to (HOST: {request.host}) (REMOTE: {request.remote}) <<<<----',
                highlight='<<<<----',
                highlight_color_bg='',
                highlight_color_fg='\033[31m'
            )

            if result.body_length:
                body = (result.body._value if not isinstance(result.body, bytes) else result.body).decode(result.body.encoding if not isinstance(result.body, bytes) else 'utf-8')
                if result.content_type == 'application/json':
                    body = json.loads(body)
            else:
                body = None
            try:
                if text := result.text:
                    if result.content_type == 'application/json':
                        text = json.loads(text)
                else:
                    text = None
            except AttributeError:
                text = None

            cprint({
                'status': result.status,
                'content-type': result.content_type,
                'headers': result.headers,
                'body': body,
                'text': text
            }, end='\n\n')
        return result
    return error_middleware


error_middleware = create_error_middleware({
    404: handle_404,
    500: handle_500
})


main_routes = web.RouteTableDef()


class MainAPI(web.Application):
    def __init__(self):
        super().__init__()
        self.versions = {}
        self.middlewares.append(error_middleware)
        self.router.add_routes(main_routes)

    @property
    def latest_version(self):
        return list(self.versions)[-1]

    def add_version_subapp(self, version: str, app: web.Application) -> None:
        self.versions[version] = app
        self.add_subapp(f'/api/{version}', app)

    @main_routes.view(r'/api/{tail:(?!(v\d)).*}')
    class Index(web.View):
        async def get(self) -> RSP:
            # noinspection PyUnresolvedReferences
            return web.HTTPFound(
                f'/api/{self.request.app.latest_version}/%s?%s' % (self.request.match_info['tail'], self.request.query_string)
            )


main_app = MainAPI()

v1 = web.RouteTableDef()


class APIv1(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_routes(v1)
        main_app.add_version_subapp('v1', self)

    @v1.view('/')
    class Index(web.View):
        async def get(self) -> RSP:
            return web.json_response({'status': 'UP'})


APIv1()


if __name__ == '__main__':
    web.run_app(main_app, port=PORT, host=HOST)
