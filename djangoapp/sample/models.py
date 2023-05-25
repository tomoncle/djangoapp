# Create your models here.
from django.db import models
from datetime import datetime
from ..common import T


class Sample(models.Model, T):
    smp_id = models.AutoField(primary_key=True)  # pk
    name = models.CharField(max_length=50, null=False)
    description = models.TextField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'test_sample'  # 定义表名
        ordering = ['-smp_id']  # 按 smp_id 倒序排序

    def __unicode__(self):
        return '%s' % self.name

    def __str__(self):
        return self.__unicode__()

    def to_dict(self):
        d = super(Sample, self).to_dict()
        for k, v in d.items():
            if isinstance(v, datetime):
                d[k] = '{v}'.format(v=v)
        return d
