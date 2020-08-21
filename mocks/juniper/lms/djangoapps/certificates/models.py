
from __future__ import absolute_import
from django.db import models
from django.contrib.auth.models import User

from openedx.core.djangoapps.xmodule_django.models import CourseKeyField

class GeneratedCertificate(models.Model):
    # TODO: Review the most appropriate on_delete behaviour
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = CourseKeyField(max_length=255, blank=True, default=None)
    created_date = models.DateTimeField()