
import httpx
import json


class HttpxAction:
    def __init__(self, *args, **kwargs):
        self.client_async = httpx.AsyncClient(**kwargs)
        self.client_async.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
        self.client = httpx.Client(**kwargs)
        self.client.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

    def get_config(self, config_key: str, environment: str = None) -> dict:
        if not self.client.auth:
            raise ValueError(f'请登录之后操作')
        if not environment:
            config_key_list = config_key.split('_')
            environment = config_key_list[0] if len(config_key_list) > 1 else 'default'
        url = f'http://43.138.130.198/drf/api/config_setting/{config_key}/?environment={environment}'
        response = self.client.get(url)
        value: dict = response.json()['parsed_value']
        return value

    def async_update_config(self, config_key: str, value: dict, environment: str = None) -> httpx.Response:
        if not self.client.auth:
            raise ValueError(f'请登录之后操作')
        if not environment:
            config_key_list = config_key.split('_')
            environment = config_key_list[0] if len(config_key_list) > 1 else 'default'
        url = f'http://43.138.130.198/drf/api/config_setting/{config_key}/?environment={environment}'
        response = self.client.put(url, json={'key': config_key, 'value': json.dumps(value, ensure_ascii=False)})
        return response

    async def async_get_config(self, config_key:str, environment:str=None) -> dict:
        if not self.client_async.auth:
            raise ValueError(f'请登录之后操作')
        if not environment:
            config_key_list = config_key.split('_')
            environment = config_key_list[0] if len(config_key_list) > 1 else 'default'
        url = f'http://43.138.130.198/drf/api/config_setting/{config_key}/?environment={environment}'
        response = await self.client_async.get(url)
        value:dict = response.json()['parsed_value']
        return value

    async def async_update_config(self, config_key:str, value:dict, environment:str=None) -> httpx.Response:
        if not self.client_async.auth:
            raise ValueError(f'请登录之后操作')
        if not environment:
            config_key_list = config_key.split('_')
            environment = config_key_list[0] if len(config_key_list) > 1 else 'default'
        url = f'http://43.138.130.198/drf/api/config_setting/{config_key}/?environment={environment}'
        response = await self.client_async.put(url, json={'key': config_key, 'value': json.dumps(value, ensure_ascii=False)})
        return response



