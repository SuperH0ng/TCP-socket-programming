# TCP-socket-programming

TCP 기반 소켓 프로그래밍 구현

1.	CODE

* server code
	client code

*	server의 host, port는 localhost, 12345로 진행 
host = "localhost"
port = 12345

*	server의 socket 생성 후 대기
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('localhost',port))
serverSocket.listen()

*	응답 format

```python
response = "HTTP/1.1 {header[0]} {header[1]}\nDate: {date}\nHost: {url}\n"
get_response = "Content-Type: application/json\nContent-Length:{l} \n\n{data}"
```

	connect할 ip와 port 설정
ip = "127.0.0.1"
port = 12345

	client에서 server에 요청할 method를 입력받고, create_socket_and_send_message메소드를 호출

```python
request = input("Method : ")
    request += (f"\r\nHost: {ip}\r\n")
    request += 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36\r\n'
    request += 'Connection: Keep-Alive\n\n'
    create_socket_and_send_message(request)
```

	client의 socket을 생성한 후 client의 Request를 server에 보냄

```python
def create_socket_and_send_message(request_message) :
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((ip,port))
    print(f"connect {ip}")
    clientSocket.send(request_message.encode("utf-8"))
```

*	server에서 client의 접속을 받음

```python
while 1 :
    connectionSocket, addr = serverSocket.accept()
    print(str(addr), "에서 접속되었습니다.")
```

*	client의 요청을 확인한 후, 각 요청에 맞는 함수를 호출
알맞지 않은 요청이 입력되었을 경우 badRequest 함수를 호출
client의 요청을 적절히 수행한 뒤 client socket의 연결을 끊음

```python
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
```

*	찾을 수 없는 정보를 요청하였을 경우 notFound 함수를 호출하여 client에게 HTTP 응답 상태 코드 404와 “Not Found” response를 보냄

```python
def notFound(cs) :
    response_message = response.format(
            header = [404, "Not Found"],
            date = datetime.datetime.now(),
            url = host,
        )
    cs.send(response_message.encode())
```

*	잘못된 요청일 경우 badRequest 함수를 호출하여 client에게 HTTP 응답 상태 코드 400과 “Bad Request” Response를 보냄

```python
def badRequest(cs) :
    response_message = response.format(
            header = [400, "Bad Request"],
            date = datetime.datetime.now(),
            url = host,
        )
    cs.send(response_message.encode())
```

*	GET 요청을 받았을 경우
요청받은 파일을 열어, client에게 보내주고 HTTP 응답 상태 코드 200과 “OK” Response를 보냄
만약 요청한 파일이 없을 경우 notFound 함수를 호출
그 외 GET 요청을 하였지만 요청이 잘못됐을 경우 등 badRequest 함수를 호출

```python
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
```

*	HEAD 요청을 받았을 경우
요청받은 파일을 열어, client에게 본문만을 포함하지 않고 리소스의 데이터를 보냄
HTTP 응답 상태 코드 200과 “OK” Response를 보냄
만약 요청한 파일이 없을 경우 notFound 함수를 호출
그 외 GET 요청을 하였지만 요청이 잘못됐을 경우 등 badRequest 함수를 호출

```python
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
```

*	POST 요청을 받았을 경우 
올바른 요청일 경우 POST에 필요한 data를 client에게 요청하며 HTTP 응답 상태 코드 300과 “Multiple Choices” Response를 보내고 client의 응답을 기다림

```python
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
```

	server에서 받은 Response의 HTTP 응답 상태 코드가 300일 경우 server에서 요청하는 정보를 client에서 추가로 입력하여 다시 server로 보냄

```python
data = clientSocket.recv(1024).decode("utf-8")
    print(data)
    if (data[9:12] == "300") :
        response = input()
        print()
        clientSocket.send(response.encode("utf-8"))
        print(clientSocket.recv(1024).decode("utf-8"))
```

*	client에서 데이터를 받고 잘못된 정보가 들어오면 raise로 error를 발생
올바른 데이터를 받았을 경우 파일에 추가

```python
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
```

*	client에게 HTTP 응답 상태 코드 201과 “Created” Response를 보냄

 ```python
 response_message = response.format(
            header = [201, "Created"],
            date = datetime.datetime.now(),
            url = host,
        )

	cs.send(response_message.encode())
```

*	PUT 요청을 받았을 경우
POST 요청을 받았을 경우와 마찬가지로 PUT에 필요한 data를 client에게 요청하며 HTTP 응답 상태 코드 300과 “Multiple Choices” Response를 보내고 client의 응답을 기다림
응답을 받고 client가 update하고 싶은 데이터를 수정한 뒤 다시 파일에 저장
client에게 HTTP 응답 상태 코드 200과 “OK” Response를 보냄

```python
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
```

