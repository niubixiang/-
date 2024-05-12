#导入相关模块
import pymssql         #后台数据库
import easygui as g    #界面化操作easygui
import random          #随机数操作
import time            #时间操作
import datetime        #时间对象操作
db=pymssql.connect(server='computer',user='hyx',password='123',database='Library') #连接数据库,服务器名，用户名，密码，操作的数据库
cursor=db.cursor(as_dict=True)   #as_dict返回的是布尔类型，如果是True则是dict字典，如果是false则是元组
db.autocommit(True) #设置立即操作
#各种命令操作
uname=[]       #创建一个用户列表存储客户信息表里的的用户
passwd=[]      #创建一个密码列表存储客户信息表里的的密码
borrow_user=[] #创建一个借书用户空列表存储出租表里的用户
#封装注册函数
#判断注册成不成功取决于账号是否存在或是否为空，以及密码是否为空
def zhuce():
    un = g.enterbox('请输入账号')
    cursor.execute("select * from 客户信息表")
    al = cursor.fetchall()
    for i in al:
        uname.append(i['user_name'])  #客户信息表里的的用户存储进uname列表
        passwd.append(i['password'])  #客户信息表里的的密码存储进passwd列表
    while 1:
        if un in uname:
            un = g.enterbox('该账号已存在请重新输入')
        elif un == '':
            un = g.enterbox('账号不能为空，请重新输入')
        else:
            g.msgbox('账号创建成功')
            pwd = g.enterbox('请输入密码')
            while 1:
                if pwd == '':
                    pwd = g.enterbox('密码不能为空！！！,请再次输入')
                else:
                    pwd2 = g.enterbox('请再次输入密码')
                    if pwd2 != pwd:
                        g.msgbox('两次密码不一致，请重新输入')
                    else:
                        sql = "insert into 客户信息表(user_name,password) values (%s,%s)"
                        cursor.executemany(sql, [(un, pwd)])
                        g.msgbox('注册成功')
                        break
            break
#封装借书函数
def jieshu(book_name,un,borrow):
    cursor.execute("select *from 出租表")
    number = []
    for qq in cursor.fetchall():
        number.append(qq['单号'])   #出租表里的单号存储进number列表
    print(number)  #控制台输出便于查看测试
    while 1:
        num = random.randint(1,1000)   #随机函数用于随机生成单号
        if num in number:
            g.msgbox('改单号已被使用(将重新生成随机单号)')  #判断随机生成的单号是否在使用，出租表里的单号是主键唯一标识，不可重复
        else:
            #这里执行else语句是借书成功后才能录入后台sql中的出租表的租金字段
            sql = "insert into 出租表(单号,书号,user_name,借出时间) values (%s,%s,%s,%s)"
            cursor.executemany(sql, [(num, book_name, un, borrow)])
            g.msgbox(f"生成订单信息:\n借书单号为{num}\n用户:{un}\n借书时间:{borrow}",image='images/5.jpeg')
            g.msgbox('借书成功',image='images/哈哈.jpeg')
            break
