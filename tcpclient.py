from socket import *

ip = "127.0.0.1"
port = 12345

ip = "172.20.10.3"
def create_socket_and_send_message(request_message) :
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((ip,port))
    print(f"connect {ip}")
    clientSocket.send(request_message.encode("utf-8"))

    data = clientSocket.recv(1024).decode("utf-8")
    print(data)
    if (data[9:12] == "300") :
        response = input()
        print()
        clientSocket.send(response.encode("utf-8"))
        print(clientSocket.recv(1024).decode("utf-8"))

    clientSocket.close()
    print(f"disconnect {ip}")


while 1 :
    request = input("Method : ")
    request += (f"\r\nHost: {ip}\r\n")
    request += 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36\r\n'
    request += 'Connection: Keep-Alive\n\n'
    create_socket_and_send_message(request)
    
