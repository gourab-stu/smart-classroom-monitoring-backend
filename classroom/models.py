from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

import datetime

# Create your models here.


class Stream(models.Model):
    STREAM_NAME_ARTS = "A"
    STREAM_NAME_ARTS = "Sc"

    stream_name = models.CharField(max_length=255, unique=True)
    stream_code = models.CharField(max_length=255, unique=True)


class Subject(models.Model):
    name = models.CharField(max_length=255)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)
    code = models.CharField(max_length=255)


class Paper(models.Model):
    paper_code = models.CharField(max_length=255, unique=True)
    paper_title = models.CharField(max_length=255)
    paper_type = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(8)
        ]
    )

    class Meta:
        unique_together = [["paper_title", "paper_type"]]


class Course(models.Model):
    degree_name = models.CharField(max_length=255, unique=True)
    degree_type = models.CharField(max_length=255, unique=True)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, null=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = [["degree_name", "degree_type", "stream", "subject"]]


class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)


class Classroom(models.Model):
    name = models.CharField(max_length=255)
    semester = models.PositiveSmallIntegerField()


class Student(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    reg_no = models.CharField(max_length=255, unique=True)
    picture_url = models.TextField(unique=True)
    admission_year = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(2023),
            MaxValueValidator(datetime.date.today().year),
        ]
    )
    stream = models.
