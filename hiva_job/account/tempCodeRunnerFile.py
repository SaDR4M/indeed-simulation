def send_sms(phone) :
    key = os.getenv('SMS_API_KEY')
    print(key)
    url = f"https://api.kavenegar.com/v1/{API_KEY}/sms/send.json"
    
    encode_message = urllib.parse.quote("این یک پیام تست است")
    data = {
        "receptor" : phone,
        # 'sneder' : "2000500666",
        "message" : encode_message,

    }
    response = requests.post(url , data=data)
    print(response.json())
response = requests.get(url=f"https://api.kavenegar.com/v1/{API_KEY}/sms/status.json?messageid=1552292381")
print(response.json())