"""Run the stock CLI, retaining paid /chat responses before trace fetching."""
import sys
from lab.audit import Audit


def capture_call(call, audit):
    def wrapped(method, path, payload=None, **kwargs):
        paid = method == 'POST' and path == '/chat'
        if paid:
            audit.ensure_room(.35)
        try:
            result = call(method, path, payload, **kwargs)
        except Exception as e:
            if paid:
                audit.record('agent', {'method': method, 'path': path, 'payload': payload}, None, e, reserve=.35)
            raise
        if paid:
            audit.record('agent', {'method': method, 'path': path, 'payload': payload}, result, reserve=.35)
        return result
    return wrapped


if __name__ == '__main__':
    import stand
    import cli
    stand._call = capture_call(stand._call, Audit())
    sys.exit(cli.main(sys.argv[1:]))
