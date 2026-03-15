from main import app as fastapi_app


class StripPrefixASGI:
    def __init__(self, app, prefix: str):
        self.app = app
        self.prefix = prefix
        self.prefix_bytes = prefix.encode("utf-8")

    async def __call__(self, scope, receive, send):
        if scope["type"] in {"http", "websocket"}:
            path = scope.get("path", "")
            if path == self.prefix or path.startswith(f"{self.prefix}/"):
                new_scope = dict(scope)
                new_scope["path"] = path[len(self.prefix) :] or "/"
                new_scope["root_path"] = f"{scope.get('root_path', '')}{self.prefix}"

                raw_path = scope.get("raw_path")
                if raw_path:
                    stripped_raw = raw_path[len(self.prefix_bytes) :] or b"/"
                    new_scope["raw_path"] = stripped_raw

                await self.app(new_scope, receive, send)
                return

        await self.app(scope, receive, send)


app = StripPrefixASGI(fastapi_app, prefix="/api")
