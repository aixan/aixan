from channels.generic.websocket import WebsocketConsumer
from apps.webssh.tools.exec import SSHExecutor
from apps.setting.utils import AppSetting
from apps.host.models import Host
from django.http.request import QueryDict
import threading
import json


class Exec(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def connect(self):
        self.accept()
        self.user = self.scope["user"]
        print(self.scope)
        query_string = self.scope.get("query_string")
        print(query_string)
        ssh_args = QueryDict(query_string=query_string, encoding='utf-8')

        host = ssh_args.get('hostname')
        host = Host.objects.get(hostname=host, deleted_by_id__isnull=True)
        exec = ssh_args.get("exec").replace(',', "\n")

        ssh_connect_dict = {
            'host': host.hostname,
            'user': host.username,
            'port': int(host.port),
            'exec': exec,
        }

        if host.pkey == '':
            private_key = AppSetting.get('private_key')
            ssh_connect_dict['ssh_key'] = private_key
        else:
            ssh_connect_dict['ssh_key'] = host.pkey

        self.ssh = SSHExecutor(websocker=self, **ssh_connect_dict)
        threading.Thread(target=self.ssh.run()).start()

    def disconnect(self, close_code):
        print(self.ssh.message)

    def receive(self, **kwargs):
        pass
