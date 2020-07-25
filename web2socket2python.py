from threading import Thread
import struct#此模块可以执行Python 值和以Python bytes 对象表示的C 结构之间的转换。
import time
import hashlib
# Python的hashlib提供了常见的摘要算法，如MD5，SHA1等等。
# 什么是摘要算法呢？摘要算法又称哈希算法、散列算法。它通过一个函数，把任意长度的数据转换为一个长度固定的数据串（通常用16进制的字符串表示）。
# 举个例子，你写了一篇文章，内容是一个字符串'how to use python hashlib - by Michael'，并附上这篇文章的摘要是'2d73d4f15c0db7f5ecb321b6a65e5d6d'。如果有人篡改了你的文章，并发表为'how to use python hashlib - by Bob'，你可以一下子指出Bob篡改了你的文章，因为根据'how to use python hashlib - by Bob'计算出的摘要不同于原始文章的摘要。
import base64#Base64是一种基于64个可打印字符来表示二进制数据的表示方法。
import socket#Socket又称"套接字"，应用程序通常通过"套接字"向网络发出请求或者应答网络请求，使主机间或者一台计算机上的进程间可以通讯。
import cv2
import numpy as np

import pickle
#import face2.py

mode = "initialize"
pic_size = 0
pic_receive = 0
pic = ""
pic_repeat = []

