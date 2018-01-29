# Slackmail
Slack app created to allow users to send emails to helpdesk and open tickets

Users can implement a /helpdesk command and the following text is sent as an email to the helpdesk where it is used to open a ticket
and respond back to the user that the ticket has been created.


Slack post command to an aws api gateway which triggers a listerner lambda function. The function passes the message to a sns topic and responds back to the user to aviod a slack timeout. The sns topic triggers a second lambda function which parses the messages creates an email and sends it to the helpdesk. Lastly it responds back to the user to confirm.

