FROM archlinux:base-devel-20220724.0.70393

RUN pacman -Syu gnupg fish --noconfirm
RUN pacman -Syu python python-pip --noconfirm

ENV USER=rootless

RUN useradd $USER
# RUN echo "$USER ALL=(ALL:ALL) ALL" >> /etc/sudoers
RUN echo "$USER ALL=(ALL:ALL) NOPASSWD: ALL" >> /etc/sudoers
#              ^ this is a tab
RUN echo $USER:123 | chpasswd
RUN mkdir -p /home/$USER
RUN chown $USER: /home/$USER
ENV PATH="${PATH}:/home/${USER}/.local/bin"
USER $USER

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Dev dependencies are not required, because this script must have zero dependencies
# COPY ./requirements /requirements
# RUN pip install -r /requirements/dev.txt