class returnCrossDomain(Thread):
    
    
    def __init__(self, connection):#构造函数
        Thread.__init__(self)#该模块支持守护线程，其工作方式：守护线程一般是一个等待客户端请求的服务器。如果没有客户端请求，守护线程就是空闲的。如果把一个线程设置为守护线程，就表示这个线程是不重要的，进程退出时不需要等待这个线程执行完成。
        self.con = connection
        #<socket.socket fd=1704, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 9999), raddr=('127.0.0.1', 62125)>
        self.isHandleShake = False

    def run(self):
        global mode
        global pic_size
        global pic_receive
        global pic
        global pic_repeat
        while True:
            if not self.isHandleShake:
                # 开始握手阶段
                header = self.analyzeReq()
                secKey = header['Sec-WebSocket-Key'];#Sec-WebSocket-Key 是由浏览器随机生成的，提供基本的防护，防止恶意或者无意的连接。#冲请求的地方拿到的安全码

                acceptKey = self.generateAcceptKey(secKey)#Sec-WebSocket-Accept=toBase64( sha1( Sec-WebSocket-Key + 258EAFA5-E914-47DA-95CA-C5AB0DC85B11 )  )
	
                response = "HTTP/1.1 101 Switching Protocols\r\n"#交换协议HTTP/1.1 101 Switching Protocols
                response += "Upgrade: websocket\r\n"#HTTP/1.1 101 Switching Protocols
                response += "Connection: Upgrade\r\n"#Connection: Upgrade
                response += "Sec-WebSocket-Accept: %s\r\n\r\n" % (acceptKey.decode('utf-8'))# yjveEbzjx3r3FZPvMkIinxWXxUU=
                
                self.con.send(response.encode())#以指定的编码格式编码字符串，默认编码为 'utf-8'。
                self.isHandleShake = True
                if(mode=="initialize"):
                    mode = "get_order"
                print('response:\r\n' + response)#响应
                # 握手阶段结束

                #读取命令阶段
            elif mode == "get_order":
                opcode = self.getOpcode()#第一步get opcode：
                if opcode == 8:
                    self.con.close()#关闭数据传输
                self.getDataLength()#第二步get datalength：
                clientData = self.readClientData()# 第三步get clientdata：
                
                print('客户端数据：' + str(clientData))#：GS| I'm Websocket client!全部打印出来
                # 处理数据
                ans = self.answer(clientData)#data前3位有用#根据命令返回输出
                self.sendDataToClient(ans)    #同样可以写出一个发送数据的方法sendDataToClient：
                
                if (ans != "Unresolvable Command!" and ans != "hello world"):
                    pic_size = int(clientData[3:])#后面的数据的个数
                    #print("pic_size",pic_size)
                    pic_receive = 0
                    pic = ""
                    pic_repeat=[]
                    print("需要接收的数据大小：", pic_size)#需要接收的数据大小：
                    mode = "get_pic"
                
                # filename = 'shoplist.data'
                # # 初始化变量
       
                # # 以二进制写模式打开目标文件
                # f = open(filename, 'wb')
                # # 将变量存储到目标文件中区
                # pickle.dump(clientData, f)
                # # 关闭文件

                # print('客户端数据：' + str(clientData[4:10])+'\n')
                
                # print('客户端数据：' + str(clientData[7:22])+'\n')
                # print('客户端数据：' + str(clientData[22:])+'\n')
                # # (type, encoding)=mimetypes.guess_type(clientData, strict=True)
                # #    acceptKey = base64.b64encode(sha1_result)
     
        
                # img_original = base64.b64decode(str(clientData[22:]))
                # img_np = np.frombuffer(img_original, dtype=np.uint8)
                # img = cv2.imdecode(img_np, cv2.IMREAD_UNCHANGED)

                # cv2.imwrite("filename.png",img)
         
                #读取图片阶段
            elif mode == "get_pic":
                opcode = self.getOpcode()#第一步get opcode：
                if opcode == 8:#%x8：表示连接断开。
                    self.con.close()
                self.getDataLength()#第二步get datalength：
                clientData = self.readClientData()# 第三步get clientdata：
                print('客户端数据：' + str(clientData))
                pic_receive += len(clientData)#一段一段接受
                pic += clientData#一段一段接受
                if pic_receive < pic_size:#接受净度显示
                    self.sendDataToClient("Receive:"+str(pic_receive)+"/"+str(pic_size))
                    print("图片接收情况:",pic_receive,"/",pic_size)
                    print("当前图片数据:",pic)
                else:
                    print("完整图片数据:",pic)
                    self.sendDataToClient("Receive:100%")
                    result = self.process(pic)
                    self.sendDataToClient(result)
                    #清零
                    pic_size = 0
                    pic_receive = 0
                    pic = ""
                    pic_repeat=[]
                    #读命令
                    mode = "get_order"
                    # 处理数据
                    #self.sendDataToClient(clientData)
                    
    def process(self,pic):

        #此处是图片处理阶段
        pic = cv2.imread('./1.png')
        return pic


    def getOpcode(self):
        first8Bit = self.con.recv(1)#不论是客户还是服务器应用程序都用recv函数从TCP连接的另一端接收数据。该函数的第一个参数指定接收端套接字描述符；bufsize指定一次最多接收的数据大小，
        first8Bit = struct.unpack('B', first8Bit)[0]#　顾名思义，解包。比如pack打包，然后就可以用unpack解包了。返回一个由解包数据(string)得到的一个元组(tuple), 即使仅有一个数据也会被解包成元组。
        # print("first8Bit=" )
        # first8Bit
        opcode = first8Bit & 0b00001111#P1 = P1 & 0b00001111 = 0b00001010
        return opcode

    def getDataLength(self):
        second8Bit = self.con.recv(1)
        second8Bit = struct.unpack('B', second8Bit)[0]
        masking = second8Bit >> 7#右移动运算符：把">>"左边的运算数的各二进位全部右移若干位，>> 右边的数字指定了移动的位数
        dataLength = second8Bit & 0b01111111
        #print("dataLength:",dataLength)
        if dataLength <= 125:#当数据长度小于126时（0-125），长度使用7位表示。
            payDataLength = dataLength
        elif dataLength == 126:#当Payload len等于126时，需要使用扩展长度（Extendedpayload length），此时用16位表示长度（0-65535）。
            payDataLength = struct.unpack('H', self.con.recv(2))[0]
        elif dataLength == 127:#当Payload len等于127时，扩展长度的位数是64位（数据最大长度为2的64次方）。
            #实际使用中，会对发送数据的长度有一定限制。比如出于安全考虑一次发送的MTU长度不大于1500个字节。而chrome中对websocket的控件一次发送数据的长度限定在128Kbytes，也就是2的17次方的长度。并且这个最大长度貌似是不能通过配置修改的。
            #通过以上情况可以看出，对于发送图片数据来说（一张图片往往会大于128KB）我们需要将图片数据进行切分
            #应用层的协议需要对切分的图片数据进行控制。同时对于发送的图片数据进行一些转码的处理。
            payDataLength = struct.unpack('Q', self.con.recv(8))[0]
        self.masking = masking
        self.payDataLength = payDataLength
        #print("payDataLength:", payDataLength)

	

    def readClientData(self):

        if self.masking == 1:
            maskingKey = self.con.recv(4)
        data = self.con.recv(self.payDataLength)

        if self.masking == 1:
            i = 0
            trueData = ''
            for d in data:
                trueData += chr(d ^ maskingKey[i % 4])
                i += 1
            return trueData
        else:
            return data

    def sendDataToClient(self, text):
        sendData = ''
        sendData = struct.pack('!B', 0x81)#按照给定的格式('!B')，把数据封装成字符串(实际上是类似于c结构体的字节流)

        length = len(text)
        if length <= 125:
            sendData += struct.pack('!B', length)
        elif length <= 65536:
            sendData += struct.pack('!B', 126)
            sendData += struct.pack('!H', length)
        elif length == 127:
            sendData += struct.pack('!B', 127)
            sendData += struct.pack('!Q', length)

        sendData += struct.pack('!%ds' % (length), text.encode())
        dataSize = self.con.send(sendData)

  
