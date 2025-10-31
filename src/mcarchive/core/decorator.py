import functools
import inspect
from collections.abc import Callable

from mcarchive.core.db.session import LocalSession


def sql_session():
    def decorator(func: Callable):
        """SQL连接装饰器，兼容同步和异步方法

        Args:
            func (Callable):

        Returns:
            _type_:
        """
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                with LocalSession() as db:
                    kwargs["db"] = db
                    return await func(*args, **kwargs)

            return async_wrapper  # type: ignore

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            with LocalSession() as db:
                kwargs["db"] = db
                return func(*args, **kwargs)

        return sync_wrapper  # type: ignore

    return decorator
