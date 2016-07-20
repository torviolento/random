from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.common.exceptions import *
# from selenium.webdriver.support.ui import WebDriverWait
# import threading
import random


def wait_for(function, wait_time, *args, **kwargs):
    start_time = time.time()
    now_time = start_time
    storba = str(function).split("<")[1].replace("bound method", "").replace(
        "of", "")
    print("Waiting for", storba, "with arguments ", args, "for", wait_time,
          "seconds")
    while now_time <= start_time + wait_time:
        try:
            element = function(*args, **kwargs)
            if element:
                print("Wait over in time {}s".format(now_time - start_time))
                return element
            else:
                pass
            now_time = time.time()
        except NoSuchElementException:
            pass
        except ElementNotSelectableException:
            pass
    return None


class Chat:
    def __init__(self, browser=None):
        if not browser:
            print('Opening Firefox')
            browser = webdriver.Firefox()
        self.browser = browser
        self.disco_btn = None
        self.textArea = None
        self.msg_handler = MessageHandler(self)

    def go_omegle(self, new_tab=False):
        print('Going Omegle')

        # go to Omegle
        if new_tab:
            # Todo: Make browser open new tab and open chat there
            pass

        self.browser.get('http://www.omegle.com/')

        # Start new chat on first page
        self.browser.find_element_by_id('textbtn').click()

        time.sleep(1)
        self.textArea = wait_for(
            self.browser.find_element_by_class_name, 5, 'chatmsg')

    def sen_dold(self, msg):
        self.textArea.send_keys(msg + Keys.RETURN)

    def send(self, msg):
        self.textArea.click()
        for i in msg:
            self.textArea.send_keys(i)
            time.sleep(0.05)
        self.textArea.send_keys(Keys.RETURN)

    def new_chat(self, self_disconnect=0):
        self.disco_btn = wait_for(self.browser.find_element_by_class_name, 5,
            'disconnectbtn')
        # Todo: Make alternative work when partner disconnects
        if self_disconnect:
            self.disco_btn.click()
        self.disco_btn.click()
        self.msg_handler.new_chat()


class MessageHandler:
    def __init__(self, parent):
        self.parent = parent
        self.browser = self.parent.browser
        self.log_box = None
        self.msgs = []
        self.old_len = 0

    def new_chat(self):
        self.log_box = wait_for(
            self.browser.find_element_by_class_name,10, 'logbox')

        # Old length of all messages
        self.old_len = 0

    def is_new_msgs(self):
        if len(self.msgs) > self.old_len:
            return 1
        else:
            return 0

    def get_msgs(self):
        matchbox = []
        self.msgs = self.log_box.find_elements_by_class_name('logitem')

        new_msg_amount = len(self.msgs) - self.old_len
        if new_msg_amount > 0:
            for msg in self.msgs[-new_msg_amount:]:
                # print(msg.text.replace("\u2022", "#!#"))
                try:
                    msg_type = msg.find_element_by_tag_name('p').get_attribute(
                        'class')

                    if msg_type in ('strangermsg', 'youmsg',):
                        matchbox.append((msg_type, msg.text))
                    elif msg_type == 'statuslog':
                        if "\u2022" in msg.text:
                            print("#", msg.text.replace("\u2022", "[]"))
                        elif "Stranger has disconnected." in msg.text or\
                             "You have disconnected" in msg.text:
                            if matchbox:
                                print("Chat closed: Remaining messages: ",
                                      *map((lambda x: x+"\n"), *matchbox))
                            else:
                                print("Chat closed")
                            return False
                        else:
                            matchbox.append((msg_type, msg.text))
                            pass
                    self.old_len = len(self.msgs)
                except NoSuchElementException:
                    print("Chat closed")
                    return False
                except StaleElementReferenceException:
                    print("Chat closed")
                    return False
                return matchbox

    def get_new_msgs(self):
        matchbox = []
        self.msgs = self.log_box.find_elements_by_class_name('logitem')

        new_msg_amount = len(self.msgs) - self.old_len

        if new_msg_amount > 0:
            for msg in self.msgs[-new_msg_amount:]:
                # print(msg.text.replace("\u2022", "#!#"))
                msg_type = msg.find_element_by_tag_name('p').get_attribute(
                    'class')
                matchbox.append((msg_type, msg.text))
        return matchbox

    def get_msgs_generator(self):

            self.msgs = self.log_box.find_elements_by_class_name('logitem')
            new_msg_amount = len(self.msgs) - self.old_len
            last_found = None
            while new_msg_amount > 0:
                print(new_msg_amount)
                for msg in self.msgs[-new_msg_amount:]:
                    # print(msg.text.replace("\u2022", "#!#"))
                    msg_type = msg.find_element_by_tag_name('p').get_attribute(
                        'class')
                    yield (msg_type, msg.text)
                    if msg == last_found):
                        new_msg_amount = 0
    class Msgs_iterator(object):
        def __init__(self, chat):
            self.last_found = None
            self.matchbox = []
            self.chat = chat
        def __iter__(self):
            return self

        def __next__(self):
            # todo: Make some sense
            # if there are found messages already return them first
            reply = self.matchbox.pop()
            if reply:
                return reply
            else:
                msgs = self.chat.log_box.find_elements_by_class_name('logitem')

                # if first run then the first found message is returned and saved to self.last_found
                if self.last_found is None:
                    self.last_found = msgs[0]
                    return self.last_found
                else:
                    for msg in self.msgs[::-1]:
                        if msg == self.last_found:
                            self.last_found = self.matchbox.pop()
                            self.matchbox.reverse()
                            return self.last_found
                        else:
                            self.matchbox.append(msg)


def interactive():
    print("Interactive python. Ctrl-C to exit")
    while 1:
        try:
            exec(input(">> "))
        except KeyboardInterrupt:
            break
        except BaseException as e:
            print(e)


def main():
    # todo: put all chat closed reakted exceptions to here, or dont
    browser = webdriver.Firefox()

    psatti = Chat(browser)
    psatti.go_omegle()
    psatti.send(random.choice(("Hi", "Hey", "Hello!", "Hi are you a bot?")))
    psatti.msg_handler.new_chat()
    time.sleep(1)
    # msgs = psatti2.msg_handler.get_msgs()
    while 1:
        try:
            msgs = psatti.msg_handler.get_msgs_generator()
            for msg in msgs:
                print("# {}: {} #".format(*msg))
                send_back(psatti, msg)
            time.sleep(1)
        except NoSuchWindowException:
            print("Window closed, bye")
            break
        except UnexpectedAlertPresentException:
            print("Window closed bye")
            break

        except NoSuchElementException:
            print("Chat closed")
            psatti.new_chat()

        except StaleElementReferenceException:
            print("Chat closed")
            psatti.new_chat()


def send_back(psatti, msgs):

    for msg in msgs:
        if msg[0] == "strangermsg":

            a = list(msg[1].replace("Stranger: ", ""))
            if len(a)>0:
                random.shuffle(a)
                psatti.send("".join(a))

if __name__ == "__main__":
    main()
