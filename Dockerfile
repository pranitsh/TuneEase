FROM python:3.9

# Set the working directory in the container
WORKDIR /backend

# Install requirements.txt
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install Flatpak and add Flathub repository
RUN apt-get update && \
    apt-get install -y flatpak && \
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
RUN flatpak install -y flathub org.musescore.MuseScore

RUN flatpak install -y flathub org.musescore.MuseScore

RUN wget https://onedrive.live.com/download?resid=CF5CD532C7BDCDB1%212273&authkey=!AOXAcumYZkpQjn4"

# Expose a port from the container to the host
EXPOSE 8080
ENV COMMON_PORT=8080

# Run the following when started
CMD ["python", "server.py"]