#封装还书函数
def huanshu(un):
    cursor.execute("select * from 出租表")
    lu = cursor.fetchall()
    for j in lu:
        borrow_user.append(j['user_name'])  #出租表里的用户存储进borrow_user列表
    if un not in borrow_user:
        g.msgbox('您还没借书',image='images/1.jpeg') #有借才有还
    else:
        cursor.execute("select * from 出租表 where user_name='" + un + "'")
        nums=[]
        for nu in cursor.fetchall():
            nums.append(nu['单号'])  #存储的是本次登录用户的所有单号（注意：不是出租表里所有的单号）
        print(nums) #控制台输出测试查看
        while 1:
            count=int(g.enterbox('请输入单号'))
            if count in nums:
                cursor.execute(f"select * from 出租表 where 单号={count}")
                #首先还书可以根据租金是否为空判断是否需要还书（为空表明需要还书）
                pr=cursor.fetchone()['租金']
                if pr is None:
                    while 1:
                        end_time = g.enterbox('请输入结束时间', '格式为（xxxx-xx-xx 00:00:00）')
                        #异常处理
                        try:
                            sql = "update 出租表 set 结束时间 =%s where 单号 =%s"
                            cursor.executemany(sql, [(end_time, count)])
                            cursor.execute("select * from 出租表")
                            #下面语句已成功将算出的借出天数录入后台出租表
                            cursor.execute("update 出租表 set 借出天数 = (select DATEDIFF(DAY, 借出时间, 结束时间))")
                            cursor.execute(f"select * from 出租表 where 单号= {count}")
                            start_time=cursor.fetchone()['借出时间']
                            en=str(end_time)  #由于下面语句用到strptime（）方法则需要强制转换为str
                            st=str(start_time)
                            # strptime()方法将一个时间字符串解析为时间的一个类型对象
                            # strptime(string, format)将时间字符串根据指定的格式化符转换成数组形式的时间
                            # datetime.strptime(date_string, format)：将格式字符串转换为datetime对象
                            # datetime.datetime：表示日期时间。
                            start = datetime.datetime.strptime(st, "%Y-%m-%d %H:%M:%S")
                            end = datetime.datetime.strptime(en, "%Y-%m-%d %H:%M:%S")
                            data = end - start  #这里返回的是天数小时分钟秒
                            days = (end - start).days  #返回的是天数
                            try:
                                hour = str(data).split(',')[1].split(':')[0].replace(' ', '')  #split分割函数，replace替换
                                h=days*24+int(hour)  #算出小时数
                            except:
                                hour=str(data).split(':')[0]
                                h=int(hour)
                            # 首先以出租表里的单号为判断条件查询出对应的书号
                            cursor.execute(f"select * from 出租表 where 单号={count}")
                            shu = cursor.fetchone()['书号']
                            # 根据以上出租表查询出的书号为判断条件查询书价表里面书号对应的单价
                            cursor.execute("select * from 书价表 where 书号='" + shu + "'")
                            price = cursor.fetchone()['单价']
                            total_price = price/24*h
                            total=round(total_price,2)  #运用round函数保留2位
                            g.msgbox(f"应付租金为{total}", image='images/money.jpeg')
                            p = "update 出租表 set 租金 =%s where 单号 =%s"
                            cursor.executemany(p, [(total, count)]) #将结算的租金运用update更新（租金先前是null）插入后台出租表（以指定的单号为条件）
                            break
                        except:
                            g.msgbox('日期格式不符合!!')
                    break
                else:
                    rels=g.buttonbox('该订单已还','是否退出',choices=('是','否'),images='images/3.jpeg')
                    if rels=='是':
                        g.msgbox('你走吧',image='images/2.jpeg')
                        g.msgbox('正在退出',image='images/tui.gif')
                        break
                    else:
                        continue
            else:
                g.msgbox('该单号不正确或不存在')
                we=g.buttonbox('是否退出',choices=("是","否"))
                if we=='是':
                    g.msgbox('你走吧',image='images/2.jpeg')
                    g.msgbox('正在退出', image='images/tui.gif')
                    break
                else:
                    continue
#封装查询函数
def chaxun(un):
    #查询可以先判断该用户是否存在出租表，接着在判断该单号是否与该用户匹配
    cursor.execute("select * from 出租表")
    lu = cursor.fetchall()
    for j in lu:
        borrow_user.append(j['user_name'])
    if un not in borrow_user:
        g.msgbox('您没有订单信息')
    else:
        while 1:
            cursor.execute("select * from 出租表 where user_name='"+un+"'")
            numbers=[]  #创建一个存放本用户的所有单号
            for w in cursor.fetchall():
                numbers.append(w['单号'])
            print(numbers)#控制台输出测试语句
            nm = int(g.enterbox('请输入订单号'))
            if nm not in numbers:
                g.msgbox('不好意思！！该单号不匹配!!!')  #查询订单信息只能自己查自己的，或者是该单号是否正确
            else:
                cursor.execute(f"select * from 出租表 where 单号={nm}")
                m = cursor.fetchone()
                g.msgbox(f"订单信息如下:\n{m}",image='images/5.jpeg')
                k=g.buttonbox('是否需要退出',choices=('是','否'),images='images/3.jpeg')
                if k=='是':
                    g.msgbox('你走吧',image='images/2.jpeg')
                    g.msgbox('正在退出', '欢迎下次登录', image='images/tui.gif')
                    break
                else:
                    continue
