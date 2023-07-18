#
# Building a Docker Image with
# the Latest Ubuntu Version and
# Basic Python Install
#
# Python for Finance, 2nd ed.
# (c) Dr. Yves J. Hilpisch
#
# latest Ubuntu version
FROM ubuntu:latest
# information about maintainer
LABEL Author SylvainC

# add the bash script
ADD ./Script/install.sh /
COPY ./Script/* ./Script/
COPY ./Config/Requirements.txt .
COPY ./Sources/*.py ./Sources/

RUN mkdir ./Config/
RUN mkdir ./Output/

# change rights for the script
RUN chmod u+x /install.sh

# run the bash script
RUN ./install.sh

# prepend the new path
ENV PATH /root/miniconda3/bin:$PATH

RUN mv ./Requirements.txt ./Config/Requirements.txt

# execute IPython when container is run
CMD ["python", "./Sources/BotInfrastructure.py"]