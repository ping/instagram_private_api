from functools import wraps
import inspect
import warnings


def warn_usage(warning=UserWarning, replaced_by='', message=''):

    def warn(fn):
        """
        Emits a warning when a decorated function is called.

        :return:
        """
        @wraps(fn)
        def wrapper(*args, **kwargs):
            fn_name = '{}{}'.format(fn.__name__, '' if not inspect.isfunction(fn) else '()')
            default_message = 'Undefined warning for {0}.'.format(fn.__name__)
            if replaced_by:
                default_message += 'Please use {0} instead.'.format(replaced_by)
            if warning == DeprecationWarning:
                msg = message or '{0} has been deprecated. Please use {1} instead.'.format(
                    fn_name, replaced_by)
            elif warning == PendingDeprecationWarning:
                msg = message \
                    or '{0} will be deprecated in a future version. ' \
                       'Please use {1} instead.'.format(fn_name, replaced_by)
            else:
                msg = message or default_message
            warnings.simplefilter('always', warning)  # turn off filter
            warnings.warn(msg, warning)
            warnings.simplefilter('default', warning)  # reset filter
            return fn(*args, **kwargs)
        return wrapper

    return warn
