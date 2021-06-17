from channels.generic.websocket import WebsocketConsumer
from kubernetes.stream import stream
from threading import Thread
from kubernetes import client
from apps.lib.k8s import auth_config
from apps.user.models import User
from django.http.request import QueryDict
import json
from apps.host.models import Host
from apps.k8s.models import K8s, Auth


# 多线程
class K8SStreamThread(Thread):
    def __init__(self, websocket, container_stream):
        Thread.__init__(self)
        self.websocket = websocket
        self.stream = container_stream

    def run(self):
        while self.stream.is_open():
            # 读取标准输出
            if self.stream.peek_stdout():
                stdout = self.stream.read_stdout()
                self.websocket.send(stdout)
            # 读取错误输出
            if self.stream.peek_stderr():
                stderr = self.stream.read_stderr()
                self.websocket.send(stderr)
        else:
            self.websocket.close()


# 继承WebsocketConsumer 类，并修改下面几个方法，主要连接到容器
class StreamConsumer(WebsocketConsumer):
    message = {'status': 0, 'message': None}

    def connect(self):
        self.accept()
        query_string = self.scope.get('query_string')
        args = QueryDict(query_string=query_string, encoding='utf-8')
        width = args.get('width')
        height = args.get('height')
        width = int(width)
        height = int(height)

        self.hostname = args.get('hostname')
        self.username = args.get('username')
        self.namespace = args.get('namespace')
        self.pod_name = args.get('pod_name')
        self.container = args.get('container')

        auth_config(self.username, self.hostname)
        core_api = client.CoreV1Api()

        exec_command = [
            "/bin/sh",
            "-c",
            'TERM=xterm-256color; export TERM; [ -x /bin/bash ] '
            '&& ([ -x /usr/bin/script ] '
            '&& /usr/bin/script -q -c "/bin/bash" /dev/null || exec /bin/bash) '
            '|| exec /bin/sh']
        try:
            self.conn_stream = stream(core_api.connect_get_namespaced_pod_exec,
                                      name=self.pod_name,
                                      namespace=self.namespace,
                                      command=exec_command,
                                      container=self.container,
                                      stderr=True, stdin=True,
                                      stdout=True, tty=True,
                                      _preload_content=False)
            self.conn_stream.write_channel(4, json.dumps({"Height": int(height), "Width": int(width)}))
            kube_stream = K8SStreamThread(self, self.conn_stream)
            kube_stream.start()
        except Exception as e:
            print(e)
            status = getattr(e, "status")
            if status == 403:
                msg = "你没有进入容器终端权限！"
            else:
                msg = "连接容器错误，可能是传递的参数有问题！"
            print(msg)

    def disconnect(self, close_code):
        try:
            self.conn_stream.write_stdin('exit\r')
        except:
            pass
        finally:
            # 过滤点结果中的颜色字符
            # res = re.sub('(\[\d{2};\d{2}m|\[0m)', '', self.ssh.res)
            print('命令: ')
            # print(self.ssh.cmd)
            # print('结果: ')
            # print(res)
            pass

    def receive(self, text_data=None, bytes_data=None):
        print(text_data)
        if text_data is None:
            self.conn_stream.write_stdin(bytes_data)
        else:
            data = json.loads(text_data)
            if type(data) == dict:
                status = data['status']
                if status == 0:
                    data = data['data']
                    self.conn_stream.write_stdin(data)
                else:
                    cols = data['cols']
                    rows = data['rows']
                    self.conn_stream.write_channel(4, json.dumps({"Height": int(rows), "Width": int(cols)}))
