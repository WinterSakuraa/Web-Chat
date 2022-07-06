from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import run_async, run_js
import argparse

import asyncio

chat_msgs = []
online_users = set()
MAX_MESSAGES_COUNT = 100


def check_age(p):  # return None when the check passes, otherwise return the error message
    if p < 10:
        return 'Too young!!'


async def main():
    global chat_msgs

    put_markdown("## 🧊 Welcome to online chat")

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)

    user = await input_group("Enter chat", [
        input(required=True, name="name", placeholder="Your nickname", validate=lambda n:
              "Such nickname has already exist" if n in online_users or n == '📢' else None),
        input(required=True, name="age", type=NUMBER,
              placeholder="Your age", validate=check_age)
    ])
    online_users.add(user['name'])

    chat_msgs.append(('📢', f"`{user['name']}` entered the room"))
    msg_box.append(put_markdown(f"📢 `{user['name']}` entered the room"))

    refresh_task = run_async(refresh_msg(user['name'], msg_box))

    while True:
        data = await input_group("💬 New Message", [
            input(placeholder="Text", name="msg"),
            actions(name="cmd", buttons=[
                    "Send", {'label': "Leave the room", 'type': 'cancel'}])
        ], validate=lambda m: ('msg', "Enter text") if m["cmd"] == "Send" and not m['msg'] else None)

        if data is None:
            break

        msg_box.append(put_markdown(f"`{user['name']}` : {data['msg']}"))
        chat_msgs.append((user['name'], data['msg']))

    # exit chat
    refresh_task.close()

    online_users.remove(user['name'])
    toast("You have left the room")
    msg_box.append(put_markdown(f"📢 `{user['name']}` has left the room"))
    chat_msgs.append(('📢', f"`{user['name']}` has left the room"))

    put_buttons(['Rejoin'], onclick=lambda btn: run_js(
        'window.location.reload()'))


async def refresh_msg(user_name, msg_box):
    global chat_msgs
    last_idx = len(chat_msgs)

    while True:
        await asyncio.sleep(1)

        for m in chat_msgs[last_idx:]:
            if m[0] != user_name:  # if not a message from current user
                msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))

        if len(chat_msgs) > MAX_MESSAGES_COUNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]

        last_idx = len(chat_msgs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()

    start_server(main, port=args.port)
