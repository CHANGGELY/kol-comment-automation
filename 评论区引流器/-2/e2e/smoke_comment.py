import asyncio
import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from services.task_service import TaskService


async def main():
    task = {
        "account_id": "default_account",
        "platform": "youtube",
        "video_id": "jNQXAC9IVRw",
        "content": "Hello from KOL 引流器",
    }
    svc = TaskService()
    ok = await svc.run_comment_task(task)
    print("OK" if ok else "FAIL")


if __name__ == "__main__":
    asyncio.run(main())
