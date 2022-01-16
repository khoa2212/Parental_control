import os
import mysql.connector
import dropbox
from dropbox.files import WriteMode
import configparser

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    port='3306',
    database='DatabaseProcess'
)
mycusor = mydb.cursor()

TOKEN = 'nEOBTK1z9mcAAAAAAAAAAXzcjPzI335QoeU3smHTig80igxXAIN3nRFnixwGqDUI'
dbx = dropbox.Dropbox(TOKEN)

#Dropbox helper func
def upload(file, des):
    with open(file, 'rb') as f:
        dbx.files_upload(f.read(), des, mode=WriteMode('overwrite'))


def download(src, des, rev=None):
    dbx.files_download_to_file(des, src, rev)
#=====


def getData():
    mycusor.execute('select ID, Time_format(StartTime, "%H:%i") , Time_format(EndTime, "%H:%i") from ManageTime')
    data = mycusor.fetchall()
    return data
#======

# Đọc file config trên dropbox
def readConfig():
    download("/config.cfg", "config.cfg")
    config = configparser.ConfigParser()
    config.read('config.cfg')
    return config


#Lấy danh sách khoảng thời gian được dùng của trẻ
def getTimeSet():
    data = getData()
    print(f'ID \t Start time: \t End time:')
    for timeset in data:
        print(f'{timeset[0]} \t {timeset[1].ljust(11," ")} \t {timeset[2]}')

#Thay đổi khoàng thời gian dùng của trẻ
def ChangeTimeSet():
    config = readConfig()
    if config.getboolean('PARENT','edit'): #database đang được chỉnh sửa
        print(f'Database is being edited by someone else \n Please try again later! ')
    else:
        config.set('PARENT','edit','true')
        with open('config.cfg', 'w') as config_file:
            config.write(config_file)
        upload('config.cfg', '/config.cfg')
        

        ID = input('Enter time ID:')
        start = input('Enter start time:')
        end = input('Enter end time:')
        sql = f"UPDATE ManageTime SET StartTime = '{start}', EndTime = '{end}' WHERE ID = '{ID}'"
        mycusor.execute(sql)
        mydb.commit()

        config = readConfig()
        config.set('PARENT','edit','false')
        with open('config.cfg', 'w') as config_file:
            config.write(config_file)

        upload('config.cfg', '/config.cfg')


#Lấy lịch sử sử dụng máy của trẻ
def GetLogFile():
    download("/upload.txt", "KeyLog.txt")
    f = open("KeyLog.txt", "r")
    data = f.readlines()
    f.close()
    return data
    

if __name__=='__main__':
    while True:
        print("1. Print list time set")
        print("2. Update time set ")
        print("3. Print keyboard log")
        option = int(input("Opion:"))
        if option == 1:
            getTimeSet()
        elif option == 2:
            ChangeTimeSet()
        elif option == 3:
            log = GetLogFile()
            for line in log:
                print(line)
            os.system('pause')
        else:
            print("invalid input")
            os.system('pause')
            os.system('cls')
            
        