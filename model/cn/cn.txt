import sys
import time
import keyboard
import pyautogui
import threading
import pywinctl as pwc
from PIL import Image
import cv2
import os.path
import PySimpleGUI as sg

PATH = "./pic/screenshot.png"
f = open('./battlelog/log.txt', 'a+')
menu = "战争雷霆苹果派助手简约（无高级功能）版：\n" \
       "▶图像设定：\n分辨率：1270x720  显示模式：窗口模式\n" \
       "▶主要参数->海战设置：\nAI攻击模式：任意目标  自动锁定目标：开\n" \
       "▶按键设置->海战：\n" \
       "目标跟踪（海战）：=\n手动瞄准修正：；\n停车：X\n" \
       "缩放轴：增加数值：\\\n缩放轴：相对轴量控制：开\n缩放轴：灵敏度：100%，步长：50%，乘数：2"

sg.theme('Reddit')

updateLog = [
    [sg.Text("免责申明：\n本软件是大学暑期图像识别基础课课上实践作业，\n没有用到高深技术，现结课后根据规定免费公开，\n请勿在技术学习范畴之外使用或售卖本软件，\n违者后果自负", key="-log-")]]

layout = [[sg.Text(menu)],
          [sg.Button("运行"), sg.VSeperator(), sg.Button("停止并退出")],
          [sg.Column(layout=updateLog, size=(300, 100))]]


def click(location):
    # click a certain location on the screen
    pyautogui.moveTo(location[0], location[1])
    time.sleep(0.2)
    pyautogui.mouseDown(button='left')
    time.sleep(0.2)
    pyautogui.mouseUp(button='left')


def log(message):
    # put the log in the GUI and the text log
    print(message)
    text = window["-log-"]
    text.update(message)
    curr_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    try:
        f.write("[" + curr_time + "] " + message + "\n")
    except:
        print("出现了日志写入错误，可能是计算机之间不同编码的问题吧？")


