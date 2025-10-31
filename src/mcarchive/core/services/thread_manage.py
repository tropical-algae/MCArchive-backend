import asyncio
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial
from typing import Any, Optional


class ThreadPoolManager:
    def __init__(self, max_workers: int | None = None):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._pending_tasks: list[Future] = []

    def submit_sync(self, func: Callable[..., Any], *args, **kwargs) -> asyncio.Future:
        # 绑定参数到函数（固定参数，方便线程池执行）
        bound_func = partial(func, *args, **kwargs)

        # 提交到线程池，获取 concurrent.futures.Future
        future = self.executor.submit(bound_func)
        self._pending_tasks.append(future)

        # 转为 asyncio.Future，方便在异步代码中 await
        loop = asyncio.get_event_loop()
        async_future = loop.run_in_executor(None, self._wait_for_future, future)
        return async_future

    @staticmethod
    def _wait_for_future(future: Future) -> Any:
        try:
            return future.result()
        except Exception as e:
            raise e

    async def shutdown(self, wait: bool = True, cancel_futures: bool = False) -> None:
        if cancel_futures and not wait:
            for future in self._pending_tasks:
                if not future.done():
                    future.cancel()

        self.executor.shutdown(wait=wait)
        self._pending_tasks.clear()


thread_pool = ThreadPoolManager()
