import uuid
import json
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Job
from .tasks import process_job

def health(request):
    return JsonResponse({"ok": True})


@csrf_exempt
def create_job(request):
    # TODO (candidate): implement POST /api/jobs/
    # Body: {"user_id": "...", "prompt": "...", "num_images": 1-4}
    # Returns: a job identifier the client can poll later.
    ##
    """
    1. POST /api/jobs/
        Accepts JSON: {"user_id": "<string>", "prompt": "<string>", "num_images": <int 1-4>}
        Creates a job record, dispatches background work, returns a job_id the client can poll
        Must return quickly — do not block on generation
        No authentication needed; trust the user_id in the body
    """

    data = request.body.decode('utf-8')
    data = json.loads(data)

    user_id = data.get('user_id')
    prompt = data.get('prompt')
    num_images = data.get('num_images', 1)
    idempotency_key = data.get('idempotency_key', uuid.uuid4())


    if not user_id or not prompt or not num_images:
        return JsonResponse({"error": "Missing required fields"}, status=400)

    # Idempotency: rely on the unique constraint instead of filter-then-create
    # to avoid TOCTOU race between concurrent requests.
    try:
        job = Job.objects.create(
            user_id=user_id,
            prompt=prompt,
            number_of_images=num_images,
            idempotency_key=idempotency_key,
        )
    except IntegrityError:
        job = Job.objects.get(idempotency_key=idempotency_key)
        return JsonResponse({"message": "Already processed", "job_id": job.id})

    # Dispatch after commit so the worker never sees a DoesNotExist
    transaction.on_commit(lambda: process_job.delay(job.id))

    return JsonResponse({"job_id": job.id}, status=201)


def get_job(request, job_id):
    # TODO (candidate): implement GET /api/jobs/{job_id}/
    # Returns: current status and result URLs when complete.

    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return JsonResponse({"error": "Job not found"}, status=404)

    return JsonResponse({
        "job_id": job.id,
        "status": job.status,
        "result": job.result,
        "error_messages": job.error_messages,
    })
