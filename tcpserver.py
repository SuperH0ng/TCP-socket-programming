from socket import *
import datetime
import json

host = "localhost"
port = 12345

serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('localhost',port))
serverSocket.listen()

response = "HTTP/1.1 {header[0]} {header[1]}\nDate: {date}\nHost: {url}\n"
get_response = "Content-Type: application/json\nContent-Length:{l} \n\n{data}"

def notFound(cs) :
    response_message = response.format(
            header = [404, "Not Found"],
            date = datetime.datetime.now(),
            url = host,
        )
    cs.send(response_message.encode())

def badRequest(cs) :
    response_message = response.format(
            header = [400, "Bad Request"],
            date = datetime.datetime.now(),
            url = host,
        )
    cs.send(response_message.encode())

def getRequest(cs, file) :
    try :
        f = open(file[1], "r")
        json_data = json.load(f)
        f.close()
        request_file = json.dumps(json_data)
        
        response_message = response.format(
            header = [200, "OK"],
            date = datetime.datetime.now(),
            url = host,
        ) + get_response.format(
            l = len(request_file),
            data = request_file
            )
        
        cs.send(response_message.encode())

    except FileNotFoundError :
        notFound(cs)
    
    except :
        badRequest(cs)

def postRequest(cs, file) :
    try :
        f = open(file[1], "r")
        json_data = json.load(f)
        f.close()

        # post에 필요한 정보
        required_contents = list(list(json_data.values())[0].keys())
        required_message = "\nEnter follow data : key "

        for key in required_contents :
            required_message += key + " "

        response_message = response.format(
            header = [300, "Multiple Choices"],
            date = datetime.datetime.now(),
            url = host,
        ) + required_message
        cs.send(response_message.encode())
    
        # contents 필요한 내용 받음
        data = cs.recv(1024).decode()
        post_content = data.split()

        # 받은 정보가 요구한 정보보다 많거나 적으면
        if len(required_contents)+1 != len(post_content) :
            raise

        new_content = {}
        for i in range(1, len(post_content)) :
            new_content[required_contents[i-1]] = post_content[i]

        new_data = {post_content[0] : new_content}
        json_data.update(new_data)

        f = open(file[1], "w")
        json.dump(json_data, f, indent="\t")
        f.close()
        
        response_message = response.format(
            header = [201, "Created"],
            date = datetime.datetime.now(),
            url = host,
        )

        cs.send(response_message.encode())

    except FileNotFoundError :
        notFound(cs)

    except :
        badRequest(cs)
    
def putRequest(cs, file) :
    try :
        f = open(file[1], "r")
        json_data = json.load(f)
        f.close()

        required_message = "key wantToUpdate value"
        response_message = response.format(
            header = [300, "Multiple Choices"],
            date = datetime.datetime.now(),
            url = host
        ) + required_message

        cs.send(response_message.encode())

        data = cs.recv(1024).decode()
        put_content = data.split()

        if len(put_content) != 3 :
            raise
        
        key = put_content[0]
        wantToUpdate = put_content[1]
        value = put_content[2]

        json_data[key][wantToUpdate] = value

        f = open(file[1], "w")
        json.dump(json_data, f, indent="\t")
        f.close()
        
        response_message = response.format(
            header = [200, "OK"],
            date = datetime.datetime.now(),
            url = host,
        )

        cs.send(response_message.encode())

    except FileNotFoundError :
        notFound(cs)
    
    except :
        badRequest(cs)
    

def headRequest(cs, file) :
    try :
        f = open(file[1], "r")
        json_data = json.load(f)
        f.close()
        request_file = json.dumps(json_data)
        
        response_message = response.format(
            header = [200, "OK"],
            date = datetime.datetime.now(),
            url = host,
        ) + get_response.format(
            l = len(request_file),
            data = "\n"
            )
        
        cs.send(response_message.encode())

    except FileNotFoundError :
        notFound(cs)
    
    except :
        badRequest(cs)

def deleteRequest(cs, file) :
    try :
        f = open(file[1], "r")
        json_data = json.load(f)
        f.close()

        required_message = "key"
        response_message = response.format(
            header = [300, "Multiple Choices"],
            date = datetime.datetime.now(),
            url = host
        ) + required_message
        
        cs.send(response_message.encode())

        data = cs.recv(1024).decode()
        delete_content = data.split()

        if len(delete_content) != 1 :
            raise
        #####
        del(json_data[delete_content[0]])

        f = open(file[1], "w")
        json.dump(json_data, f, indent="\t")
        f.close()
        
        response_message = response.format(
            header = [200, "OK"],
            date = datetime.datetime.now(),
            url = host,
        )

        cs.send(response_message.encode())

    except FileNotFoundError :
        notFound(cs)
    
    except :
        badRequest(cs)


while 1 :
    connectionSocket, addr = serverSocket.accept()
    print(str(addr), "에서 접속되었습니다.")

    data = connectionSocket.recv(1024)
    request_message = data.decode().split()
    request = request_message[0]
    print(str(addr), "에서 ", request, "를 요청하였습니다.")
    if request == "GET" :
        getRequest(connectionSocket, request_message)
    elif request == "POST":
        postRequest(connectionSocket, request_message)
    elif request == "PUT":
        putRequest(connectionSocket, request_message)
    elif request == "HEAD":
        headRequest(connectionSocket, request_message)
    elif request == "DELETE" :
        deleteRequest(connectionSocket, request_message)
    else :
        badRequest(connectionSocket)
    connectionSocket.close()