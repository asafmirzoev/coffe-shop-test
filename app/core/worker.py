import multiprocessing


def get_worker_id() -> int:
    """
    :return: worker id (number)
    """
    return (
        multiprocessing.current_process()._identity[0]
        if multiprocessing.current_process()._identity
        else 1
    )
