from apps.lib.exec import SSH
import socket
import json


class SSHExecutor:
    def __init__(self, websocker, host, user, ssh_key=None, port=22, exec=None):
        self.websocker = websocker
        self.ssh_cli = SSH(host, port, user, ssh_key)
        self.command = exec
        self.message = ""

    def send(self, data):
        self.message += data
        message = {'code': 0, 'type': 'info', 'data': data}
        message = json.dumps(message)
        self.websocker.send(message)

    def send_system(self, data):
        self.message += data
        message = {'code': 0, 'type': 'system', 'data': data}
        message = json.dumps(message)
        self.websocker.send(message)

    def send_error(self, data):
        self.message += data
        message = {'code': 0, 'type': 'error', 'data': data}
        message = json.dumps(message)
        self.websocker.send(message)

    def send_status(self, code):
        self.message += f'### Exit code:{code}'
        message = {'code': code, 'data': f'### Exit code:{code}'}
        message = json.dumps(message)
        self.websocker.send(message, True)

    def run(self):
        self.send_system('### Executing')
        code = -1
        try:
            for code, out in self.ssh_cli.exec_command_with_stream(self.command):
                self.send(out)
        except socket.timeout:
            code = 130
            self.send_error('### Time out')
        except Exception as e:
            code = 131
            self.send_error(f'{e}')
        finally:
            self.send_status(code)
            self.websocker.close()