def hasImage(name, threshold, message):
    # returns true if the current screenshot has the desired image
    wholeWindow = cv2.imread(PATH)
    targetImg = cv2.imread("./model/" + name + ".png")
    "start matching"
    result = cv2.matchTemplate(wholeWindow, targetImg, cv2.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val > threshold:
        return True
    else:
        if message is not None:
            log(message)
        return False


def getButtonLocation(name):
    # get the button's location
    wholeWindow = cv2.imread(PATH)
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
    time.sleep(1)
    getScreen(window, PATH)
    click(getButtonLocation("researchdone"))
    time.sleep(3)
    getScreen(window, PATH)
    if hasImage("newshipreseached", 0.85, None):
        getScreen(window, PATH)
        time.sleep(1)
        click(getButtonLocation("shop"))
        time.sleep(1)
        getScreen(window, PATH)
        time.sleep(1)
        click(getButtonLocation("itemshop"))
        time.sleep(1)
        getScreen(window, PATH)
        time.sleep(1)
        click(getButtonLocation("exitout"))
        time.sleep(1)
        getScreen(window, PATH)
        time.sleep(1)
        pressWithDelay('esc', 0.1, 0.5)
        pressWithDelay('esc', 0.1, 0.5)
        pressWithDelay('esc', 0.1, 0.5)


def getScreen(window, location):
    # screenshot the current screen
    left, top = window.topleft
    right, bottom = window.bottomright
    pyautogui.screenshot(location)
    img = Image.open(location)
    img = img.crop((left + 10, top, right - 10, bottom - 10))
    img.save(location)


def pressWithDelay(c, d, t):
    # press the button c, for d seconds, and wait t seconds
    keyboard.press(c)
    time.sleep(d)
    keyboard.release(c)
    time.sleep(t)


def maneuverPattern():
    # Have the ship go forward, turn to the left, stop, then open fire
    time.sleep(15)
    keyboard.press('a')
    time.sleep(18)
    keyboard.press('x')
    time.sleep(10)
    keyboard.release('a')
    keyboard.release('x')


def attackPattern():
    # open fire at the enemy
    pressWithDelay('=', 0.1, 0.1)
    pressWithDelay('\\', 0.5, 0.1)
    pressWithDelay('=', 0.1, 0.5)
    pyautogui.mouseDown(button='left')
    time.sleep(0.4)
    pyautogui.mouseUp(button='left')
    pressWithDelay(';', 0.1, 0.1)
    pressWithDelay('=', 0.1, 1)
    pressWithDelay('=', 0.1, 1)


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
    pressWithDelay('esc', 0.1, 0.5)
    pressWithDelay('esc', 0.1, 0.5)
    pressWithDelay('esc', 0.1, 0.5)
    pressWithDelay('esc', 0.1, 0.5)
    pressWithDelay('esc', 0.1, 0.5)
    pressWithDelay('esc', 0.1, 0.5)
    pressWithDelay('esc', 0.1, 0.5)
    pressWithDelay('esc', 0.1, 0.5)
    pressWithDelay('esc', 0.1, 0.5)


def WTScript(window):
    getScreen(window, PATH)
    windowName = window.title
    print(windowName)
    if not (windowName.__contains__("试") or windowName.__contains__("战") or windowName.__contains__("载")):
        # We are at the hanger. Have to enter a game first
        if hasImage("naval", 0.91, "未检测到海战！请调成海战模式！"):
            if hasImage("enterbattle", 0.95, None):
                click(getButtonLocation("enterbattle"))
                time.sleep(5)
                getScreen(window, PATH)
                if hasImage("downloadprompt", 0.95, None):
                    # If the texture download happens to be there, close it
                    click(getButtonLocation("downloadprompt"))
                while window.title.__contains__("等"):
                    time.sleep(1)
                log("已进入海战！")
    elif windowName.__contains__("试"):
        # We are in testing mode. Under this mode it only fires to check if the attack pattern works
        attackPattern()
    elif windowName.__contains__("载"):
        # We are loading into one game
        time.sleep(4)
    elif windowName.__contains__("战"):
        # We are currently in a game
        # First sleep for a while
        time.sleep(25)
        getScreen(window, PATH)
        time.sleep(1)
        # Then, let it auto spawn to avoid being locked on
        while hasImage("spawn", 0.9, "等待中……"):
            getScreen(window, PATH)
            time.sleep(2)
        log("加入战斗")
        time.sleep(5)
        log("开始机动")
        # After getting closer to the battlefield, start maneuvering
        maneuverPattern()
        log("开火")
        i = 0
        # Lock on to the enemy and open fire
        while windowName.__contains__("战"):
            i = i + 1
            windowName = window.title
            attackPattern()
            getScreen(window, PATH)
            time.sleep(1)
            if i > 750:
                # Game is stuck, try to escape
                log("检测到卡死")
                timeoutEscape()
                getScreen(window, PATH)
                time.sleep(1)
            if hasImage("creates", 0.92, None):
                # unlocked crates
                log("出了个箱子，记得查看背包")
                getScreen(window, PATH)
                time.sleep(15)
                pressWithDelay('esc', 0.1, 0.5)
                break
            if hasImage("youdied", 0.95, None):
                # died before the game ended
                log("已死亡，返回主界面中，为防止网络情况卡死，等待15秒")
                getScreen(window, PATH)
                time.sleep(1)
                while hasImage("youdied", 0.94, None):
                    click(getButtonLocation("youdied"))
                    getScreen(window, PATH)
                    time.sleep(1)
                time.sleep(15)
                break
            if hasImage("respawn", 0.95, None):
                # died but has enough points for a respawn
                log("已死亡，但有分数")
                getScreen(window, PATH)
                time.sleep(0.5)
                click(getButtonLocation("respawn"))
                time.sleep(2)
                maneuverPattern()
        # game is over
        log("结束战斗，等待结算")
        # wait for the points
        time.sleep(20)
        getScreen(window, PATH)
        time.sleep(0.5)
        researchDone = False
        i = 0
        while not hasImage("gotobase", 0.92, None):
            i = i + 1
            if i > 30:
                log("检测到卡死")
                timeoutEscape()
                break
            time.sleep(1)
            getScreen(window, PATH)
            time.sleep(1)
            if hasImage("researchdone", 0.91, None):
                # new ship got researched. To avoid spending all SL, we glitch the research out
                researchDone = True
                log("解锁了配件或新船，将卡掉研发")
                log("如果需要购买或研发特定船只请暂停脚本")
                saveResults(window, 150)
                escapeBuying(window)
                break
            if hasImage("exitout", 0.91, None):
                click(getButtonLocation("exitout"))
        if not researchDone:
            saveResults(window, 150)
            getScreen(window, PATH)
            time.sleep(1)
            log("结算完成，返回主界面")
            click(getButtonLocation("gotobase"))
        time.sleep(5)
        getScreen(window, PATH)


def anchorWindow(window):
    # move war thunder to the top left of the screen
    window.moveTo(0, 0)
    time.sleep(0.5)


def detectWindow():
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
                log("未检测到战争雷霆！")
                time.sleep(3)

        except KeyboardInterrupt:
            break


def startScript():
    # start the whole script
    detectWindow()


if __name__ == '__main__':
    isRunning = False
    window = sg.Window(title="苹果派助手", layout=layout)
    app = threading.Thread(target=startScript, daemon=True)
    while True:
        event, values = window.read()
        # End program if user closes window or
        # presses the OK button
        if event == "停止并退出" or event == sg.WIN_CLOSED:
            f.close()
            sys.exit()
        if event == "运行" and not isRunning:
            isRunning = True
            log("开始运行")
            app.start()
