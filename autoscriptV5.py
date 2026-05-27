import random
import sys
import time
import keyboard
import pyautogui
import threading
import pywinctl as pwc              #检测窗口
from PIL import Image               #导入图片
import cv2                          #图形识别、模版匹配
import os.path                      #检测文件名是否被占用
import PySimpleGUI as sg            #用于创建图形界面
import ctypes                       #用于生成鼠标连续移动
from ctypes import wintypes         #用于生成鼠标连续移动
import numpy as np

#————————————————————UI界面——————————————————
turntime = 0
gotime = 0
reloadtime = 4
shoot_round = 1
windowIsAnchored = True
speed = 0
menu =  "此智驾系统源自战争雷霆苹果派助手，\n"\
        "由 Adobe_Hit_乐 改进\n" \
        "▶图像设定：\n分辨率：1270x720"\
        "显示模式：窗口模式\nUI大小：100%\n" \
        "▶主要参数->海战设置：\nAI攻击模式：任意目标  自动锁定目标：开\n" \
        "▶按键设置->海战：     \n" \
        "目标跟踪（海战）：=     \n"\
        "手动瞄准修正： ；      \n"\
        "停车：b               \n" \
        "海战瞄准控制X轴：增加数值：]，减少数值：[\n" \
        "视角缩放：鼠标右键\n" \
        "请只派遣一条船参加海战历史模式\n"

sg.theme('Reddit')

updateLog = [
    [sg.Text("人生多么美好\n何不采用智驾减少路上的疲劳？", key="-log-")]]

layout = [[sg.Text(menu)],
        [sg.Button("驱逐"), sg.VSeperator(), sg.Button("轻巡"), sg.VSeperator(), sg.Button("重巡"), sg.VSeperator(), sg.Button("停止并退出")],
        [sg.Text("turntime"),sg.Input(default_text=turntime, key='-VAR_t-', size=(5,1)), sg.Button("读取_t")],
        [sg.Text("gotime"),sg.Input(default_text=gotime, key='-VAR_g-', size=(5,1)), sg.Button("读取_g")],
        [sg.Text("reloadtime"),sg.Input(default_text=reloadtime, key='-VAR_r-', size=(5,1)), sg.Button("读取_r")],
        [sg.Text("shoot_round"),sg.Input(default_text=shoot_round, key='-VAR_sr-', size=(5,1)), sg.Button("读取_sr")],
        [sg.Text("speed"),sg.Input(default_text=speed, key='-VAR_sp-', size=(5,1)), sg.Button("读取_sp")]]
          
#——————————————————————————————————————————————————————



#————————————————在游戏中生成鼠标移动————————————————————
# Windows API 常量
INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000

sensibility_x=0.7
sensibility_y=0.7

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    ]

class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("mi", MOUSEINPUT)]

def send_input_mouse(dx, dy, absolute=False):
    """
    使用 SendInput 发送底层鼠标输入
    absolute=True 时，dx/dy 是 0-65535 的绝对坐标
    """
    flags = MOUSEEVENTF_MOVE
    if absolute:
        flags |= MOUSEEVENTF_ABSOLUTE
    
    mi = MOUSEINPUT(dx, dy, 0, flags, 0, None)
    inp = INPUT(INPUT_MOUSE, mi)
    
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
#————————————————————————————————————————————————————

#鼠标点击
def click(location=None,duration=0.2):
    # click a certain location on the screen
    if location:
        pyautogui.moveTo(location[0], location[1])
    time.sleep(0.2)
    pyautogui.mouseDown(button='left')
    time.sleep(duration)
    pyautogui.mouseUp(button='left')

#键盘按键
def pressWithDelay(c, d=0.1, t=0.1):
    # press the button c, for d seconds, and wait t seconds
    keyboard.press(c)
    time.sleep(d)
    keyboard.release(c)
    time.sleep(t)

PATH = "./pic/screenshot.png"           #游戏截屏保存位置
#截屏整个游戏画面
def getScreen(window, location):
    # screenshot the current screen
    left, top = window.topleft
    right, bottom = window.bottomright
    pyautogui.screenshot(location)
    global windowIsAnchored
    if windowIsAnchored:
        img = Image.open(location)
        img = img.crop((left + 10, top, right - 10, bottom - 10))
        img.save(location)

def spamESC(times):
    for i in range(times):
        pressWithDelay('esc', 0.1, 0.5)

f = open('./battlelog/log.txt', 'a+')   #log文件
def log(message):
    # put the log in the GUI and the text log
    print(message)
    curr_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    try:
        f.write("[" + curr_time + "] " + message + "\n")
    except:
        print("出现了日志写入错误，可能是计算机之间不同编码的问题吧？")

