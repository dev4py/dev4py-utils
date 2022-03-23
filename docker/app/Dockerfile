FROM python:alpine
WORKDIR /app

ARG wheel_name
ARG entrypoint="python"
ARG cmd

RUN : "${wheel_name:?'wheel_name' build-arg is required}"

COPY dist/${wheel_name} .

RUN pip install -qq ${wheel_name}

RUN rm -f ${wheel_name}

ENV COMMAND ${cmd}
ENV ENTRYPOINT ${entrypoint}
ENTRYPOINT ["sh", "-c", "eval ${ENTRYPOINT} $@", "-s"]
CMD ["${COMMAND}"]