while 1:
    ret=g.buttonbox('欢迎来到图书馆租赁系统','系统提示',choices=('注册','登录'),images='images/book.jpeg')
    #注册
    if ret=='注册':
        zhuce()  # 调用注册函数
    #登录
    #登录成功取决于账号是否注册，密码是否正确
    else:
        cursor.execute("select * from 客户信息表")
        al = cursor.fetchall()
        for i in al:
            uname.append(i['user_name'])  #客户信息表里的的用户存储进uname列表
            passwd.append(i['password'])  #客户信息表里的的密码存储进passwd列表
        while 1:
            un = g.enterbox('请输入账号名')
            if un in uname:
                while 1:
                    pwd=g.passwordbox('请输入密码')
                    #这里注意捋清思路，根据客户信息表里的数据，要想登录成功需要登录名与密码一一对应，
                    # 这也是前面为什么把user_name与password存入列表的理由，这里需判断uname列表与passwd列表的里面每个数据一一对应的索引号是否一致即可
                    # index()是返回列表索引号的函数 用法list.index(obj)
                    # index()函数用于从列表中找出某个值第一个匹配项的索引位置。
                    ind=uname.index(un)
                    pw=passwd[ind]
                    if pwd==pw:
                        g.msgbox('登录成功')
                        rel=g.buttonbox('您是否需要进入图书馆','系统提示',choices=('是','否'),images='images/book5.jpeg')
                        if rel=='是':
                            ret=g.buttonbox('欢迎进入图书馆','系统提示',choices=('借书功能','还书功能','查询订单功能'),images='images/lib.jpeg')
                            #借书功能
                            #以下借书功能为了实现点击不同书型号显示不同图片，所以使用if elif else条件判断语句进行输出
                            if ret=='借书功能':
                                book_name = g.buttonbox('请选择书型号', '系统提示', choices=('报纸', '外语小说', '杂志', '中文小说'),images='images/jieshu.jpeg')
                                if book_name == '报纸':
                                    while 1:
                                        borrow = g.enterbox('请输入借出时间', '格式为（xxxx-xx-xx 00:00:00）', image='images/报纸.jpeg')
                                        #异常处理处理时间格式
                                        # 由于出租表中的时间类型为datetime
                                        # 异常处理判断输入的借出时间是否符合格式为（xxxx-xx-xx 00:00:00）如果try语句无异常,则程序继续执行,
                                        try:
                                            time.strptime(borrow,"%Y-%m-%d %H:%M:%S")
                                            jieshu(book_name, un, borrow)  # 调用借书函数
                                            break
                                        except:
                                            g.msgbox('不是有效日期')
                                elif book_name == '外语小说':
                                    while 1:
                                        borrow = g.enterbox('请输入借出时间', '格式为（xxxx-xx-xx 00:00:00）',image='images/外语小说.jpeg')
                                        try:
                                            time.strptime(borrow, "%Y-%m-%d %H:%M:%S")
                                            jieshu(book_name, un, borrow)  # 调用借书函数
                                            break
                                        except:
                                            g.msgbox('不是有效日期')
                                elif book_name == '杂志':
                                    while 1:
                                        borrow = g.enterbox('请输入借出时间', '格式为（xxxx-xx-xx 00:00:00）',image='images/杂志.jpeg')
                                        try:
                                            time.strptime(borrow, "%Y-%m-%d %H:%M:%S")
                                            jieshu(book_name, un, borrow)  # 调用借书函数
                                            break
                                        except:
                                            g.msgbox('不是有效日期')
                                else:
                                    while 1:
                                        borrow = g.enterbox('请输入借出时间', '格式为（xxxx-xx-xx 00:00:00）',image='images/中文小说.jpeg')
                                        try:
                                            time.strptime(borrow, "%Y-%m-%d %H:%M:%S")
                                            jieshu(book_name, un, borrow)  #调用借书函数
                                            break
                                        except:
                                            g.msgbox('不是有效日期')
                            #还书功能
                            elif ret=='还书功能':
                                huanshu(un)   #调用还书函数
                            #查询订单
                            else:
                                chaxun(un)    #调用查询函数
                            break
                        else:
                            break
                    else:
                        g.msgbox('密码错误')
                break
            else:
                msg=g.buttonbox('账号不存在（该账号可能没注册过）是否退出',choices=('是','否'))
                if msg=='是':
                    g.msgbox('正在退出', '欢迎下次登录', image='images/tui.gif')
                    break
                else:
                    g.msgbox('请准确无误输入账号名')
                    continue
#关闭游标与数据库连接
cursor.close()
db.close()
