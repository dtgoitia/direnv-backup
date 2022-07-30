FROM archlinux:base-devel-20220724.0.70393

RUN pacman -Syu gnupg fish --noconfirm
RUN pacman -Syu python --noconfirm

ENV USER=rootless

RUN useradd $USER
RUN echo "$USER ALL=(ALL:ALL) ALL" >> /etc/sudoers
#              ^ this is a tab
RUN echo $USER:123 | chpasswd
RUN mkdir -p /home/$USER
RUN chown $USER: /home/$USER
USER $USER

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Dev dependencies are not required, because this script must have zero dependencies
# COPY ./requirements /requirements
# RUN pip install -r /requirements/dev.txt
