import glob                             # for searching for json file 
import os                               # for setting and reading environment variables
from google.cloud import pubsub_v1      # pip install google-cloud-pubsub  ##to install
import time                             # for sleep function
import json;                            # to deal with json objects
import sys;                             # fot exit function

# Search the current directory for the JSON file (including the Google Pub/Sub credential) 
# to set the GOOGLE_APPLICATION_CREDENTIALS environment variable.
files=glob.glob("*.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=files[0];

# Get the environment variables to set the crossponding variables
project_id = os.environ["GCP_PROJECT"];
subscription_id = os.environ["SUB_ID"];
topic_name = os.environ["TOPIC_NAME"];

debug=True;  # change to True for debugging
if "Debug" in os.environ:  # or define it as an environment variable
    debug=True;
if debug:
    print(files[0])
    print(project_id)
    print(subscription_id)
    print(topic_name)

# create a publisher and get the topic path for the publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)

# The callback function for handling received messages
def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    # Make sure that the global variables are accessed from within the function.
    global publisher, topic_path
    # get the message content
    message_data = json.loads(message.data)
   
    if debug:
        print(f"Received {message_data}.")
    
    if message_data["temperature"] != None and message_data["humidity"] != None and message_data["pressure"] != None:
        print("publish")
        future = publisher.publish(topic_path, message.data, function="filtered");
    else:
        print("fail")
    # Report To Google Pub/Sub the successful processed of the received messages
    message.ack()
    
# create a subscriber to the subscriber for the project using the subscription_id
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)
sub_filter = "attributes.function=\"raw\""  # the condition used for filtering the messages to be recieved 

print(f"Listening for messages on {subscription_path}..\n")

with subscriber:
    # Create a subscription with the given ID and filter for the first time, if already not existed
    try:
        subscription = subscriber.create_subscription(
            request={"name": subscription_path, "topic": topic_path, "filter": sub_filter}
        )
    except:
        pass;
    
    # Now, the subscription is already existing or has been created. 
    # The call back function will be called for each message match the filter from the topic.
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    try:
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()
