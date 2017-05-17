#
# Image for project.
#
FROM python:3.5

MAINTAINER Mike McConnell

EXPOSE 8080


# Set-up installation
COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt
COPY . /tmp/


# Add source
RUN mkdir -p /ticketer-dist/ticketer
ADD . /ticketer-dist/ticketer
RUN mv /ticketer-dist/ticketer/setup.py /ticketer-dist/


# Install source -- basic setup.py
RUN cd /ticketer-dist &&\
    python setup.py build &&\
    python setup.py install


# Default command
CMD ["python"]
