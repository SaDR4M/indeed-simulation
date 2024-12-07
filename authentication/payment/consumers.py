# import json
# from channels.generic.websocket import AsyncWebsocketConsumer

# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # Get the user ID from the authenticated user
#         self.user_id = self.scope['user'].id
#         self.channel_name = f"notification_{self.user_id}"  # Unique channel name for the user

#         # Accept the WebSocket connection
#         await self.accept()

#     async def disconnect(self, close_code):
#         # Handle any clean-up tasks when the WebSocket connection closes
#         pass
    
#     async def receive(self, text_data):
#         # Receive a message from the WebSocket
#         data = json.loads(text_data)  # Parse incoming JSON message
#         message = data['message']  # Extract message from the received data

#         # Send the received message back to the WebSocket (you can modify this)
#         await self.send(text_data=f"received_{message}")

#     async def send_message(self, event):
#         # Send a message to the WebSocket when an event occurs
#         message = event['message']
        
#         # Send the message as JSON to the WebSocket client
#         await self.send(
#             text_data=json.dumps({
#                 'type': "send_message",  # Event type to identify the message
#                 'message': message  # The actual message to send
#             })
#         )
