import logging

_log_orig = logging.Logger._log


def _kargs_log(self, level, msg, args, exc_info=None, extra=None, **kargs):
    kwmsg = ''.join(' %s=%s' % (k, str(v)) for k, v in kargs.items())
    _log_orig(self, level, str(msg) + kwmsg, args, exc_info, extra)


logging.Logger._log = _kargs_log

get_logger = logging.getLogger
