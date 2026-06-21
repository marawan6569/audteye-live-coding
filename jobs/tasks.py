from config.celery import app


@app.task(bind=True)
def process_job(self, job_id):
    # TODO (candidate): implement the worker that:
    # - Loads the Job from the database
    # - Calls jobs.providers.generate(prompt)
    # - Persists the result and updates job state
    # - Handles failures appropriately
    pass
