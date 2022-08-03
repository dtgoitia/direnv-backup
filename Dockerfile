FROM archlinux:base-devel-20220724.0.70393 as base

RUN pacman -Syu --noconfirm \
  python \
  python-pip \
  gnupg \
  fish

# TODO: this should perhaps go above the package installations
ENV USER=rootless
ENV USERPASSWORD=123

RUN useradd $USER
RUN echo "$USER ALL=(ALL:ALL) NOPASSWD: ALL" >> /etc/sudoers
#              ^ this is a tab
RUN echo $USER:$USERPASSWORD | chpasswd
RUN mkdir -p /home/$USER
RUN chown $USER: /home/$USER
ENV PATH="${PATH}:/home/${USER}/.local/bin"
USER $USER

ENV PYTHONUNBUFFERED 1

WORKDIR /app

FROM base as test
COPY ./requirements/dev.txt .
RUN pip install --upgrade pip \
  && pip install -r dev.txt \
  && rm dev.txt
