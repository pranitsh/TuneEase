FROM python:3.9

WORKDIR /app
COPY . /app

RUN apt-get update && apt install -y libfuse2 fuse3 libgl1-mesa-glx
RUN apt-get update && apt-get install -y qtwayland5 jackd qjackctl
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir temp && cd temp
RUN wget https://cdn.jsdelivr.net/musescore/v4.1.1/MuseScore-4.1.1.232071203-x86_64.AppImage -O "MuseScore.AppImage"
RUN chmod +x ./MuseScore.AppImage && cd ..

RUN wget -O 'checkpoint.pth' 'https://1drv.ms/u/s!ArHNvccy1VzPkWGKXZDQY5k-kDi4?e=fFxcEq'

# Expose a port from the container to the host
EXPOSE 8080
ENV COMMON_PORT=8080

# Run the following when started
CMD ["python", "-m", "tuneease.server"]