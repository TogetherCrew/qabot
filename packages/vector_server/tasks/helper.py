def set_status(_self, state='PROGRESS', meta=None):
    if meta is None:
        meta = {'current': 'BEGIN'}

    if not _self.request.called_directly:
        _self.update_state(state=state,
                           meta=meta)