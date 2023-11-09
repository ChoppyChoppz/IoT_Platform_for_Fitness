# IoT_Platform_for_Fitness
An IoT project that aims to provide services for fitness management, weight loss and healthy lifestyle. Project carried out for the "Programming for IoT applications" course at the Politecnico di Torino, Italy.

The solution proposed aims to improve the lifestyle of athletes and people with weight and therefore health problems. It integrates different IoT devices to monitor a person's vital parameters in any kind of environment like gym or home. The overall platform provides unified interfaces (through both REST and MQTT) to integrate sensors to everyday life. Finally, the platform provides end-users with detailed knowledge of the calories and the weight trend. 

Summarizing, the main features it offers are:  
• remote control of health signals; 

• unified interfaces (i.e. REST Web Services and MQTT queues); 

• end-user applications for self-awareness, carried out via telegram bot

Two videos were made to sponsor the service and explain to the user how it works.

[VIDEO PROMO](https://www.youtube.com/watch?v=aDHM0BEvmKE&t=3s&ab_channel=IoTProject_Group23)

[VIDEO DEMO](https://www.youtube.com/watch?v=ZF9cDwG5808&ab_channel=IoTProject_Group23)


In this context, these actors have been identified and introduced in the following: 

• The Fitness Catalog works as service and device registry system for all the actors in the system. It provides information about end-points (i.e. REST Web Services and MQTT topics) of all the devices, resources and services in the platform. It also provides configuration settings for applications and control strategies (e.g. timers and list of sensors). Each actor, during its start-up, must retrieve such information from the Fitness Catalog exploiting its REST Web Services.  

• The Raspberry Pi Connector is a Device Connector that integrates into the platform raspberry pi boards. The raspberry is connected with fitness sensors to provide information about the status of patient. It provides Rest Web Services to retrieve patient’s information (i.e. oxygenation, blood glucose, calories burned, etc). It also works as an MQTT publisher sending information of patient data.

• The Message Broker provides an asynchronous communication based on the publish/subscribe approach. It exploits the MQTT protocol.

• The Data Analysis is an algorithm that allows to process patient measurements to get daily, weekly, or monthly statistics.

• The Patient Alarm is an algorithm that allows to monitor the patient and detect abnormal values. 

• The Patient Training is an algorithm that compares different parameters trend (about calories burned, distance travelled, etc) to analyse patient’s performance during the week and communicate 
his results (i.e. training score).

• The Thingspeak Adaptor is an MQTT subscriber that receives measurements on wellness measurements and upload them on Thingspeak through REST Web Services. 

• Thingspeak is a third-party software (https://thingspeak.com/) that provides REST Web Services. It is an open-data platform for the Internet of Things to store and visualize data (through plots). 
 
• Telegram Bot is a service to integrate the proposed infrastructure into Telegram platform, which is a cloud-based instant messaging infrastructure. It retrieves measurements from IoT devicesv exploiting the subscription to Message Broker. It also speaks with Thingspeak and the Catalog through REST Web Services. 

A complete use-case diagram can be viewed [Here](use-case-diagram.png)

