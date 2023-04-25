FROM python:3.9-slim
COPY requirements.txt ./requirements.txt
COPY ./DashApp/ /DashApp/
COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt
RUN pip install openpyxl
RUN pip install gunicorn
COPY . ./
EXPOSE 8050
CMD ["python", "DashApp/population.py"]