from django.db import models
import os
class UsersModel(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=100)
    profile = models.FileField(upload_to=os.path.join('static', 'userprofiles'))
    status=models.CharField(max_length=100,default='pending')
    

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = "UsersModel"



class A_Cloud(models.Model):
    file = models.FileField(upload_to=os.path.join('static', 'EncryptedFiles'))
    filename = models.CharField(max_length=100)
    email=models.EmailField()
    key = models.BinaryField()
    filedata= models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=100,default='Encrypted')

    def __str__(self):
        return self.filename
    class Meta:
        db_table = "A_Cloud"


class B_Cloud(models.Model):
    cloud = models.ForeignKey(A_Cloud, on_delete=models.CASCADE)
    filedata= models.TextField()

    def __str__(self):
        return self.filedata
    class Meta:
        db_table = "B_Cloud"



class DecryptModel(models.Model):
    data = models.ForeignKey(B_Cloud,on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=100,default='Decrypted')
    decrypted_data = models.TextField(null=True)

    def __str__(self):
        return self.data
    class Meta:
        db_table = "DecryptModel"