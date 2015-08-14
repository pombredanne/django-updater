try:
    from celery import shared_task

    @shared_task()
    def run_check():
        from updater import package
        package.run_check()
except ImportError:
    pass