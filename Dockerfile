#
# Image for project.
#
FROM alpine:3.6

MAINTAINER Mike McConnell

EXPOSE 8080


# Run update.
RUN apk add --update python py-pip

# Set-up installation
COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt
COPY . /tmp/


# Add source
RUN mkdir -p /tickets-dist/tickets
ADD . /tickets-dist/tickets
RUN mv /tickets-dist/tickets/setup.py /tickets-dist/


# Install source -- basic setup.py
RUN cd /tickets-dist &&\
    python setup.py build &&\
    python setup.py install


# Default command
CMD ["python"]
