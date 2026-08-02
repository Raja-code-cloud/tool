from cloud_content_hub.bootstrap.worker import create_celery_app
from cloud_content_hub.workers.routing import build_celery_task_routes

celery_app = create_celery_app()
celery_app.conf.update(
    task_routes=build_celery_task_routes(),
    task_default_queue="maintenance",
)

import cloud_content_hub.workers.tasks as _worker_tasks  # noqa: E402

_ = _worker_tasks
