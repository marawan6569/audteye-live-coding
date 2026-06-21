from django.db import models

# TODO (candidate): design the Job model.
#
# Consider:
# - What states does a job progress through?
# - What fields support idempotency, retries, and status polling?
# - What needs indexing for production query patterns?


class Job(models.Model):
    """
    user_id
    prompt
    number_of_images
    idempotency_key
    status
    max_retries_number
    retry_count
    error_message
    created_at
    updated_at
    """

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (PROCESSING, "Processing"),
        (FAILED, "Failed"),
        (COMPLETED, "Completed"),
    ]

    user_id = models.UUIDField()
    prompt = models.TextField()
    number_of_images = models.IntegerField(default=1)
    idempotency_key = models.UUIDField(unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    # Celery
    celery_task_id = models.UUIDField(null=True, blank=True)
    max_retries_number = models.IntegerField(default=3)
    retry_count = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    # result
    image_url = models.URLField(null=True, blank=True)
    cost_usd = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["idempotency_key"]),
            models.Index(fields=["user_id", "status"]),
        ]

    def __str__(self):
        return f"Job {self.id} - {self.status}"