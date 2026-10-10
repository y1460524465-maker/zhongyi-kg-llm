import asyncio


class MsgQueueManager:
    def __init__(self):
        self.msg_queue_dict = {}
        # 保存事件循环引用，在 FastAPI 启动后由 lifespan 或首次请求时设置
        self._loop: asyncio.AbstractEventLoop = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    def get_msg_queue(self, user_id) -> asyncio.Queue:
        if user_id not in self.msg_queue_dict:
            self.msg_queue_dict[user_id] = asyncio.Queue()
        return self.msg_queue_dict[user_id]

    def del_msg_queue(self, user_id):
        if user_id in self.msg_queue_dict:
            del self.msg_queue_dict[user_id]

    def _put_sync(self, user_id, item):
        """从同步线程安全地向 asyncio.Queue 投递消息"""
        queue = self.get_msg_queue(user_id)
        if self._loop is None:
            raise RuntimeError("MsgQueueManager: event loop not set. Call set_loop() first.")
        self._loop.call_soon_threadsafe(queue.put_nowait, item)

    # 供同步节点（线程池中）调用
    def put_msg_content(self, user_id, content):
        self._put_sync(user_id, {"type": "msg", "msg": content})

    def put_reply_content(self, user_id, content):
        self._put_sync(user_id, {"type": "reply", "msg": content})

    def put_done_content(self, user_id):
        self._put_sync(user_id, {"type": "done", "msg": ""})


msg_queue_manager = MsgQueueManager()
