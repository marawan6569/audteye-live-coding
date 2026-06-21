import logging

from config.celery import app
from jobs.models import Job
from jobs.providers import (
    generate,
    ProviderTimeout,
    ProviderRateLimit,
    ProviderInternalError,
    ProviderInvalidPrompt,
)

logger = logging.getLogger(__name__)

TRANSIENT_EXCEPTIONS = (ProviderTimeout, ProviderRateLimit, ProviderInternalError)


@app.task(bind=True)
def process_job(self, job_id):
    """
    Process an image generation job.

    - Calls providers.generate() once per requested image.
    - Saves partial results after each successful call so retries
      don't re-generate (and re-charge) images already completed.
    - Retries on transient provider errors with exponential backoff.
    - Fails immediately on permanent errors (ProviderInvalidPrompt).
    """
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        logger.error("Job %s not found, aborting task.", job_id)
        return

    job.status = Job.PROCESSING
    job.save(update_fields=["status", "updated_at"])

    results = job.result or []

    for i in range(len(results), job.number_of_images):
        try:
            gen = generate(job.prompt)
            results.append({
                "image_url": gen.image_url,
                "cost_usd": gen.cost_usd,
            })
            # Persist after each image so retries can resume
            job.result = results
            job.save(update_fields=["result", "updated_at"])

        except ProviderInvalidPrompt as e:
            # Permanent failure — do NOT retry
            job.status = Job.FAILED
            job.error_message = str(e)
            job.save(update_fields=["status", "error_message", "updated_at"])
            logger.warning("Job %s failed permanently: %s", job_id, e)
            return

        except TRANSIENT_EXCEPTIONS as e:
            # Transient failure — retry with exponential backoff
            job.retry_count = self.request.retries + 1
            job.error_message = str(e)
            job.save(update_fields=["retry_count", "error_message", "updated_at"])
            logger.info(
                "Job %s hit transient error (attempt %d/%d): %s",
                job_id, job.retry_count, job.max_retries_number, e,
            )
            raise self.retry(
                exc=e,
                countdown=2 ** self.request.retries,  # 1s, 2s, 4s, 8s ...
                max_retries=job.max_retries_number,
            )

    # All images generated successfully
    job.status = Job.COMPLETED
    job.result = results
    job.save(update_fields=["status", "result", "updated_at"])
    logger.info("Job %s completed with %d images.", job_id, len(results))
