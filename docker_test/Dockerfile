# Import Python runtime and set up working directory
FROM python:2.7-slim
WORKDIR /app
COPY . /app

# Install any necessary dependencies
RUN pip install -r requirements.txt

# Open port 5000 for serving the webpage
EXPOSE 5000

# set up the environmental variables
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/cc-isv-02ae247345db.json"

# Run app.py when the container launches
CMD ["python", "video_search.py"]