#进行图形识别
def hasImage(name, threshold, message=None,position=PATH):
    # returns true if the current screenshot has the desired image
    wholeWindow = cv2.imread(position)
    time.sleep(0.5)
    #if not wholeWindow:time.sleep(1)
    targetImg = cv2.imread("./model/" + name + ".png")
    "start matching"
    result = cv2.matchTemplate(wholeWindow, targetImg, cv2.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print(name + "\t" + str(max_val) + str(max_loc))
    if max_val > threshold:
        return True
    else:
        if message is not None:
            log(message)
        return False

#提取图片中某种特定颜色，处理图片
def Get_Color_In_IMG(image_path, target_color=(251, 109, 108),background_colot=(255,255,255), threshold=50):
    #识别图中红色区域，非红色区域变成白色
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    width, height = img.size
    pixels = np.array(img)

    # 计算颜色距离
    target = np.array(target_color)
    diff = pixels.astype(float) - target
    distances = np.sqrt(np.sum(diff ** 2, axis=2))

    # 红色区域掩码
    mask = distances <= threshold

    # 非红色变白
    height, width = pixels.shape[:2]  # 获取尺寸（兼容灰度/RGB/RGBA）
    result = np.full((height, width, 3), background_colot, dtype=np.uint8)
    result[mask] = pixels[mask]

    result_img = Image.fromarray(result)
    try:
        result_img.save(image_path, format='PNG')
    except OSError as e:
        print(f"保存图片失败，跳过: {e}")

def getButtonLocation(name,path=PATH):
    # get the button's location
    wholeWindow = cv2.imread(path)
    targetImg = cv2.imread("./model/" + name + ".png")
    "start matching"
    height, width, channel = targetImg.shape
    result = cv2.matchTemplate(wholeWindow, targetImg, cv2.TM_SQDIFF_NORMED)
    ul = cv2.minMaxLoc(result)[2]
    lr = (ul[0] + width, ul[1] + height)
    center = (int((ul[0] + lr[0]) / 2), int((ul[1] + lr[1]) / 2))
    return center

def escapeBuying(window):
    # if a ship is researched, escape buying via the item shop
    click(getButtonLocation("researchdone"))
    time.sleep(3)
    getScreen(window, PATH)
    if hasImage("newshipresearched", 0.91, None) and not hasImage("partsdone", 0.91, None):
        click(getButtonLocation("shop"))
        getScreen(window, PATH)
        click(getButtonLocation("itemshop"))
        spamESC(3)
    partsDone(window)

def partsDone(window):
    time.sleep(1)
    getScreen(window, PATH)
    if hasImage("autoresearch", 0.92, None):
        click(getButtonLocation("autoresearch"))
        time.sleep(10)
        spamESC(5)

#行动规律：先直行然后右转巡航
def move_strategy(stop_event):
    for i in range(speed):
        pressWithDelay('w')
    time.sleep(gotime)
    pressWithDelay('d',turntime,0.1)
    for i in range(speed):
        pressWithDelay('s')

#躲避障碍：若触礁告警则紧急停船
nav_scrPATH='./pic/nav_scr.png'     #检测告警的图片单独保存
def hide_obstacles(stop_event):
    while not stop_event.is_set():
        pyautogui.screenshot(nav_scrPATH,region=(400,213,430,330))
        Get_Color_In_IMG(nav_scrPATH,(255,255,255),(0,0,0),30)
        if hasImage('obstacles',0.90,position=nav_scrPATH):
            pressWithDelay('a',5,0)
        else:
            time.sleep(5)
    
        
#检测是否已触礁
nav_agr_scrPATH='./pic/nav_agr_scr.png'
def prevent_aground(stop_event):
    while not stop_event.is_set():
        pyautogui.screenshot(nav_agr_scrPATH,region=(450,550,300,150))
        Get_Color_In_IMG(nav_agr_scrPATH,target_color=(200,30,30),threshold=100)
        if hasImage('aground',0.97,position=nav_agr_scrPATH):
            pressWithDelay('s',d=3)
            for i in range(5):
                if not stop_event.is_set():
                    time.sleep(4)
            pressWithDelay('w',d=3,t=1)
            for i in range(speed):
                pressWithDelay('s')
        for i in range(10):
            if not stop_event.is_set():
                time.sleep(4)

target_status_PATH='./pic/target_status.png'
def findtarget():
    pressWithDelay('x')
    pyautogui.screenshot(target_status_PATH,region=(90,173,80,80))
    Get_Color_In_IMG(image_path=target_status_PATH,target_color=(255,20,30),threshold=100)
    if hasImage('reddot', threshold=0.93, position=target_status_PATH ):
        pressWithDelay('=')
        return True
    else:
        pressWithDelay(']',0.6,0.1)
        return False

#截屏左上角坐标、长度高度
x00,y00,x01,y01=356,385,544,18
#准心位置
x0,y0=643,395
aim_PATH='./pic/aim_scr.png'

def attackPattern():
    pressWithDelay('x')
    # open fire at the enemy
    pressWithDelay(';')
    pressWithDelay('=')
    send_input_mouse(int(30*(random.random()-0.5)),15+int(15*random.random()))
    pyautogui.screenshot(aim_PATH,region=(x00,y00,x01,y01))
    Get_Color_In_IMG(aim_PATH)
    if hasImage( 'v_red_only' , threshold=0.993,position=aim_PATH):
        x1,y1=getButtonLocation('v_red_only',path=aim_PATH)
        #print('v at',x1+x00,y1+y00)
        #print('pos ',x0,y0)
        send_input_mouse(int((x1+x00-x0)/sensibility_x),int((y1+y00-y0)/sensibility_y))
        time.sleep(1)
        click()
        click()
        for _ in range(shoot_round-1):
            time.sleep(reloadtime)
            click()
            click()
        send_input_mouse(-int((x1+x00-x0)/sensibility_x),-int((y1+y00-y0)/sensibility_y))
        time.sleep(reloadtime-3)
    else:
        click()
        click()
        time.sleep(10)
    
    pressWithDelay(';')

def saveResults(window, times):
    # Save the results after a battle is done
    log("保存收益截图，最多保存" + str(times) + "张，请按需清理")
    i = 0
    while i < times:
        temppath = './battlelog/result' + str(i) + '.png'
        if not os.path.isfile(temppath):
            getScreen(window, temppath)
            break
        else:
            i = i + 1
    time.sleep(0.5)

def timeoutEscape():
    # a dumb way to escape timeouts: spam esc many times.
    spamESC(10)

def leave_game(window):
    pressWithDelay('esc')
    '''getScreen(window=window,location=PATH)
    if not hasImage('backtobase',threshold=0.93):
        pressWithDelay('esc')'''
    time.sleep(1)
    click((640,498))
    time.sleep(1)
    click((580,468))
    time.sleep(10)

def WTScript(window):
    getScreen(window, PATH)
    windowName = window.title
    print(windowName)
    if not (windowName.__contains__("试") or windowName.__contains__("战") or windowName.__contains__("载")):
        # We are at the hanger. Have to enter a game first
        if hasImage("naval", 0.91, "未检测到海战！可能被阻挡或未调成海战"):
            #加入战斗的过程
            if hasImage("enterbattle", 0.95, None):
                click(getButtonLocation("enterbattle"))
                getScreen(window, PATH)
                if hasImage("downloadprompt", 0.98, None):
                    # If the texture download happens to be there, close it
                    click(getButtonLocation("downloadprompt"))
                    getScreen(window, PATH)
                    if hasImage("exitout", 0.92, None):
                        click(getButtonLocation(("exitout")))
                        getScreen(window, PATH)
                while window.title.__contains__("等"):
                    time.sleep(1)
                log("已进入海战！")
        elif hasImage("newshipresearched", 0.97, None):
            escapeBuying(window)
        elif hasImage("researchdone", 0.97, None):
            timeoutEscape()
        elif hasImage("autoresearch", 0.95, None):
            partsDone(window)
        elif hasImage("cancelsmall", 0.98, None):
            click(getButtonLocation("cancelsmall"))
        elif hasImage("exitout", 0.92, None):
            click(getButtonLocation("exitout"))
        else:
            timeoutEscape()
    elif windowName.__contains__("试"):
        # We are in testing mode. Under this mode it only fires to check if the attack pattern works
        print('界面为试驾，测试移动与攻击')
        stop_event = threading.Event()
        move_strategy_progress=threading.Thread(target=move_strategy,args=(stop_event,))
        move_strategy_progress.start()

        hide_obstacles_progress = threading.Thread(target=hide_obstacles,args=(stop_event,))
        hide_obstacles_progress.start()

        prevent_aground_progress = threading.Thread(target=prevent_aground,args=(stop_event,))
        prevent_aground_progress.start()
        while windowName.__contains__("试"):
            getScreen(window,location=PATH)
            if findtarget():
                attackPattern()
        stop_event.set()
        while hide_obstacles_progress.is_alive():
            print('waiting for hide_obstacles_progress to stop')
            time.sleep(1)
    elif windowName.__contains__("载"):
        # We are loading into one game
        print('界面正在载入')
        time.sleep(4)
    elif windowName.__contains__("战"):
        # We are currently in a game
        # First sleep for a while
        if hasImage("respawnship", 0.99, None) or hasImage("enteragain",0.99, None) or hasImage("youdied", 0.95, None):
                log("已死亡，返回主界面中")
                leave_game(window)
                return
        print('界面显示战斗开始，等待自动出生')
        # Then, let it auto spawn to avoid being locked on
        while True:
            getScreen(window, PATH)
            if not hasImage("spawn", 0.97, "等待中……"):
                break
            time.sleep(5)
        log("加入战斗")
        time.sleep(5)
        # After getting closer to the battlefield, start maneuvering
        print('开始机动')
        stop_event = threading.Event()
        move_strategy_progress=threading.Thread(target=move_strategy,args=(stop_event,))
        move_strategy_progress.start()

        hide_obstacles_progress = threading.Thread(target=hide_obstacles,args=(stop_event,))
        hide_obstacles_progress.start()

        prevent_aground_progress = threading.Thread(target=prevent_aground,args=(stop_event,))
        prevent_aground_progress.start()

        print('开火')
        i = 0
        # Lock on to the enemy and open fire
        while windowName.__contains__("战"):
            i = i + 1
            windowName = window.title
            i_findtarget=0
            while True:
                if findtarget():
                    i_findtarget=0
                    attackPattern()
                else:
                    i_findtarget+=1
                if i_findtarget>10:break

            getScreen(window,location=PATH)
            if i > 650:
                # try to escape
                log("炮弹应该打光了/出bug了")
                leave_game(window)
                break
            if hasImage("respawnship", 0.99, None) or hasImage("enteragain",0.99, None) or hasImage("youdied", 0.95, None):
                log("已死亡，返回主界面中")
                leave_game(window)
                break
        stop_event.set()
        while hide_obstacles_progress.is_alive() or prevent_aground_progress.is_alive():
            print('waiting for progress to stop')
            time.sleep(1)
        # game is over
        log("结束战斗，等待结算")
        # wait for the points
        time.sleep(10)
        getScreen(window, PATH)
        time.sleep(0.5)
        if hasImage("crates", 0.95, None):
            # unlocked crates
            log("===出了个箱子，记得查看背包===")
        pressWithDelay('esc')

def anchorWindow(window):
    # move war thunder to the top left of the screen
    global windowIsAnchored
    if windowIsAnchored:
        try:
            window.moveTo(0, 0)
            time.sleep(0.5)
        except:
            windowIsAnchored = False

def startScript():
    # detect if the current window is war thunder. If not, don't input anything to avoid accidents
    while True:
        try:
            window = pwc.getActiveWindow()
            if window is None:
                continue
            windowName = window.title
            if windowName.__contains__("War Thunder"):
                "Currently in War Thunder"
                anchorWindow(window)
                WTScript(window)
                time.sleep(0.5)
            else:
                "Currently not in War Thunder"
                print("未检测到战争雷霆！")
                time.sleep(3)

        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    isRunning = False
    window = sg.Window(title="海军舰船智驾系统", layout=layout)
    app = threading.Thread(target=startScript,daemon=True)
    while True:
        event, values = window.read()
        # End program if user closes window or
        # presses the OK button
        if event == "停止并退出" or event == sg.WIN_CLOSED:
            f.close()
            sys.exit()
        if event == "驱逐" and not isRunning:
            isRunning = True
            gotime = 40
            turntime = 5
            reloadtime = 4
            shoot_round = 3
            speed = 2
            log("开始运行")
            app.start()
        if event == "轻巡" and not isRunning:
            isRunning = True
            gotime = 80
            turntime = 15
            reloadtime = 8.5
            shoot_round = 1
            speed = 0
            log("开始运行")
            app.start()
        if event == "重巡" and not isRunning:
            isRunning = True
            gotime = 50
            turntime = 32
            log("开始运行")
            app.start()
        if event == "读取_t":
            turntime = values['-VAR_t-']
            print('变量 turntime 被修改为',turntime)
        if event == "读取_g":
            gotime = values['-VAR_g-']
            print('变量 gotime 被修改为',gotime)
        if event == "读取_r":
            reloadtime = values['-VAR_r-']
            print('变量 reloadtime 被修改为',reloadtime)
        if event == "读取_sr":
            shoot_round = values['-VAR_sr-']
            print('变量 shoot_round 被修改为',shoot_round)
        if event == "读取_sp":
            speed = values['-VAR_sp-']
            print('变量 speed 被修改为',speed)
        window['-VAR_t-'].update(float(turntime))
        window['-VAR_g-'].update(float(gotime))
        window['-VAR_r-'].update(float(reloadtime))
        window['-VAR_sr-'].update(int(shoot_round))
        window['-VAR_sp-'].update(int(speed))