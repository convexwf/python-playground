# -*- coding: utf-8 -*-
import email
import poplib
import time
from email.header import decode_header
from email.parser import Parser
from email.utils import parseaddr


class recv_email:

    def __init__(self, username, password, email_server):
        # 邮件地址, 口令和POP3服务器地址:
        self.username = username
        self.password = password  # 此处密码是授权码,用于登录第三方邮件客户端
        self.pop3_server = email_server

        self.server = poplib.POP3(self.pop3_server, 110, timeout=10)
        # 身份认证:
        self.server.user(self.username)
        self.server.pass_(self.password)

        # 返回邮件数量和占用空间:
        num, size = self.server.stat()
        self.msg_num = int(num)
        self.msg_size = self.bytes2human(size)
        print("Messages: {}. Size: {}".format(self.msg_num, self.msg_size))

        resp, self.mails, octets = self.server.list()

    def close(self):
        self.server.quit()

    def bytes2human(self, n):
        symbols = ("K", "M", "G", "T", "P", "E", "Z", "Y")
        prefix = {}
        for i, s in enumerate(symbols):
            prefix[s] = 1 << (i + 1) * 10
        for s in reversed(symbols):
            if n >= prefix[s]:
                value = float(n) / prefix[s]
                return "%.1f%s" % (value, s)
        return "%sB" % n

    # 获得msg的编码
    def guess_charset(self, msg):
        charset = msg.get_charset()
        if charset is None:
            content_type = msg.get("Content-Type", "").lower()
            pos = content_type.find("charset=")
            if pos >= 0:
                charset = content_type[pos + 8 :].strip()
        return charset

    # 字符编码转换
    def decode_str(self, str_in):
        value, charset = decode_header(str_in)[0]
        if charset:
            value = value.decode(charset)
        return value

    # 获取邮件内容
    def get_content(self, msg):
        content = ""
        content_type = msg.get_content_type()
        # print('content_type:',content_type)
        if content_type == "text/plain":  # or content_type == 'text/html'
            content = msg.get_payload(decode=True)
            charset = self.guess_charset(msg)
            if charset:
                content = content.decode(charset)
        return content

    def get_msg(self, idx):
        resp, lines, octets = self.server.retr(idx)
        # lines存储了邮件的原始文本的每一行,
        # 邮件的原始文本:
        msg_content = b"\r\n".join(lines).decode("utf-8")
        # 解析邮件:
        msg = Parser().parsestr(msg_content)
        return msg

    def get_info(self, msg):
        # 获取邮件的发件人，收件人， 抄送人,主题
        From = parseaddr(msg.get("from"))[1]
        To = parseaddr(msg.get("To"))[1]
        Cc = parseaddr(msg.get_all("Cc"))[1]  # 抄送人
        Subject = self.decode_str(msg.get("Subject"))
        # 获取邮件时间,格式化收件时间
        date = time.strptime(msg.get("Date")[0:24], "%a, %d %b %Y %H:%M:%S")
        # 邮件时间格式转换
        date_str = time.strftime("%Y-%m-%d %H:%M", date)
        return From, To, Cc, Subject, date_str

    # 解析邮件,获取附件名字
    def get_attach(self, msg_in):
        for part in msg_in.walk():
            # 获取附件名称类型
            file_name = part.get_param("name")  # 如果是附件，这里就会取出附件的文件名
            if file_name:
                h = email.header.Header(file_name)
                # 对附件名称进行解码
                dh = email.header.decode_header(h)
                filename = dh[0][0]
                if dh[0][1]:
                    # 将附件名称可读化
                    filename = self.decode_str(str(filename, dh[0][1]))
                # 下载附件
                attach_data = part.get_payload(decode=True)
                return filename, attach_data
        return None, None


if __name__ == "__main__":
    email_addr = "XXXXXX@163.com"
    password = "XXXXX"
    pop3_server = "pop.163.com"
    dl = recv_email(username=email_addr, password=password, email_server=pop3_server)

    for idx in range(1, 10):
        # for idx in range(1, dl.msg_num+1):
        msg = dl.get_msg(idx)
        info = dl.get_info(msg)
        print(info)
    #
    # resp, mails, octets = dl.server.list()
    # # 可以查看返回的列表类似[b'1 82923', b'2 2184', ...]
    # print(mails)
    # index = len(mails)
    #
    # for i in range(1, index+1, 1):  # 倒序遍历邮件
    #     resp, lines, octets = dl.server.retr(i)
    #     # lines存储了邮件的原始文本的每一行,
    #     # 邮件的原始文本:
    #     msg_content = b'\r\n'.join(lines).decode('utf-8')
    #     # 解析邮件:
    #     msg = Parser().parsestr(msg_content)
    #     # 获取邮件的发件人，收件人， 抄送人,主题
    #     From = parseaddr(msg.get('from'))[1]
    #     To = parseaddr(msg.get('To'))[1]
    #     Cc = parseaddr(msg.get_all('Cc'))[1]  # 抄送人
    #     Subject = dl.decode_str(msg.get('Subject'))
    #     # print('from:%s,to:%s,Cc:%s,subject:%s' % (From, To, Cc, Subject))
    #
    #     attach_name, attach_data = dl.get_attach(msg)
    #
    #     if attach_name:
    #         print(i, attach_name)
    #         # 在指定目录下创建文件，注意二进制文件需要用wb模式打开
    #         with open(attach_name, 'wb') as fp:
    #             fp.write(attach_data)
    #     else:
    #         print(i, Subject)
    dl.close()
