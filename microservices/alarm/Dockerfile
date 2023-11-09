# set the kernel to use
FROM python:3.10
# copy the requirements file
COPY requirements.txt ./
# install the needed requirements
RUN pip3 install -r requirements.txt
# copy the all the file in the container
COPY . .
# the command that will be executed when the container will start
CMD ["python3","-u", "alarm.py"]
