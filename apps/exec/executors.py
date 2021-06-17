from queue import Queue
from threading import Thread
from apps.host.models import Host
from django.db import close_old_connections
from apps.lib.exec import AuthenticationException
import subprocess
import socket
import time


def host_executor(q, host, command):
    exit_code, out, now = -1, None, time.time()
    try:
        cli = host.get_ssh()
        exit_code, out = cli.exec_command(command)
        out = out if out else None
    except AuthenticationException:
        out = 'ssh authentication fail'
    except socket.error as e:
        out = f'network error {e}'
    finally:
        q.put((host.id, exit_code, round(time.time() - now, 3), out))


def dispatch(command, targets, in_view=False):
    if not in_view:
        close_old_connections()
    threads, q = [], Queue()
    for t in range(len(targets)):
        host = Host.objects.filter(hostname=targets[t]).first()
        if not host:
            raise ValueError(f'unknown host id: {targets[t]!r}')
        threads.append(Thread(target=host_executor, args=(q, host, command)))
    for t in threads:
        t.start()
    return [q.get() for _ in threads]