*	DELETE 요청을 받았을 경우
POST 요청을 받았을 경우와 마찬가지로 DELETE에 필요한 data를 client에게 요청하며 HTTP 응답 상태 코드 300과 “Multiple Choices” Response를 보내고 client의 응답을 기다림
응답을 받고 client가 delete하고 싶은 데이터를 삭제한 뒤 다시 파일에 저장
client에게 HTTP 응답 상태 코드 200과 “OK” Response를 보냄

```python
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
```

2.	TEST

*	초기 students.json 파일

```json
{
    "Chan_Jin": {
        "student_number": "20181692",
        "grade": "3.5",
        "department": "software"
    },
    "Da_Eun": {
        "student_number": "20203112",
        "grade": "4.2",
        "department": "software"
    },
    "So_Jeong": {
        "student_number": "20201234",
        "grade": "3.8",
        "department": "software"
    }
}
```

*	 tcpserver.py와 tcoclient.py를 각각 실행


![image](https://user-images.githubusercontent.com/81635179/168081383-57f0ba31-6988-4ef4-a35a-8d743c1916e4.png)

1.	GET 요청이 올바른 경우

![image](https://user-images.githubusercontent.com/81635179/168081409-73270f1f-b450-4b25-8589-c9d54bebff48.png)

2.	GET 요청을 하였지만 찾을 수 없는 파일을 요청하였을 경우

![image](https://user-images.githubusercontent.com/81635179/168081425-b71c731b-4b9e-49ef-a42d-897be9d9416b.png)

3.	POST 요청을 하였을 경우

![image](https://user-images.githubusercontent.com/81635179/168081442-14f0deba-0a09-4de3-9873-ea609c4ee607.png)

HTTP 응답 상태 코드 300과 “Multiple Choices” Response를 client에 보냄
client에서 post할 값을 입력하여 주면 post가 되고
HTTP 응답 상태 코드 201과 “Created” Response”를 client에 보냄

![image](https://user-images.githubusercontent.com/81635179/168081451-361311a6-7520-4921-ba88-b286e96e6042.png)

students.json 파일에 데이터가 생성됨

```json
{
    "Chan_Jin": {
        "student_number": "20181692",
        "grade": "3.5",
        "department": "software"
    },
    "Da_Eun": {
        "student_number": "20203112",
        "grade": "4.2",
        "department": "software"
    },
    "So_Jeong": {
        "student_number": "20201234",
        "grade": "3.8",
        "department": "software"
    },
    "Seung_Hyun": {
        "student_number": "20213100",
        "grade": "4.3",
        "department": "software"
    }
}
```

4.	PUT 요청을 하였을 경우
HTTP 응답 상태 코드 300과 “Multiple Choices” Response를 client에 보냄
client에서 put할 값을 입력하여 주면 update가 되고
HTTP 응답 상태 코드 200과 “OK”를 client에 보냄

![image](https://user-images.githubusercontent.com/81635179/168081464-5c9ce85b-7dfb-4ff2-b9ea-6b288cf665c7.png)

students.json 파일의 Seung_Hyun의 데이터가 update됨

```json
{
    "Chan_Jin": {
        "student_number": "20181692",
        "grade": "3.5",
        "department": "software"
    },
    "Da_Eun": {
        "student_number": "20203112",
        "grade": "4.2",
        "department": "software"
    },
    "So_Jeong": {
        "student_number": "20201234",
        "grade": "3.8",
        "department": "software"
    },
    "Seung_Hyun": {
        "student_number": "20213100",
        "grade": "4.5",
        "department": "software"
    }
}
```

5.	잘못된 요청을 받았을 경우

![image](https://user-images.githubusercontent.com/81635179/168081484-d3ab637e-e056-4aed-a292-0a91e26ab140.png)


6.	HEAD 요청을 받았을 경우
 
![image](https://user-images.githubusercontent.com/81635179/168081495-626ac9dc-91a5-474b-b799-c0a5349403c7.png)

7.	DELETE 요청을 받았을 경우
HTTP 응답 상태 코드 300과 “Multiple Choices” Response를 client에 보냄
client에서 delete할 값을 입력하여 주면 해당 데이터가 삭제되고
HTTP 응답 상태 코드 200과 “OK”를 client에 보냄

![image](https://user-images.githubusercontent.com/81635179/168081499-918702dd-f52c-4c03-8d6e-8613e9cf76a7.png)

students.json 파일의 So_Jeong 데이터가 삭제됨

```json
{
    "Chan_Jin": {
        "student_number": "20181692",
        "grade": "3.5",
        "department": "software"
    },
    "Da_Eun": {
        "student_number": "20203112",
        "grade": "4.2",
        "department": "software"
    },
    "Seung_Hyun": {
        "student_number": "20213100",
        "grade": "4.5",
        "department": "software"
    }
}
```

3.	WireShark로 캡쳐한 HTTP 명령어 수행 결과
 
![image](https://user-images.githubusercontent.com/81635179/168081518-981dbab5-1545-49b9-936e-5036fb088492.png)
