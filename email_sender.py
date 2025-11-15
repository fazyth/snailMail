import yagmail
import json



def send_email(client_json, reciever, subject, contents):

    with open(client_json, 'r') as file:
        dict = json.load(file)

        
        # dict = json.read("john.json")
        sender_email = dict["email"]
        # Your Gmail app password
        app_password = dict["password"]

        # Initialize the yagmail SMTP client
        yag = yagmail.SMTP(user=sender_email, password=app_password)

        # Send an email
        yag.send(
        to="testedinburgh2@gmail.com",
        subject="Hello from Python!",
        contents="This is a test email sent using yagmail."
        )

        return 0

