import asyncio
from typing import List
import aiohttp
import requests
from requests import Response


class ManyHTTPRequester:

    def __init__(self, is_async=True, host_count=10):

        self.is_async = is_async

        # limit_per_host : 호스트당 최대 연결수
        # limit : 전체 최대 연결수
        if is_async:
            self.tcp_connector = aiohttp.TCPConnector(limit_per_host=host_count, limit=host_count)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tcp_connector.close()

    def request_all(self, host_url: str, parameters: List[str])->List[str]:
        """
        async request
        :param host_url:
        :param parameters:
        :return:
        """

        if self.is_async:
            results = asyncio.run(self.__request_async(host_url, parameters))
        else:
            results = []
            for parameter in parameters:
                result = self.request(host_url, parameter)
                results.append(result)

        return results

    @classmethod
    def request(cls, uri: str, parameter: str) -> Response:
        """
        sync request batch
        """
        response = requests.post(uri, data=parameter)
        return response

    async def __request_async(self, host_url: str, parameters: List[str]):
        async_requests = []

        for parameter in parameters:
            async_requests.append(self.__create_request(host_url, parameter))
        return await asyncio.gather(*async_requests)

    async def __create_request(self, host_url: str, parameter: str):
        tcp_connector = self.tcp_connector
        async with aiohttp.ClientSession(connector=tcp_connector, connector_owner=False) as session:
            async with session.post(host_url, data=parameter) as response:
                return await response.text()

