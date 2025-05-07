from django.db import models


# Create your models here.

class Sample(models.Model):
    sample_id = models.AutoField(primary_key=True)
    name = models.CharField('姓名', max_length=50, null=False)
    number = models.IntegerField('number', default=1)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'sample'  # 定义表名
        ordering = ['-sample_id']  # 按sample_id倒序排序

    def __unicode__(self):
        return '%s' % self.name

    def __str__(self):
        return self.__unicode__()
