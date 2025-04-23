# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.core.exceptions import ValidationError


class AiQa(models.Model):
    qa_id = models.CharField(primary_key=True, max_length=10)
    user = models.ForeignKey('User', models.DO_NOTHING, null=True)
    qa_content = models.CharField(max_length=1000)
    create_time = models.DateTimeField()
    answers = models.CharField(max_length=2000, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ai_qa'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DocComment(models.Model):
    comment_id = models.CharField(primary_key=True, max_length=10)
    doc = models.ForeignKey('Document', models.DO_NOTHING, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING, null=True)
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    comment = models.CharField(max_length=50)
    create_time = models.DateTimeField()
    status = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'doc_comment'


class DocUserAction(models.Model):
    action_id = models.CharField(primary_key=True, max_length=10)
    doc = models.ForeignKey('Document', models.DO_NOTHING, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING, null=True)
    action_type = models.CharField(max_length=2)
    create_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'doc_user_action'


class Document(models.Model):
    doc_id = models.CharField(primary_key=True, max_length=10)
    doc_type = models.CharField(max_length=2)
    post_user = models.ForeignKey('User', models.DO_NOTHING, null=True)
    title = models.CharField(max_length=20)
    summary = models.CharField(max_length=30, blank=True, null=True)
    text = models.CharField(max_length=1000, blank=True, null=True)
    image_url = models.CharField(max_length=20, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        managed = True
        db_table = 'document'

class SleepChallenge(models.Model):
    challenge_id = models.CharField(primary_key=True, max_length=10, default='1000000000')
    challenge_title = models.CharField(max_length=50)
    initiator = models.ForeignKey('User', models.DO_NOTHING)
    create_time = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'sleep_challenge'

    def __str__(self):
        return self.challenge_title

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("结束日期不能早于开始日期")


class SleepRecord(models.Model):
    record_id = models.CharField(primary_key=True, max_length=15)
    user = models.ForeignKey('User', models.DO_NOTHING, null=True)
    record_time = models.DateTimeField()
    sleep_time = models.DateTimeField()
    wake_time = models.DateTimeField()
    rating = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sleep_record'


class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=10)
    phone_number = models.CharField(unique=True, max_length=20)
    password = models.CharField(max_length=255)
    user_name = models.CharField(max_length=20, blank=True, null=True, db_comment='默认值需应用层设置为phone_number')
    age = models.IntegerField(blank=True, null=True)
    user_type = models.CharField(max_length=2)
    gender = models.CharField(max_length=2, blank=True, null=True, db_comment='0:男,1:女,2:其他')
    tag = models.CharField(max_length=10, blank=True, null=True)
    description = models.CharField(max_length=40, blank=True, null=True)
    birthday = models.DateTimeField(blank=True, null=True)
    email = models.CharField(unique=True, max_length=20, blank=True, null=True)
    sleep_notice = models.CharField(max_length=8, blank=True, null=True)
    wake_notice = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'user'


class UserChallenge(models.Model):
    id = models.CharField(primary_key=True, max_length=20, default='1000000000')
    user = models.ForeignKey(User, models.DO_NOTHING)
    challenge = models.ForeignKey(SleepChallenge, models.DO_NOTHING)
    join_time = models.DateTimeField(auto_now_add=True)
    completed_days = models.IntegerField(default=0)

    class Meta:
        managed = True
        db_table = 'user_challenge'
        unique_together = (('user', 'challenge'),)

class ChallengeCheckIn(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, default=1000000000)
    user_challenge = models.ForeignKey(UserChallenge, models.DO_NOTHING)
    checkin_date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'challenge_checkin'
        unique_together = (('user_challenge', 'checkin_date'),)

    def clean(self):
        challenge = self.user_challenge.challenge
        if self.checkin_date < challenge.start_date or self.checkin_date > challenge.end_date:
            raise ValidationError("打卡日期必须在挑战有效期内")

class SleepGroup(models.Model):
    group_id = models.CharField(primary_key=True, max_length=10)
    group_name = models.CharField(max_length=50)
    owner = models.ForeignKey('User', models.DO_NOTHING)
    description = models.CharField(max_length=200, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2, default='1')  # 1-active, 0-inactive
    avatar = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sleep_group'

class UserGroup(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey('SleepGroup', models.DO_NOTHING)
    member = models.ForeignKey('User', models.DO_NOTHING)
    join_time = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=2, default='0')  # 0-member, 1-admin

    class Meta:
        managed = True
        db_table = 'user_group'
        unique_together = (('group', 'member'),)

class ChatHistory(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey('SleepGroup', models.DO_NOTHING)
    member = models.ForeignKey('User', models.DO_NOTHING)
    content = models.TextField()
    msg_type = models.CharField(max_length=2, default='0')  # 0-text, 1-image, 2-link
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'chat_history'
