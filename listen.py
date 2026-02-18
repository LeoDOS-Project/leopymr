import sseclient

messages = sseclient.SSEClient('http://localhost:8089/subscribe')
for msg in messages:
    print(msg)