####################################################################################################
    def answer(self,data):
        if(data[0:3]=="TC|"):
            return "hello world"
        elif(data[0:3]=="GS|"):
            return "Gaosi Deblur Survice"
        elif (data[0:3] == "DT|"):
            return "DongTai Deblur Survice"#動態模糊
        else:
            return "Unresolvable Command!"
        

    
    # def legal(self, string):  # python总会胡乱接收一些数据。。只好过滤掉
    #     if len(string) == 0:
    #         return 0
    #     elif len(string) <= 100:
    #         if self.loc(string) != len(string):
    #             return 0
    #         else:
    #             if mode != "get_pic":
    #                 return 1
    #             elif len(string) + pic_receive == pic_size:
    #                 return 1
    #             else:
    #                 return 0
    #     else:
    #         if self.loc(string) > 100:
    #             if mode != "get_pic":
    #                 return 1
    #             elif string[0:100] not in pic_repeat:
    #                 pic_repeat.append(string[0:100])
    #                 return 1
    #             else:
    #                 return -1  # 收到重复数据，需要重定位
    #         else:
    #             return 0

    # def loc(self, string):
    #     i = 0
    #     while(i<len(string) and self.rightbase64(string[i])):
    #         i = i+1
    #     return i

    # def rightbase64(self, ch):
    #     if (ch >= "a") and (ch <= "z"):
    #         return 1
    #     elif (ch >= "A") and (ch <= "Z"):
    #         return 1
    #     elif (ch >= "0") and (ch <= "9"):
    #         return 1
    #     elif ch == '+' or ch == '/' or ch == '|' or ch == '=' or ch == ' ' or ch == "'" or ch == '!' or ch == ':':
    #         return 1
    #     else:
    #         return 0

    def analyzeReq(self):
        reqData = self.con.recv(1024).decode()
        reqList = reqData.split('\r\n')
        headers = {}
        for reqItem in reqList:
            if ': ' in reqItem:
                unit = reqItem.split(': ')
                headers[unit[0]] = unit[1]
        return headers

    def generateAcceptKey(self, secKey):
        sha1 = hashlib.sha1()
        sha1.update((secKey + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode())#258EAFA5-E914-47DA-95CA-C5AB0DC85B11，计算安全码
        sha1_result = sha1.digest()
        acceptKey = base64.b64encode(sha1_result)
        return acceptKey


    # def padding(self,data):
    #     missing_padding = 4 - len(data) % 4
    #     if missing_padding:
    #         data += '='*missing_padding
    #     return data



def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 第1步是创建socket对象。调用socket构造函数。
    # family的值可以是AF_UNIX(Unix域，用于同一台机器上的进程间通讯)，也可以是AF_INET（对于IPV4协议的TCP和 UDP），至于type参数，SOCK_STREAM（流套接字）或者 SOCK_DGRAM（数据报文套接字）,SOCK_RAW（raw套接字）。
    sock.bind(('127.0.0.1', 9999))
    #第2步则address必须是一个双元素元组,((host,port)),主机名或者ip地址+端口号。如果端口号正在被使用或者保留，或者主机名或ip地址错误，则引发socke.error异常。
    sock.listen(5)
    #第3步，绑定后，必须准备好套接字，以便接受连接请求。backlog指定了最多连接数，至少为1，接到连接请求后，这些请求必须排队，如果队列已满，则拒绝请求。
    while True:# conn就是客户端链接过来而在服务端为期生成的一个链接实例
        # 获取连接
        try:
            connection, address = sock.accept()#等待链接,多个链接的时候就会出现问题,其实返回了两个值#address=(127.0.0.1,62125)connection=socket object
            #第4步，服务器套接字通过socket的accept方法等待客户请求一个连接：调用accept方法时，socket会进入'waiting'（或阻塞）状态。客户请求连接时，方法建立连接并返回服务器。accept方法返回一个含有俩个元素的元组，形如(connection,address)。第一个元素（connection）是新的socket对象，服务器通过它与客户通信；第二个元素（address）是客户的internet地址。
            
            returnCrossDomain(connection).start()#输入了sock类
        except:
            time.sleep(1)#延迟一秒
# 第5步是处理阶段，服务器和客户通过send和recv方法通信（传输数据）。服务器调用send，并采用字符串形式向客户发送信息。send方法返回已发送的字符个数。服务器使用recv方法从客户接受信息。调用recv时，必须指定一个整数来控制本次调用所接受的最大数据量。recv方法在接受数据时会进入'blocket'状态，最后返回一个字符串，用它来表示收到的数据。如果发送的量超过recv所允许，数据会被截断。多余的数据将缓冲于接受端。以后调用recv时，多余的数据会从缓冲区删除。

# 第6步，传输结束，服务器调用socket的close方法以关闭连接。
if __name__ == "__main__":
    main()
