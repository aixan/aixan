from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from apps.webssh.tools.webssh import SSH
from apps.setting.utils import AppSetting
from django.http.request import QueryDict
import json
from apps.host.models import Host


class WebSSH(WebsocketConsumer):
    message = {'status': 0, 'message': None}
    """
    status:
        0: ssh 连接正常, websocket 正常
        1: 发生未知错误, 关闭 ssh 和 websocket 连接

    message:
        status 为 1 时, message 为具体的错误信息
        status 为 0 时, message 为 ssh 返回的数据, 前端页面将获取 ssh 返回的数据并写入终端页面
    """
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     print(self.scope)

    def connect(self):
        """
        打开 websocket 连接, 通过前端传入的参数尝试连接 ssh 主机
        :return:
        """
        self.accept()

        query_string = self.scope.get('query_string')
        ssh_args = QueryDict(query_string=query_string, encoding='utf-8')

        width = int(ssh_args.get('width'))
        height = int(ssh_args.get('height'))

        id = ssh_args.get('id')
        host = Host.objects.get(id=id)

        self.ssh = SSH(websocker=self, message=self.message)

        ssh_connect_dict = {
            'host': host.hostname,
            'user': host.username,
            'port': host.port,
            'timeout': 30,
            'pty_width': width,
            'pty_height': height,
        }

        if host.pkey == '':
            private_key = AppSetting.get('private_key')
            ssh_connect_dict['ssh_key'] = private_key
        else:
            ssh_connect_dict['ssh_key'] = host.pkey

        self.ssh.connect(**ssh_connect_dict)

    def disconnect(self, close_code):
        try:
            if close_code == 3001:
                pass
            else:
                self.ssh.close()
        except:
            pass
        finally:
            # 过滤点结果中的颜色字符
            # res = re.sub('(\[\d{2};\d{2}m|\[0m)', '', self.ssh.res)
            print('命令: ')
            print(self.ssh.cmd)
            # print('结果: ')
            # print(res)
            pass

    def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            self.ssh.django_bytes_to_ssh(bytes_data)
        else:
            data = json.loads(text_data)
            if type(data) == dict:
                status = data['status']
                if status == 0:
                    data = data['data']
                    self.ssh.shell(data)
                else:
                    cols = data['cols']
                    rows = data['rows']
                    self.ssh.resize_pty(cols=cols, rows=rows)
