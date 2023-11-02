from logger.embedding_logger import logger


def set_status(_self, state='PROGRESS', meta=None):
    if meta is None:
        meta = {'current': 'BEGIN'}
    logger.debug(f"set status: {state} and meta: {meta}")
    if not _self.request.called_directly:
        _self.update_state(state=state,
                           meta=meta)
